#!/usr/bin/env python
# coding:utf-8
"""
Name  : sta_TPLink_channel_encryption.py
Author: xh
Time  : 2021/12/15 15:23
Desc  :
        1. check_rndis_exist                   # adjust rndis whether is exist
        2. query_version                       # check query_version
        3. class :: NetCardInfo
                get_all_ethernet_cards_info    # get netlink info
                ping_rndis_network             # get ip of rndis, and use it to ping baidu
        4  call 10010
                ATD_check_clcc                 # call 10010
                check_clcc                     # check call status
        5. cs_ps_event_random                  # choose the operatoe from ping and call
        6. N3 :
                get_N3_serial                  # get N3 serial
                n3_wifi_on                     # open N3
                n3_wifi_scan                   # check whether ap_name is in the list of N3
        7. lock network:
                lock_lte_network               # lock 4G
                lock_wcdma_network             # lock 3G

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

# check whether rndis is exist
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
                continue                 #

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
                    net_card = NetCardInfo()                             # define new object
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
            mars.Print("check call status failed {} times".format(retry_times))
            time.sleep(5)
            continue

def ATD_check_clcc():
    """
    call 10000(check clcc)
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
        mars.SendAT('at+cops?', 1000, 1)
        mars.Print("send atd10010; failed")
        mars.Verdict("fail", "send atd10010; failed")

def cs_ps_event_random():
    """
    randomly do cs or ps event
    """
    event_num = random.randint(1, 2)
    if event_num == 1:
        mars.Print("do cs event")
        ATD_check_clcc()
    else:
        mars.Print("do ps event")
        NetCardInfo().ping_rndis_network()


def get_N3_serial():
    serialN = ''
    sn = os.popen('adb devices').readlines()
    num = len(sn)
    if num < 3:
        mars.Print("No Devices,please connect the device")
        return False
    else:
        if '* daemon not running' in sn[1]:
            for i in range(3, (num - 1)):
                serialN = sn[i].split("\t")[0]
        else:
            for i in range(1, (num - 1)):
                serialN = sn[i].split("\t")[0]
    return serialN

def n3_wifi_on(serialN):
    """
    open n3 wifi
    :param serialN: devices serial number
    """
    # adb shell
    obj = subprocess.Popen('adb -s %s shell' % serialN, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, shell=True)
    # open n3 wifi
    obj.communicate(input='svc wifi enable'.encode())

