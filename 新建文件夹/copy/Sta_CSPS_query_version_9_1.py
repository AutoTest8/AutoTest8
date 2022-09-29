#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Sta_idle_query_version.py
# @Author: xh
# @Date  : 2022/3/3
# @Desc  : 1.query version
#          2.open sta
#          3.randomly do PS or CS event
#          4.standby for one minute
#          5.query version
#          6.close sta

import os
import mars
import time
import random


# user define ap_name ap_pwd
ap_name = "tlwr886n"
ap_pwd = "123456789"

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


def check_rndis_exist():
    cmd = os.popen("ipconfig -all")
    result = cmd.read()
    result = str(result)
    mars.Print("rndis result = %s" %result)                       # add by luliangliang 2022.8.3    打印rndis
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
            mars.Print("rndis result = %s" % result)                         # add by luliangliang
            if result.find("NDIS") != -1:
                mars.Print("rndis -----exist")
                break
            else:
                if i == 4:
                    mars.Verdict("fail", "rndis -----not exist--------")
                continue

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
    event_num = 2
    if event_num == 1:
        mars.Print("do cs event")
        ATD_check_clcc()
    else:
        mars.Print("do ps event")
        NetCardInfo().ping_rndis_network()

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
        ping_result = False
        ping_count = 0
        net_domain = 'www.baidu.com'
        net_card_list = NetCardInfo().get_all_ethernet_cards_info()

        for card_test in net_card_list:                     #add by luliangliang 2022.8.23  输出所有ip，判断lte ip是否存在
            mars.Print("each_ip %s" %card_test.ip)

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
        while ping_count < 5:
            net_card_ip = ip
            ping_cmd = "ping {0} -S {1} -n 10".format(net_domain, net_card_ip)
            mars.Print(ping_cmd)
            mars.Print('at+cops?')
            mars.SendAT('at+cops?', 1000, 1)
            result = os.popen(ping_cmd).readlines()
            result_str = ''.join(result)
            mars.Print(result_str)
            ping_success_num = result_str.count("字节=")
            if ping_success_num >= 2:
                mars.Print('PC ping baidu sucess')
                ping_result = True
                ping_count = 5
            else:
                mars.Print('PC ping baidu failed by modem,it not related to wifi operation')
                # lock_lte_network()
                mars.Verdict("fail", "PC ping baidu fail,it not related to wifi operation")
                ping_count = ping_count + 1
        return ping_result
class HeronWifiBaseaction(object):

    def close_sta(self):
        """
        close sta
        :return: True/False\
        """
        mars.Print("close sta")
        mars.SendAT('at+wifi=sdio_wifi_open', 1)
        atRespSdio = mars.WaitAT('OK', False, 20000)
        if atRespSdio:
            mars.SendAT('at+wifi=wifi_close', 1)
            atRespCops = mars.WaitAT('OK', False, 20000)
            mars.Print(atRespCops)
            if atRespCops:
                mars.Print("at+wifi=wifi_close")
                time.sleep(10)
                return True
            else:
                return False
        else:
            mars.Print("send at command:at+wifi=sdio_wifi_open failed")

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
        find_ap1 = False
        find_scan_num = 0
        if atResp:
            time.sleep(15)
            mars.Print("send 'at+wifi=sdio_wifi_open' success")
            mars.Print("send 'at+wifi=sdio_scan' ")
            # atResp = mars.WaitAT('OK', False, 10000)
            # mars.Print(atResp)

            while (not find_ap1):                           # add by luliangliang 8.28 为了避免出现扫描网络中没有tlwr886n,所以选择重扫
                time.sleep(5)
                mars.Print("send 'at+wifi=sdio_scan' % scan_num" % find_scan_num)
                mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                atResp = mars.WaitAT()
                mars.Print(atResp)
                if atResp.find(ap_name) != -1:
                    mars.Print("scan tlwr886n successful")
                    break
                elif find_scan_num >= 3:
                    mars.Print("not scan tlwr886n")
                    mars.Print("Scan hotspots fail:not found {0}".format(ap_name))
                    mars.Verdict("fail", "Scan hotspots fail:not found {0}".format(ap_name))
                    return False
                else:
                    find_scan_num = find_scan_num + 1


            # mars.SendAT('at+wifi=wifi_scan', 1000, 1)
            # atResp = mars.WaitAT('OK', False, 10000)
            # mars.Print(atResp)
            mars.SendAT('at+wifi=wifi_open sta {0} {1}'.format(ap_name, ap_pwd), 1000, 1)
            atResp = mars.WaitAT('OK', False, 10000)
            mars.Print(atResp)
            if atResp:
                mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                atResp = mars.WaitAT('ssid={0}'.format(ap_name), False, 15000)
                if atResp:
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




    def wifi_connect_encryption_ap1(self):
        """connect user define AP_NAME AP_PSW"""
        # scan_c = 0
        find_ap1 = False
        find_scan_num = 0
        mars.SendAT('at+wifi=sdio_wifi_open', 1000, 1)
        atResp = mars.WaitAT('OK', False, 10000)
        scan_fail = 0
        if atResp:
            time.sleep(15)  ###等待bin文件加载完成
            mars.Print("send 'at+wifi=sdio_wifi_open' success")
            # mars.SendAT('at+wifi=wifi_scan', 1000, 1)
            # mars.WaitAT('OK', False, 10000)
            # mars.Print(atResp)

            while (not find_ap1):  # add by luliangliang 8.28 为了避免出现扫描网络中没有tlwr886n,所以选择重扫
                time.sleep(5)
                mars.Print("send 'at+wifi=sdio_scan' % scan_num" % find_scan_num)
                mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                atResp = mars.WaitAT()
                mars.Print(atResp)
                if atResp.find(ap_name) != -1:
                    mars.Print("scan tlwr886n successful")
                    break
                elif find_scan_num >= 3:
                    mars.Print("not scan tlwr886n")
                    mars.Print("Scan hotspots fail:not found {0}".format(ap_name))
                    mars.Verdict("fail", "Scan hotspots fail:not found {0}".format(ap_name))
                    return False
                else:
                    find_scan_num = find_scan_num + 1
            time.sleep(2)
            mars.SendAT('at+wifi=wifi_open sta {0} {1}'.format(ap_name, ap_pwd), 1000, 1)
            atResp = mars.WaitAT('OK', False, 10000)
            mars.Print(atResp)
            find_ap = False
            if atResp:
                mars.Print('at+wifi=wifi_open sta {0} {1} success'.format(ap_name, ap_pwd))










