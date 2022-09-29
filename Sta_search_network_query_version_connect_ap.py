#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Sta_search_network_query_version.py
# @Author: xh
# @Date  : 2022/3/3
# @Desc  : 1.search network
#          2.query version
#          3.open sta(connect ap)
#          4.standby for one minute
#          5.search network
#          6.query version
#          7.close sta

import mars
import time
from wifilib import heron_wifi
from wifilib import net_card
from wifilib import basic_fun

# user define ap_name ap_pwd
ap_name = "tlwr886n"
ap_pwd = "123456789"

def query_version():
    """
    query version information
    """

def search_network():
    """
    search network information
    """
    atResp = "ok"
    if atResp:
        mars.SendAT('at+cops=?', 1000, 1)
        mars.Print("send AT command: at+cops=?")
        atResp = mars.WaitAT('OK', False, 360000)
        mars.Print(atResp)
        if atResp:
            mars.Print("send AT command:at+cops=? success")
            mars.SendAT('at+cops=0', 1000, 1)
            atResp = mars.WaitAT('OK', False, 360000)
            if atResp:
                mars.Print("send AT command:at+cops=0 success")
                time.sleep(15)
                mars.Print("start check network")
                check_network()
            else:
                mars.SendAT('at+cops=0', 1000, 1)
                mars.Print("send AT command:at+cops=0 failed")
                mars.Verdict("fail", "send AT command:at+cops=0 failed")
        else:
            mars.Print("send AT command:at+cops=? failed")
            mars.Verdict("fail", "send AT command:at+cops=? failed")
    else:
        mars.Print("send AT command:at+cops=2 failed")
        mars.Verdict("fail", "send AT command:at+cops=2 failed")

def check_network():
    """
    check network
    """
    for retry_times in range(1, 7):
        mars.SendAT('AT+COPS?', 1000, 1)
        atResp2 = mars.WaitAT(',7', False, 10000)
        mars.Print("atResp2 = %s" % atResp2)
        if atResp2:
            mars.Print("registered LTE network successfully")
            break
        else:
            if retry_times == 6:
                mars.Verdict("fail", "registered LTE network failed")
            mars.Print("registered LTE network failed {} times".format(retry_times))
            time.sleep(15)
            continue

# class HeronWifiBaseaction(object):
#
#     def close_sta(self):
#         """
#         close sta
#         :return: True/False
#         """
#
#
#     def check_wifi_scan(self, atResp):
#
#
#     def open_sta_notconnect_ap(self):
#         """
#         just open sta(without connect ap)
#         :return: True/False
#         """
#
#
#     def wifi_connect_encryption_ap(self, ap_name, ap_pwd):
#         """
#         connect encryption ap
#         :param ap_name: name of router
#         :param ap_pwd: password of router
#         :return: True/False
#         """


if __name__ == '__main__':
    basic_fun.check_rndis_exist()
    search_network()
    if heron_wifi.heron_wifi_baseaction().close_sta():
        mars.Print("close sta pass")
        if heron_wifi.heron_wifi_baseaction().wifi_connect_encryption_ap():
            mars.Print("open sta pass")
            time.sleep(60)
            search_network()
            basic_fun.query_version()
        else:
            mars.Print("open sta fail")
            mars.Verdict("fail", "open sta fail")
    else:
        mars.Print("close sta fail")
        mars.Verdict("fail", "close sta fail")