def n3_wifi_scan(serialN):
    """
    search for visible wifi
    :param serialN: devices serial number
    :return: True/False
    """
    for scan_num in range(1, 4):
        # adb shell
        obj = subprocess.Popen(['adb', '-s', '{0}'.format(serialN), 'shell'], shell=True, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # obtain system level permissions
        obj.stdin.write('su\n'.encode('utf-8'))
        time.sleep(1)
        # search for visible wifi
        obj.stdin.write('wpa_cli -i wlan0 scan\n'.encode('utf-8'))
        time.sleep(15)
        # search for visible wifi results
        obj.stdin.write('wpa_cli -i wlan0 scan_results\n'.encode('utf-8'))
        time.sleep(15)
        # the key point is to execute exit
        obj.stdin.write('exit\n'.encode('utf-8'))
        info, err = obj.communicate()
        if err.decode('gbk'):
            mars.Print("the {0} N3 wifi cannot work well!!".format(scan_num))
            mars.Print(err.decode('gbk'))
        else:
            if ap_name in info.decode('gbk'):
                mars.Print("ap {0} find in N3 WLAN list".format(ap_name))
                return True
            else:
                mars.Print("the {0} ap not find in N3 WLAN list".format(scan_num))
                mars.Print(info.decode('gbk'))
        # search four times
        if scan_num > 4:
            mars.Print("N3 cannot find this ap in 3 times")
            # return False


def lock_lte_network():
    """
    lock lte network
    """
    mars.Print("lock LTE network")
    mars.SendAT('AT*BAND=5', 1000, 1)
    atResp = mars.WaitAT('OK', False, 10000)
    if atResp:
        mars.Print("send AT command:AT*BAND=11 success")
        time.sleep(5)
        for retry_times in range(1, 7):
            mars.SendAT('AT+COPS?', 1000, 1)
            atResp2 = mars.WaitAT(',7', False, 10000)
            if atResp2:
                mars.Print("registered LTE network successfully")
                break
            else:
                if retry_times == 6:
                    mars.Verdict("fail", "registered LTE network failed")
                mars.Print("registered LTE network failed {} times".format(retry_times))
                time.sleep(15)
                continue
    else:
        mars.Print("send AT command:AT*BAND=11 failed")
        mars.Verdict("fail", "send AT command:AT*BAND=11 failed")


## 添加WCDMA 3G网络
def lock_wcdma_network():
    """
    lock wcdma network
    """
    mars.Print("lock WCDMA network")
    mars.SendAT('AT*BAND=1', 1000, 1)
    atResp = mars.WaitAT('OK', False, 10000)
    if atResp:
        mars.Print("send AT command:AT*BAND=1 success")
        time.sleep(5)
        for retry_times in range(1, 7):
            mars.SendAT('AT+COPS?', 1000, 1)
            atResp2 = mars.WaitAT(',2', False, 10000)
            if atResp2:
                mars.Print("registered WCDMA network successfully")
                break
            else:
                if retry_times == 6:
                    mars.Verdict("fail", "registered WCDMA network failed")
                mars.Print("registered WCDMA network failed {} times".format(retry_times))
                time.sleep(15)
                continue
    else:
        mars.Print("send AT command:AT*BAND=1 failed")
        mars.Verdict("fail", "send AT command:AT*BAND=1 failed")





#
#
# def lock_lte_network():
#     """
#     lock lte network
#     """
#     mars.Print("lock LTE network")
#     mars.SendAT('AT*BAND=5', 1000, 1)
#     atResp = mars.WaitAT('OK', False, 10000)
#     if atResp:
#         mars.Print("send AT command:AT*BAND=11 success")
#         time.sleep(5)
#         for retry_times in range(1, 7):
#             mars.SendAT('AT+COPS?', 1000, 1)
#             atResp2 = mars.WaitAT(',7', False, 10000)
#             if atResp2:
#                 mars.Print("registered LTE network successfully")
#                 break
#             else:
#                 if retry_times == 6:
#                     mars.Verdict("fail", "registered LTE network failed")
#                 mars.Print("registered LTE network failed {} times".format(retry_times))
#                 time.sleep(15)
#                 continue
#     else:
#         mars.Print("send AT command:AT*BAND=11 failed")
#         mars.Verdict("fail", "send AT command:AT*BAND=11 failed")
#
# ## 添加WCDMA 3G网络
# def lock_wcdma_network():
#     """
#     lock wcdma network
#     """
#     mars.Print("lock WCDMA network")
#     mars.SendAT('AT*BAND=1', 1000, 1)
#     atResp = mars.WaitAT('OK', False, 10000)
#     if atResp:
#         mars.Print("send AT command:AT*BAND=1 success")
#         time.sleep(5)
#         for retry_times in range(1, 7):
#             mars.SendAT('AT+COPS?', 1000, 1)
#             atResp2 = mars.WaitAT(',2', False, 10000)
#             if atResp2:
#                 mars.Print("registered WCDMA network successfully")
#                 break
#             else:
#                 if retry_times == 6:
#                     mars.Verdict("fail", "registered WCDMA network failed")
#                 mars.Print("registered WCDMA network failed {} times".format(retry_times))
#                 time.sleep(15)
#                 continue
#     else:
#         mars.Print("send AT command:AT*BAND=1 failed")
#         mars.Verdict("fail", "send AT command:AT*BAND=1 failed")
#
#
#
#
#
# class N3_wifi():
#     #
#     def n3_wifi_on(self):
#         """
#         open n3 wifi
#         :param serialN: devices serial number
#         """
#         serialN = N3_wifi().serialN_get()
#         # adb shell
#         obj = subprocess.Popen('adb -s %s shell' % serialN, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
#                                stderr=subprocess.PIPE, shell=True)
#         # open n3 wifi
#         obj.communicate(input='svc wifi enable'.encode())
#
#     # Scan wifi whther is exist in N3's list
#     def n3_wifi_scan(self):
#         """
#         search for visible wifi
#         :param serialN: devices serial number
#         :return: True/False
#         """
#         serialN = N3_wifi().serialN_get()
#         for scan_num in range(1, 4):
#             # adb shell
#             obj = subprocess.Popen(['adb', '-s', '{0}'.format(serialN), 'shell'], shell=True, stdin=subprocess.PIPE,
#                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#             # obtain system level permissions
#             obj.stdin.write('su\n'.encode('utf-8'))
#             time.sleep(1)
#             # search for visible wifi
#             obj.stdin.write('wpa_cli -i wlan0 scan\n'.encode('utf-8'))
#             time.sleep(15)
#             # search for visible wifi results
#             obj.stdin.write('wpa_cli -i wlan0 scan_results\n'.encode('utf-8'))
#             time.sleep(15)
#             # the key point is to execute exit
#             obj.stdin.write('exit\n'.encode('utf-8'))
#             info, err = obj.communicate()
#             if err.decode('gbk'):
#                 mars.Print("the {0} N3 wifi cannot work well!!".format(scan_num))
#                 mars.Print(err.decode('gbk'))
#             else:
#                 if ap_name in info.decode('gbk'):
#                     mars.Print("ap {0} find in N3 WLAN list".format(ap_name))
#                     return True
#                 else:
#                     mars.Print("the {0} ap not find in N3 WLAN list".format(scan_num))
#                     mars.Print(info.decode('gbk'))
#             # search four times
#             if scan_num > 4:
#                 mars.Print("N3 cannot find this ap in 3 times")
#                 # return False
#     # Get N3's serial number
#     def serialN_get(self):
#         serialN = ''
#         sn = os.popen('adb devices').readlines()
#         num = len(sn)
#         if num < 3:
#             mars.Print("No Devices,please connect the device")
#             return False
#         else:
#             if '* daemon not running' in sn[1]:
#                 for i in range(3, (num - 1)):
#                     serialN = sn[i].split("\t")[0]
#             else:
#                 for i in range(1, (num - 1)):
#                     serialN = sn[i].split("\t")[0]
#         return serialN
#
# class PcNetworkUtil():
#
#    """
#         获取config 的name': '', 'DNS(连接特定的 DNS 后缀)': '', 'ip(IPv4 地址)': '', 'desc(描述)':
#    """
#     def get_network_info(self):
#         '''
#             获取ipconfig数据
#             Returns:
#                 [{'name': '', 'DNS(连接特定的 DNS 后缀)': '', 'ip(IPv4 地址)': '', 'desc()': ''}]
#         '''
#         net_ipconfig_list = []
#         network= subprocess.Popen('ipconfig /all', stdout=subprocess.PIPE, shell=True)
#         network_infos = network.stdout.readlines()
#         # network_infos = (temp_list).split(b'\r\n')
#         tmp_network_name = None
#         for line_byte in network_infos:
#             line = line_byte.decode('gbk').strip()    # 解码encode
#             if line.startswith('以太网适配器'):
#                 tmp_network_name = line[7:-1]         # copy line 第七行到倒数第2行字符
#                 net_ipconfig_list.append({'name': tmp_network_name, 'DNS': '', 'ip': '', 'desc': ''})
#             else:
#                 if tmp_network_name is not None:
#                     if line.startswith('描述'):
#                         net_ipconfig_list[-1]['desc'] = line.split('. . : ')[1]
#                     elif line.startswith('连接特定的 DNS 后缀'):
#                         if len(line.split('. . : ')) > 1:
#                             net_ipconfig_list[-1]['DNS'] = line.split('. . : ')[1]
#                         else:
#                             net_ipconfig_list[-1]['DNS'] = ''
#                     elif line.startswith('IPv4 地址'):
#                         net_ipconfig_list[-1]['ip'] = line.split('. . : ')[1].split('(')[0]
#                         tmp_network_name = None
#         print("====>", net_ipconfig_list)
#         return net_ipconfig_list
#
#     """
#         auto serchwork
#         at + cops=? at+cops=0
#     """
#     def search_network(self):
#         """
#         search network information
#         """
#         atResp = 'ok'
#         if atResp:
#             mars.SendAT('at+cops=?', 1000, 1)
#             mars.Print("send AT command: at+cops=?")
#             atResp = mars.WaitAT('OK', False, 360000)
#             if atResp:
#                 mars.Print("send AT command:at+cops=? success")
#                 mars.SendAT('at+cops=0', 1000, 1)
#                 atResp = mars.WaitAT('OK', False, 360000)
#                 if atResp:
#                     mars.Print("send AT command:at+cops=0 success")
#                     time.sleep(15)
#                     mars.Print("start check network")
#                     check_network()
#                 else:
#                     mars.SendAT('at+cops=0', 1000, 1)
#                     mars.Print("send AT command:at+cops=0 failed")
#                     mars.Verdict("fail", "send AT command:at+cops=0 failed")
#             else:
#                 mars.Print("send AT command:at+cops=? failed")
#                 mars.Verdict("fail", "send AT command:at+cops=? failed")
#         else:
#             mars.Print("send AT command:at+cops=2 failed")
#             mars.Verdict("fail", "send AT command:at+cops=2 failed")
#
# class heron_wifi_baseaction():
#
#     """
#         close sta
#         at+wifi=wifi_close
#     """
#     def close_sta(self):
#         mars.Print("close sta ,send AT")
#         mars.SendAT('at+wifi=wifi_close', 1)
#         atRespCops = mars.WaitAT('OK', False, 20000)
#         mars.Print(atRespCops)
#         if atRespCops:
#             time.sleep(10)
#             return True
#         else:
#             return False
#
#     """
#         get every sta's ip
#         at + wifi =wifi_get_peer_sta_info
#     """
#     def ip_check(self):
#         mars.SendAT('at + wifi =wifi_get_peer_sta_info', 1)
#         atRespCops = mars.WaitAT('OK', False, 20000)
#         mars.Print(atRespCops)
#         if atRespCops:
#             return True
#         else:
#             return False
#
#     """
#         check ap_name whether is in the result list of scan.if not, so Cycle scan three times
#         at+wifi=wifi_scan
#     """
#     def check_wifi_scan(self, atResp):
#
#         mars.Print("check_wifi_scan")
#         find_scan_num = 0
#         if atResp.find(ap_name) != -1:
#             mars.Print("scan {0} successful".format(ap_name))
#             return True
#         else:
#             while(True):
#                 time.sleep(5)
#                 mars.Print("send 'at+wifi=sdio_scan' % scan_num" % find_scan_num)
#                 mars.SendAT('at+wifi=wifi_scan', 1000, 1)
#                 atResp = mars.WaitAT()
#                 mars.Print(atResp)
#                 if atResp.find(ap_name) != -1:
#                     mars.Print("scan {0} successful".format(ap_name))
#                     return True
#                 elif find_scan_num >= 3:
#                     mars.Print("not scan {0}".format(ap_name))
#                     mars.Print("Scan hotspots fail:not found {0}".format(ap_name))
#                     return False
#                 else:
#                     find_scan_num = find_scan_num + 1
#
#     """
#
#     """
#     def notebook_ping(self):
#         try:
#             mars.SendAT('at+log=15,0', 1000, 1)
#             time.sleep(3)
#             ping_url = 'ping www.baidu.com'
#             exit_code = os.system(ping_url)
#             time.sleep(5)
#             # 网络连通 exit_code == 0，否则返回非0值。
#             if exit_code == 0:
#                 mars.Print("ping baidu pass")
#                 return True
#             else:
#                 mars.Print("ping baidu fail")
#                 mars.Verdict("fail", "ping baidu fail")
#                 return False
#         except Exception as e:
#             mars.Print("ping baidu fail")
#             mars.Verdict("fail", "ping baidu fail")
#             return False
#
#     def NetWork_enabled(self):
#         for tmp_network in PcNetworkUtil.get_network_info():
#             if 'Intel(R) Ethernet Connection' not in tmp_network['desc']:
#                 operate = 'enabled'
#                 cmd = 'netsh interface set interface name="{0}" admin={1}'.format(
#                     tmp_network['name'], operate)
#                 subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
#                 # CraneFunHeronWifiEncryptionEnumAP().runAdmin(cmd)
#             else:
#                 mars.Print("enable Ethernet Connection fail")
#
# class wifi_scan_and_connect_baseaction(heron_wifi_baseaction):
#     def wifi_scan_before_connect(self):
#         mars.Print("***********wifi_scan_before_connect*********")
#
#         mars.SendAT('at+wifi=sdio_wifi_open', 1000, 1)
#         atResp = mars.WaitAT('OK', False, 10000)
#         scan_fail = 0
#         if atResp:
#             time.sleep(15)  ###等待bin文件加载完成
#             mars.Print("send 'at+wifi=sdio_wifi_open' success")
#             mars.SendAT('at+wifi=wifi_open sta', 1000, 1)
#             atResp = mars.WaitAT('OK', False, 10000)
#             if atResp:
#                 time.sleep(10)
#                 mars.Print("open sta success")
#                 mars.SendAT('at+wifi=wifi_scan', 1000, 1)
#                 result = mars.WaitAT()
#                 mars.Print("result %s {0}" % result)
#                 if heron_wifi_baseaction().check_wifi_scan(result):
#                     mars.Print("Scan hotspots pass:found {0}".format(ap_name))
#                 else:
#                     mars.Print("wifi_scan_before_connect Scan hotspots fail:not found {0}".format(ap_name))
#                     mars.Verdict("fail", "wifi_scan_before_connect Scan hotspots fail:not found {0}".format(ap_name))
#                     return False
#             else:
#                 mars.Print("open sta fail")
#                 mars.Verdict("fail", "open sta fail")
#                 return False
#         else:
#             mars.Print("send 'at+wifi=sdio_wifi_open' fail")
#             mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")
#             return False
#
#     def wifi_scan_connected(self):
#
#         mars.Print("************** wifi_scan_connected *********************")
#
#         mars.SendAT('at+wifi=wifi_scan', 1000, 1)
#         result = mars.WaitAT()
#         mars.Print("result %s {0}" % result)
#         if heron_wifi_baseaction().check_wifi_scan(result):
#             mars.Print("Scan hotspots pass:found {0}".format(ap_name))
#         else:
#             mars.Print("wifi_scan_before_connect Scan hotspots fail:not found {0}".format(ap_name))
#             mars.Verdict("fail", "wifi_scan_before_connect Scan hotspots fail:not found {0}".format(ap_name))
#             return False
#
#     def wifi_connect_no_encryption_ap(self):
#         """connect user define AP_NAME AP_PSW"""
#         mars.SendAT('at+wifi=sdio_wifi_open', 1000, 1)
#         atResp = mars.WaitAT('OK', False, 10000)
#         if atResp:
#             time.sleep(15)  ###等待bin文件加载完成
#             mars.Print("send 'at+wifi=sdio_wifi_open' success")
#             mars.SendAT('at+wifi= wifi_open sta {0}'.format(ap_name), 1000, 1)
#             atResp = mars.WaitAT('OK', False, 10000)
#             mars.Print(atResp)
#             if atResp:
#                 mars.SendAT('at*lwipctrl=mode,dongle,0', 1000, 1)
#                 atResp = mars.WaitAT('OK', False, 10000)
#                 if atResp:
#                     mars.SendAT('at*lwipctrl=debug,wificlient,1', 1000, 1)
#                     atResp = mars.WaitAT('OK', False, 10000)
#                     if atResp:
#                         mars.SendAT('at*lwipctrl=log,dhcp,1', 1000, 1)
#                         atResp = mars.WaitAT('OK', False, 10000)
#                         time.sleep(45)
#                         if atResp:
#                             mars.SendAT('AT+wifi=wifi_get_ip', 1000, 1)
#                             atResp = mars.WaitAT('OK', False, 360000)
#                             if atResp:
#                                 mars.Print("send AT success: AT+wifi=wifi_get_ip")
#                                 mars.SendAT('at+wifi=wifi_open sta {0} {1}'.format(ap_name, ap_pwd), 1000,
#                                             1)  ###验证脚本用，后续需要去除
#                                 time.sleep(2)  ###验证脚本用，后续需要去除
#                                 return True
#                             else:
#                                 mars.Print("send AT fail: AT+wifi=wifi_get_ip")
#                                 mars.Verdict("fail", "send AT fail: AT+wifi=wifi_get_ip")
#                                 return False
#                         else:
#                             mars.Print("send AT fail: at*lwipctrl=log,dhcp,1")
#                             mars.Verdict("fail", "send AT fail: at*lwipctrl=log,dhcp,1")
#                             return False
#                     else:
#                         mars.Print("send AT fail: at*lwipctrl=debug,wificlient,1")
#                         mars.Verdict("fail", "send AT fail: at*lwipctrl=debug,wificlient,1")
#                         return False
#                 else:
#                     mars.Print("send AT fail: at*lwipctrl=mode,dongle,0")
#                     mars.Verdict("fail", "send AT fail: at*lwipctrl=mode,dongle,0")
#                     return False
#             else:
#                 mars.Print('Scan hotspots fail:not found tlwr886n')
#                 mars.Verdict("fail", "Scan hotspots fail:not found tlwr886n")
#                 return False
#         else:
#             mars.Print("send 'at+wifi=sdio_wifi_open' fail")
#             mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")
#
#     def wifi_connect_encryption_ap(self):
#         """connect user define AP_NAME AP_PSW"""
#         mars.Print("wifi_connect_encryption_ap")
#
#         mars.SendAT('at+wifi=sdio_wifi_open', 1000, 1)
#         atResp = mars.WaitAT('OK', False, 10000)
#         if atResp:
#             time.sleep(15)
#             mars.Print("send 'at+wifi=sdio_wifi_open' success")
#             mars.SendAT('at+wifi=wifi_open sta', 1000, 1)  # add by luliangliang
#             atResp = mars.WaitAT('OK', False, 10000)
#             if atResp:
#                 mars.Print("at+wifi=wifi_open sta success")
#                 mars.SendAT('at+wifi=wifi_scan', 1000, 1)
#                 atResp = mars.WaitAT()
#                 mars.Print(" scan result %s " % atResp)
#                 if heron_wifi_baseaction().check_wifi_scan(atResp):
#                     mars.Print("wifi_scan {0} success".format(ap_name))
#                 else:
#                     mars.Print("wifi_scan {0} fail".format(ap_name))
#
#             mars.SendAT('at+wifi=wifi_open sta {0} {1}'.format(ap_name, ap_pwd), 1000, 1)
#             atResp = mars.WaitAT('OK', False, 10000)
#             mars.Print(atResp)
#             if atResp:
#                 mars.SendAT('at+wifi=wifi_scan', 1000, 1)
#                 atResp = mars.WaitAT()
#                 mars.Print(" scan result %s " % atResp)
#                 if heron_wifi_baseaction().check_wifi_scan(atResp):
#                     mars.Print("Scan hotspots pass:found {0}".format(ap_name))
#                     mars.SendAT('at*lwipctrl=mode,dongle,0', 1000, 1)
#                     atResp = mars.WaitAT('OK', False, 10000)
#                     if atResp:
#                         mars.SendAT('at*lwipctrl=debug,wificlient,1', 1000, 1)
#                         atResp = mars.WaitAT('OK', False, 10000)
#                         if atResp:
#                             mars.SendAT('at*lwipctrl=log,dhcp,1', 1000, 1)
#                             atResp = mars.WaitAT('OK', False, 10000)
#                             time.sleep(45)
#                             if atResp:
#                                 mars.SendAT('AT+wifi=wifi_get_ip', 1000, 1)
#                                 atResp = mars.WaitAT('OK', False, 360000)
#                                 if atResp:
#                                     mars.Print("send AT success: AT+wifi=wifi_get_ip")
#                                     time.sleep(2)  ###验证脚本用，后续需要去除
#                                     return True
#                                 else:
#                                     mars.Print("send AT fail: AT+wifi=wifi_get_ip")
#                                     mars.Verdict("fail", "send AT fail: AT+wifi=wifi_get_ip")
#                                     return False
#                             else:
#                                 mars.Print("send AT fail: at*lwipctrl=log,dhcp,1")
#                                 mars.Verdict("fail", "send AT fail: at*lwipctrl=log,dhcp,1")
#                                 return False
#                         else:
#                             mars.Print("send AT fail: at*lwipctrl=debug,wificlient,1")
#                             mars.Verdict("fail", "send AT fail: at*lwipctrl=debug,wificlient,1")
#                             return False
#                     else:
#                         mars.Print("send AT fail: at*lwipctrl=mode,dongle,0")
#                         mars.Verdict("fail", "send AT fail: at*lwipctrl=mode,dongle,0")
#                         return False
#                 else:
#                     mars.Print("Scan hotspots fail:not found {0}".format(ap_name))
#                     mars.Verdict("fail", "Scan hotspots fail:not found {0}".format(ap_name))
#                     return False
#             else:
#                 mars.Print('Scan hotspots fail:not found tlwr886n')
#                 mars.Verdict("fail", "Scan hotspots fail:not found tlwr886n")
#                 return False
#         else:
#             mars.Print("send 'at+wifi=sdio_wifi_open' fail")
#             mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")
#
# class router_process(object):
#     def __init__(self, router_password, username, password,wlan_channel,wlan_mode, wlan_width, wlan_encryption):
#         self.username = username
#         self.password = password
#         self.router_password = router_password
#         self.wlan_channel = wlan_channel
#         self.wlan_mode = wlan_mode
#         self.wlan_width = wlan_width
#         self.wlan_encryption = wlan_encryption
#
#         self.driver = Chrome(executable_path='C:\Program Files\Google\Chrome\Application\chromedriver.exe')
#         self.my_action = ActionChains(self.driver)
#
#     def process_all(self):
#         self.log_in()
#         time.sleep(0.5)
#         if self.wlan_encryption:
#             mars.Print(" add_encryption mode ")
#             time.sleep(2)
#             self.wlan_set_encryption()
#             self.mode_slete()
#         else:
#             mars.Print(" no encryption mode ")
#             time.sleep(2)
#             self.wlan_no_encryption()
#             self.mode_slete()
#
#         mars.Print("setting success")
#
#     def log_in(self):
#         self.driver.maximize_window()
#         url = "http://192.168.1.1/"
#         self.driver.get(url)
#         # self.driver.find_element(By.ID, "inputPwd").click()
#         time.sleep(2)
#         self.driver.find_element(By.ID, "lgPwd").send_keys("AAbbcc123")
#         time.sleep(1)
#         self.driver.find_element(By.ID, "loginSub").click()
#
#
#     def wlan_set_encryption(self):
#         self.driver.find_element(By.ID, "routerSetMbtn").click()  # 路由设置
#         time.sleep(1)
#         self.driver.find_element(By.ID, "wireless2G_rsMenu").click()  # 无线设置
#         time.sleep(2)
#         mars.Print(" log in setting")
#         self.driver.find_element(By.ID, "wlanPwd").clear()
#         time.sleep(1)
#         self.driver.find_element(By.ID, "wlanPwd").click()
#         self.driver.find_element(By.ID, "wlanPwd").send_keys(self.password)  # 登录密码
#         time.sleep(2)
#         mars.Print("password has set done")
#         self.driver.find_element(By.ID, "saveBasic").click()  # 点击保存
#
#     def wlan_no_encryption(self):
#         self.driver.find_element(By.ID, "routerSetMbtn").click()  # 路由设置
#         time.sleep(0.5)
#         self.driver.find_element(By.ID, "wireless2G_rsMenu").click()  # 无线设置
#
#         time.sleep(1)
#         mars.Print(" log in setting")
#         self.driver.find_element(By.ID, "wlanPwd").clear()
#         time.sleep(1)
#         self.driver.find_element(By.ID, "saveBasic").click()  # 点击保存
#
#     def box_click(self, type, id_str, idx1):
#
#         str1 = "// *[ @ id = '{0}'] / li[{1}]".format(id_str, idx1)
#         mars.Print(str1)
#         self.driver.find_element(By.ID, type).click()
#         # time.sleep(5)
#         time.sleep(2)
#         mars.Print("click end ")
#         my_error_element = self.driver.find_element(By.XPATH, str1)
#         # time.sleep(6)
#         time.sleep(2)
#         self.my_action.move_to_element(my_error_element).perform()  # 将鼠标移动到点击的位置
#         time.sleep(2)
#         mars.Print("move end")
#         self.driver.find_element(By.XPATH, str1).click()
#
#     def mode_slete(self):
#         time.sleep(6)
#         self.box_click("channel", "selOptsUlchannel", self.wlan_channel)
#         time.sleep(3)
#         self.box_click("wlanMode", "selOptsUlwlanMode", self.wlan_mode)
#         time.sleep(5)
#         try:
#             target = self.driver.find_element(By.ID, "save")
#             self.driver.execute_script("arguments[0].scrollIntoView();", target)  # 拖动到可见的元素去
#             mars.Print("move save")
#             time.sleep(10)
#             self.driver.find_element(By.ID, "save").click()  # 点击保存
#             time.sleep(10)
#             mars.Print("save success")
#         except:
#             mars.Print("errior")


