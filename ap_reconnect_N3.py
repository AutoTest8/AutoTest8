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
from wifilab import wifi_falcon
# import serial

wifi_num = random.randint(0, 9999999)
AP_NAME = 'AWIFI_{0}'.format(wifi_num)
KEY = 'asr123456'
sn_num = 0


def case():
    mars.Print("start")
    heron_basicaction = wifi_falcon.heron_baseaction_fun(AP_NAME, KEY)
    n3_operator = wifi_falcon.N3_operator(AP_NAME, KEY)
    if n3_operator.open_ap_N3_checkIP():
        mars.Print("pass,open ap and N3 connect, pass")
        n3_operator.N3_re_run()
        if heron_basicaction.ip_check() == 1:
            n3_operator.n3_unsave_ap()
            mars.Verdict("pass", "N3 close-open and ip check, pass")
        else:
            mars.Verdict("fail", "N3 close-open andip check, fail")
    else:
        mars.Verdict("fail", "open ap and N3 connect, fail")

if __name__ == '__main__':
    case()