if __name__ == '__main__':
    check_rndis_exist()
    if HeronWifiBaseaction().close_sta():
        mars.Print("close sta pass")

        mars.Print("*****************************************")
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
        net_card_list1 = NetCardInfo().get_all_ethernet_cards_info()

        for card_test in net_card_list1:  # add by luliangliang 2022.8.23  输出所有ip，判断lte ip是否存在
            mars.Print("each_ip %s" % card_test.ip)

        for each_card in net_card_list1:
            if each_card.is_rndis == True:
                mars.Print("ip = %s" % each_card.ip)
                break
        mars.Print("*****************************************")


        if HeronWifiBaseaction().open_sta_notconnect_ap():
            mars.Print("open sta pass")
            # lock_wcdma_network()
            mars.SendAT('at+wifi=wifi_close', 1)
            time.sleep(5)

            net_card_list = NetCardInfo().get_all_ethernet_cards_info()

            for card_test in net_card_list:  # add by luliangliang 2022.8.23  输出所有ip，判断lte ip是否存在
                mars.Print("each_ip %s" % card_test.ip)

            for each_card in net_card_list:
                if each_card.is_rndis == True:
                    mars.Print("ip = %s" %each_card.ip)
                    break

            mars.Print("*****************************************")
            lock_lte_network()
            # ##    add by luliangliang
            # mars.Print("send at retry check rndis")
            # mars.SendAT('at+log=15,1', 1000, 1)
            # atResp = mars.WaitAT('OK', False, 10000)
            # if atResp:
            #     time.sleep(5)
            #     mars.SendAT('at+log=15,0', 1000, 1)
            #     atResp = mars.WaitAT('OK', False, 20000)
            #     if atResp:
            #         mars.Print("at+log=15,0,success")
            # #
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
            net_card_list1 = NetCardInfo().get_all_ethernet_cards_info()

            for card_test in net_card_list1:  # add by luliangliang 2022.8.23  输出所有ip，判断lte ip是否存在
                mars.Print("each_ip %s" % card_test.ip)

            for each_card in net_card_list1:
                if each_card.is_rndis == True:
                    mars.Print("ip = %s" %each_card.ip)
                    break
            mars.Print("*****************************************")

            time.sleep(10)
            cs_ps_event_random()
            time.sleep(20)
            query_version()
            HeronWifiBaseaction().wifi_connect_encryption_ap1()

        else:
            mars.Print("open sta fail")
            mars.Verdict("fail", "open sta fail")
    else:
        mars.Print("close sta fail")
        mars.Verdict("fail", "close sta fail")