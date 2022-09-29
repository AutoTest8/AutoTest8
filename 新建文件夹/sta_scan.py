#!/usr/bin/env python
# coding:utf-8
"""
Name  : sta_scan.py
Author: zhf
Time  : 2021/11/16 17:53
Desc  :
        1.open sta
        2.scan at+wifi=wifi_scan,check at response
        3.Traversal test(channel, encryption)
        4.scan ap
        5.close sta
"""
import os
import traceback
import mars
import time
import json
import subprocess
from urllib import request
from abc import ABCMeta, abstractmethod
from wifilib import heron_wifi

# ========= 用户设置参数 ===========
#本测试脚本是基于TPLink:TL-WDR7400 AC1750双频路由器 编写（不同路由器设置有差异）
# router = "tlwr886n"
# 路由器登录相关信息
router_username = "admin"
router_password = "AAbbcc123"
# host = "192.168.1.1"
host = "tplogin.cn"
wireless_setting = "2.4G"
# ap热点名字
ap_name = "tlwr886n"     ###路由器名称SSID
ap_pwd = "123456789"     ###路由器密码
# tplink 待设置参数
channel=[1,6,11] # 1--13
mode=["0","1","2","3","4"] # bgn  bg n g b
bandwidth=["1"]  #20
ssidbrd=[1]  # 0为隐藏  1为可见

class RouterBase(metaclass=ABCMeta):
    @abstractmethod
    def login_ap(self):
        pass
    @abstractmethod
    def set_encryption_ap(self):
        pass
    @abstractmethod
    def set_no_encryption_ap(self):
        pass

class TPLinkBase(RouterBase):
    def __init__(self):
        self.host = ""
        self.login_info = []
        self.headers = {}
        self.router_username = ""
        self.router_password = ""

    def login_ap(self, host, router_username, router_password):
        """获取stok"""
        self.host = host
        self.router_username = router_username
        self.router_password = router_password
        self.headers = {
            'Origin': r'http://{0}'.format(self.host),
            'Accept-Encoding': r'Accept-Encoding: gzip, deflate',
            'Accept-Language': r'en-US,en;q=0.9',
            'User-Agent': r'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)Ubuntu Chromium/64.0.3282.167 Chrome/64.0.3282.167 Safari/537.36',
            'Content-Type': r'application/json; charset=UTF-8',
            'Accept': r'application/json, text/javascript, */*; q=0.01',
            'Referer': r'http://{0}/'.format(self.host),
            'X-Requested-With': r'XMLHttpRequest',
            'Connection': r'keep-alive',
        }
        url = r'http://{0}/'.format(self.host)
        data = {
            "method": "do",
            "login": {
                "password": "408yB04wBTefbwK"
            }
        }
        data_byte = bytes(json.dumps(data), 'utf-8')
        req = request.Request(url, headers=self.headers, data=data_byte)
        respones = request.urlopen(req).read().decode('utf-8')
        infos = json.loads(respones)
        if isinstance(infos, dict):
            temp_stok = {}
            temp_stok.setdefault("stok", infos["stok"])
            self.login_info.append(temp_stok)
            mars.Print(str(self.login_info))
        else:
            mars.Print("login fail")
            # raise TPLinkBaseException("login {0} fail".format(self.host))

    def request_router(self, data_byte, mars=None):
        """请求设置参数"""
        self.url = "http://{0}/stok={1}/ds".format(self.host, self.login_info[0]["stok"])
        # mars.Print("==============>",self.url)
        req = request.Request(self.url, headers=self.headers, data=data_byte)
        respones = request.urlopen(req).read().decode('utf-8')
        infos = json.loads(respones)
        if isinstance(infos, dict):
            if 0 == infos['error_code']:
                print("{0}:success".format(data_byte))
                return infos
            else:
                mars.Print("{0}: fail".format(data_byte))
                # raise TPLinkBaseException("{0}:fail".format(data_byte))

    def check_ap(self, wireless_setting, ssid="", pwd="", enum_list=None):
        settings_json = json.dumps({"wireless": {"name": "wlan_host_2g"}, "method": "get"})
        data_byte = bytes(settings_json, "utf-8")
        check_result = self.request_router(data_byte)
        mars.Print("check...")
        mars.Print(str(check_result))
        aaa = int(check_result.get('wireless').get('wlan_host_2g').get('channel'))
        mars.Print(str(aaa))
        bbb =enum_list[0]
        mars.Print(str(bbb))
        if int(check_result.get('wireless').get('wlan_host_2g').get('channel')) == enum_list[0]:
            return True

