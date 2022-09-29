#!/usr/bin/env python
# coding:utf-8
"""
Name  : sta_connected_close.py
Author: zhf
Time  : 2021/11/17 14:07
Desc  :
        1.open sta
        2.scan at+wifi=wifi_scan,check at response
        3.connect user define ap at+wifi=wifi_open sta AP_NAME AP_PSW
        4.sta close
"""
import os
import mars
import time
import traceback
import subprocess
from wifilib import heron_wifi
from wifilib import net_card
from wifilib import basic_fun


# user define AP_NAME AP_PSW
#AP_NAME = "bj111111111122222222223333333333"
#AP_PSW = "asr111111111122222222223333333333444444444455555555556666666666 "
ap_name = "tlwr886n"
ap_pwd = "123456789"

def run():

    basic_fun.check_rndis_exist()
    heron_wifi.heron_wifi_baseaction.close_sta(())
    mars.Print("close sta pass")

    serialN = basic_fun.get_N3_serial()
    mars.Print(serialN)
    # basic_fun.n3_wifi_scan(serialN)

    heron_wifi.heron_wifi_baseaction.wifi_scan_before_connect(())
    if heron_wifi.heron_wifi_baseaction.wifi_connect_encryption_ap(()):
        mars.Print("open sta pass")
        heron_wifi.heron_wifi_baseaction.wifi_scan_connected(())
        time.sleep(60)          ####验证脚本用，后续需要去除
        if net_card.net_card_info.ping_RNDIS_network(()):
            mars.Print("ping baidu pass")
        else:
            mars.Print("ping baidu fail")
            mars.Verdict("fail", "ping baidu fail")
            return False
    else:
        mars.Print("open sta fail")

if __name__ == '__main__':
    run()


