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

class net_card_info(object):
    def __init__(self):
        self.mac_addr = ''
        self.ip = ''
        self.net_card_name = ''
        self.is_rndis = False
        self.info_start_line = 0
        self.info_end_line = 0

    def get_all_ethernet_cards_info(self):
        #log = LogHandler('script_log')
        rndis_line = 0
        ip_line = ''
        info_start_line = 0
        ethernet_cards_list = []
        cmd = os.popen("ipconfig -all")
        result = cmd.read()
        all_lines = result.splitlines()
        for line_index in range(len(all_lines)):
            #Windows IP 配置
            #以太网适配器 以太网:
            #以太网适配器 rndis:
            if len(all_lines[line_index]) > 0 and all_lines[line_index][0] != ' ':
                if all_lines[line_index].find("以太网适配器") != -1:
                    info_start_line = line_index
                    if len(ethernet_cards_list) != 0:
                        ethernet_cards_list[len(ethernet_cards_list) - 1].info_end_line = line_index -1
                    net_card = net_card_info()
                    net_card.net_card_name = all_lines[line_index].split(' ')[1]#以太网:
                    net_card.net_card_name = net_card.net_card_name.replace(":","")#去掉冒号
                    net_card.info_start_line = info_start_line
                    ethernet_cards_list.append(net_card)
                    print("net_card.net_card_name： ",net_card.net_card_name)
                    #log.info('net_card.net_card_name: %s' % net_card.net_card_name)
        if len(ethernet_cards_list) >= 1:
            ethernet_cards_list[len(ethernet_cards_list) - 1].info_end_line = len(all_lines) -1

        for each in ethernet_cards_list:
            for index in range(each.info_start_line,each.info_end_line):
                if all_lines[index].find("Remote NDIS") != -1:
                    each.is_rndis = True
                if all_lines[index].find("IPv4") != -1:
                    ip_line = all_lines[index]
                    print("***************: ", all_lines[index])
                    ip_line = ip_line.split(":")[1].strip()
                    ip_line = ip_line.split("(")[0]  # 192.168.0.100(首选)
                    each.ip = ip_line
                    break
        return ethernet_cards_list

    def get_pc_ip_of_rndis(self):
        net_card_ip = ''
        #log = LogHandler('script_log')
        net_card_list = net_card_info().get_all_ethernet_cards_info()
        for each_card in net_card_list:
            if each_card.is_rndis == True:
                net_card_ip = each_card.ip
                break
        if len(net_card_ip) > 0:
            print('ip rndis addr: %s' % net_card_ip)
        else:
            print('get rndis ip failed')
        return net_card_ip

    def ping_RNDIS_network(self):
        net_domain = 'www.baidu.com'
        net_card_ip = net_card_info.get_pc_ip_of_rndis()
        ping_cmd = "ping {0} -S {1}".format(net_domain, net_card_ip)
        mars.Print("start")
        result = os.popen(ping_cmd).readlines()
        mars.Print("stop")
        result_str = ''.join(result)
        mars.Print(result_str)
        ping_success_num = result_str.count("字节=")
        mars.Print("ping_success_num: ",ping_success_num)
        if ping_success_num >= 2:
            mars.Print('ping baidu sucess')
            #log.shutdown()
            return True
        else:
            mars.Print('ping baidu failed')
            #log.shutdown()
            return False

