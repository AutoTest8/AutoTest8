#!/usr/bin/env python
# coding:utf-8
"""
Name  : sta_connect_ap.py
Author: zhf
Time  : 2021/11/17 10:39
Desc  :
        1.scan ap
        2.open sta
        3.scan ap
        4.data service(ping baidu.com)
        5.close sta
"""
import os
import traceback
import mars
import time
import subprocess
from wifilib import heron_wifi
from wifilib import net_card
from wifilib import basic_fun


# user define AP_NAME AP_PSW
ap_name = "tlwr886n"
ap_pwd = "123456789"

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
        if err.decode('gbk'):
            mars.Print("the {0} N3 wifi cannot work well!!".format(scan_num))
            mars.Print(err.decode('gbk'))
        else:
            if ap_name in info.decode('gbk'):
                mars.Print("ap {0} find in N3 WLAN list".format(ap_name))
                return True
            else:
                mars.Print("the {0} ap not find in N3 WLAN list".format(scan_num))
                mars.Print(info.decode('gbk'))
        # search four times
        if scan_num > 4:
            mars.Print("N3 cannot find this ap in 3 times")
            # return False

def run():
    cycle_counter = 10000
    current_time = 0
    basic_fun.check_rndis_exist()
    
    #n3_wifi_scan(serialN)
    mars.SendAT('at+wifi=sdio_wifi_open', 1000, 1)
    atResp = mars.WaitAT('OK', False, 10000)
    scan_fail = 0
    time.sleep(5)
    if atResp:
        mars.Print("send 'at+wifi=sdio_wifi_open' success")
        mars.SendAT('at+wifi=wifi_open sta', 1000, 1)
        atResp = mars.WaitAT('OK', False, 10000)
        if atResp:
            mars.Print("open sta success")
            time.sleep(5)
            mars.SendAT('at+wifi=wifi_scan', 1000, 1)
            result = mars.WaitAT()
            if result.find(ap_name) != -1:
                mars.Print("scan {0} successful".format(ap_name))
                result_list = result.split("scan ap=")
                for line in result_list:
                    mars.Print(line)
                return True
            else:
                mars.Print("cannot found {0} fail".format(ap_name))
                mars.Verdict("fail", "cannot found {0} fail".format(ap_name))
        else:
            mars.Print("open sta fail")
            mars.Verdict("fail", "open sta fail")
            return False
    else:
        mars.Print("send 'at+wifi=sdio_wifi_open' fail")
        mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")
        return False
    

if __name__ == '__main__':
    run()
