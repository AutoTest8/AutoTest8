#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Lock_WCDMA_N3_Data.py
# @Author: xh
# @Date  : 2022/2/25
# @Desc  : 1.lock wcdma network
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
                    mars.Verdict("fail", "registered WCDMA network failed")
                mars.Print("registered WCDMA network failed {} times".format(retry_times))
                time.sleep(15)
                continue
    else:
        mars.Print("send AT command:AT*BAND=1 failed")
        mars.Verdict("fail", "send AT command:AT*BAND=1 failed")


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


def ping_rndis_network_wcdma():
    """
    ping rndis network(lock wcdma network)
    """
    mars.Print("ping_rndis_network_wcdma")
    if NetCardInfo().ping_rndis_network():
        mars.Print("PC ping baidu pass")
    else:
        mars.Print("PC ping baidu fail")
        mars.Verdict("fail", "PC ping baidu fail")


def determin_wifi_exists(serialN):
    mars.Print("determine wifi whether exists")
    d = u2.connect_usb(serialN)
    if d(text=AP_NAME).exists:                  # add by luliangliang  for ajust the wifi whether exists  2022.9.15
        mars.Print("ping baidu:AP_name exists")
        d(text=AP_NAME).click()
        time.sleep(2)
        if d(text="已连接").exists:
            mars.Print(" ping baidu:network have connected")
            return True
        else:
            mars.Print("ping baidu: connect have close")
            return False
    else:
        mars.Print("ping baidu: AP_NAME is not exists")
        return False

def test(serialN):
    mars.Print("send ping operator")
    mars.SendAT('AT+COPS?', 1000, 1)
    atResp2 = mars.WaitAT(',2', False, 10000)
    if atResp2:
        mars.Print(" network is ok ")
    else:
        mars.Print(" network is disconnect ")

    pi = subprocess.Popen('adb -s {0} shell ping -c 10 www.baidu.com'.format(serialN), shell=True, stdout=subprocess.PIPE)
    time.sleep(5)
    if determin_wifi_exists(serialN):
        mars.Print(" N3 have connect AP ")
    else:
        mars.Print("N3 have disconnect AP")

    for i in iter(pi.stdout.readline, 'b'):
        mars.Print('adb ping record: {0}'.format(i.decode()))
        if "time=" in i.decode():
            p_result = 'pingPASS'
            mars.Print("pass,N3 ping baidu,pass")
            break
        elif "" == i.decode():
            n3_screen(serialN)
            mars.Print('N3 ping baidu fail')
            break
        else:
            mars.Print("{}".format(i.decode()))


if __name__ =='__main__':
    n3_operator = wifi_falcon.N3_operator(AP_NAME, KEY)
    lock_wcdma_network()
    if n3_operator.open_ap_n3_check_ip():
        mars.Print("pass,open ap and N3 connect, pass")
        serialN = n3_operator.adb_devcies()
        # service = Thread(target=ping_rndis_network_wcdma())
        # service.start()
        time.sleep(5)
        n3_operator.N3_ping(serialN)
        restore_LTE_preferred_network()
        n3_operator.n3_unsave_ap()
        mars.Verdict("pass", "lock wcdma network test, pass")
    else:
        mars.Verdict("fail", "open ap and N3 connect, fail")

