import os
import mars
import time
import traceback
import subprocess
import json
from wifilib import heron_wifi
import random
from wifilib import heron_wifi
from wifilib import net_card
from wifilib import basic_fun

ap_name = "tlwr886n"
ap_pwd = "123456789"


# def query_version():
#     """
#     query version information
#     """
#
# def check_clcc():
#     """
#     check call status
#     """
#
# def ATD_check_clcc():
#     """
#     call 10000(check clcc)
#     """
#
# class NetCardInfo(object):
#     def __init__(self):
#         self.mac_addr = ''
#         self.ip = ''
#         self.net_card_name = ''
#         self.is_rndis = False
#         self.info_start_line = 0
#         self.info_end_line = 0
#
#     def get_all_ethernet_cards_info(self):
#         """
#         get ethernet cards information
#         """
#
#     def ping_rndis_network(self):
#         """
#         ping RNDIS network
#         :return: True/False
#         """
#
# def cs_ps_event_random():
#     """
#     randomly do cs or ps event
#     """
#
# class heron_wifi_baseaction():
#
#     def close_sta(self):
#
#     def check_wifi_scan(self, atResp):
#
#     def wifi_scan_before_connect(self):
#
#
#     def wifi_connect_before_scan(self):
#

def run():
    basic_fun.check_rndis_exist()
    if heron_wifi.heron_wifi_baseaction().close_sta():
        heron_wifi.heron_wifi_baseaction().wifi_scan_before_connect()
        if heron_wifi.heron_wifi_baseaction().wifi_connect_before_scan():
            mars.Print(" STA connect AP successful ")
            time.sleep(2)
            basic_fun.cs_ps_event_random()
            time.sleep(20)
            basic_fun.query_version()
        else:
            mars.Print(" STA connct AP fail ")
    else:
        mars.Print(" close AP fail ")


if __name__ == '__main__':
    run()