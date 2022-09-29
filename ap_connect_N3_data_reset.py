# -*- coding: utf-8 -*-
import sys
from ctypes import *
import os
import threading
import time
from datetime import datetime
import mars
import subprocess
import re
import random
import uiautomator2 as u2

wifi_num = random.randint(0,9999999)
AP_NAME = 'AWIFI_{0}'.format(wifi_num)
KEY = 'asr123456'
sn_num=0
from wifilab import wifi_falcon
from wifilab import netcard

def case():
    n3_operator = wifi_falcon.N3_operator(AP_NAME, KEY)
    heron_basicaction = wifi_falcon.heron_baseaction_fun(AP_NAME, KEY)
    mars.Print("start")
    if n3_operator.open_ap_N3_checkIP():
        n3_operator.n3_unsave_ap()
        if heron_basicaction.reset_ap()==1:
            mars.Print("pass,reset, pass")
            if n3_operator.open_ap_N3_checkIP():
                n3_operator.n3_unsave_ap()
                mars.Verdict("pass","reset and reconnect pass, pass")
            else:
                mars.Verdict("fail", "reset and reconnect pass, fail")
        else:
            mars.Verdict("fail", "reset, fail")
    else:
        mars.Verdict("fail", "open ap, fail")

if __name__ =='__main__':
    case()