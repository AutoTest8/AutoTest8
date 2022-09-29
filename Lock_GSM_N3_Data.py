#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Lock_GSM_N3_Data.py
# @Author: xh
# @Date  : 2022/2/25
# @Desc  : 1.lock gsm network
#          2.open ap
#          3.N3 connect AP( 2.1.get device information 2.2.open wifi connection 2.3.scan wifi 2.4.connect ap )
#          4.PC ping baidu 60s
#          5.N3 ping baidu

import math
import time
import sys
from ctypes import *
import os
import threading
import time
from threading import Thread
from datetime import datetime
import mars
import subprocess
import re
import random
import uiautomator2 as u2
from wifilab import wifi_falcon
from wifilab import netcard
# set ap name
wifi_num = random.randint(0, 9999999)
AP_NAME = 'AWIFI_{0}'.format(wifi_num)
# set ap key
KEY = 'asr123456'

##########################################
# call
call_time = 60000
call_112_once = 65000
adbout_times = math.ceil(call_time / call_112_once)
##########################################

def lock_lte_network():
    """
    lock lte network
    """
    mars.Print("lock LTE network")
    mars.SendAT('AT*BAND=5', 1000, 1)
    atResp = mars.WaitAT('OK', False, 10000)
    if atResp:
        mars.Print("send AT command:AT*BAND=5 success")
        time.sleep(5)
        for retry_times in range(1, 7):
            mars.SendAT('AT+COPS?', 1000, 1)
            atResp2 = mars.WaitAT(',7', False, 10000)
            if atResp2:
                mars.Print("registered LTE network successfully")
                break
            else:
                if retry_times == 6:
                    mars.Verdict("fail", "registered LTE network failed")
                mars.Print("registered LTE network failed {} times".format(retry_times))
                time.sleep(15)
                continue
    else:
        mars.Print("send AT command:AT*BAND=5 failed")
        mars.Verdict("fail", "send AT command:AT*BAND=5 failed")

def lock_wcdma_network():
    """
    lock wcdma network
    """
    mars.Print("lock WCDMA network")
    mars.SendAT('AT*BAND=1', 1000, 1)
    atResp = mars.WaitAT('OK', False, 10000)
    if atResp:
        mars.Print("send AT command:AT*BAND=1 success")
        time.sleep(5)
        for retry_times in range(1, 7):
            mars.SendAT('AT+COPS?', 1000, 1)
            atResp2 = mars.WaitAT(',2', False, 10000)
            if atResp2:
                mars.Print("registered WCDMA network successfully")
                break
            else:
                if retry_times == 6:
                    mars.Verdict("fail", "registered WCDMA network failed")
                mars.Print("registered WCDMA network failed {} times".format(retry_times))
                time.sleep(15)
                continue
    else:
        mars.Print("send AT command:AT*BAND=1 failed")
        mars.Verdict("fail", "send AT command:AT*BAND=1 failed")

def lock_gsm_network():
    """
    lock gsm network
    """
    mars.Print("lock gsm network")
    mars.SendAT('AT*BAND=0', 1000, 1)
    atResp = mars.WaitAT('OK', False, 10000)
    if atResp:
        mars.Print("send AT command:AT*BAND=0 success")
        time.sleep(5)
        for retry_times in range(1, 7):
            mars.SendAT('AT+COPS?', 1000, 1)
            atResp2 = mars.WaitAT('",0', False, 10000)
            if atResp2:
                mars.Print("registered gsm network successfully")
                break
            else:
                if retry_times == 6:
                    mars.Verdict("fail", "registered gsm network failed")
                mars.Print("registered gsm network failed {} times".format(retry_times))
                time.sleep(15)
                continue
    else:
        mars.Print("send AT command:AT*BAND=0 failed")
        mars.Verdict("fail", "send AT command:AT*BAND=0 failed")

def restore_LTE_preferred_network():
    """
    restore LTE preferred network
    """
    mars.Print("restore LTE preferred network")
    for retry_times in range(1, 7):
        mars.SendAT('AT*BAND=15', 1000, 1)
        atResp = mars.WaitAT('OK', False, 10000)
        if atResp:
            mars.Print("send AT command:AT*BAND=15 success")
            break
        else:
            if retry_times == 6:
                mars.Verdict("fail", "send AT command:AT*BAND=15 failed")
            mars.Print("send AT command:AT*BAND=15 failed {} times".format(retry_times))
            time.sleep(15)
            continue

