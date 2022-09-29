#!/usr/bin/env python
# coding:utf-8
"""
Name  : sta_scan_without_connect_ap.py
Author: xh
Time  : 2021/12/17 17:22
Desc  :
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
# scan_times =10   #设置单次测试扫描次数

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
     heron_wifi.heron_wifi_baseaction.wifi_scan_before_connect_UserDefineScanTimes(())

if __name__ == '__main__':
    run()
