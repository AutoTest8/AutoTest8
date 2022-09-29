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

ap_name = ["tlwr886n", "ase-guest"]
ap_pwd = ["123456789", "asr123456"]






def check_rndis_exist():
    cmd = os.popen("ipconfig -all")
    result = cmd.read()
    result = str(result)
    mars.Print("result is %s" % result)
    if result.find("NDIS") != -1:
        mars.Print("rndis -----exist")
    else:
        for i in range(5):
            mars.Print("send at retry check rndis")
            mars.SendAT('at+log=15,1', 1000, 1)
            atResp = mars.WaitAT('OK', False, 10000)
            if atResp:
                mars.Print("at+log=15,1 success")
                time.sleep(5)
                mars.SendAT('at+log=15,0', 1000, 1)
                atResp = mars.WaitAT('OK', False, 10000)
                if atResp:
                    mars.Print("at+log=15,0 success")
                    time.sleep(15)
            cmd = os.popen("ipconfig -all")
            result = cmd.read()
            result = str(result)
            if result.find("NDIS") != -1:
                mars.Print("rndis -----exist")
                break
            else:
                if i == 4:
                    mars.Verdict("fail", "rndis -----not exist--------")
                continue

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

class heron_wifi_baseaction():

    def close_sta(self):
        mars.Print("close sta ,send AT")
        mars.SendAT('at+wifi=wifi_close', 1)
        atRespCops = mars.WaitAT('OK', False, 20000)
        mars.Print(atRespCops)
        if atRespCops:
            time.sleep(10)
            return True
        else:
            return False

    def check_wifi_scan(self, atResp):

        mars.Print("check_wifi_scan")
        find_scan_num = 0
        if atResp.find(ap_name) != -1:
            mars.Print("scan {0} successful".format(ap_name))
            return True
        else:
            while(True):
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


    def wifi_scan_before_connect(self):
        mars.Print("***********wifi_scan_before_connect*********")

        mars.SendAT('at+wifi=sdio_wifi_open', 1000, 1)
        atResp = mars.WaitAT('OK', False, 10000)
        if atResp:
            time.sleep(15)  ###等待bin文件加载完成
            mars.Print("send 'at+wifi=sdio_wifi_open' success")
            mars.SendAT('at+wifi=wifi_open sta', 1000, 1)
            atResp = mars.WaitAT('OK', False, 10000)
            if atResp:
                time.sleep(10)
                mars.Print("open sta success")
                mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                result = mars.WaitAT()
                mars.Print("result %s {0}" % result)
                if heron_wifi_baseaction().check_wifi_scan(result):
                    mars.Print("Scan hotspots pass:found {0}".format(ap_name))
                else:
                    mars.Print("wifi_scan_before_connect Scan hotspots fail:not found {0}".format(ap_name))
                    mars.Verdict("fail", "wifi_scan_before_connect Scan hotspots fail:not found {0}".format(ap_name))
                    return False
            else:
                mars.Print("open sta fail")
                mars.Verdict("fail", "open sta fail")
                return False
        else:
            mars.Print("send 'at+wifi=sdio_wifi_open' fail")
            mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")
            return False

    def wifi_connect_before_scan(self):

        heron_wifi_baseaction().close_sta()
        mars.SendAT('at+wifi=sdio_wifi_open', 1)
        atRespCops = mars.WaitAT('OK', False, 10000)
        if atRespCops:
            mars.Print(" 'at+wifi=sdio_wifi_open' have successful")
            mars.SendAT('at+wifi=wifi_open sta {0} 7 {1}'.format(ap_name, ap_pwd), 1000, 1)
            atRespCops = mars.WaitAT('OK', False, 10000)
            if atRespCops:
                mars.Print(" Station have successful connect ")
                mars.SendAT('at*lwipctrl=mode,dongle,0', 1000, 1)
                atResp = mars.WaitAT('OK', False, 10000)
                if atResp:
                    mars.SendAT('at*lwipctrl=debug,wificlient,1', 1000, 1)
                    atResp = mars.WaitAT('OK', False, 10000)
                    if atResp:
                        mars.SendAT('at*lwipctrl=log,dhcp,1', 1000, 1)
                        atResp = mars.WaitAT('OK', False, 10000)
                        time.sleep(45)
                        if atResp:
                            mars.SendAT('AT+wifi=wifi_get_ip', 1000, 1)
                            atResp = mars.WaitAT('OK', False, 360000)
                            if atResp:
                                mars.Print("send AT success: AT+wifi=wifi_get_ip")
                                time.sleep(2)  ###验证脚本用，后续需要去除
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
                mars.Print(" Station connect {0} fail".format(ap_name))
                mars.Verdict("fail", "connect AP fail: ")
                return False
        else:
            mars.Print(" 'at+wifi=sdio_wifi_open' have successful")
            mars.Verdict("fail", "send AT fail: at+wifi=sdio_wifi_open")
            return False

    def wifi_connect_encryption_ap(self):
        """connect user define AP_NAME AP_PSW"""
        mars.Print("wifi_connect_encryption_ap")

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
                if heron_wifi_baseaction().check_wifi_scan(atResp):
                    mars.Print("wifi_scan {0} success".format(ap_name))
                else:
                    mars.Print("wifi_scan {0} fail".format(ap_name))
                    mars.Verdict("fail", "Scan hotspots fail:not found {0}".format(ap_name))

            mars.SendAT('at+wifi=wifi_open sta {0} {1}'.format(ap_name, ap_pwd), 1000, 1)
            atResp = mars.WaitAT('OK', False, 10000)
            mars.Print(atResp)
            if atResp:
                mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                atResp = mars.WaitAT()
                mars.Print(" scan result %s " % atResp)
                if heron_wifi_baseaction().check_wifi_scan(atResp):
                    mars.Print("Scan hotspots pass:found {0}".format(ap_name))
                    mars.SendAT('at*lwipctrl=mode,dongle,0', 1000, 1)
                    atResp = mars.WaitAT('OK', False, 10000)
                    if atResp:
                        mars.SendAT('at*lwipctrl=debug,wificlient,1', 1000, 1)
                        atResp = mars.WaitAT('OK', False, 10000)
                        if atResp:
                            mars.SendAT('at*lwipctrl=log,dhcp,1', 1000, 1)
                            atResp = mars.WaitAT('OK', False, 10000)
                            time.sleep(45)
                            if atResp:
                                mars.SendAT('AT+wifi=wifi_get_ip', 1000, 1)
                                atResp = mars.WaitAT('OK', False, 360000)
                                if atResp:
                                    mars.Print("send AT success: AT+wifi=wifi_get_ip")
                                    time.sleep(2)  ###验证脚本用，后续需要去除
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
                mars.Print('connect encryption {0} fail'.format(ap_name))
                mars.Verdict("fail", "connect encryption {0} fail".format(ap_name))
                return False
        else:
            mars.Print("send 'at+wifi=sdio_wifi_open' fail")
            mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")


def run():
    time.sleep(5)
    if heron_wifi_baseaction().close_sta():
        mars.Print(" ***** wifi close success ")
        heron_wifi_baseaction().wifi_scan_before_connect()
        if heron_wifi_baseaction().wifi_connect_encryption_ap():
            mars.Print(" *** connect ap successful")
            time.sleep(5)
            query_version()
        else:
            mars.Print("**** connect ap fail")
            mars.Verdict("fail", "connect ap fail")
    else:
        mars.Print("****wifi_close fail")
        mars.Verdict("fail", "wifi_close fail")

    time.sleep(5)
    if heron_wifi_baseaction().close_sta():
        mars.Print(" ***** wifi close successful ")
        heron_wifi_baseaction().wifi_scan_before_connect()
        if heron_wifi_baseaction().wifi_connect_encryption_ap():
            mars.Print(" *** connect ap successful")
            time.sleep(5)
            query_version()
        else:
            mars.Print("**** connect ap fail")
            mars.Verdict("fail", "connect ap fail")
    else:
        mars.Print("****wifi_close fail")
        mars.Verdict("fail", "wifi_close fail")


if __name__ == '__main__':
    run()
