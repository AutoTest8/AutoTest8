import os
import mars
import time
import traceback
import subprocess
import json
from urllib import request
from abc import ABCMeta, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver as Chrome
from selenium.webdriver.common.action_chains import ActionChains
import random
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
encryption = [0, 1]  # 0为不加密  1为加密


# def query_version():
#     """
#     query version information
#     """
# def check_clcc():
#     """
#     check call status
#     """
#
# def ATD_check_clcc():
#     """
#     call 10000(check clcc)
#     """
#
# class NetCardInfo(object):
#     def __init__(self):
#         self.mac_addr = ''
#         self.ip = ''
#         self.net_card_name = ''
#         self.is_rndis = False
#         self.info_start_line = 0
#         self.info_end_line = 0
#
#     def get_all_ethernet_cards_info(self):
#         """
#         get ethernet cards information
#         """
#
#     def ping_rndis_network(self):
#         """
#         ping RNDIS network
#         :return: True/False
#         """
#
# def cs_ps_event_random():
#     """
#     randomly do cs or ps event
#     """
#
# class heron_wifi_baseaction():
#
#     def close_sta(self):
#
#     def check_wifi_scan(self, atResp):
#
#
#     def wifi_scan_before_connect(self):
#
#     def wifi_connect_encryption_ap(self):
#
#     def wifi_connect_no_encryption(self):

# def n3_wifi_scan(serialN):
#     """
#     search for visible wifi
#     :param serialN: devices serial number
#     :return: True/False
#     """

class router_process(object):
    def __init__(self, router_password, username, password,wlan_channel,wlan_mode, wlan_width, wlan_encryption):
        self.username = username
        self.password = password
        self.router_password = router_password
        self.wlan_channel = wlan_channel
        self.wlan_mode = wlan_mode
        self.wlan_width = wlan_width
        self.wlan_encryption = wlan_encryption

        self.driver = Chrome(executable_path='C:\Program Files\Google\Chrome\Application\chromedriver.exe')
        self.my_action = ActionChains(self.driver)

    def process_all(self):
        self.log_in()
        time.sleep(0.5)
        if self.wlan_encryption:
            mars.Print(" add_encryption mode ")
            time.sleep(2)
            self.wlan_set_encryption()
            self.mode_slete()
        else:
            mars.Print(" no encryption mode ")
            time.sleep(2)
            self.wlan_no_encryption()
            self.mode_slete()

        mars.Print("setting success")

    def log_in(self):
        self.driver.maximize_window()
        url = "http://192.168.1.1/"
        self.driver.get(url)
        # self.driver.find_element(By.ID, "inputPwd").click()
        time.sleep(2)
        self.driver.find_element(By.ID, "lgPwd").send_keys("AAbbcc123")
        time.sleep(1)
        self.driver.find_element(By.ID, "loginSub").click()


    def wlan_set_encryption(self):
        self.driver.find_element(By.ID, "routerSetMbtn").click()  # 路由设置
        time.sleep(1)
        self.driver.find_element(By.ID, "wireless2G_rsMenu").click()  # 无线设置
        time.sleep(2)
        mars.Print(" log in setting")
        self.driver.find_element(By.ID, "wlanPwd").clear()
        time.sleep(1)
        self.driver.find_element(By.ID, "wlanPwd").click()
        self.driver.find_element(By.ID, "wlanPwd").send_keys(self.password)  # 登录密码
        time.sleep(2)
        mars.Print("password has set done")
        self.driver.find_element(By.ID, "saveBasic").click()  # 点击保存

    def wlan_no_encryption(self):
        self.driver.find_element(By.ID, "routerSetMbtn").click()  # 路由设置
        time.sleep(0.5)
        self.driver.find_element(By.ID, "wireless2G_rsMenu").click()  # 无线设置

        time.sleep(1)
        mars.Print(" log in setting")
        self.driver.find_element(By.ID, "wlanPwd").clear()
        time.sleep(1)
        self.driver.find_element(By.ID, "saveBasic").click()  # 点击保存

    def box_click(self, type, id_str, idx1):

        str1 = "// *[ @ id = '{0}'] / li[{1}]".format(id_str, idx1)
        mars.Print(str1)
        self.driver.find_element(By.ID, type).click()
        # time.sleep(5)
        time.sleep(2)
        mars.Print("click end ")
        my_error_element = self.driver.find_element(By.XPATH, str1)
        # time.sleep(6)
        time.sleep(2)
        self.my_action.move_to_element(my_error_element).perform()  # 将鼠标移动到点击的位置
        time.sleep(2)
        mars.Print("move end")
        self.driver.find_element(By.XPATH, str1).click()

    def mode_slete(self):
        time.sleep(6)
        self.box_click("channel", "selOptsUlchannel", self.wlan_channel)
        time.sleep(3)
        self.box_click("wlanMode", "selOptsUlwlanMode", self.wlan_mode)
        time.sleep(5)
        try:
            target = self.driver.find_element(By.ID, "save")
            self.driver.execute_script("arguments[0].scrollIntoView();", target)  # 拖动到可见的元素去
            mars.Print("move save")
            time.sleep(10)
            self.driver.find_element(By.ID, "save").click()  # 点击保存
            time.sleep(10)
            mars.Print("save success")
        except:
            mars.Print("errior")