def open_ap():
    """
    open ap
    :return: True/False
    """
    mars.Print("open ap ,send AT")
    mars.SendAT('at+wifi=wifi_open ap {0} {1} 11'.format(AP_NAME, KEY), 1)
    atRespCops = mars.WaitAT('wifi_softap_open_done', False, 20000)
    if atRespCops:
        mars.Print(atRespCops)
        time.sleep(10)
    else:
        time.sleep(10)
        mars.Print("open ap ,resend AT")
        mars.SendAT('at+wifi=wifi_open ap {0} {1} 11'.format(AP_NAME, KEY), 1)
        atRespCops1 = mars.WaitAT('wifi_softap_open_done', False, 20000)
        if atRespCops1:
            mars.Print(atRespCops1)
            time.sleep(10)
        else:
            mars.Print("send open ap AT fail")
            return False
    return True

def close_ap():
    """
    close ap
    :return: True/False
    """
    mars.Print("close ap ,send AT")
    mars.SendAT('at+wifi=wifi_close', 1)
    atRespCops = mars.WaitAT('OK', False, 20000)
    mars.Print(atRespCops)
    if atRespCops:
        time.sleep(10)
        return True
    else:
        return False

def ip_check():
    """
    check ip
    :return: True/False
    """
    mars.SendAT('at + wifi =wifi_get_peer_sta_info', 1)
    atRespCops = mars.WaitAT('OK', False, 20000)
    mars.Print(atRespCops)
    if atRespCops:
        return True
    else:
        return False

def n3_run():
    """
    n3 open wifi
    n3 scan wifi
    n3 connect ap
    n3 ping baidu
    :return: True/False
    """
    serialN = ''
    sn = os.popen('adb devices').readlines()
    num = len(sn)
    if num < 3:
        print("No Devices,please connect the device")
        return
    else:
        if '* daemon not running' in sn[1]:
            for i in range(3, (num - 1)):
                serialN = sn[i].split("\t")[0]
        else:
            for i in range(1, (num - 1)):
                serialN = sn[i].split("\t")[0]
    n3_wifi_on(serialN)
    if n3_wifi_scan(serialN):
        mars.Print("N3 cli_supplicant command can find ap pass,will connect this ap...")
        if n3_connect_ap(serialN) == 1:
            time.sleep(10)
            if n3_ping(serialN):
                return True
            else:
                return False
    else:
        mars.Verdict("fail", "N3 cli_supplicant command can not find ap , fail")

def n3_wifi_on(serialN):
    """
    open n3 wifi
    :param serialN: devices serial number
    """
    # adb shell
    obj = subprocess.Popen('adb -s %s shell' % serialN, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, shell=True)
    # open n3 wifi
    obj.communicate(input='svc wifi enable'.encode())

