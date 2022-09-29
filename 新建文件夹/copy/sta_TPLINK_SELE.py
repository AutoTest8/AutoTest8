import json
import re
import os
import subprocess
import time
import mars
import traceback
from abc import ABCMeta, abstractmethod

# ========= 用户设置参数 ===========
#本测试脚本是基于TPLink:TL-WDR7400 AC1750双频路由器 编写（不同路由器设置有差异）
router = "tlwr886n"
# 路由器登录相关信息
router_username = "admin"
router_password = "AAbbcc123"
# host = "192.168.1.1"
host = "tplogin.cn"
wireless_setting = "2.4G"
# ap热点名字
ap_name = "tlwr886n"
ap_pwd = "123456789"
# tplink 待设置参数
channel=[1, 6, 11] # 1--13
# mode=["0","1","2","3","4"] # bgn  bg n g b
mode=["0"] # bgn  bg n g b
bandwidth=["1"]  #自动/20
ssidbrd=[1]  # 0为隐藏  1为可见


def check_rndis_exist():
    cmd = os.popen("ipconfig -all")
    result = cmd.read()
    result = str(result)
    if result.find("NDIS") != -1:
        mars.Print("rndis -----exist")
    else:
        for i in range(5):
            mars.Print("send at retry check rndis")
            mars.SendAT('at+log=15,1', 1000, 1)
            atResp = mars.WaitAT('OK', False, 10000)
            if atResp:
                mars.Print("at+log=15,1 success")
                time.sleep(5)
                mars.SendAT('at+log=15,0', 1000, 1)
                atResp = mars.WaitAT('OK', False, 10000)
                if atResp:
                    mars.Print("at+log=15,0 success")
                    time.sleep(15)
            cmd = os.popen("ipconfig -all")
            result = cmd.read()
            result = str(result)
            if result.find("NDIS") != -1:
                mars.Print("rndis -----exist")
                break
            else:
                if i == 4:
                    mars.Verdict("fail", "rndis -----not exist--------")
                continue



class RouterBase(metaclass=ABCMeta):
    @abstractmethod
    def login_ap(self, host, router_username, router_password):
        pass
    @abstractmethod
    def set_encryption_ap(self, wireless_setting, ssid="1", pwd="", enum_list=None):
        pass
    @abstractmethod
    def set_no_encryption_ap(self, wireless_setting, ssid="", pwd="", enum_list=None):
        pass

class TPLinkBase(RouterBase):
    def __init__(self):
        self.host = ""
        self.login_info = []
        self.headers = {}
        self.router_username = ""
        self.router_password = ""


def run():
    check_rndis_exist()
    # 获取可遍历参数
    obj_json = []
    for c in channel:
        for m in mode:
            for b in bandwidth:
                for s in ssidbrd:
                    list = [c, m, b, s]
                    obj_json.append(list)
    mars.Print("sta_TPLink_channel_encryption test begin")
    mars.Print("obj_json %s" %obj_json)




if __name__ == '__main__':
    run()