# def serialN_get():
#


def run():
    serialN = basic_fun.get_N3_serial()
    mars.Print(serialN)
    basic_fun.n3_wifi_scan(serialN)

    heron_wifi.heron_wifi_baseaction().wifi_scan_before_connect()
    obj_json = []
    for c in channel:
        for m in mode:
            for b in bandwidth:
                for e in encryption:
                    list = [c, m, b, e]
                    obj_json.append(list)
    mars.Print("sta_TPLink_channel_encryption test begin")
    for list in obj_json:
        mars.Print("list:{}".format(list))
        time.sleep(3)
        timess = 0
        while timess <= 3:
            r = router_process(router_password, ap_name, ap_pwd, list[0], list[1], list[2], list[3])
            try:
                r.process_all()
                r.driver.quit()
                time.sleep(3)
                break
            except:
                mars.Print("*********")
                r.driver.quit()
                time.sleep(3)
                timess = timess + 1
                mars.Print("Failed to access mode three times")
        time.sleep(60)

        mars.Print("*****************************************************")
        if heron_wifi.heron_wifi_baseaction().close_sta():
            mars.Print(" close wifi successful ")
            if list[3] == 0:
                if heron_wifi.heron_wifi_baseaction().wifi_connect_no_encryption_ap():
                    mars.Print("*** connect ap success")
                    try:
                        basic_fun.n3_wifi_scan(serialN)
                        # heron_wifi_baseaction().wifi_scan_connected(ap_name)
                        time.sleep(20)
                    except:
                        time.sleep(20)  ####验证脚本用，后续需要去除
                    time.sleep(2)
                    basic_fun.cs_ps_event_random()
                    time.sleep(20)
                    basic_fun.query_version()
                else:
                    mars.Print("**** connect ap fail")
            else:
                if heron_wifi.heron_wifi_baseaction().wifi_connect_encryption_ap():
                    mars.Print("*** connect ap success")
                    try:
                        basic_fun.n3_wifi_scan(serialN)
                        # heron_wifi_baseaction().wifi_scan_connected(ap_name)
                        time.sleep(20)
                    except:
                        time.sleep(20)  ####验证脚本用，后续需要去除
                    time.sleep(2)
                    basic_fun.cs_ps_event_random()
                    time.sleep(20)
                    basic_fun.query_version()
                else:
                    mars.Print("**** connect ap fail")
        else:
            mars.Print("** close fail ")
    mars.Print("case have ended")


if __name__ == '__main__':
    run()