class heron_wifi_baseaction(object):
    def close_sta(self):
        mars.Print("close sta ,send AT")
        mars.SendAT('at+wifi=wifi_close', 1)
        atRespCops = mars.WaitAT('OK', False, 20000)
        mars.Print(atRespCops)
        if atRespCops:
            time.sleep(10)
            return True
        else:
            return False

    def ip_check(self):
        mars.SendAT('at + wifi =wifi_get_peer_sta_info', 1)
        atRespCops = mars.WaitAT('OK', False, 20000)
        mars.Print(atRespCops)
        if atRespCops:
            return True
        else:
            return False

    def check_wifi_scan(self, atResp):

        find_scan_num = 0
        if atResp.find(ap_name) != -1:
            mars.Print("scan {0} successful".format(ap_name))
            return True
        else:
            while (True):
                time.sleep(5)
                mars.Print("send 'at+wifi=sdio_scan' % scan_num" % find_scan_num)
                mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                atResp = mars.WaitAT()
                mars.Print(atResp)
                if atResp.find(ap_name) != -1:
                    mars.Print("scan {0} successful".format(ap_name))
                    return True
                elif find_scan_num >= 3:
                    mars.Print("not scan {0}".format(ap_name))
                    mars.Print("Scan hotspots fail:not found {0}".format(ap_name))
                    return False
                else:
                    find_scan_num = find_scan_num + 1

    def wifi_connect_encryption_ap(self, ap_name, ap_pwd):
        """connect user define AP_NAME AP_PSW"""
        """
                connect encryption ap
                :param ap_name: name of router
                :param ap_pwd: password of router
                :return: True/False
                """
        mars.SendAT('at+wifi=sdio_wifi_open', 1000, 1)
        atResp = mars.WaitAT('OK', False, 10000)
        if atResp:
            time.sleep(15)
            mars.Print("send 'at+wifi=sdio_wifi_open' success")
            mars.SendAT('at+wifi=wifi_open sta', 1000, 1)  # add by luliangliang
            atResp = mars.WaitAT('OK', False, 10000)
            if atResp:
                mars.Print("at+wifi=wifi_open sta success")
                mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                atResp = mars.WaitAT()
                mars.Print(" scan result %s " % atResp)
                if heron_wifi_baseaction().check_wifi_scan(atResp):
                    mars.Print("wifi_scan {0} success".format(ap_name))

                else:
                    mars.Print("wifi_scan {0} fail".format(ap_name))
                    mars.Verdict("fail", "Scan hotspots fail:not found {0}".format(ap_name))
                    return False

            mars.SendAT('at+wifi=wifi_open sta {0} {1}'.format(ap_name, ap_pwd), 1000, 1)
            atResp = mars.WaitAT('OK', False, 10000)
            mars.Print(atResp)
            if atResp:
                mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                atResp = mars.WaitAT()
                mars.Print(" scan result %s " % atResp)
                if heron_wifi_baseaction().check_wifi_scan(atResp):
                    mars.Print("Scan hotspots pass:found {0}".format(ap_name))
                    mars.SendAT('at*lwipctrl=mode,dongle,0', 1000, 1)
                    atResp = mars.WaitAT('OK', False, 10000)
                    if atResp:
                        mars.SendAT('at*lwipctrl=debug,wificlient,1', 1000, 1)
                        atResp = mars.WaitAT('OK', False, 10000)
                        if atResp:
                            mars.SendAT('at*lwipctrl=log,dhcp,1', 1000, 1)
                            atResp = mars.WaitAT('OK', False, 10000)
                            if atResp:
                                time.sleep(45)
                                mars.SendAT('AT+wifi=wifi_get_ip', 1000, 1)
                                atResp = mars.WaitAT('OK', False, 120000)
                                if atResp:
                                    mars.Print("send AT success: AT+wifi=wifi_get_ip")
                                    time.sleep(2)
                                    return True
                                else:
                                    mars.Print("send AT fail: AT+wifi=wifi_get_ip")
                                    mars.Verdict("fail", "send AT fail: AT+wifi=wifi_get_ip")
                                    return False
                            else:
                                mars.Print("send AT fail: at*lwipctrl=log,dhcp,1")
                                mars.Verdict("fail", "send AT fail: at*lwipctrl=log,dhcp,1")
                                return False
                        else:
                            mars.Print("send AT fail: at*lwipctrl=debug,wificlient,1")
                            mars.Verdict("fail", "send AT fail: at*lwipctrl=debug,wificlient,1")
                            return False
                    else:
                        mars.Print("send AT fail: at*lwipctrl=mode,dongle,0")
                        mars.Verdict("fail", "send AT fail: at*lwipctrl=mode,dongle,0")
                        return False
                else:
                    mars.Print("Scan hotspots fail:not found {0}".format(ap_name))
                    mars.Verdict("fail", "Scan hotspots fail:not found {0}".format(ap_name))
                    return False
            else:
                mars.Print('connect ap fail')
                mars.Verdict("fail", "connect ap fail")
                return False
        else:
            mars.Print("send 'at+wifi=sdio_wifi_open' fail")
            mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")


    def wifi_connect_no_encryption_ap(self, ap_name, ap_pwd):
        """connect user define AP_NAME AP_PSW"""
        mars.SendAT('at+wifi=wifi_close', 1)
        heron_wifi_baseaction().wifi_scan_before_connect(ap_name)
        mars.SendAT('at+wifi= wifi_open sta {0}'.format(ap_name), 1000, 1)  ###验证脚本用，后续需要去除
        atResp = mars.WaitAT('OK', False, 10000)
        if atResp:
            time.sleep(2)
            mars.SendAT('at+wifi=wifi_scan', 1)
            atResp = mars.WaitAT('ssid={0}'.format(ap_name), False, 15000)
            if atResp:
                mars.Print('Scan hotspots success:found TL-WDR7400')
            else:
                mars.Print('Scan hotspots fail:not found {0}'.format(ap_name))
                if heron_wifi_baseaction.wifi_rescan():
                    mars.Print("send 'at+wifi=wifi_scan' success")
                else:
                    mars.Print("send 'at+wifi=wifi_scan' rescan {0} fail".format(ap_name))
                    mars.Verdict("fail", "Scan hotspots fail:not found {0}".format(ap_name))
                return False
        else:
            mars.Print('connect ap fail')
            mars.Verdict("fail", "connect ap fail")
            return False

    def notebook_ping(self):
        try:
            mars.SendAT('at+log=15,0', 1000, 1)
            time.sleep(3)
            ping_url = 'ping www.baidu.com'
            exit_code = os.system(ping_url)
            time.sleep(5)
            # 网络连通 exit_code == 0，否则返回非0值。
            if exit_code == 0:
                mars.Print("ping baidu pass")
                return True
            else:
                mars.Print("ping baidu fail")
                mars.Verdict("fail", "ping baidu fail")
                return False
        except Exception as e:
            mars.Print("ping baidu fail")
            mars.Verdict("fail", "ping baidu fail")
            return False


    def wifi_scan_before_connect(self, ap_name):
        mars.SendAT('at+wifi=sdio_wifi_open', 1000, 1)
        atResp = mars.WaitAT('OK', False, 10000)
        if atResp:
            time.sleep(15)   ###等待bin文件加载完成
            mars.Print("send 'at+wifi=sdio_wifi_open' success")
            mars.SendAT('at+wifi=wifi_open sta', 1000, 1)
            atResp = mars.WaitAT('OK', False, 10000)
            if atResp:
                mars.Print("open sta success")
                mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                result = mars.WaitAT()
                result_list =result.split("scan ap=")
                for line in result_list:
                    mars.Print(line)
                if heron_wifi_baseaction().check_wifi_scan(result):
                    mars.Print("Scan hotspots pass:found {0}".format(ap_name))
                else:
                    mars.Print("wifi_scan_before_connect Scan hotspots fail:not found {0}".format(ap_name))
                    mars.Verdict("fail", "wifi_scan_before_connect Scan hotspots fail:not found {0}".format(ap_name))
                    return False
            else:
                mars.Print("open sta fail")
                mars.Verdict("fail", "open sta fail")
                return False
        else:
            mars.Print("send 'at+wifi=sdio_wifi_open' fail")
            mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")
            return False


    def wifi_scan_connected(self, ap_name):
        mars.SendAT('at+wifi=wifi_scan', 1000, 1)
        result = mars.WaitAT()
        result_list =result.split("scan ap=")
        for line in result_list:
            mars.Print(line)
        if "ssid={0}".format(ap_name) in result:
            mars.Print("Scan hotspots pass:found {0}".format(ap_name))
        else:
            mars.Print("Scan hotspots fail:not found {0}".format(ap_name))
            mars.Verdict("fail", "Scan hotspots fail:not found {0}".format(ap_name))
            return False

    def wifi_scan_before_connect_UserDefineScanTimes(self, ap_name):
        current_test_times = 0
        scan_times = 10
        mars.SendAT('at+wifi=sdio_wifi_open', 1000, 1)
        atResp = mars.WaitAT('OK', False, 10000)
        if atResp:
            time.sleep(15)   ###等待bin文件加载完成
            mars.Print("send 'at+wifi=sdio_wifi_open' success")
            mars.SendAT('at+wifi=wifi_open sta', 1000, 1)
            atResp = mars.WaitAT('OK', False, 10000)
            if atResp:
                mars.Print("open sta success")
                for i in range(scan_times):
                    current_test_times= i + 1
                    mars.Print('******excute {0} times , total test need {1} times.******'.format(current_test_times,scan_times))
                    mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                    result = mars.WaitAT()
                    result_list = result.split("scan ap=")
                    for line in result_list:
                        mars.Print(line)
                    if heron_wifi_baseaction().check_wifi_scan(result):
                        mars.Print("Scan hotspots pass:found {0}".format(ap_name))
                    else:
                        mars.Print("wifi_scan_before_connect Scan hotspots fail:not found {0}".format(ap_name))
                        mars.Verdict("fail", "wifi_scan_before_connect Scan hotspots fail:not found {0}".format(ap_name))
                        return False
            else:
                mars.Print("open sta fail")
                mars.Verdict("fail", "open sta fail")
                return False
        else:
            mars.Print("send 'at+wifi=sdio_wifi_open' fail")
            mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")
            return False


