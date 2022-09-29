#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Sta_idle_query_version.py
# @Author: xh
# @Date  : 2022/3/3
# @Desc  : 1.query version
#          2.open sta(connect ap)
#          3.randomly do PS or CS event
#          4.standby for one minute
#          5.query version
#          6.close sta

import os
import mars
import time
import random
from wifilib import heron_wifi
from wifilib import net_card
from wifilib import basic_fun

# user define ap_name ap_pwd
ap_name = "tlwr886n"
ap_pwd = "123456789"

# def check_clcc():
#     """
#     check call status
#     """

# def ATD_check_clcc():
#     """
#     call 10000(check clcc)
#     """

# def cs_ps_event_random():
#     """
#     randomly do cs or ps event
#     """


# def query_version():
#     """
#     query version information
#     """

# def check_rndis_exist():


# class NetCardInfo(object):
#     def __init__(self):
#
#     def get_all_ethernet_cards_info(self):
#
#     def ping_rndis_network(self):

# class HeronWifiBaseaction(object):

#   def check_wifi_scan(self, atResp):

#   def open_sta_notconnect_ap(self):
#   """
#   just open sta(without connect ap)
#   :return: True/False
#   """

#   def wifi_connect_encryption_ap(self, ap_name, ap_pwd):
#   """
#      connect encryption ap
#      :param ap_name: name of router
#       :param ap_pwd: password of router
#         :return: True/False
#   """


if __name__ == '__main__':
    if heron_wifi.heron_wifi_baseaction().close_sta():
        mars.Print("close sta pass")
        basic_fun.check_rndis_exist()             #add check rndis whether exist
        if heron_wifi.heron_wifi_baseaction.wifi_connect_encryption_ap(()):
            mars.Print("open sta pass")
            basic_fun.cs_ps_event_random()
            time.sleep(60)
            basic_fun.query_version()
        else:
            mars.Print("open sta fail")
            mars.Verdict("fail", "open sta fail")
    else:
        mars.Print("close sta fail")
        mars.Verdict("fail", "close sta fail")