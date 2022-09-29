#!/usr/bin/env python
# coding:utf-8
"""
Name  : sta_TPLink_channel_encryption.py
Author: xh
Time  : 2021/12/15 15:23
Desc  :
        1.open sta
        2.scan ap
        3.TPLink Router traversal test(channel, encryption)
        4.connect user define ap
        5.data service（ping baidu.com）
        6.close sta
"""
import json
import re
import os
import subprocess
import time
import mars
import traceback
from urllib import request
from abc import ABCMeta, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver as Chrome
from selenium.webdriver.common.action_chains import ActionChains

from wifilib import heron_wifi
from wifilib import net_card
from wifilib import basic_fun

# from selenium import webdriver
# ========= 用户设置参数 ===========
# 本测试脚本是基于TPLink:TL-WDR7400 AC1750双频路由器 编写（不同路由器设置有差异）
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
channel = [12]  # 1--13
mode = [2, 4, 1]  # bgn  bg n g b
bandwidth = ["1"]  # 20
ssidbrd = [1]  # 0为隐藏  1为可见
#
# class net_card_info(object):
#     def __init__(self):
#         self.mac_addr = ''
#         self.ip = ''
#         self.net_card_name = ''
#         self.is_rndis = False
#         self.info_start_line = 0
#         self.info_end_line = 0
#
#     def get_all_ethernet_cards_info(self):
#
#     def get_pc_ip_of_rndis(self):
#
#     def ping_RNDIS_network(self):
#
#
# class heron_wifi_baseaction(object):
#     def close_sta(self):
#
#     def ip_check(self):
#
#     def check_wifi_scan(self, atResp):
#
#     def wifi_connect_encryption_ap(self, ap_name, ap_pwd):
#         """connect user define AP_NAME AP_PSW"""
#         """
#                 connect encryption ap
#                 :param ap_name: name of router
#                 :param ap_pwd: password of router
#                 :return: True/False
#                 """
#
#     def wifi_connect_no_encryption_ap(self, ap_name, ap_pwd):
#         """connect user define AP_NAME AP_PSW"""
#
#
#     def notebook_ping(self):
#
#     def wifi_scan_before_connect(self, ap_name):
#
#     def wifi_scan_connected(self, ap_name):
#
#     def wifi_scan_before_connect_UserDefineScanTimes(self, ap_name):
#
#
# def n3_wifi_scan(serialN):
#     """
#     search for visible wifi
#     :param serialN: devices serial number
#     :return: True/False
#     """


