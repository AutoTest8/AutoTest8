# -*- coding: utf-8 -*-
import sys
from ctypes import *
import os
import threading
import time
from datetime import datetime
import mars
# import serial as Serialn

import subprocess
import re
import random
import uiautomator2 as u2


def N3_Reboot():
    mars.Print('N3 Reboot ,please wait for a moment')
    os.system('adb  reboot')
    time.sleep(25)
    serialN = ''
    sn = os.popen('adb devices').readlines()
    num = len(sn)
    if num < 3:
        mars.Print("No Devices,please connect the device")
        return
    else:
        mars.Print("N3 Reboot successfully")
    mars.Print('unlock N3 screen')
    os.system('adb shell input keyevent 82')

def DKB_Reboot():
    mars.Print("DKB Reboot ,please wait for a moment")
    mars.SendAT('at+reset', 1)
    atRespCops = mars.WaitAT('OK', False, 20000)
    mars.Print(atRespCops)
    if atRespCops:
        time.sleep(30)
        mars.SendAT('at', 1)
        atRespCops = mars.WaitAT('OK', False, 20000)
        if atRespCops:
            mars.Print('DKB Reboot successfully')
    else:
        mars.Print('DKB Reboot failed')

def run():

    # mars.Print("打印串口信息")
    # port_list = list(serial.tools.list_ports.comports())
    # for i in port_list:
    #     mars.Print("port: %s" % i)

    N3_Reboot()
    if DKB_Reboot():
        mars.Verdict('DKB ready')
    else:
        mars.Print('DKB Reboot retry')
        DKB_Reboot()


if __name__ == '__main__':
    run()