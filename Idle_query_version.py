#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Idle_query_version.py
# @Author: xh
# @Date  : 2022/3/1
# @Desc  : 1.open ap(no device connected)
#          2.standby for one minute
#          3.query version information(just check OK)
#          4.close ap

import time
import mars
import random
from wifilab import wifi_falcon
# set ap name
wifi_num = random.randint(0, 9999999)
AP_NAME = 'AWIFI_{0}'.format(wifi_num)
# set ap key
KEY = 'asr123456'
#


if __name__ =='__main__':
    heron_basicaction = wifi_falcon.heron_baseaction_fun(AP_NAME, KEY)
    n3_operator = wifi_falcon.N3_operator(AP_NAME, KEY)
    if heron_basicaction.open_ap():
        mars.Print("pass,open ap, pass")
        time.sleep(60)
        heron_basicaction.query_version()
        if heron_basicaction.close_ap():
            mars.Verdict("pass", "close ap, pass")
        else:
            mars.Verdict("fail", "close ap, fail")
    else:
        mars.Verdict("fail", "open ap, fail")