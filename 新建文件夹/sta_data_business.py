#!/usr/bin/env python
# coding:utf-8
"""
Name  : sta_data_business.py
Author: xh
Time  : 2021/11/17 15:36
Desc  :
        1.open sta
        2.Open webpage to play video
        3.Standby for a period of time(standby_time)
        4.close webpage
        5.close sta
"""
import os
import mars
import time
import webbrowser

#user define
#STANDBY_TIME = 1000
# AP_NAME = "bj111111111122222222223333333333"
# AP_PSW = "asr111111111122222222223333333333444444444455555555556666666666"
STANDBY_TIME = 10
AP_NAME = "asr-guest"
AP_PSW = "asr123456"
URL = "https://www.huya.com/"


def wifi_connect_ap():
    """connect user define AP_NAME AP_PSW"""
    mars.Print("{}: sta_connect test start".format(os.path.basename(__file__)))
    mars.SendAT('at+wifi=wifi_open sta {0} {1}'.format(AP_NAME, AP_PSW), 1000, 1)
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


def sta_data_business():
    """connect ap,browse the web to play video"""
    #check open
    if wifi_connect_ap():
        mars.Print("{}: sta_open pass".format(os.path.basename(__file__)))
        #Open web to play video
        webbrowser.open_new(URL)
        #Standby for a period of time
        time.sleep(STANDBY_TIME)
        #close web
        #使用的是IE浏览器，命令为：os.system('taskkill /F /IM Iexplore.exe')；
        #使用的是chrome浏览器，命令为：os.system('taskkill /F /IM chrome.exe')。
        os.system('taskkill /F /IM chrome.exe')
        #check close
        if wifi_close_sta():
            mars.Print("{}: sta_close pass".format(os.path.basename(__file__)))
        else:
            mars.Print("{}: sta_close fail".format(os.path.basename(__file__)))
            mars.Verdict("fail", "sta_close fail")
    else:
        mars.Print("{}: connect ap fail".format(os.path.basename(__file__)))
        mars.Verdict("fail", "connect ap fail")


if __name__ == '__main__':
    sta_data_business()
