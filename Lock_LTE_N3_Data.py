#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Lock_LTE_N3_Data.py
# @Author: xh
# @Date  : 2022/2/25
# @Desc  : 1.lock lte network
#          2.open ap
#          3.N3 connect AP( 2.1.get device information 2.2.open wifi connection 2.3.scan wifi 2.4.connect ap )
#          4.establish a call(60s)
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
#

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


if __name__ =='__main__':
    lock_lte_network()
    heron_basicaction = wifi_falcon.heron_baseaction_fun(AP_NAME, KEY)
    n3_operator = wifi_falcon.N3_operator(AP_NAME, KEY)
    if n3_operator.open_ap_n3_check_ip():
        mars.Print("pass,open ap and N3 connect, pass")
        serialN = n3_operator.adb_devcies()
        call = Thread(target=netcard.ATD())
        call.start()
        time.sleep(10)
        n3_operator.N3_ping(serialN)
        time.sleep(50)
        restore_LTE_preferred_network()
        n3_operator.n3_unsave_ap()
        mars.Verdict("pass", "lock lte network test, pass")
    else:
        mars.Verdict("fail", "open ap and N3 connect, fail")