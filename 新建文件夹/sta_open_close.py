#!/usr/bin/env python
# coding:utf-8
"""
Name  : sta_open_close.py
Author: zhf
Time  : 2021/11/16 16:18
Desc  :
        1.open sta
        2.close sta
        3.Cycle 100 times
"""
import os
import mars
from wifilib import heron_wifi

def run():
    current_test_times = 0
    for i in range(20):
        current_test_times= i + 1
        mars.Print('excute {0} times , total test need 100 times.'.format(current_test_times))
        heron_wifi.heron_wifi_baseaction.wifi_scan_before_connect(())
        if heron_wifi.heron_wifi_baseaction.close_sta(()):
            mars.Print("close sta pass")
            if heron_wifi.heron_wifi_baseaction.wifi_connect_encryption_ap(()):
                mars.Print("open sta pass")
            else:
                mars.Print("open sta fail")
                mars.Verdict("fail", "open sta fail")
                return False
        else:
            mars.Print("close sta fail")
            mars.Verdict("fail", "close sta fail")
            return False

if __name__ == '__main__':
    run()

