'''
python： 3.12
os：win11

wxauto4：41.1.2

author: bibo19842003
date：2026-04-20
version：v1.0

描述：用于微信电脑端指定用户/群消息的回复
备注: 未找到项目的开源代码，仅用于学习和测试
'''

import time
import threading
from wxauto4 import WeChat



wx = WeChat(ads=False)

# 查看所有方法和属性
print("=== wx 对象所有可用方法/属性 ===")
for item in dir(wx):
    if not item.startswith('_'):  # 过滤掉内部私有方法
        print(item)

# 切换到你要监听的聊天对象
# wx.ChatWith("饺子")
wx.ChatWith("二宝宝的账号")


def listen_messages():
    while True:
        msgs = wx.GetAllMessage()
        if msgs:
            last_msg = msgs[-1]
            if last_msg.content == "111":
                wx.SendMsg(f'{last_msg.content} \n 你好 hello 啦啦啦 \n @{last_msg.sender}')
        time.sleep(3)

listener_thread = threading.Thread(target=listen_messages, daemon=True)
listener_thread.start()

listener_thread.join()
