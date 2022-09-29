import os
import mars
import time
import traceback
import subprocess
import json
from wifilib import heron_wifi
import random
from wifilib import heron_wifi
from wifilib import net_card
from wifilib import basic_fun

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


def run():
    basic_fun.check_rndis_exist()
    if heron_wifi_baseaction().close_sta():
        heron_wifi_baseaction().wifi_scan_before_connect()
        if heron_wifi_baseaction().wifi_connect_before_scan():
            mars.Print(" STA connect AP successful ")
            time.sleep(2)
            cs_ps_event_random()
            time.sleep(20)
            query_version()
        else:
            mars.Print(" STA connct AP fail ")
    else:
        mars.Print(" close AP fail ")


if __name__ == '__main__':
    run()