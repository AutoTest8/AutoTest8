#!/usr/bin/env python
# coding:utf-8
"""
Name  : sta_TPLink_channel_encryption.py
Author: xh
Time  : 2021/12/15 15:23
Desc  :
        1.close ap
        2.scan ap before connect
        3.connect ap (tlwr866n) and register lwip
        4.get version
        5.repeat the above action
"""
import json
import re
import os
import subprocess
import time
import mars
import traceback
from urllib import request
from abc import ABCMeta, abstractmethod
import random
from wifilib import heron_wifi
from wifilib import net_card
from wifilib import basic_fun


ap_name = "tlwr886n"
ap_pwd = "123456789"

# class heron_wifi_baseaction():
#
#     def check_wifi_scan(self, atResp):
#
#     def wifi_connect_before_scan(self):
#
#     def wifi_connect_encryption_ap(self):
#         """connect user define AP_NAME AP_PSW"""

def run():
    basic_fun.check_rndis_exist()
    time.sleep(5)
    if heron_wifi.heron_wifi_baseaction.close_sta(()):
        mars.Print(" ***** wifi close success ")
        heron_wifi.heron_wifi_baseaction().wifi_scan_before_connect()
        if heron_wifi.heron_wifi_baseaction().wifi_connect_encryption_ap():
            mars.Print(" *** connect ap successful")
            time.sleep(5)
            basic_fun.query_version()
        else:
            mars.Print("**** connect ap fail")
            mars.Verdict("fail", "connect ap fail")
    else:
        mars.Print("****wifi_close fail")
        mars.Verdict("fail", "wifi_close fail")

    time.sleep(5)
    if heron_wifi.heron_wifi_baseaction.close_sta(()):
        mars.Print(" ***** wifi close successful ")
        heron_wifi.heron_wifi_baseaction().wifi_scan_before_connect()
        if heron_wifi.heron_wifi_baseaction().wifi_connect_encryption_ap():
            mars.Print(" *** connect ap successful")
            time.sleep(5)
            basic_fun.query_version()
        else:
            mars.Print("**** connect ap fail")
            mars.Verdict("fail", "connect ap fail")
    else:
        mars.Print("****wifi_close fail")
        mars.Verdict("fail", "wifi_close fail")


if __name__ == '__main__':
    run()
