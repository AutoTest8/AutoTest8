#!/usr/bin/env python
# coding:utf-8
"""
Name  : sta_connect_ap.py
Author: zhf
Time  : 2021/11/17 10:39
Desc  :
        1.scan ap
        2.open sta
        3.scan ap
        4.data service(ping baidu.com)
        5.close sta
"""
import os
import traceback
import mars
import time
import subprocess
from wifilib import heron_wifi
from wifilib import net_card
from wifilib import basic_fun


# user define AP_NAME AP_PSW
ap_name = "tlwr886n"
ap_pwd = "123456789"

def run():
    basic_fun.check_rndis_exist()

    heron_wifi.heron_wifi_baseaction.close_sta(())
    mars.Print("close sta pass")
    serialN = basic_fun.get_N3_serial()
    mars.Print(serialN)
    basic_fun.n3_wifi_scan(serialN)

    mars.Print("n3_wifi_scan end")
    heron_wifi.heron_wifi_baseaction.wifi_scan_before_connect(())
    mars.Print("close sta pass")
    if heron_wifi.heron_wifi_baseaction.wifi_connect_encryption_ap(()):
        mars.Print("open sta pass")
        time.sleep(60)          ####验证脚本用，后续需要去除
        if net_card.net_card_info.ping_RNDIS_network(()):
            mars.Print("ping baidu pass")
        else:
            mars.Print("ping baidu fail")
            mars.Verdict("fail", "ping baidu fail")
            return False
    else:
        mars.Print("open sta fail")
        mars.Verdict("fail", "open sta fail")
        return False

if __name__ == '__main__':
    run()
