
import math
import time
import sys
from ctypes import *
import os
import threading
import time
from threading import Thread
from datetime import datetime
import mars
import subprocess
import re
import random
import uiautomator2 as u2
call_time = 60000
call_112_once = 65000
adbout_times = math.ceil(call_time / call_112_once)


def adb_devcies():
    """
    get N3's serial number
    """
    serialN = ''
    sn = os.popen('adb devices').readlines()
    num = len(sn)
    if num < 3:
        print("No Devices,please connect the device")
        # mars.Verdict("fail", "NO N3 connect to PC")
        return
    else:
        if '* daemon not running' in sn[1]:
            for i in range(3, (num - 1)):
                serialN = sn[i].split("\t")[0]
        else:
            for i in range(1, (num - 1)):
                serialN = sn[i].split("\t")[0]
    return serialN

def ATD():
    """
    call 112
    """
    mars.Print("CALL 112 and hold up {0}".format(call_time))
    mars.SendAT('atd112;', 1)
    for i in range(call_time // 1000):
        atRespCops = mars.WaitAT('CALLDISCONNECT', False, 1000)
        mars.Print(atRespCops)
        if atRespCops:
            mars.SendAT('atd112;', 1)
        else:
            mars.Print("{0}s 112 ".format(i))

def check_clcc():
    """
    check call status
    """
    mars.Print("check call status")
    for retry_times in range(1, 6):
        mars.SendAT('at+clcc', 1000, 1)
        atRespClcc = mars.WaitAT('+CLCC: 1,0,0', False, 20000)
        if atRespClcc:
            mars.Print("call established successfully")
            break
        else:
            if retry_times == 5:
                mars.Verdict("fail", "call established failed")
            mars.Print("call established failed {} times".format(retry_times))
            time.sleep(5)
            continue

def ATD_check_clcc():
    """
    call 10010(check clcc)
    """
    mars.Print("start call 10010")
    mars.SendAT('atd10010;', 1000, 1)
    atRespCops = mars.WaitAT('OK', False, 20000)
    if atRespCops:
        mars.Print("send atd10010; success")
        time.sleep(5)
        check_clcc()
        mars.SendAT('ath', 1000, 1)
    else:
        mars.SendAT('ath', 1000, 1)
        mars.Print("send atd10010; failed")
        mars.Verdict("fail", "send atd10010; failed")

def ping_rndis_network_gsm():
    """
    ping rndis network(lock gsm network)
    """
    if NetCardInfo().ping_rndis_network():
        mars.Print("PC ping baidu pass")
    else:
        mars.Print("PC ping baidu fail")
        mars.Verdict("fail", "PC ping baidu fail")

def cs_ps_event_random():
    event_num = random.randint(1, 2)
    if event_num == 1:
        mars.Print("do cs event")
        ATD_check_clcc()
    else:
        mars.Print("do ps event")
        NetCardInfo().ping_rndis_network()

class NetCardInfo(object):
    def __init__(self):
        self.mac_addr = ''
        self.ip = ''
        self.net_card_name = ''
        self.is_rndis = False
        self.info_start_line = 0
        self.info_end_line = 0

    def get_all_ethernet_cards_info(self):
        """
        get ethernet cards information
        """
        ethernet_cards_list = []
        cmd = os.popen("ipconfig -all")
        result = cmd.read()
        all_lines = result.splitlines()
        for line_index in range(len(all_lines)):
            # Windows IP configuration
            if len(all_lines[line_index]) > 0 and all_lines[line_index][0] != ' ':
                if all_lines[line_index].find("以太网适配器") != -1:
                    info_start_line = line_index
                    if len(ethernet_cards_list) != 0:
                        ethernet_cards_list[len(ethernet_cards_list) - 1].info_end_line = line_index - 1
                    net_card = NetCardInfo()
                    net_card.net_card_name = all_lines[line_index].split(' ')[1]  # Ethernet:
                    net_card.net_card_name = net_card.net_card_name.replace(":", "")  # remove the colon
                    net_card.info_start_line = info_start_line
                    ethernet_cards_list.append(net_card)
                    print("net_card.net_card_name： ", net_card.net_card_name)
        if len(ethernet_cards_list) >= 1:
            ethernet_cards_list[len(ethernet_cards_list) - 1].info_end_line = len(all_lines) - 1
        for each in ethernet_cards_list:
            for index in range(each.info_start_line, each.info_end_line):
                if all_lines[index].find("Remote NDIS") != -1:
                    each.is_rndis = True
                if all_lines[index].find("IPv4") != -1:
                    ip_line = all_lines[index]
                    print("***************: ", all_lines[index])
                    ip_line = ip_line.split(":")[1].strip()
                    ip_line = ip_line.split("(")[0]  # 192.168.0.100(first choice)
                    each.ip = ip_line
                    break
        return ethernet_cards_list

    def ping_rndis_network(self):
        """
        ping RNDIS network
        :return: True/False
        """
        ip = ''
        net_domain = 'www.baidu.com'
        net_card_list = NetCardInfo().get_all_ethernet_cards_info()
        for each_card in net_card_list:
            if each_card.is_rndis == True:
                ip = each_card.ip
                break
        if len(ip) > 0:
            mars.Print('ip rndis addr: %s' % ip)
        else:
            mars.Print('get rndis ip failed')
        net_card_ip = ip
        ping_cmd = "ping {0} -S {1} -n 10".format(net_domain, net_card_ip)
        mars.Print(ping_cmd)
        result = os.popen(ping_cmd).readlines()
        result_str = ''.join(result)
        mars.Print(result_str)
        ping_success_num = result_str.count("字节=")
        if ping_success_num >= 2:
            mars.Print('PC ping baidu sucess')
            return True
        else:
            mars.Print('PC ping baidu failed')
            mars.Verdict("fail", "PC ping baidu fail")
            return False
