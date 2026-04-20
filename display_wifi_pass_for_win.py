'''
python： 3.12
os：win11

author: bibo19842003
date：2026-04-20
version：v1.0

描述：获取Windows上已连接过的WiFi名称和密码
'''



import subprocess
import re

def get_wifi_passwords():
    """
    获取Windows上已连接过的WiFi名称和密码
    """
    wifi_list = []
    
    try:
        # 获取所有WiFi配置文件
        command_output = subprocess.run(
            ["netsh", "wlan", "show", "profiles"], 
            capture_output=True
        ).stdout.decode('gbk', errors='replace')
        
        # 提取WiFi名称（逐行解析）
        profile_names = []
        for line in command_output.split('\n'):
            line = line.strip()
            if line.startswith('所有用户配置文件'):
                # 提取WiFi名称
                parts = line.split(':', 1)
                if len(parts) == 2:
                    ssid = parts[1].strip()
                    if ssid:
                        profile_names.append(ssid)
        
        if not profile_names:
            print("未找到WiFi配置文件")
            return []
        
        for name in profile_names:
            # 获取密码信息
            profile_info_pass = subprocess.run(
                ["netsh", "wlan", "show", "profile", name, "key=clear"], 
                capture_output=True
            ).stdout.decode('gbk', errors='replace')
            
            password = "获取失败"
            # 逐行解析获取密码
            for line in profile_info_pass.split('\n'):
                line = line.strip()
                if '关键内容' in line or 'Key Content' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        password = parts[1].strip()
                        break
            
            wifi_list.append({
                "SSID": name,
                "密码": password
            })
                    
    except Exception as e:
        print(f"获取WiFi信息时出错: {e}")
    
    return wifi_list

def display_wifi_table(wifi_list):
    """
    以表格形式显示WiFi信息
    """
    if not wifi_list:
        return
    
    print("=" * 80)
    print("\nWindows 已连接WiFi密码列表")
    print("=" * 80)
    
    # 计算最大宽度
    max_ssid_len = max(len(wifi["SSID"]) for wifi in wifi_list)
    max_pass_len = max(len(wifi["密码"]) for wifi in wifi_list)
    max_ssid_len = max(max_ssid_len, len("WiFi名称 (SSID)"))
    max_pass_len = max(max_pass_len, len("密码"))
    
    # 打印表头
    print(f"│ {'WiFi名称 (SSID)':<{max_ssid_len}} │ {'密码':<{max_pass_len}} │")
    print(f"├{'─' * (max_ssid_len + 2)}┼{'─' * (max_pass_len + 2)}┤")
    
    # 打印数据
    for wifi in wifi_list:
        print(f"│ {wifi['SSID']:<{max_ssid_len}} │ {wifi['密码']:<{max_pass_len}} │")
    
    print("=" * 80)
    print(f"总计: {len(wifi_list)} 个WiFi配置")
    print("=" * 80)

if __name__ == "__main__":
    print("正在获取WiFi信息...")
    wifi_list = get_wifi_passwords()
    display_wifi_table(wifi_list)

