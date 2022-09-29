#!/usr/bin/env python
# coding:utf-8
"""
Name  : sta_TPLink_channel_encryption.py
Author: xh
Time  : 2021/12/15 15:23
Desc  :
        1.open sta
        2.scan ap
        3.TPLink Router traversal test(channel, encryption)
        4.connect user define ap
        5.data service（ping baidu.com）
        6.close sta
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

# ========= 用户设置参数 ===========
# 本测试脚本是基于TPLink:TL-WDR7400 AC1750双频路由器 编写（不同路由器设置有差异）
router = "tlwr886n"
# 路由器登录相关信息
router_username = "admin"
router_password = "AAbbcc123"
# host = "192.168.1.1"
host = "tplogin.cn"
wireless_setting = "2.4G"
# ap热点名字
ap_name = "tlwr886n"
ap_pwd = "123456789"
# tplink 待设置参数
channel = [1, 6, 11]  # 1--13
mode = ["0"]  # bgn  bg n g b
bandwidth = ["1"]  # 20
ssidbrd = [1]  # 0为隐藏  1为可见


class net_card_info(object):
    def __init__(self):
        self.mac_addr = ''
        self.ip = ''
        self.net_card_name = ''
        self.is_rndis = False
        self.info_start_line = 0
        self.info_end_line = 0

    def get_all_ethernet_cards_info(self):
        # log = LogHandler('script_log')
        rndis_line = 0
        ip_line = ''
        # info_start_line = 0
        ethernet_cards_list = []
        cmd = os.popen("ipconfig -all")
        result = cmd.read()
        all_lines = result.splitlines()
        for line_index in range(len(all_lines)):
            # Windows IP 配置
            # 以太网适配器 以太网:
            # 以太网适配器 rndis:
            if len(all_lines[line_index]) > 0 and all_lines[line_index][0] != ' ':
                if all_lines[line_index].find("以太网适配器") != -1:
                    info_start_line = line_index
                    if len(ethernet_cards_list) != 0:
                        ethernet_cards_list[len(ethernet_cards_list) - 1].info_end_line = line_index - 1
                    net_card = net_card_info()
                    net_card.net_card_name = all_lines[line_index].split(' ')[1]  # 以太网:
                    net_card.net_card_name = net_card.net_card_name.replace(":", "")  # 去掉冒号
                    net_card.info_start_line = info_start_line
                    ethernet_cards_list.append(net_card)
                    print("net_card.net_card_name： ", net_card.net_card_name)
                    # log.info('net_card.net_card_name: %s' % net_card.net_card_name)
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
                    ip_line = ip_line.split("(")[0]  # 192.168.0.100(首选)
                    each.ip = ip_line
                    break

        return ethernet_cards_list

    def get_pc_ip_of_rndis(self):
        net_card_ip = ''
        # log = LogHandler('script_log')
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

    def ping_network(net_domain, net_card_ip):
        ping_cmd = "ping {0} -S {1}".format(net_domain, net_card_ip)
        result = os.popen(ping_cmd).read()
        print("---------: ", result)
        ping_success_num = result.count("字节=")
        print("ping_success_num: ", ping_success_num)
        if ping_success_num >= 2:
            mars.Print('ping sucess')
            # log.shutdown()
            return True
        else:
            mars.Print('ping_failed')
            # log.shutdown()
            return False

    def ping_RNDIS_network(self):
        ip = ''
        net_domain = 'www.baidu.com'
        # log = LogHandler('script_log')
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
        ping_cmd = "ping {0} -S {1}".format(net_domain, net_card_ip)
        mars.Print(ping_cmd)
        result = os.popen(ping_cmd).readlines()
        result_str = ''.join(result)
        mars.Print(result_str)
        ping_success_num = result_str.count("字节=")
        # mars.Print("ping_success_num: ",ping_success_num)
        if ping_success_num >= 2:
            mars.Print('ping baidu sucess')
            # log.shutdown()
            # return True
        else:
            mars.Print('ping baidu failed')
            # log.shutdown()
            return False


class heron_wifi_baseaction(object):

    def runAdmin(self, cmd, timeout=1800000):
        f = None
        try:
            bat = os.getcwd() + r"\cmd_tool\cmd.bat"
            f = open(bat, 'w')
            f.write(cmd)
        except Exception as e:
            traceback.print_exc()
            raise e
        finally:
            if f:
                f.close()
        try:
            shell = os.getcwd() + r"\cmd_tool\shell.vbs"
            sp = subprocess.Popen(
                shell,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("[PID] %s: %s" % (sp.pid, cmd))
            sp.wait(timeout=timeout)

            stderr = str(sp.stderr.read().decode("gbk")).strip()
            stdout = str(sp.stdout.read().decode("gbk")).strip()
            if "" != stderr:
                raise Exception(stderr)
            if stdout.find("失败") > -1:
                raise Exception(stdout)
        except Exception as e:
            raise e

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

    def ip_check(self):
        mars.SendAT('at + wifi =wifi_get_peer_sta_info', 1)
        atRespCops = mars.WaitAT('OK', False, 20000)
        mars.Print(atRespCops)
        if atRespCops:
            return True
        else:
            return False

    def wifi_connect_encryption_ap(self, ap_name, ap_pwd):
        """connect user define AP_NAME AP_PSW"""
        mars.SendAT('at+wifi=sdio_wifi_open', 1000, 1)
        atResp = mars.WaitAT('OK', False, 10000)
        if atResp:
            time.sleep(15)  ###等待bin文件加载完成
            mars.Print("send 'at+wifi=sdio_wifi_open' success")
            mars.SendAT('at+wifi=wifi_scan', 1000, 1)
            time.sleep(8)
            mars.SendAT('at+wifi=wifi_open sta {0} {1}'.format(ap_name, ap_pwd), 1000, 1)
            atResp = mars.WaitAT('OK', False, 10000)
            mars.Print(atResp)
            if atResp:
                scan_fail = 0
                while True:
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
                                mars.Print('t*lwipctrl=log,dhcp,1')
                                mars.SendAT('at*lwipctrl=log,dhcp,1', 1000, 1)
                                atResp = mars.WaitAT('OK', False, 10000)
                                time.sleep(45)
                                if atResp:
                                    mars.Print('AT+wifi=wifi_get_ip')
                                    mars.SendAT('AT+wifi=wifi_get_ip', 1000, 1)
                                    atResp = mars.WaitAT('OK', False, 10000)
                                    if atResp:
                                        mars.Print("send AT success: AT+wifi=wifi_get_ip")
                                        # mars.SendAT('at+wifi=wifi_open sta {0} {1}'.format(ap_name, ap_pwd), 1000, 1)  ###验证脚本用，后续需要去除
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
                        if scan_fail == 3:
                            mars.Print("wifi_connect_encryption_ap Scan hotspots fail:not found {0}".format(ap_name))
                            mars.Verdict("fail",
                                         "wifi_connect_encryption_ap Scan hotspots fail:not found {0}".format(ap_name))
                            return False
                        else:
                            scan_fail = scan_fail + 1
                            mars.Print("wifi_connect_encryption_ap Scan fail count {0}".format(scan_fail))
                            time.sleep(2)
            else:
                mars.Print('Scan hotspots fail:not found tlwr886n')
                mars.Verdict("fail", "Scan hotspots fail:not found tlwr886n")
                return False
        else:
            mars.Print("send 'at+wifi=sdio_wifi_open' fail")
            mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")

    def wifi_connect_no_encryption_ap(self, ap_name):
        """connect user define AP_NAME AP_PSW"""
        mars.SendAT('at+wifi=sdio_wifi_open', 1000, 1)
        atResp = mars.WaitAT('OK', False, 10000)
        if atResp:
            time.sleep(15)  ###等待bin文件加载完成
            mars.Print("send 'at+wifi=sdio_wifi_open' success")
            mars.SendAT('at+wifi= wifi_open sta {0}'.format(ap_name), 1000, 1)
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
                        time.sleep(45)
                        if atResp:
                            mars.SendAT('AT+wifi=wifi_get_ip', 1000, 1)
                            atResp = mars.WaitAT('OK', False, 10000)
                            if atResp:
                                mars.Print("send AT success: AT+wifi=wifi_get_ip")
                                # mars.SendAT('at+wifi= wifi_open sta {0}'.format(ap_name), 1000, 1)  ###验证脚本用，后续需要去除
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
                mars.Print('connect ap fail')
                mars.Verdict("fail", "connect ap fail")
                return False
        else:
            mars.Print("send 'at+wifi=sdio_wifi_open' fail")
            mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")

    def notebook_ping(self):
        try:
            mars.SendAT('at+log=15,0', 1000, 1)
            time.sleep(3)
            ping_url = 'ping www.baidu.com'
            exit_code = os.system(ping_url)
            time.sleep(5)
            # 网络连通 exit_code == 0，否则返回非0值。
            if exit_code == 0:
                mars.Print("ping baidu pass")
                return True
            else:
                mars.Print("ping baidu fail")
                mars.Verdict("fail", "ping baidu fail")
                return False
        except Exception as e:
            mars.Print("ping baidu fail")
            mars.Verdict("fail", "ping baidu fail")
            return False

    def wifi_scan_before_connect(self, ap_name):
        mars.SendAT('at+wifi=sdio_wifi_open', 1000, 1)
        atResp = mars.WaitAT('OK', False, 10000)
        scan_fail = 0
        if atResp:
            time.sleep(15)  ###等待bin文件加载完成
            mars.Print("send 'at+wifi=sdio_wifi_open' success")
            mars.SendAT('at+wifi=wifi_open sta', 1000, 1)
            atResp = mars.WaitAT('OK', False, 10000)
            if atResp:
                mars.Print("open sta success")
                while True:
                    mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                    result = mars.WaitAT()
                    result_list = result.split("scan ap=")
                    for line in result_list:
                        mars.Print(line)
                    if "ssid={0}".format(ap_name) in result:
                        mars.Print("Scan hotspots pass:found {0}".format(ap_name))
                        break
                    else:
                        if scan_fail == 3:
                            mars.Print("wifi_scan_before_connect Scan hotspots fail:not found {0}".format(ap_name))
                            mars.Verdict("fail",
                                         "wifi_scan_before_connect Scan hotspots fail:not found {0}".format(ap_name))
                            return False
                        else:
                            scan_fail = scan_fail + 1
                            mars.Print("wifi_scan_before_connect Scan fail count {0}".format(scan_fail))
                            time.sleep(2)

            else:
                mars.Print("open sta fail")
                mars.Verdict("fail", "open sta fail")
                return False
        else:
            mars.Print("send 'at+wifi=sdio_wifi_open' fail")
            mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")
            return False

    def wifi_scan_connected(self, ap_name):
        scan_fail = 0
        while True:
            mars.SendAT('at+wifi=wifi_scan', 1000, 1)
            result = mars.WaitAT()
            result_list = result.split("scan ap=")
            for line in result_list:
                mars.Print(line)
            if "ssid={0}".format(ap_name) in result:
                mars.Print("wifi_scan_connected Scan hotspots pass:found {0}".format(ap_name))
                break
            else:
                if fail_scan == 3:
                    mars.Print("wifi_scan_connected Scan hotspots fail:not found {0}".format(ap_name))
                    mars.Verdict("fail", "wifi_scan_connected Scan hotspots fail:not found {0}".format(ap_name))
                    return False
                else:
                    scan_fail = scan_fail + 1
                    mars.Print("wifi_scan_connected Scan fail count {0}".format(scan_fail))
                    time.sleep(2)

    def wifi_scan_before_connect_UserDefineScanTimes(self, ap_name):
        current_test_times = 0
        scan_times = 1
        scan_fail = 0
        mars.SendAT('at+wifi=sdio_wifi_open', 1000, 1)
        atResp = mars.WaitAT('OK', False, 10000)
        if atResp:
            time.sleep(15)  ###等待bin文件加载完成
            mars.Print("send 'at+wifi=sdio_wifi_open' success")
            mars.SendAT('at+wifi=wifi_open sta', 1000, 1)
            atResp = mars.WaitAT('OK', False, 10000)
            if atResp:
                mars.Print("open sta success")
                for i in range(scan_times):
                    current_test_times = i + 1
                    mars.Print('******excute {0} times , total test need {1} times.******'.format(current_test_times,
                                                                                                  scan_times))
                    while True:
                        mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                        result = mars.WaitAT()
                        result_list = result.split("scan ap=")
                        for line in result_list:
                            mars.Print(line)
                            pass
                        if "ssid={0}".format(ap_name) in result:
                            mars.Print("Scan hotspots pass:found {0}".format(ap_name))
                            break
                        else:
                            if scan_fail == 3:
                                mars.Print(
                                    "wifi_scan_before_connect_UserDefineScanTimes Scan hotspots fail:not found {0}".format(
                                        ap_name))
                                mars.Verdict("fail",
                                             "wifi_scan_before_connect_UserDefineScanTimes Scan hotspots fail:not found {0}".format(
                                                 ap_name))
                                return False
                            else:
                                scan_fail = scan_fail + 1
                                mars.Print(
                                    "wifi_scan_before_connect_UserDefineScanTimes Scan fail count {0}".format(ap_name))
                                time.sleep(2)
            else:
                mars.Print("open sta fail")
                mars.Verdict("fail", "open sta fail")
                return False
        else:
            mars.Print("send 'at+wifi=sdio_wifi_open' fail")
            mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")
            return False


class RouterBase(metaclass=ABCMeta):
    @abstractmethod
    def login_ap(self):
        pass

    @abstractmethod
    def set_encryption_ap(self):
        pass

    @abstractmethod
    def set_no_encryption_ap(self):
        pass


class TPLinkBase(RouterBase):
    def __init__(self):
        self.host = ""
        self.login_info = []
        self.headers = {}
        self.router_username = ""
        self.router_password = ""

    def login_ap(self, host, router_username, router_password):
        """获取stok"""
        self.host = host
        self.router_username = router_username
        self.router_password = router_password
        self.headers = {
            'Origin': r'http://{0}'.format(self.host),
            'Accept-Encoding': r'Accept-Encoding: gzip, deflate',
            'Accept-Language': r'en-US,en;q=0.9',
            'User-Agent': r'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)Ubuntu Chromium/64.0.3282.167 Chrome/64.0.3282.167 Safari/537.36',
            'Content-Type': r'application/json; charset=UTF-8',
            'Accept': r'application/json, text/javascript, */*; q=0.01',
            'Referer': r'http://{0}/'.format(self.host),
            'X-Requested-With': r'XMLHttpRequest',
            'Connection': r'keep-alive',
        }
        url = r'http://{0}/'.format(self.host)
        data = {
            "method": "do",
            "login": {
                "password": "408yB04wBTefbwK"
            }
        }
        data_byte = bytes(json.dumps(data), 'utf-8')
        req = request.Request(url, headers=self.headers, data=data_byte)
        mars.Print("req success")                                               #add by luliangliang``
        respones = request.urlopen(req).read().decode('utf-8')
        mars.Print("respones success")                                          #add by luliangliang

        infos = json.loads(respones)
        if isinstance(infos, dict):
            temp_stok = {}
            temp_stok.setdefault("stok", infos["stok"])
            self.login_info.append(temp_stok)
            mars.Print(str(self.login_info))
        else:
            mars.Print("login fail")
            # raise TPLinkBaseException("login {0} fail".format(self.host))

    def request_router(self, data_byte, mars=None):
        """请求设置参数"""
        self.url = "http://{0}/stok={1}/ds".format(self.host, self.login_info[0]["stok"])
        # mars.Print("==============>",self.url)
        req = request.Request(self.url, headers=self.headers, data=data_byte)
        respones = request.urlopen(req).read().decode('utf-8')
        infos = json.loads(respones)
        if isinstance(infos, dict):
            if 0 == infos['error_code']:
                # mars.Print("{0}:success".format(data_byte))
                return infos
            else:
                mars.Print("{0}: fail".format(data_byte))
                # raise TPLinkBaseException("{0}:fail".format(data_byte))

    def check_ap(self, wireless_setting, ssid="", pwd="", enum_list=None):
        settings_json = json.dumps({"wireless": {"name": "wlan_host_2g"}, "method": "get"})
        data_byte = bytes(settings_json, "utf-8")
        check_result = self.request_router(data_byte)
        mars.Print("check...")
        mars.Print(str(check_result))
        aaa = int(check_result.get('wireless').get('wlan_host_2g').get('channel'))
        mars.Print(str(aaa))
        bbb = enum_list[0]
        mars.Print(str(bbb))
        if int(check_result.get('wireless').get('wlan_host_2g').get('channel')) == enum_list[0]:
            return True


class TLWR886N(TPLinkBase):

    def __init__(self):
        super().__init__()

    def set_ap(self, wireless_setting, ssid="", pwd="", encryption="", enum_list=None):
        settings = {
            "method": "set"
        }
        wlan_host = {}
        wlan_host.setdefault("ssid", ssid)
        wlan_host.setdefault("key", pwd)
        wlan_host.setdefault("encryption", encryption)
        wlan_host.setdefault("channel", enum_list[0])
        wlan_host.setdefault("mode", enum_list[1])
        wlan_host.setdefault("bandwidth", enum_list[2])
        wlan_host.setdefault("ssidbrd", enum_list[3])
        if "2.4G" == wireless_setting:
            settings['wireless'] = {
                'wlan_host_2g': wlan_host
            }
        elif "5G" == wireless_setting:
            settings['wireless'] = {
                'wlan_host_5g': wlan_host
            }
        settings_json = json.dumps(settings)
        data_byte = bytes(settings_json, "utf-8")
        self.request_router(data_byte)

    def set_encryption_ap(self, wireless_setting, ssid="", pwd="", enum_list=None):
        self.set_ap(wireless_setting, ssid, pwd, encryption=1, enum_list=enum_list)  # by luliangliang 2022.8.26
        mars.Print("set_encryption_ap")
        for _ in range(3):
            try:
                mars.Print("set_encryption_ap  try")
                self.set_ap(wireless_setting, ssid, pwd, encryption=1, enum_list=enum_list)  # by luliangliang 2022.8.26
                time.sleep(30)
                if self.check_ap(wireless_setting, ssid, pwd, enum_list=enum_list):
                    return True
            except Exception as e:
                pass
        mars.Print("set fail {0}".format(enum_list))

    def set_no_encryption_ap(self, wireless_setting, ssid="", pwd="", enum_list=None):
        self.set_ap(wireless_setting, ssid, pwd, encryption=0, enum_list=enum_list)
        for _ in range(3):
            try:
                time.sleep(30)
                if self.check_ap(wireless_setting, ssid, pwd, enum_list=enum_list):
                    return True
            except Exception as e:
                pass
        mars.Print("set fail {0}".format(enum_list))

    def set_apname_nonepassword(self, ap_name):
        settings = {
            "method": "set",
            "wireless": {
                "wlan_bs":
                    {
                        "ssid": ap_name, "key": "", "encryption": 0}
            }
        }
        settings_json = json.dumps(settings)
        data_byte = bytes(settings_json, "utf-8")
        self.request_router(data_byte)

    def set_apname_password(self, ap_name, ap_pwd):
        settings = {
            "method": "set",
            "wireless": {
                "wlan_bs":
                    {
                        "ssid": ap_name, "key": ap_pwd, "encryption": 0}
            }
        }
        settings_json = json.dumps(settings)
        data_byte = bytes(settings_json, "utf-8")
        self.request_router(data_byte)


def check_rndis_exist():
    cmd = os.popen("ipconfig -all")
    result = cmd.read()
    result = str(result)
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


def run():
    check_rndis_exist()
    # TLWR886N().n3_wifi_on()
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
    n3_wifi_scan(serialN)
    heron_wifi_baseaction().wifi_scan_before_connect(ap_name)
    # 获取可遍历参数
    obj_json = []
    for c in channel:
        for m in mode:
            for b in bandwidth:
                for s in ssidbrd:
                    list = [c, m, b, s]
                    obj_json.append(list)
    # print(obj_json)
    mars.Print("sta_TPLink_channel_encryption test begin")
    # 初始化对应ap
    obj = TLWR886N()
    # 登录
    mars.Print("get stok")
    obj.login_ap(host, router_username, router_password)
    mars.Print("login success")

    # if 0:
    #     # 设置无密码的
    #     for list in obj_json:
    #         # 设置
    #         # print(list)
    #         mars.Print("no key ------------")
    #         mars.Print(str(list))
    #         obj.set_apname_nonepassword(ap_name)
    #         obj.set_no_encryption_ap(wireless_setting, ap_name, pwd="", enum_list=list)
    #         time.sleep(30)
    #         if heron_wifi_baseaction().close_sta():
    #             mars.Print("close sta pass")
    #             n3_wifi_scan(serialN)
    #             if heron_wifi_baseaction().wifi_connect_no_encryption_ap(ap_name):
    #                 mars.Print("open sta pass")
    #                 heron_wifi_baseaction().wifi_scan_connected(ap_name)
    #                 time.sleep(60)          ####验证脚本用，后续需要去除
    #                 if net_card_info().ping_RNDIS_network():
    #                     mars.Print("ping baidu pass")
    #                 else:
    #                     mars.Print("ping baidu fail")
    #                     mars.Verdict("fail", "ping baidu fail")
    #             else:
    #                 mars.Print("open sta fail")
    #                 mars.Verdict("fail", "open sta fail")
    #                 return False
    #         else:
    #             mars.Print("close sta fail")
    #             mars.Verdict("fail", "close sta fail")
    #             return False
    # 设置有密码的
    if 1:
        for list in obj_json:
            mars.Print(str(list))
            obj.set_apname_password(ap_name, ap_pwd)
            obj.set_encryption_ap(wireless_setting, ap_name, ap_pwd, list)
            # obj.set_no_encryption_ap(wireless_setting, ap_name, ap_pwd, list)
            time.sleep(30)
            mars.Print("info set success")
            if heron_wifi_baseaction().close_sta():
                mars.Print("close sta pass")
                if heron_wifi_baseaction().wifi_connect_encryption_ap(ap_name, ap_pwd):
                    mars.Print("open sta pass")
                    n3_wifi_scan(serialN)
                    heron_wifi_baseaction().wifi_scan_connected(ap_name)
                    time.sleep(60)  ####验证脚本用，后续需要去除
                    # if net_card_info().ping_RNDIS_network():
                    #     mars.Print("ping baidu pass")
                    # else:
                    #     mars.Print("ping baidu fail")
                    #     mars.Verdict("fail", "ping baidu fail")
                else:
                    mars.Print("open sta fail")
                    mars.Verdict("fail", "open sta fail")
                    return False
            else:
                mars.Print("close sta fail")
                mars.Verdict("fail", "close sta fail")
                return False


if __name__ == '__main__':
    run()