def n3_wifi_scan(serialN):
    """
    search for visible wifi
    :param serialN: devices serial number
    :return: True/False
    """
    for scan_num in range(1, 4):
        obj = subprocess.Popen(['adb', '-s', '{0}'.format(serialN), 'shell'], shell=True, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        obj.stdin.write('su\n'.encode('utf-8'))
        time.sleep(1)
        # search for visible wifi
        obj.stdin.write('wpa_cli -i wlan0 scan\n'.encode('utf-8'))
        time.sleep(15)
        # search for visible wifi results
        obj.stdin.write('wpa_cli -i wlan0 scan_results\n'.encode('utf-8'))
        time.sleep(15)
        # exit
        obj.stdin.write('exit\n'.encode('utf-8'))
        info, err = obj.communicate()
        if err.decode('gbk'):
            mars.Print("the {0} N3 wifi cannot work well!!".format(scan_num))
            mars.Print(err.decode('gbk'))
        else:
            if AP_NAME in info.decode('gbk'):
                mars.Print("ap find in list")
                return True
            else:
                mars.Print("the {0} ap not find in list".format(scan_num))
                mars.Print(info.decode('gbk'))
        # search four times
        if scan_num > 4:
            mars.Print("N3 cannot find this ap in 3 times")
            return False

def n3_screen(serialN):
    """
    n3 screenshot
    :param serialN: devices serial number
    """
    tasktime = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
    # n3 screenshot
    subprocess.Popen('adb -s {0} shell /system/bin/screencap -p /sdcard/{1}_{2}.png'.format(serialN, AP_NAME, tasktime),
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

def n3_wifi_off(serialN):
    """
    close n3 wifi
    :param serialN: devices serial number
    """
    obj = subprocess.Popen('adb -s %s shell' % serialN, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, shell=True)
    # close n3 wifi
    obj.communicate(input='svc wifi disable'.encode())

# def n3_connect_ap(serialN):
#     """
#     n3 connect ap
#     :param serialN: devices serial number
#     :return: True/False
#     """
#     d = u2.connect_usb(serialN)
#     mars.Print("home")
#     d.press("home")
#     # open settings
#     d.app_start("com.android.settings")
#     time.sleep(1)
#     # open n3 wifi
#     d(scrollable=True).scroll.toBeginning()
#     net_name = ["网络和互联网", "Network & Internet", "Network & internet"]
#     net_result = ''
#     for net in net_name:
#         if d(text=net).exists:
#             d(text=net).click()
#             net_result = 1
#     time.sleep(1)
#     # open n3 wifi
#     if net_result:
#         wlan_name = ["WLAN", "Wi‑Fi"]
#         wlan_result = ''
#         for wlan in wlan_name:
#             if d(text=wlan).exists:
#                 d(text=wlan).click()
#                 wlan_result = 1
#                 time.sleep(5)
#         if wlan_result:
#             ap_find_result = ''
#             for scan_num in range(1, 4):
#                 if scan_num > 1:
#                     mars.Print("close N3 WIFI,and rescan ap...")
#                     n3_wifi_off(serialN)
#                     time.sleep(2)
#                     n3_wifi_on(serialN)
#                     time.sleep(15)
#                 # determine whether ap exists
#                 if d(text=AP_NAME).exists:
#                     mars.Print("ap in UI")
#                     ap_find_result = 1
#                     break
#                 else:
#                     mars.Print("ap not in UI,scroll to find")
#                     if scan_num > 1:
#                         n3_screen(serialN)
#                     d(scrollable=True).scroll.toBeginning()
#                     for i in range(1, 100):
#                         d.swipe(0.5, 0.8, 0.5, 0.6)
#                         if d(text=AP_NAME).exists:
#                             ap_find_result = 1
#                             break
#                         elif d(text="Add network").exists and d(text=AP_NAME).exists is not True:
#                             mars.Print('swipe end,not find ap')
#                             if scan_num > 1:
#                                 n3_screen(serialN)
#                             mars.Print("not this ap")
#                             break
#                 if scan_num == 3:
#                     mars.Print("N3 cannot find ap in 3 times,please check picture")
#                     return False
#             if ap_find_result:
#                 # ap connect
#                 time.sleep(3)
#                 mars.Print("prepare to connect")
#                 d(text=AP_NAME).click()
#                 if d(text="FORGET").exists:
#                     mars.Print("connected")
#                 elif d(text="取消保存").exists:
#                     mars.Print("connected")
#                 elif d(text="WLAN").exists:
#                     mars.Print("connected")
#                 elif d(text="Wi‑Fi").exists:
#                     mars.Print("connected")
#                 else:
#                     d.send_keys(KEY)
#                     if d(text="连接").exists:
#                         d(text="连接").click()
#                         time.sleep(15)
#                         if d(text=AP_NAME).exists:
#                             d(resourceId="android:id/title", text=AP_NAME).click()
#                             time.sleep(5)
#                             if d(text="已连接").exists:
#                                 mars.Print('n3 connect pass')
#                             else:
#                                 mars.Verdict("fail", "N3 connect ap, fail")
#                         else:
#                             mars.Verdict("fail", "N3 cannot find ap, fail")
#                             return False
#                     else:
#                         d(text="CONNECT").click()
#                         time.sleep(15)
#                         if d(text=AP_NAME).exists:
#                             d(resourceId="android:id/title", text=AP_NAME).click()
#                             time.sleep(5)
#                             if d(text="Connected").exists:
#                                 mars.Print('n3 connect pass')
#                             else:
#                                 mars.Verdict("fail", "N3 connect ap, fail")
#                         else:
#                             mars.Verdict("fail", "N3 cannot find ap, fail")
#                             return False
#                 # n3 connect pass
#                 return True
#             else:
#                 mars.Verdict("fail", "find ap, fail")
#         else:
#             mars.Verdict("fail", "into wlan, fail")
#     else:
#         mars.Verdict("fail", "into net  setting, fail")

def N3_send_keys(serialN):
    d = u2.connect_usb(serialN)
    d.send_keys(KEY)
    if d(text="连接").exists:
        d(text="连接").click()
        time.sleep(15)
        if d(text=AP_NAME).exists:
            d(resourceId="android:id/title", text=AP_NAME).click()
            time.sleep(5)
            if d(text="已连接").exists:
                mars.Print('n3 connect pass')
            else:
                mars.Verdict("fail", "N3 connect ap, fail")
        else:
            mars.Verdict("fail", "N3 cannot find ap, fail")
            return False
    else:
        d(text="CONNECT").click()
        time.sleep(15)
        if d(text=AP_NAME).exists:
            d(resourceId="android:id/title", text=AP_NAME).click()
            time.sleep(5)
            if d(text="Connected").exists:
                mars.Print('n3 connect pass')
            else:
                mars.Verdict("fail", "N3 connect ap, fail")
        else:
            mars.Verdict("fail", "N3 cannot find ap, fail")
            return False

def n3_connect_ap(serialN):
    """
    n3 connect ap
    :param serialN: devices serial number
    :return: True/False
    """
    d = u2.connect_usb(serialN)
    mars.Print("home")
    d.press("home")
    # open settings
    d.app_start("com.android.settings")
    time.sleep(1)
    # open n3 wifi
    d(scrollable=True).scroll.toBeginning()
    net_name = ["网络和互联网", "Network & Internet", "Network & internet"]
    net_result = ''
    for net in net_name:
        if d(text=net).exists:
            d(text=net).click()
            net_result = 1
    time.sleep(1)
    # open n3 wifi
    if net_result:
        wlan_name = ["WLAN", "Wi‑Fi"]
        wlan_result = ''
        for wlan in wlan_name:
            if d(text=wlan).exists:
                d(text=wlan).click()
                wlan_result = 1
                time.sleep(5)
        if wlan_result:
            ap_find_result = ''
            for scan_num in range(1, 4):
                if scan_num > 1:
                    mars.Print("close N3 WIFI,and rescan ap...")
                    n3_wifi_off(serialN)
                    time.sleep(2)
                    n3_wifi_on(serialN)
                    time.sleep(15)
                # determine whether ap exists
                if d(text=AP_NAME).exists:
                    mars.Print("ap in UI")
                    ap_find_result = 1
                    break
                else:
                    mars.Print("ap not in UI,scroll to find")
                    if scan_num > 1:
                        n3_screen(serialN)
                    d(scrollable=True).scroll.toBeginning()
                    for i in range(1, 100):
                        d.swipe(0.5, 0.8, 0.5, 0.6)
                        if d(text=AP_NAME).exists:
                            ap_find_result = 1
                            break
                        elif d(text="Add network").exists and d(text=AP_NAME).exists is not True:
                            mars.Print('swipe end,not find ap')
                            if scan_num > 1:
                                n3_screen(serialN)
                            mars.Print("not this ap")
                            break
                if scan_num == 3:
                    mars.Print("N3 cannot find ap in 3 times,please check picture")
                    return False
            if ap_find_result:
                # ap connect
                time.sleep(3)
                mars.Print("prepare to connect")
                d(text=AP_NAME).click()
                if d(text="FORGET").exists:
                    mars.Print("connected")
                elif d(text="取消保存").exists:
                    mars.Print("connected")
                elif d(text="WLAN").exists:
                    mars.Print("connected")
                elif d(text="Wi‑Fi").exists:
                    mars.Print("connected")
                else:
                    d.send_keys(KEY)
                    if d(text="连接").exists:
                        d(text="连接").click()
                        time.sleep(15)
                        if d(text=AP_NAME).exists:
                            d(resourceId="android:id/title", text=AP_NAME).click()
                            time.sleep(5)
                            if d(text="已连接").exists:
                                mars.Print('n3 connect pass')
                            else:
                                # mars.Verdict("fail", "N3 connect ap, fail")
                                N3_send_keys(serialN)
                        else:
                            mars.Verdict("fail", "N3 cannot find ap, fail")
                            return False
                    else:
                        d(text="CONNECT").click()
                        time.sleep(25)
                        if d(text=AP_NAME).exists:
                            d(resourceId="android:id/title", text=AP_NAME).click()
                            time.sleep(5)
                            if d(text="Connected").exists:
                                mars.Print('n3 connect pass')
                            else:
                                mars.Verdict("fail", "N3 connect ap, fail")
                        else:
                            mars.Verdict("fail", "N3 cannot find ap, fail")
                            return False
                # n3 connect pass
                return True
            else:
                mars.Verdict("fail", "find ap, fail")
        else:
            mars.Verdict("fail", "into wlan, fail")
    else:
        mars.Verdict("fail", "into net  setting, fail")


def n3_ping(serialN):
    """
    n3 ping baidu
    :param sn_name:n3 devices
    :return:p_result
    """
    mars.Print('N3 ping baidu')
    p_result = ''
    pi = subprocess.Popen('adb -s {0} shell ping www.baidu.com'.format(serialN), shell=True, stdout=subprocess.PIPE)
    for i in iter(pi.stdout.readline, 'b'):
        mars.Print('adb ping record: {0}'.format(i.decode()))
        if "time=" in i.decode():
            p_result = 'pingPASS'
            print("N3 ping www.baidu.com pass!!!!")
            mars.Print('N3 ping baidu pass')
            mars.Print("pass,N3 ping baidu,pass")
            break
        elif "" == i.decode():
            print("N3 ping www.baidu.com fail!!!!")
            mars.Print('N3 ping baidu fail')
            mars.Verdict("fail", "N3 ping baidu,fail")
            break
    return p_result

def open_ap_n3_check_ip():
    """
    open ap
    n3_run
    ip_check
    :return: True/False
    """
    if open_ap():
        mars.Print("pass,open ap, pass")
        if n3_run():
            mars.Print("pass,n3 connect, pass")
            if ip_check():
                mars.Print("pass,ip check, pass")
                return True
            else:
                mars.Verdict("fail", "ip check, fail")
        else:
            mars.Verdict("fail", "n3 connect, fail")
    else:
        mars.Verdict("fail", "open ap, fail")
    return False

def adb_devcies():
    """
    get N3's serial number
    """
    serialN = ''
    sn = os.popen('adb devices').readlines()
    num = len(sn)
    if num < 3:
        print("No Devices,please connect the device")
        # mars.Verdict("fail", "NO N3 connect to PC")
        return
    else:
        if '* daemon not running' in sn[1]:
            for i in range(3, (num - 1)):
                serialN = sn[i].split("\t")[0]
        else:
            for i in range(1, (num - 1)):
                serialN = sn[i].split("\t")[0]
    return serialN

def ATD():
    """
    call 112
    """
    mars.Print("CALL 112 and hold up {0}".format(call_time))
    mars.SendAT('atd112;', 1)
    for i in range(call_time // 1000):
        atRespCops = mars.WaitAT('CALLDISCONNECT', False, 1000)
        mars.Print(atRespCops)
        if atRespCops:
            mars.SendAT('atd112;', 1)
        else:
            mars.Print("{0}s 112 ".format(i))

def ping_rndis_network_gsm():
    """
    ping rndis network(lock gsm network)
    """
    if NetCardInfo().ping_rndis_network():
        mars.Print("PC ping baidu pass")
    else:
        mars.Print("PC ping baidu fail")
        mars.Verdict("fail", "PC ping baidu fail")

class NetCardInfo(object):
    def __init__(self):
        self.mac_addr = ''
        self.ip = ''
        self.net_card_name = ''
        self.is_rndis = False
        self.info_start_line = 0
        self.info_end_line = 0

    def get_all_ethernet_cards_info(self):
        """
        get ethernet cards information
        """
        ethernet_cards_list = []
        cmd = os.popen("ipconfig -all")
        result = cmd.read()
        all_lines = result.splitlines()
        for line_index in range(len(all_lines)):
            # Windows IP configuration
            if len(all_lines[line_index]) > 0 and all_lines[line_index][0] != ' ':
                if all_lines[line_index].find("以太网适配器") != -1:
                    info_start_line = line_index
                    if len(ethernet_cards_list) != 0:
                        ethernet_cards_list[len(ethernet_cards_list) - 1].info_end_line = line_index - 1
                    net_card = NetCardInfo()
                    net_card.net_card_name = all_lines[line_index].split(' ')[1]  # Ethernet:
                    net_card.net_card_name = net_card.net_card_name.replace(":", "")  # remove the colon
                    net_card.info_start_line = info_start_line
                    ethernet_cards_list.append(net_card)
                    print("net_card.net_card_name： ", net_card.net_card_name)
        if len(ethernet_cards_list) >= 1:
            ethernet_cards_list[len(ethernet_cards_list) - 1].info_end_line = len(all_lines) - 1
        for each in ethernet_cards_list:
            for index in range(each.info_start_line, each.info_end_line):
                if all_lines[index].find("Remote NDIS") != -1:
                    each.is_rndis = True
                if all_lines[index].find("IPv4") != -1:
                    ip_line = all_lines[index]
                    print("***************: ", all_lines[index])
                    ip_line = ip_line.split(":")[1].strip()
                    ip_line = ip_line.split("(")[0]  # 192.168.0.100(first choice)
                    each.ip = ip_line
                    break
        return ethernet_cards_list

    def ping_rndis_network(self):
        """
        ping RNDIS network
        :return: True/False
        """
        ip = ''
        net_domain = 'www.baidu.com'
        net_card_list = NetCardInfo().get_all_ethernet_cards_info()
        for each_card in net_card_list:
            if each_card.is_rndis == True:
                ip = each_card.ip
                break
        if len(ip) > 0:
            mars.Print('ip rndis addr: %s' % ip)
        else:
            mars.Print('get rndis ip failed')
        net_card_ip = ip
        ping_cmd = "ping {0} -S {1} -n 60".format(net_domain, net_card_ip)
        mars.Print(ping_cmd)
        result = os.popen(ping_cmd).readlines()
        result_str = ''.join(result)
        mars.Print(result_str)
        ping_success_num = result_str.count("字节=")
        if ping_success_num >= 2:
            mars.Print('PC ping baidu sucess')
            return True
        else:
            mars.Print('PC ping baidu failed')
            return False

def n3_unsave_ap():
    serialN = ''
    sn = os.popen('adb devices').readlines()
    num = len(sn)
    if num < 3:
        mars.Print("No Devices,please connect the device")
        # mars.Verdict("fail", "NO N3 connect to PC")
        return
    else:
        if '* daemon not running' in sn[1]:
            for i in range(3, (num - 1)):
                serialN = sn[i].split("\t")[0]
        else:
            for i in range(1, (num - 1)):
                serialN = sn[i].split("\t")[0]
    d = u2.connect_usb(serialN)
    if d(text="取消保存").exists:
        d(resourceId="com.android.settings:id/button1_negative").click()
    else:
        # d(resourceId="android:id/title", text=AP_NAME).click()
        # time.sleep(5)
        # d(resourceId="com.android.settings:id/button1_negative").click()
        mars.Print('claer saved wifi-network failed')

if __name__ =='__main__':
    lock_gsm_network()
    if open_ap_n3_check_ip():
        mars.Print("pass,open ap and N3 connect, pass")
        serialN = adb_devcies()
        call = Thread(target=ping_rndis_network_gsm())
        call.start()
        time.sleep(5)
        n3_ping(serialN)
        restore_LTE_preferred_network()
        n3_unsave_ap()
        mars.Verdict("pass", "lock gsm network test, pass")
    else:
        mars.Verdict("fail", "open ap and N3 connect, fail")

