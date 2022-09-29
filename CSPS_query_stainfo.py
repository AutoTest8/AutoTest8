#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : CSPS_query_stainfo.py
# @Author: xh
# @Date  : 2022/3/1
# @Desc  : 1.open ap
#          2.n3 connect ap
#          3.randomly do PS or CS event
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

if __name__ =='__main__':
    heron_basicaction = wifi_falcon.heron_baseaction_fun(AP_NAME, KEY)
    n3_operator = wifi_falcon.N3_operator(AP_NAME, KEY)
    n3_operator.open_ap_n3_check_ip_without_ping()
    mars.Print("open ap, success")
    netcard.cs_ps_event_random()
    time.sleep(60)
    heron_basicaction.check_sta_information()
    n3_operator.n3_unsave_ap()
    if heron_basicaction.close_ap():
        mars.Verdict("pass", "close ap, pass")
    else:
        mars.Verdict("fail", "close ap, fail")
