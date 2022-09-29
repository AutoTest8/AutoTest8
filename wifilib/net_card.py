#!/usr/bin/env python
# coding:utf-8
"""
Name  : net_card.py
Author:
Time  : 2021/12/17 10:36
Desc  :
    net_card
"""
import os
import mars
import time
import webbrowser
import traceback
import subprocess

#user define
STANDBY_TIME = 10
AP_NAME = "asr-guest"
AP_PSW = "asr123456"
URL = "https://www.huya.com/"

class net_card_info(object):
    def __init__(self):
        self.mac_addr = ''
        self.ip = ''
        self.net_card_name = ''
        self.is_rndis = False
        self.info_start_line = 0
        self.info_end_line = 0

    def get_all_ethernet_cards_info(self):
        #log = LogHandler('script_log')
        rndis_line = 0
        ip_line = ''
        info_start_line = 0
        ethernet_cards_list = []
        cmd = os.popen("ipconfig -all")
        result = cmd.read()
        all_lines = result.splitlines()
        for line_index in range(len(all_lines)):
            #Windows IP 配置
            #以太网适配器 以太网:
            #以太网适配器 rndis:
            if len(all_lines[line_index]) > 0 and all_lines[line_index][0] != ' ':
                if all_lines[line_index].find("以太网适配器") != -1:
                    info_start_line = line_index
                    if len(ethernet_cards_list) != 0:
                        ethernet_cards_list[len(ethernet_cards_list) - 1].info_end_line = line_index -1
                    net_card = net_card_info()
                    net_card.net_card_name = all_lines[line_index].split(' ')[1]#以太网:
                    net_card.net_card_name = net_card.net_card_name.replace(":","")#去掉冒号
                    net_card.info_start_line = info_start_line
                    ethernet_cards_list.append(net_card)
                    print("net_card.net_card_name： ",net_card.net_card_name)
                    #log.info('net_card.net_card_name: %s' % net_card.net_card_name)
        if len(ethernet_cards_list) >= 1:
            ethernet_cards_list[len(ethernet_cards_list) - 1].info_end_line = len(all_lines) -1

        for each in ethernet_cards_list:
            for index in range(each.info_start_line,each.info_end_line):
                if all_lines[index].find("Remote NDIS") != -1:
                    each.is_rndis = True
                if all_lines[index].find("IPv4") != -1:
                    ip_line = all_lines[index]
                    print("***************: ", all_lines[index])
                    ip_line = ip_line.split(":")[1].strip()
                    ip_line = ip_line.split("(")[0]  # 192.168.0.100(首选)
                    each.ip = ip_line
                    break

        return ethernet_cards_list

    def get_pc_ip_of_rndis(self):
        net_card_ip = ''
        #log = LogHandler('script_log')
        net_card_list = net_card_info().get_all_ethernet_cards_info()
        for each_card in net_card_list:
            if each_card.is_rndis == True:
                net_card_ip = each_card.ip
                break
        if len(net_card_ip) > 0:
            print('ip rndis addr: %s' % net_card_ip)
        else:
            print('get rndis ip failed')
        return net_card_ip

    def ping_network(net_domain,net_card_ip):
        ping_cmd = "ping {0} -S {1}".format(net_domain,net_card_ip)
        result = os.popen(ping_cmd).read()
        print("---------: ",result)
        ping_success_num = result.count("字节=")
        print("ping_success_num: ",ping_success_num)
        if ping_success_num >= 2:
            mars.Print('ping sucess')
            #log.shutdown()
            return True
        else:
            mars.Print('ping_failed')
            #log.shutdown()
            return False

    # def ping_RNDIS_network(self):
    #     ip = ''
    #     net_domain = 'www.baidu.com'
    #     #log = LogHandler('script_log')
    #     net_card_list = net_card_info().get_all_ethernet_cards_info()
    #     for each_card in net_card_list:
    #         if each_card.is_rndis == True:
    #             ip = each_card.ip
    #             break
    #     if len(ip) > 0:
    #         print('ip rndis addr: %s' % ip)
    #     else:
    #         print('get rndis ip failed')
    #     net_card_ip = ip
    #     ping_cmd = "ping {0} -S {1}".format(net_domain,net_card_ip)
    #     mars.Print(ping_cmd)
    #     result = os.popen(ping_cmd).read()
    #     mars.Print("---------: ",result)
    #     ping_success_num = result.count("字节=")
    #     mars.Print("ping_success_num: ",ping_success_num)
    #     if ping_success_num >= 2:
    #         mars.Print('ping baidu sucess')
    #         #log.shutdown()
    #         return True
    #     else:
    #         mars.Print('ping baidu failed')
    #         #log.shutdown()
    #         return False

    def ping_RNDIS_network(self):
        ip = ''
        net_domain = 'www.baidu.com'
        #log = LogHandler('script_log')
        net_card_list = net_card_info().get_all_ethernet_cards_info()
        for each_card in net_card_list:
            if each_card.is_rndis == True:
                ip = each_card.ip
                break
        if len(ip) > 0:
            mars.Print('ip rndis addr: %s' % ip)
        else:
            mars.Print('get rndis ip failed')
        net_card_ip = ip
        ping_cmd = "ping {0} -S {1}".format(net_domain,net_card_ip)
        mars.Print(ping_cmd)
        ping_cnt = 0
        while(True):
            mars.Print("start")
            result = os.popen(ping_cmd).readlines()
            mars.Print("stop")
            result_str = ''.join(result)
            mars.Print(result_str)
            ping_success_num = result_str.count("字节=")
            # mars.Print("ping_success_num: ",ping_success_num)
            if ping_success_num >= 2:
                mars.Print('ping baidu sucess')
                #log.shutdown()
                return True
            elif ping_cnt == 3:
                mars.Print('ping baidu failed')
                #log.shutdown()
                return False
            else:
                ping_cnt =ping_cnt+1
                mars.Print("ping baidu number %d" % ping_cnt)
                
