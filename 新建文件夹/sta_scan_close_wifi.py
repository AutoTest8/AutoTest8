#!/usr/bin/env python
# coding:utf-8
"""
Name  : sta_scan.py
Author: xh
Time  : 2021/11/16 15:33
Desc  :
        1.open sta
        2.scan at+wifi=wifi_scan, scaning
        3.sta close
"""
import os
import mars


def wifi_open_sta():
    """open sta"""
    mars.Print("{}: sta_open test start".format(os.path.basename(__file__)))
    mars.SendAT('at+wifi=wifi_open sta', 1000, 1)
    atResp = mars.WaitAT('OK', False, 10000)
    mars.Print(atResp)
    if atResp:
        return True
    else:
        return False


def wifi_close_sta():
    """close sta"""
    mars.Print("{}: sta_close test start".format(os.path.basename(__file__)))
    mars.SendAT('at+wifi=wifi_close', 1000, 1)
    atResp = mars.WaitAT('OK', False, 10000)
    mars.Print(atResp)
    if atResp:
        return True
    else:
        return False


def wifi_scan_uncheck_result():
    mars.SendAT('at+wifi=wifi_scan')


def wifi_sta_close_wifi():
    #check open
    if wifi_open_sta():
        mars.Print("{}: open sta success".format(os.path.basename(__file__)))
        #scaning,
        if wifi_scan_uncheck_result():
            mars.Print("{}: wifi scan command send success".format(os.path.basename(__file__)))
            # close sta
            if wifi_close_sta():
                mars.Print("{}: close sta success".format(os.path.basename(__file__)))
                mars.Verdict("pass", "close sta success")
            else:
                mars.Print("{}: close sta fail".format(os.path.basename(__file__)))
                mars.Verdict("fail", "close sta fail")
    else:
        mars.Print("{}: open sta fail".format(os.path.basename(__file__)))
        mars.Verdict("fail", "open sta fail")


if __name__ == '__main__':
    for i in range(10):
        wifi_sta_close_wifi()

