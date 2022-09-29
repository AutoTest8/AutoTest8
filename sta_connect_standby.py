#!/usr/bin/env python
# coding:utf-8
"""
Name  : sta_connect_standby.py
Author: xh
Time  : 2021/11/17 15:23
Desc  :
        1.scan ap
        2.open sta
        3.scan ap
        4.Standby for a period of time(standby_time)
        5.data service(ping baidu.com)
        6.close sta
"""
import os
import mars
import time
import traceback
import subprocess
from wifilib import heron_wifi
from wifilib import net_card
from wifilib import basic_fun

#user define
# AP_NAME = "bj111111111122222222223333333333"
# AP_PSW = "asr111111111122222222223333333333444444444455555555556666666666"
STANDBY_TIME = 100
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
        basic_fun.n3_wifi_scan(serialN)
        heron_wifi.heron_wifi_baseaction.wifi_scan_connected(())
        time.sleep(STANDBY_TIME)

        ping_cnt = 0
        while(ping_cnt <= 3):
            if net_card.net_card_info.ping_RNDIS_network(()):
                mars.Print("ping baidu pass")
                break
            else:
                if ping_cnt == 3:
                    mars.Print("ping baidu fail")
                    mars.Verdict("fail", "ping baidu fail")
                    return False
                else:
                    mars.SendAT('at+log=15,1', 1000, 1)
                    atResp = mars.WaitAT('OK', False, 10000)
                    mars.Print("atResp = %s" %atResp)
                    time.sleep(5)
                    check_rndis_exist()
                    time.sleep(20)
                    ping_cnt = ping_cnt+1
                    mars.Print("try ping num = %d" % ping_cnt)
    else:
        mars.Print("open sta fail")
        mars.Verdict("fail", "open sta fail")
        return False

if __name__ == '__main__':
    run()


