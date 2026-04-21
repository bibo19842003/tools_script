'''
python： 3.12
os：win11

author: bibo19842003
date：2026-04-21
version：v1.0

描述：获取Windows电脑详细硬件信息
'''

import subprocess
import platform
import psutil
import socket
import uuid
import re
from datetime import datetime

def run_cmd(command):
    """执行命令并返回输出"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.decode('gbk', errors='replace') if isinstance(result.stdout, bytes) else result.stdout
    except Exception as e:
        return f"获取失败: {e}"

def get_cpu_info():
    """获取CPU信息"""
    print("\n" + "=" * 80)
    print("【CPU 信息】")
    print("=" * 80)
    
    info = {
        "名称": platform.processor(),
        "物理核心数": psutil.cpu_count(logical=False),
        "逻辑核心数": psutil.cpu_count(logical=True),
        "当前频率": f"{psutil.cpu_freq().current:.2f} MHz" if psutil.cpu_freq() else "不支持",
        "最大频率": f"{psutil.cpu_freq().max:.2f} MHz" if psutil.cpu_freq() else "不支持",
        "最小频率": f"{psutil.cpu_freq().min:.2f} MHz" if psutil.cpu_freq() else "不支持",
        "CPU使用率": f"{psutil.cpu_percent(interval=1)}%",
    }
    
    # 尝试获取更多CPU信息
    cmd_output = run_cmd("wmic cpu get Name,MaxClockSpeed,CurrentClockSpeed,NumberOfCores,NumberOfLogicalProcessors /value")
    for line in cmd_output.split('\n'):
        if '=' in line:
            key_value = line.split('=', 1)
            if len(key_value) == 2:
                key = key_value[0].strip()
                value = key_value[1].strip()
                if key == "MaxClockSpeed":
                    info["最大时钟速度"] = f"{value} MHz"
                elif key == "CurrentClockSpeed":
                    info["当前时钟速度"] = f"{value} MHz"
    
    for key, value in info.items():
        print(f"{key}: {value}")

def get_memory_manufacturer_from_partnumber(partnumber):
    """
    根据内存型号识别颗粒厂商
    规则来源：玩家已破解的金士顿、芝奇、海盗船、英睿达 颗粒后缀编码
    """
    if not partnumber:
        return "未知"

    partnumber = partnumber.upper().strip()

    # ==================== 品牌前缀识别 ====================
    # Kingston FURY 系列前缀
    if partnumber.startswith("KF"):
        brand = "金士顿 (Kingston FURY)"
    elif partnumber.startswith("KVR"):
        brand = "金士顿 (Kingston)"
    elif partnumber.startswith("F4"):
        brand = "芝奇 (G.SKILL)"
    elif partnumber.startswith("CM"):
        brand = "海盗船 (Corsair)"
    elif partnumber.startswith("CP"):
        brand = "海盗船 (Corsair)"
    elif partnumber.startswith("BL"):
        brand = "英睿达 (Crucial/镁光)"
    elif partnumber.startswith("CT"):
        brand = "英睿达 (Crucial/镁光)"
    else:
        brand = None

    # ==================== 金士顿颗粒后缀（末尾字母） ====================
    # Kingston / Kingston FURY DDR4
    # X = Micron（镁光）, S = Samsung（三星）, H = SK Hynix（海力士）, N = Nanya（南亚）, C = CXMT（长鑫）
    if brand in ["金士顿 (Kingston FURY)", "金士顿 (Kingston)"]:
        if partnumber.endswith("X"):
            return "Micron（镁光）"
        elif partnumber.endswith("S"):
            return "Samsung（三星）"
        elif partnumber.endswith("H"):
            return "SK Hynix（海力士）"
        elif partnumber.endswith("N"):
            return "Nanya（南亚）"
        elif partnumber.endswith("C"):
            return "CXMT（长鑫）"

    # ==================== 芝奇颗粒后缀（末尾4位/2位） ====================
    # G.SKILL DDR4 格式：F4-3200C16D-16GVK → VK 或 F4-3600C17D-16GTZ → TZ
    if brand == "芝奇 (G.SKILL)":
        # 提取末尾4位（去掉分隔符后的最后4个字母）
        clean_part = partnumber.replace("-", "").replace("_", "")
        suffix_4 = clean_part[-4:] if len(clean_part) >= 4 else clean_part
        suffix_2 = clean_part[-2:] if len(clean_part) >= 2 else clean_part

        # Samsung（三星）
        if suffix_4 in ["10BC", "10CB", "10D", "10ND"]:
            return "Samsung B-die（三星）"
        elif suffix_4 in ["10CC", "10CR"]:
            return "Samsung C-die（三星）"

        # SK Hynix（海力士）
        elif suffix_4 in ["20CR", "21CR", "20CK", "21CK"]:
            return "SK Hynix CJR（海力士）"
        elif suffix_4 in ["20JR", "21JR", "20JK", "21JK"]:
            return "SK Hynix JJR（海力士）"

        # Micron（镁光）
        elif suffix_4 in ["30XR", "31XR", "30X", "31X"]:
            return "Micron D9/C9（镁光）"
        elif suffix_4 in ["33XR", "33X"]:
            return "Spectek 大S（镁光降级片）"

        # Nanya（南亚）
        elif suffix_4 in ["60NR", "61NR", "60N", "61N"]:
            return "Nanya（南亚）"

        # CXMT（长鑫）
        elif suffix_4 in ["70CR", "71CR", "70C", "71C"]:
            return "CXMT（长鑫）"

    # ==================== 海盗船颗粒版本号（Ver x.xx） ====================
    # Corsair DDR4，看标签上 Ver x.xx
    # Ver 3.xx = Micron/Spectek（镁光系）
    # Ver 4.xx = Samsung（三星）
    # Ver 5.xx = SK Hynix（海力士）
    if brand == "海盗船 (Corsair)":
        # 检查是否包含 Ver 标记
        if "VER" in partnumber:
            # 格式：Ver 3.20 或 ver3.20
            import re
            ver_match = re.search(r'[Vv][Ee][Rr]\s*(\d)\.(\d+)', partnumber)
            if ver_match:
                major = ver_match.group(1)
                minor = ver_match.group(2)
                if major == "3":
                    return f"Micron/Spectek（镁光系）Ver {major}.{minor}"
                elif major == "4":
                    return f"Samsung（三星）Ver {major}.{minor}"
                elif major == "5":
                    return f"SK Hynix（海力士）Ver {major}.{minor}"

    # ==================== 通用 SPD 颗粒编码（M/T/K开头） ====================
    # 这是模组厂商自己加的前缀，不代表 DRAM 颗粒厂商
    # M3/M4/M5 = Samsung（三星）
    if partnumber.startswith("M3") or partnumber.startswith("M4") or partnumber.startswith("M5"):
        return "Samsung（三星）- M系列"
    # K4/K5 = Samsung（三星）
    elif partnumber.startswith("K4") or partnumber.startswith("K5"):
        return "Samsung（三星）- K系列"

    # H9/H8/HT = SK Hynix（海力士）
    elif partnumber.startswith("H9") or partnumber.startswith("H8") or partnumber.startswith("HT"):
        return "SK Hynix（海力士）"

    # MTA/MT = Micron（镁光）
    elif partnumber.startswith("MTA") or partnumber.startswith("MT"):
        return "Micron（镁光）"
    # D9 = Micron（镁光）
    elif partnumber.startswith("D9"):
        return "Micron D9（镁光）"

    # NT = Nanya（南亚）
    elif partnumber.startswith("NT"):
        return "Nanya（南亚）"

    # 无法识别
    return "未知（可能为小厂或特殊编码）"

def get_memory_info():
    """获取内存信息"""
    print("\n" + "=" * 80)
    print("【内存 信息】")
    print("=" * 80)
    
    mem = psutil.virtual_memory()
    print(f"物理内存总量: {mem.total / (1024**3):.2f} GB")
    print(f"已使用内存: {mem.used / (1024**3):.2f} GB")
    print(f"可用内存: {mem.available / (1024**3):.2f} GB")
    print(f"内存使用率: {mem.percent}%")
    
    # 交换内存
    swap = psutil.swap_memory()
    print(f"\n交换内存总量: {swap.total / (1024**3):.2f} GB")
    print(f"交换内存使用率: {swap.percent}%")
    
    # 详细内存信息
    print("\n--- 内存条详细信息 ---")
    cmd_output = run_cmd("wmic memorychip get Capacity,Speed,Manufacturer,PartNumber,SMBIOSMemoryType /value")
    mem_count = 0
    for line in cmd_output.split('\n'):
        if '=' in line:
            key_value = line.split('=', 1)
            if len(key_value) == 2:
                key = key_value[0].strip()
                value = key_value[1].strip()
                if key == "Capacity":
                    mem_count += 1
                    print(f"\n内存条 {mem_count}:")
                    print(f"  容量: {int(value) / (1024**3):.2f} GB")
                elif key == "Speed":
                    print(f"  速度: {value} MHz")
                elif key == "Manufacturer":
                    print(f"  制造商: {value}")
                elif key == "PartNumber":
                    print(f"  型号: {value}")
                    颗粒厂商 = get_memory_manufacturer_from_partnumber(value)
                    print(f"  颗粒厂商: {颗粒厂商}")
                elif key == "SMBIOSMemoryType":
                    type_map = {"20": "DDR", "21": "DDR2", "24": "DDR3", "26": "DDR4", "34": "DDR5"}
                    print(f"  类型: {type_map.get(value, value)}")

def get_disk_info():
    """获取磁盘信息"""
    print("\n" + "=" * 80)
    print("【磁盘 信息】")
    print("=" * 80)
    
    # 分区信息
    print("--- 磁盘分区 ---")
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            print(f"\n驱动器: {partition.device}")
            print(f"  分区类型: {partition.fstype}")
            print(f"  总容量: {usage.total / (1024**3):.2f} GB")
            print(f"  已用: {usage.used / (1024**3):.2f} GB")
            print(f"  可用: {usage.free / (1024**3):.2f} GB")
            print(f"  使用率: {usage.percent}%")
        except:
            continue
    
    # 物理磁盘
    print("\n--- 物理磁盘 ---")
    cmd_output = run_cmd("wmic diskdrive get Model,Size,SerialNumber,MediaType /value")
    for line in cmd_output.split('\n'):
        if '=' in line:
            key_value = line.split('=', 1)
            if len(key_value) == 2:
                key = key_value[0].strip()
                value = key_value[1].strip()
                if key == "Model":
                    print(f"\n磁盘型号: {value}")
                elif key == "Size":
                    print(f"  容量: {int(value) / (1024**3):.2f} GB")
                elif key == "SerialNumber":
                    print(f"  序列号: {value}")
                elif key == "MediaType":
                    print(f"  介质类型: {value}")

def get_gpu_info():
    """获取显卡信息"""
    print("\n" + "=" * 80)
    print("【显卡 信息】")
    print("=" * 80)
    
    cmd_output = run_cmd("wmic path win32_VideoController get Name,AdapterRAM,DriverVersion,CurrentRefreshRate /value")
    gpu_count = 0
    for line in cmd_output.split('\n'):
        if '=' in line:
            key_value = line.split('=', 1)
            if len(key_value) == 2:
                key = key_value[0].strip()
                value = key_value[1].strip()
                if key == "Name":
                    gpu_count += 1
                    print(f"\n显卡 {gpu_count}: {value}")
                elif key == "AdapterRAM":
                    if value and value != "0":
                        print(f"  显存: {int(value) / (1024**3):.2f} GB")
                elif key == "DriverVersion":
                    print(f"  驱动版本: {value}")
                elif key == "CurrentRefreshRate":
                    print(f"  当前刷新率: {value} Hz")

def get_network_info():
    """获取网络信息"""
    print("\n" + "=" * 80)
    print("【网络 信息】")
    print("=" * 80)
    
    # MAC地址
    print("\n--- MAC地址 ---")
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 2)][::-1])
    print(f"MAC地址: {mac}")
    
    # 计算机名和IP
    print("\n--- 网络配置 ---")
    hostname = socket.gethostname()
    print(f"计算机名: {hostname}")
    
    # 获取所有网络接口
    cmd_output = run_cmd("ipconfig /all")
    current_adapter = None
    for line in cmd_output.split('\n'):
        line = line.strip()
        if line and not line.startswith(' '):
            if '适配器' in line or 'adapter' in line.lower():
                current_adapter = line.split('适配器')[0].split('adapter')[0].strip() if '适配器' in line else line.split('adapter')[0].strip()
                print(f"\n适配器: {current_adapter}")
        elif '=' in line:
            key_value = line.split(':', 1)
            if len(key_value) == 2:
                key = key_value[0].strip()
                value = key_value[1].strip()
                if 'IPv4' in key or 'IP' in key:
                    print(f"  IP地址: {value}")
                elif '子网掩码' in key or 'Subnet' in key:
                    print(f"  子网掩码: {value}")
                elif '默认网关' in key or 'Default Gateway' in key:
                    print(f"  默认网关: {value}")
                elif 'DNS' in key:
                    print(f"  DNS: {value}")
                elif 'MAC' in key and '媒体' not in key:
                    print(f"  MAC地址: {value}")

def get_motherboard_info():
    """获取主板信息"""
    print("\n" + "=" * 80)
    print("【主板 信息】")
    print("=" * 80)
    
    cmd_output = run_cmd("wmic baseboard get Manufacturer,Product,SerialNumber,Version /value")
    for line in cmd_output.split('\n'):
        if '=' in line:
            key_value = line.split('=', 1)
            if len(key_value) == 2:
                key = key_value[0].strip()
                value = key_value[1].strip()
                if key == "Manufacturer":
                    print(f"制造商: {value}")
                elif key == "Product":
                    print(f"产品名称: {value}")
                elif key == "SerialNumber":
                    print(f"序列号: {value}")
                elif key == "Version":
                    print(f"版本: {value}")
    
    # BIOS信息
    print("\n--- BIOS 信息 ---")
    cmd_output = run_cmd("wmic bios get Manufacturer,SerialNumber,SMBIOSBIOSVersion,ReleaseDate /value")
    for line in cmd_output.split('\n'):
        if '=' in line:
            key_value = line.split('=', 1)
            if len(key_value) == 2:
                key = key_value[0].strip()
                value = key_value[1].strip()
                if key == "Manufacturer":
                    print(f"BIOS制造商: {value}")
                elif key == "SMBIOSBIOSVersion":
                    print(f"BIOS版本: {value}")
                elif key == "SerialNumber":
                    print(f"BIOS序列号: {value}")
                elif key == "ReleaseDate":
                    print(f"发布日期: {value}")

def get_system_info():
    """获取系统信息"""
    print("\n" + "=" * 80)
    print("【系统 信息】")
    print("=" * 80)
    
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"版本: {platform.version()}")
    print(f"架构: {platform.machine()}")
    print(f"处理器: {platform.processor()}")
    print(f"计算机名: {socket.gethostname()}")
    print(f"当前用户: {psutil.users()[0].name if psutil.users() else '未知'}")
    
    # 开机时间
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    now = datetime.now()
    uptime = now - boot_time
    print(f"开机时间: {boot_time}")
    print(f"运行时长: {uptime.days}天 {uptime.seconds // 3600}小时 {(uptime.seconds % 3600) // 60}分钟")

def get_monitor_info():
    """获取显示器信息"""
    print("\n" + "=" * 80)
    print("【显示器 信息】")
    print("=" * 80)
    
    cmd_output = run_cmd("wmic desktopmonitor get Name,ScreenWidth,ScreenHeight,MonitorType /value")
    for line in cmd_output.split('\n'):
        if '=' in line:
            key_value = line.split('=', 1)
            if len(key_value) == 2:
                key = key_value[0].strip()
                value = key_value[1].strip()
                if key == "Name":
                    print(f"显示器名称: {value}")
                elif key == "ScreenWidth":
                    print(f"屏幕宽度: {value} 像素")
                elif key == "ScreenHeight":
                    print(f"屏幕高度: {value} 像素")
                elif key == "MonitorType":
                    print(f"显示器类型: {value}")

def get_battery_info():
    """获取电池信息"""
    print("\n" + "=" * 80)
    print("【电池 信息】")
    print("=" * 80)
    
    battery = psutil.sensors_battery()
    if battery:
        print(f"电池状态: {'已连接电源' if battery.power_plugged else '未连接电源'}")
        print(f"电池百分比: {battery.percent}%")
        if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
            hours = battery.secsleft // 3600
            minutes = (battery.secsleft % 3600) // 60
            print(f"剩余时间: {hours}小时 {minutes}分钟")
        else:
            print("剩余时间: 无限")
    else:
        print("无电池（台式机）")

def get_usb_info():
    """获取USB设备信息"""
    print("\n" + "=" * 80)
    print("【USB 设备】")
    print("=" * 80)
    
    cmd_output = run_cmd("wmic path Win32_USBControllerDevice get Dependent /value")
    devices = set()
    for line in cmd_output.split('\n'):
        if '=' in line:
            value = line.split('=', 1)[1].strip()
            if value:
                # 提取设备名称
                if 'Device' in value:
                    parts = value.split('Device.')
                    if len(parts) > 1:
                        device_name = parts[1].replace('"', '').split('.')[0]
                        devices.add(device_name)
    
    for i, device in enumerate(sorted(devices), 1):
        print(f"{i}. {device}")

def get_printer_info():
    """获取打印机信息"""
    print("\n" + "=" * 80)
    print("【打印机 信息】")
    print("=" * 80)
    
    cmd_output = run_cmd("wmic printer get Name,PortName,DriverName,Default /value")
    for line in cmd_output.split('\n'):
        if '=' in line:
            key_value = line.split('=', 1)
            if len(key_value) == 2:
                key = key_value[0].strip()
                value = key_value[1].strip()
                if key == "Name":
                    print(f"\n打印机: {value}")
                elif key == "PortName":
                    print(f"  端口: {value}")
                elif key == "DriverName":
                    print(f"  驱动: {value}")
                elif key == "Default":
                    print(f"  默认打印机: {'是' if value == 'TRUE' else '否'}")

def main():
    print("=" * 80)
    print(" " * 20 + "Windows 硬件信息获取工具")
    print("=" * 80)
    print(f"获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    get_system_info()
    get_cpu_info()
    get_memory_info()
    get_disk_info()
    get_gpu_info()
    get_network_info()
    get_motherboard_info()
    get_monitor_info()
    get_battery_info()
    get_usb_info()
    get_printer_info()
    
    print("\n" + "=" * 80)
    print("硬件信息获取完成")
    print("=" * 80)

if __name__ == "__main__":
    main()
