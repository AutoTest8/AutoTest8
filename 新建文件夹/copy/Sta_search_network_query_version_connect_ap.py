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
    mars.Print("query version information")
    mars.Print("send AT command: at+wifi=version")
    mars.SendAT('at+wifi=version', 1000, 1)
    atResp = mars.WaitAT('OK', False, 10000)
    if atResp:
        mars.Print("send AT command:at+wifi=version success")
    else:
        mars.Print("send AT command:at+wifi=version failed")
        mars.Verdict("fail", "send AT command:at+wifi=version failed")

# def search_network():
#     """
#     search network information
#     """
#     mars.Print("search network information")
#     mars.Print("send AT command: at+cops=2")
#     mars.SendAT('at+cops=2', 1000, 1)
#     atResp = mars.WaitAT('OK', False, 120000)
#     mars.Print("send AT command: at+cops=?")
#     mars.SendAT('at+cops=?', 1000, 1)
#     atResp = mars.WaitAT('OK', False, 360000)
#     if atResp:
#         mars.Print("send AT command:at+cops=? success")
#     else:
#         mars.Print("send AT command:at+cops=? failed")
#         mars.Verdict("fail", "send AT command:at+cops=? failed")

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

class HeronWifiBaseaction(object):

    def close_sta(self):
        """
        close sta
        :return: True/False
        """
        mars.Print("close sta")
        mars.SendAT('at+wifi=sdio_wifi_open', 1)
        atRespSdio = mars.WaitAT('OK', False, 20000)
        if atRespSdio:
            mars.SendAT('at+wifi=wifi_close', 1)
            atRespCops = mars.WaitAT('OK', False, 20000)
            mars.Print(atRespCops)
            if atRespCops:
                time.sleep(10)
                return True
            else:
                return False
        else:
            mars.Print("send at command:at+wifi=sdio_wifi_open failed")

    def check_wifi_scan(self, atResp):

        find_scan_num = 0
        if atResp.find(ap_name) != -1:
            mars.Print("scan {0} successful".format(ap_name))
            return True
        else:
            while (True):
                time.sleep(5)
                mars.Print("send 'at+wifi=sdio_scan' % scan_num" % find_scan_num)
                mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                atResp = mars.WaitAT()
                mars.Print(atResp)
                if atResp.find(ap_name) != -1:
                    mars.Print("scan {0} successful".format(ap_name))
                    return True
                elif find_scan_num >= 3:
                    mars.Print("not scan {0}".format(ap_name))
                    mars.Print("Scan hotspots fail:not found {0}".format(ap_name))
                    return False
                else:
                    find_scan_num = find_scan_num + 1

    def open_sta_notconnect_ap(self):
        """
        just open sta(without connect ap)
        :return: True/False
        """
        mars.SendAT('at+wifi=sdio_wifi_open', 1000, 1)
        atResp = mars.WaitAT('OK', False, 10000)
        if atResp:
            time.sleep(15)
            mars.Print("send 'at+wifi=sdio_wifi_open' success")
            mars.SendAT('at+wifi=wifi_open sta', 1000, 1)
            atResp = mars.WaitAT('OK', False, 10000)
            mars.Print(atResp)
            if atResp:
                mars.SendAT('at*lwipctrl=mode,dongle,0', 1000, 1)
                atResp = mars.WaitAT('OK', False, 10000)
                if atResp:
                    mars.SendAT('at*lwipctrl=debug,wificlient,1', 1000, 1)
                    atResp = mars.WaitAT('OK', False, 10000)
                    if atResp:
                        mars.SendAT('at*lwipctrl=log,dhcp,1', 1000, 1)
                        atResp = mars.WaitAT('OK', False, 10000)
                        if atResp:
                            mars.Print("send AT success: at*lwipctrl=log,dhcp,1")
                            time.sleep(2)
                            return True
                        else:
                            mars.Print("send AT fail: at*lwipctrl=log,dhcp,1")
                            mars.Verdict("fail", "send AT fail: at*lwipctrl=log,dhcp,1")
                            return False
                    else:
                        mars.Print("send AT fail: at*lwipctrl=debug,wificlient,1")
                        mars.Verdict("fail", "send AT fail: at*lwipctrl=debug,wificlient,1")
                        return False
                else:
                    mars.Print("send AT fail: at*lwipctrl=mode,dongle,0")
                    mars.Verdict("fail", "send AT fail: at*lwipctrl=mode,dongle,0")
                    return False
            else:
                mars.Print('open sta fail')
                mars.Verdict("fail", "open sta fail")
                return False
        else:
            mars.Print("send 'at+wifi=sdio_wifi_open' fail")
            mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")

    def wifi_connect_encryption_ap(self, ap_name, ap_pwd):
        """
        connect encryption ap
        :param ap_name: name of router
        :param ap_pwd: password of router
        :return: True/False
        """
        mars.SendAT('at+wifi=sdio_wifi_open', 1000, 1)
        atResp = mars.WaitAT('OK', False, 10000)
        if atResp:
            time.sleep(15)
            mars.Print("send 'at+wifi=sdio_wifi_open' success")
            mars.SendAT('at+wifi=wifi_open sta', 1000, 1)  # add by luliangliang
            atResp = mars.WaitAT('OK', False, 10000)
            if atResp:
                mars.Print("at+wifi=wifi_open sta success")
                mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                atResp = mars.WaitAT()
                mars.Print(" scan result %s " % atResp)
                if HeronWifiBaseaction().check_wifi_scan(atResp):
                    mars.Print("wifi_scan {0} success".format(ap_name))
                else:
                    mars.Print("wifi_scan {0} fail".format(ap_name))

            mars.SendAT('at+wifi=wifi_open sta {0} {1}'.format(ap_name, ap_pwd), 1000, 1)
            atResp = mars.WaitAT('OK', False, 10000)
            mars.Print(atResp)
            if atResp:
                mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                atResp = mars.WaitAT()
                mars.Print(" scan result %s " % atResp)
                if HeronWifiBaseaction().check_wifi_scan(atResp):
                    mars.Print("Scan hotspots pass:found {0}".format(ap_name))
                    mars.SendAT('at*lwipctrl=mode,dongle,0', 1000, 1)
                    atResp = mars.WaitAT('OK', False, 10000)
                    if atResp:
                        mars.SendAT('at*lwipctrl=debug,wificlient,1', 1000, 1)
                        atResp = mars.WaitAT('OK', False, 10000)
                        if atResp:
                            mars.SendAT('at*lwipctrl=log,dhcp,1', 1000, 1)
                            atResp = mars.WaitAT('OK', False, 10000)
                            if atResp:
                                time.sleep(45)
                                mars.SendAT('AT+wifi=wifi_get_ip', 1000, 1)
                                atResp = mars.WaitAT('OK', False, 120000)
                                if atResp:
                                    mars.Print("send AT success: AT+wifi=wifi_get_ip")
                                    time.sleep(2)
                                    return True
                                else:
                                    mars.Print("send AT fail: AT+wifi=wifi_get_ip")
                                    mars.Verdict("fail", "send AT fail: AT+wifi=wifi_get_ip")
                                    return False
                            else:
                                mars.Print("send AT fail: at*lwipctrl=log,dhcp,1")
                                mars.Verdict("fail", "send AT fail: at*lwipctrl=log,dhcp,1")
                                return False
                        else:
                            mars.Print("send AT fail: at*lwipctrl=debug,wificlient,1")
                            mars.Verdict("fail", "send AT fail: at*lwipctrl=debug,wificlient,1")
                            return False
                    else:
                        mars.Print("send AT fail: at*lwipctrl=mode,dongle,0")
                        mars.Verdict("fail", "send AT fail: at*lwipctrl=mode,dongle,0")
                        return False
                else:
                    mars.Print("Scan hotspots fail:not found {0}".format(ap_name))
                    mars.Verdict("fail", "Scan hotspots fail:not found {0}".format(ap_name))
                    return False
            else:
                mars.Print('connect ap fail')
                mars.Verdict("fail", "connect ap fail")
                return False
        else:
            mars.Print("send 'at+wifi=sdio_wifi_open' fail")
            mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")

if __name__ == '__main__':
    basic_fun.check_rndis_exist()
    search_network()
    if HeronWifiBaseaction().close_sta():
        mars.Print("close sta pass")
        if HeronWifiBaseaction().wifi_connect_encryption_ap(ap_name, ap_pwd):
            mars.Print("open sta pass")
            time.sleep(60)
            search_network()
            query_version()
        else:
            mars.Print("open sta fail")
            mars.Verdict("fail", "open sta fail")
    else:
        mars.Print("close sta fail")
        mars.Verdict("fail", "close sta fail")