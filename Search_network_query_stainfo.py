#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Search_network_query_stainfo.py
# @Author: xh
# @Date  : 2022/3/1
# @Desc  : 1.open ap
#          2.n3 connect ap
#          3.search network
#          4.standby for one minute
#          5.query sta information(just check OK)
#          6.close ap

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

# def quit_send_key(AP_NAME):
#     d = u2.connect_usb(serialN)
#     time_send_key = 0
#     while time_send_key < 3:
#         d(text='取消').click()
#         time.sleep(5)
#         d(text=AP_NAME).click()
#         time.sleep(5)
#         try:
#             d(resourceId="com.android.settings:id/password").click()
#             d.send_keys("asr123456", clear=True)
#             return True
#         except:
#             time_send_key = time_send_key + 1
#             continue
#     return False

def search_network():
    """
    search network information
    """
    mars.Print("search network")
    mars.Print("search network information")
    mars.Print("send AT command: at+cops=2")
    mars.SendAT('at+cops=2', 1000, 1)
    mars.WaitAT('OK', False, 60000)
    mars.Print("send AT command: at+cops=?")
    mars.SendAT('at+cops=?', 1000, 1)
    atResp = mars.WaitAT('OK', False, 300000)
    mars.Print("atResp is")
    mars.Print(atResp)
    if atResp:
        mars.Print("send AT command:at+cops=? success")
    else:
        mars.Print("send AT command:at+cops=? failed")
        mars.Verdict("fail", "send AT command:at+cops=? failed")



if __name__ =='__main__':
    search_network()
    heron_basicaction = wifi_falcon.heron_baseaction_fun(AP_NAME, KEY)
    n3_operator = wifi_falcon.N3_operator(AP_NAME, KEY)

    if n3_operator.open_ap_n3_check_ip_without_ping():
        mars.Print("pass,open ap and N3 connect, pass")
        time.sleep(60)
        search_network()
        heron_basicaction.check_sta_information()
        n3_operator.n3_unsave_ap()
        if heron_basicaction.close_ap():
            mars.Verdict("pass", "close ap, pass")
        else:
            mars.Verdict("fail", "close ap, fail")
    else:
        mars.Verdict("fail", "open ap and N3 connect, fail")

