#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Search_network_query_version.py
# @Author: xh
# @Date  : 2022/3/1
# @Desc  : 1.open ap(no device connected)
#          2.search network
#          3.standby for one minute
#          4.search network
#          5.query version information(just check OK)
#          6.close ap

import time
import mars
import random
from wifilab import wifi_falcon
from wifilab import netcard
# set ap name
wifi_num = random.randint(0, 9999999)
AP_NAME = 'AWIFI_{0}'.format(wifi_num)
# set ap key
KEY = 'asr123456'



def search_network():
    """
    search network information
    """
    mars.Print("search network information")
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
    if heron_basicaction.open_ap():
        mars.Print("pass,open ap, pass")
        time.sleep(60)
        search_network()
        heron_basicaction.query_version()
        if heron_basicaction.close_ap():
            mars.Verdict("pass", "close ap, pass")
        else:
            mars.Verdict("fail", "close ap, fail")
    else:
        mars.Verdict("fail", "open ap, fail")