def n3_wifi_scan(serialN):
    """
    search for visible wifi
    :param serialN: devices serial number
    :return: True/False
    """
    for scan_num in range(1, 4):
        # adb shell
        obj = subprocess.Popen(['adb', '-s', '{0}'.format(serialN), 'shell'], shell=True, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # obtain system level permissions
        obj.stdin.write('su\n'.encode('utf-8'))
        time.sleep(1)
        # search for visible wifi
        obj.stdin.write('wpa_cli -i wlan0 scan\n'.encode('utf-8'))
        time.sleep(15)
        # search for visible wifi results
        obj.stdin.write('wpa_cli -i wlan0 scan_results\n'.encode('utf-8'))
        time.sleep(15)
        # the key point is to execute exit
        obj.stdin.write('exit\n'.encode('utf-8'))
        info, err = obj.communicate()
        try:
            if err.decode('gbk'):
                mars.Print("the {0} N3 wifi cannot work well!!".format(scan_num))
                mars.Print(err.decode('gbk'))
                return False
            else:
                if ap_name in info.decode('gbk'):
                    mars.Print("ap {0} find in N3 WLAN list".format(ap_name))
                    return True
                else:
                    mars.Print("the {0} ap not find in N3 WLAN list".format(scan_num))
                    mars.Print(info.decode('gbk'))
                    return False
        except:
            mars.Print("n3 scan innoc")
            return True

        # search four times
        if scan_num > 4:
            mars.Print("N3 cannot find this ap in 3 times")
            # return False


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
    serialN = ''
    sn = os.popen('adb devices').readlines()
    num = len(sn)
    if num < 3:
        mars.Print("No Devices,please connect the device")
        return False
    else:
        if '* daemon not running' in sn[1]:
            for i in range(3, (num - 1)):
                serialN = sn[i].split("\t")[0]
        else:
            for i in range(1, (num - 1)):
                serialN = sn[i].split("\t")[0]
    n3_wifi_scan(serialN)
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
        heron_wifi_baseaction().wifi_scan_before_connect(ap_name)
        mars.Print("************************************************************")
        if heron_wifi_baseaction().close_sta():
            mars.Print(" heron has closs sta successful ")
            if heron_wifi_baseaction().wifi_connect_encryption_ap(ap_name, ap_pwd):
                mars.Print("open sta pass")
                try:
                    if n3_wifi_scan(serialN):
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