class TLWR886N(TPLinkBase):

    def __init__(self):
        super().__init__()

    def set_ap(self, wireless_setting, ssid="", pwd="", encryption="", enum_list=None):
        settings = {
            "method": "set"
        }
        wlan_host = {}
        wlan_host.setdefault("ssid", ssid)
        wlan_host.setdefault("key", pwd)
        wlan_host.setdefault("encryption", encryption)
        wlan_host.setdefault("channel", enum_list[0])
        wlan_host.setdefault("mode", enum_list[1])
        wlan_host.setdefault("bandwidth", enum_list[2])
        wlan_host.setdefault("ssidbrd", enum_list[3])
        if "2.4G" == wireless_setting:
            settings['wireless'] = {
                'wlan_host_2g': wlan_host
            }
        elif "5G" == wireless_setting:
            settings['wireless'] = {
                'wlan_host_5g': wlan_host
            }
        settings_json = json.dumps(settings)
        data_byte = bytes(settings_json, "utf-8")
        self.request_router(data_byte)

    def set_encryption_ap(self, wireless_setting, ssid="", pwd="", enum_list=None):
        self.set_ap(wireless_setting, ssid, pwd, encryption=1, enum_list=enum_list)
        for _ in range(3):
            try:
                time.sleep(30)
                if self.check_ap(wireless_setting, ssid, pwd, enum_list=enum_list):
                    return True
            except Exception as e:
                pass
        mars.Print("set fail {0}".format(enum_list))

    def set_no_encryption_ap(self, wireless_setting, ssid="", pwd="", enum_list=None):
        self.set_ap(wireless_setting, ssid, pwd, encryption=0, enum_list=enum_list)
        for _ in range(3):
            try:
                time.sleep(30)
                if self.check_ap(wireless_setting, ssid, pwd, enum_list=enum_list):
                    return True
            except Exception as e:
                pass
        mars.Print("set fail {0}".format(enum_list))


def run():
    heron_wifi.heron_wifi_baseaction.wifi_scan_before_connect(())
    # 获取可遍历参数
    obj_json =[]
    for c in channel:
        for m in mode:
            for b in bandwidth:
                for s in ssidbrd:
                    list = [c,m,b,s]
                    obj_json.append(list)
    # print(obj_json)
    mars.Print("sta_TPLink_channel_encryption test begin")
    # 初始化对应ap
    obj =TLWR886N()
    # 登录
    mars.Print("get stok")
    obj.login_ap(host, router_username, router_password)
    # 设置有密码的
    for list in obj_json:
        mars.Print(str(list))
        obj.set_encryption_ap(wireless_setting, ap_name, ap_pwd, list)
        # obj.set_no_encryption_ap(wireless_setting, ap_name, ap_pwd, list)
        time.sleep(30)
        if heron_wifi.heron_wifi_baseaction.close_sta(()):
            mars.Print("close sta pass")
            if heron_wifi.heron_wifi_baseaction.wifi_connect_encryption_ap(()):
                mars.Print("open sta pass")
                heron_wifi.heron_wifi_baseaction.wifi_scan_connected(())
            else:
                mars.Print("open sta fail")
                mars.Verdict("fail", "open sta fail")
                return False
        else:
            mars.Print("close sta fail")
            mars.Verdict("fail", "close sta fail")
            return False
    # 设置无密码的
    for list in obj_json:
        # 设置
        # print(list)
        obj.set_no_encryption_ap(wireless_setting, ap_name, pwd="",enum_list=list)
        time.sleep(30)
        if heron_wifi.heron_wifi_baseaction.close_sta(()):
            mars.Print("close sta pass")
            if heron_wifi.heron_wifi_baseaction.wifi_connect_no_encryption_ap(()):
                mars.Print("open sta pass")
            else:
                mars.Print("open sta fail")
                mars.Verdict("fail", "open sta fail")
                return False
        else:
            mars.Print("close sta fail")
            mars.Verdict("fail", "close sta fail")
            return False

if __name__ == '__main__':
    run()