class router_process(object):
    def __init__(self, router_password, username, password,wlan_channel,wlan_mode, wlan_width):
        self.username = username
        self.password = password
        self.router_password = router_password
        self.wlan_channel = wlan_channel
        self.wlan_mode = wlan_mode
        self.wlan_width = wlan_width

        self.driver = Chrome(executable_path='C:\Program Files\Google\Chrome\Application\chromedriver.exe')
        self.my_action = ActionChains(self.driver)

    def process_all(self):
        self.log_in()
        time.sleep(2)
        # self.wlan_set()
        self.mode_slete()

    def log_in(self):

        self.driver.maximize_window()
        url = "http://192.168.1.1/"
        self.driver.get(url)
        # self.driver.find_element(By.ID, "inputPwd").click()
        time.sleep(5)
        self.driver.find_element(By.ID, "lgPwd").send_keys("AAbbcc123")
        time.sleep(2)
        self.driver.find_element(By.ID, "loginSub").click()

    def wlan_set(self):
        self.driver.find_element(By.ID, "routerSetMbtn").click()            # 路由设置
        time.sleep(1)
        self.driver.find_element(By.ID, "wireless2G_rsMenu").click()        # 无线设置
        time.sleep(1)
        # self.driver.find_element(By.ID, "wifiUniteOn").click()              #
        # self.driver.find_element(By.ID, "wifiSwitchOn").click()
        # self.driver.find_element(By.ID, "ssidBrd").click()
        self.driver.find_element(By.ID, "ssid").clear()
        self.driver.find_element(By.ID, "ssid").send_keys(self.username)           # 设备名称
        time.sleep(1)
        self.driver.find_element(By.ID, "wlanPwd").clear()
        self.driver.find_element(By.ID, "wlanPwd").send_keys(self.password)         # 登录密码
        time.sleep(1)
        self.driver.find_element(By.ID, "saveBasic").click()                 #点击保存

    def box_click(self, type, id_str, idx1):

        str1 = "// *[ @ id = '{0}'] / li[{1}]".format(id_str, idx1)
        mars.Print(str1)
        self.driver.find_element(By.ID, type).click()
        time.sleep(5)
        mars.Print("click end ")
        my_error_element = self.driver.find_element(By.XPATH, str1)
        time.sleep(6)
        self.my_action.move_to_element(my_error_element).perform()  # 将鼠标移动到点击的位置
        time.sleep(2)
        mars.Print("move end")
        self.driver.find_element(By.XPATH, str1).click()

    def mode_slete(self):
        self.driver.find_element(By.ID, "routerSetMbtn").click()  # 路由设置
        time.sleep(1)
        self.driver.find_element(By.ID, "wireless2G_rsMenu").click()  # 无线设置
        time.sleep(6)
        time.sleep(3)
        self.box_click("channel", "selOptsUlchannel", self.wlan_channel)
        time.sleep(3)

        self.box_click("wlanMode", "selOptsUlwlanMode", self.wlan_mode)
        time.sleep(5)
        # self.driver.find_element(By.ID, "wlanWidth").click()
        try:
            mars.Print("start")
            target = self.driver.find_element(By.ID, "save")
            mars.Print("target")
            self.driver.execute_script("arguments[0].scrollIntoView();", target)  # 拖动到可见的元素去
            mars.Print("tuodong")
            time.sleep(15)
            self.driver.find_element(By.ID, "save").click()  # 点击保存
            time.sleep(20)
        except:
            mars.Print("errior")


def run():
    basic_fun.check_rndis_exist()
    serialN = basic_fun.get_N3_serial()
    mars.Print(serialN)
    basic_fun.n3_wifi_scan(serialN)

    obj_json = []
    for c in channel:
        for m in mode:
            for b in bandwidth:
                list = [c, m, b]
                obj_json.append(list)
    mars.Print("sta_TPLink_channel_encryption test begin")
    mars.Print("obj_json %s" % obj_json)

    for list in obj_json:
        mars.Print("list = %s" %list)
        try:
            print(list)
            r = router_process(router_password, ap_name, ap_pwd, list[0], list[1], list[2])
            r.process_all()
            r.driver.quit()
            time.sleep(10)
        except:
            continue
        heron_wifi.heron_wifi_baseaction().wifi_scan_before_connect()
        mars.Print("************************************************************")
        if heron_wifi.heron_wifi_baseaction().close_sta():
            mars.Print(" heron has closs sta successful ")
            if heron_wifi.heron_wifi_baseaction().wifi_connect_encryption_ap():
                mars.Print("open sta pass")
                try:
                    if basic_fun.n3_wifi_scan(serialN):
                        mars.Print(" n3 scan successful ")
                    else:
                        mars.Print(" n3 scan fail ")

                    # heron_wifi_baseaction().wifi_scan_connected(ap_name)
                    time.sleep(20)
                except Exception as e:
                    mars.Print(" N3 inconc ")
                    print(str(e))
                    time.sleep(20)  ####验证脚本用，后续需要去除
                    pass
            else:
                mars.Print("open sta fail")
                mars.Verdict("fail", "open sta fail")
                return False
        else:
            mars.Print("close sta fail")
            mars.Verdict("fail", "close sta fail")
            return False
    mars.Print("case have ended")

if __name__ == '__main__':
    run()
