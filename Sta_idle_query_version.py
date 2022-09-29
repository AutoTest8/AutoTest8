#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Sta_idle_query_version.py
# @Author: xh
# @Date  : 2022/3/3
# @Desc  : 1.query version
#          2.open sta
#          3.standby for one minute
#          4.query version
#          5.close sta

import mars
import time
from wifilib import heron_wifi
from wifilib import net_card
from wifilib import basic_fun

# user define ap_name ap_pwd
ap_name = "tlwr886n"
ap_pwd = "123456789"

# def query_version():
#     """
#     query version information
#     """
#
# class HeronWifiBaseaction(object):
#
#     def close_sta(self):
#         """
#         close sta
#         :return: True/False
#         """
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
#     def wifi_connect_encryption_ap(self, ap_name, ap_pwd):
#         """
#         connect encryption ap
#         :param ap_name: name of router
#         :param ap_pwd: password of router
#         :return: True/False
#         """


if __name__ == '__main__':
    if heron_wifi.heron_wifi_baseaction().close_sta():
        mars.Print("close sta pass")
        if heron_wifi.heron_wifi_baseaction().open_sta_notconnect_ap():
            mars.Print("open sta pass")
            time.sleep(60)
            basic_fun.query_version()
        else:
            mars.Print("open sta fail")
            mars.Verdict("fail", "open sta fail")
    else:
        mars.Print("close sta fail")
        mars.Verdict("fail", "close sta fail")