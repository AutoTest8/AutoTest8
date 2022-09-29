#!/usr/bin/env python
# coding:utf-8
"""
Name  : heron_wifi.py
Author: xh
Time  : 2021/12/15 15:23
Desc  :
     heron wifi test related custom library
"""
import json
import re
import subprocess
import time
import traceback
from urllib import request
from abc import ABCMeta, abstractmethod
import mars

###########用户自定义设置参数###########
ap_name = "tlwr886n"       ###路由器名称SSID
ap_pwd = "123456789"       ###路由器密码

class PcNetworkUtil(object):
    def ExecuteOneShellCommand(cmd, timeout=None, callback_on_timeout=None, *args):
        if timeout is None:
            p = subprocess.Popen(
                str(cmd),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            return (stdout, stderr, p.returncode)
        else:
            return ('stdout fail')

    @classmethod
    def get_network_info(cls):
        '''
            获取ipconfig数据
            Returns:
                [{'name': '', 'DNS': '', 'ip': '', 'desc': ''}]
        '''
        net_ipconfig_list = []
        network= subprocess.Popen('ipconfig /all', stdout=subprocess.PIPE, shell=True)
        network_infos = network.stdout.readlines()
        # network_infos = (temp_list).split(b'\r\n')
        tmp_network_name = None
        for line_byte in network_infos:
            line = line_byte.decode('gbk').strip()
            if line.startswith('以太网适配器'):
                tmp_network_name = line[7:-1]
                net_ipconfig_list.append({'name': tmp_network_name, 'DNS': '', 'ip': '', 'desc': ''})
            else:
                if tmp_network_name is not None:
                    if line.startswith('描述'):
                        net_ipconfig_list[-1]['desc'] = line.split('. . : ')[1]
                    elif line.startswith('连接特定的 DNS 后缀'):
                        if len(line.split('. . : ')) > 1:
                            net_ipconfig_list[-1]['DNS'] = line.split('. . : ')[1]
                        else:
                            net_ipconfig_list[-1]['DNS'] = ''
                    elif line.startswith('IPv4 地址'):
                        net_ipconfig_list[-1]['DNS'] = line.split('. . : ')[1].split('(')[0]
                        tmp_network_name = None
        print("====>", net_ipconfig_list)
        return net_ipconfig_list

class often_called_function():

    def query_version(self):
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

    def check_rndis_exist(self):
        cmd = os.popen("ipconfig -all")
        result = cmd.read()
        result = str(result)
        mars.Print("rndis result = %s" % result)  # add by luliangliang 2022.8.3    打印rndis
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
                mars.Print("rndis result = %s" % result)  # add by luliangliang
                if result.find("NDIS") != -1:
                    mars.Print("rndis -----exist")
                    break
                else:
                    if i == 4:
                        mars.Verdict("fail", "rndis -----not exist--------")
                    continue

class heron_wifi_baseaction():

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
                    if atResp.find(-3) != -1:
                        mars.Print("send at+reset")
                        mars.SendAT('at+reset', 1000, 1)
                        time.sleep(60)
                        mars.Print("sdio_err, at+reset")
                        mars.Verdict("fail", "sdio_err, at+reset")
                    mars.Print("not scan {0}".format(ap_name))
                    mars.Print("Scan hotspots fail:not found {0}".format(ap_name))

                    return False
                else:
                    find_scan_num = find_scan_num + 1

    def runAdmin(self,cmd, timeout=1800000):
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
        time.sleep(5)
        mars.Print("sdio_wifi_open, send AT")
        atResp = mars.SendAT('at+wifi=sdio_wifi_open', 20000)
        if atResp:
            mars.Print("sdio_wifi_open, success")
            mars.Print("close sta ,send AT")
            mars.SendAT('at+wifi=wifi_close', 1)
            atRespCops = mars.WaitAT('OK', False, 20000)
            mars.Print(atRespCops)
            if atRespCops:
                mars.Print(" 'at+wifi=wifi_close' is ok ")
                return True
            else:
                mars.Print(" 'at+wifi=wifi_close' is fail ")
                mars.Verdict("fail", "wifi close fail")
                return False
        else:
            mars.Print("sdio_wifi_open, fail")
            mars.Verdict("fail", "sdio_wifi_open")
            return False

    def ip_check(self):
        mars.SendAT('at + wifi =wifi_get_peer_sta_info', 1)
        atRespCops = mars.WaitAT('OK', False, 20000)
        mars.Print(atRespCops)
        if atRespCops:
            mars.Print(" 'at + wifi =wifi_get_peer_sta_info' is ok ")
            return True
        else:
            mars.Print(" 'at + wifi =wifi_get_peer_sta_info' is fail ")
            mars.Verdict("fail", "get_peer_sta_info fail")
            return False


    def wifi_connect_encryption_ap(self):

        """
        connect encryption ap
        :param ap_name: name of router
        :param ap_pwd: password of router
        :return: True/False
        """
        heron_wifi_baseaction().close_sta()
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
                result = mars.WaitAT()
                result_list = result.split("scan ap=")
                for line in result_list:
                    mars.Print(line)
                if heron_wifi_baseaction().check_wifi_scan(result):
                    mars.Print("wifi_scan {0} success".format(ap_name))
                else:
                    mars.Print("wifi_scan {0} fail".format(ap_name))
                    mars.Verdict("fail", "Scan hotspots fail:not found {0}".format(ap_name))
                    return False

            mars.SendAT('at+wifi=wifi_open sta {0} {1}'.format(ap_name, ap_pwd), 1000, 1)
            atResp = mars.WaitAT('OK', False, 10000)
            mars.Print(atResp)
            if atResp:
                mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                mars.Print("connect AP success")
                result = mars.WaitAT()
                result_list = result.split("scan ap=")
                for line in result_list:
                    mars.Print(line)
                if heron_wifi_baseaction().check_wifi_scan(result):
                    # atResp = mars.WaitAT('ssid={0}'.format(ap_name), False, 15000)
                    # if atResp:
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
            
    def wifi_connect_no_encryption_ap(self):
        self.close_sta()
        mars.SendAT('at+wifi=sdio_wifi_open', 1)
        atRespCops = mars.WaitAT('OK', False, 10000)
        if atRespCops:
            mars.Print(" 'at+wifi=sdio_wifi_open' have successful")
            mars.SendAT('at+wifi=wifi_open sta', 1000, 1)
            atRespCops = mars.WaitAT('OK', False, 10000)
            if atRespCops:
                mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                result = mars.WaitAT()
                mars.Print(" scan result %s" %result)
                if heron_wifi_baseaction().check_wifi_scan(result):
                    mars.Print("Scan hotspots pass:found {0}".format(ap_name))
                    mars.SendAT('at+wifi=wifi_open sta {0}'.format(ap_name), 1000, 1)
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
                    mars.Print("wifi_connect_no_encryption_apt Scan hotspots fail:not found {0}".format(ap_name))
                    mars.Verdict("fail", "wifi_connect_no_encryption_ap Scan hotspots fail:not found {0}".format(ap_name))
                    return False
            else:
                mars.Print("open sta fail")
                mars.Verdict("fail", "open sta fail")
                return False
        else:
            mars.Print("send 'at+wifi=sdio_wifi_open' fail")
            mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")
            return False

    # def wifi_connect_no_encryption_ap(self):
    #     """connect user define AP_NAME AP_PSW"""
    #     #mars.SendAT('at+wifi=sdio_wifi_open', 1000, 1)
    #     #atResp = mars.WaitAT('OK', False, 10000)
    #     find_ap1 =False
    #     find_scan_num = 0
    #     while (not find_ap1):                           # add by luliangliang 8.28 为了避免出现扫描网络中没有tlwr886n,所以选择重扫
    #         time.sleep(5)
    #         mars.Print("send 'at+wifi=sdio_scan' % scan_num" % find_scan_num)
    #         mars.SendAT('at+wifi=wifi_scan', 1000, 1)
    #         # atResp = mars.WaitAT('OK', False, 10000)
    #         # mars.Print(atResp)
    #         atResp = mars.WaitAT()
    #         mars.Print(atResp)
    #         if atResp.find(ap_name) != -1:
    #             mars.Print("scan tlwr886n successful")
    #             find_scan_num = 0
    #             atResp = True
    #             break
    #         elif find_scan_num == 3:
    #             mars.Print("not scan tlwr886n")
    #             find_scan_num = 0
    #             mars.Verdict("fail", "Scan hotspots fail:not found tlwr886n")
    #             return False
    #         else:
    #             find_scan_num = find_scan_num + 1
    #
    #     if atResp:
    #         time.sleep(15)  ###等待bin文件加载完成
    #         mars.Print("send 'at+wifi=sdio_wifi_open' success")
    #         mars.SendAT('at+wifi= wifi_open sta {0}'.format(ap_name), 1000, 1)
    #         atResp = mars.WaitAT('OK', False, 10000)
    #         mars.Print(atResp)
    #         if atResp:
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
    #                             #time.sleep(45)
    #                             mars.SendAT('AT+wifi=wifi_get_ip', 1000, 1)
    #                             atResp = mars.WaitAT('OK', False, 360000)
    #                             if atResp:
    #                                 mars.Print("send AT success: AT+wifi=wifi_get_ip")
    #                                 mars.SendAT('at+wifi=wifi_open sta {0} {1}'.format(ap_name, ap_pwd), 1000, 1)  ###验证脚本用，后续需要去除
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
    #         else:
    #             mars.Print('Connect hotspots fail:connect tlwr886n fail')
    #             mars.Verdict("fail", "Connect hotspots fail:connect tlwr886n fail")
    #             return False
    #     else:
    #         mars.Print("send 'at+wifi=sdio_wifi_open' fail")
    #         mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")

       
    def set_apname_nonepassword(self,ap_name):
        settings = {
            "method": "set",
            "wireless":{
                "wlan_bs":
                    {
                "ssid": ap_name, "key": "", "encryption": 0}
            }
        }
        settings_json = json.dumps(settings)
        data_byte = bytes(settings_json, "utf-8")
        self.request_router(data_byte)

    def set_apname_password(self,ap_name,ap_pwd):
        settings = {
            "method": "set",
            "wireless":{
                "wlan_bs":
                    {
                "ssid": ap_name, "key": ap_pwd, "encryption": 0}
            }
        }
        settings_json = json.dumps(settings)
        data_byte = bytes(settings_json, "utf-8")
        self.request_router(data_byte)            


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
                time.sleep(5)
                mars.Print("open sta success")
                mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                result = mars.WaitAT()
                result_list = result.split("scan ap=")
                for line in result_list:
                    mars.Print(line)
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


    def wifi_scan_connected(self):
        scan_fail = 0
        while True:
            mars.SendAT('at+wifi=wifi_scan', 1000, 1)
            result = mars.WaitAT()
            result_list =result.split("scan ap=")
            for line in result_list:
                mars.Print(line)
            if "ssid={0}".format(ap_name) in result:
                mars.Print("Scan hotspots pass:found {0}".format(ap_name))
                break
            else:
                if scan_fail >= 3:
                    mars.Print("wifi_scan_connected Scan hotspots fail:not found {0}".format(ap_name))
                    mars.Verdict("fail", "wifi_scan_connected Scan hotspots fail:not found {0}".format(ap_name))
                    return False
                else:
                    scan_fail = scan_fail + 1
                    mars.Print("wifi_scan_connected Scan fail count {0}".format(scan_fail))
                    time.sleep(2)

    def wifi_scan_before_connect_UserDefineScanTimes(self):
        scan_times = 1
        mars.SendAT('at+wifi=sdio_wifi_open', 1000, 1)
        atResp = mars.WaitAT('OK', False, 10000)
        if atResp:
            time.sleep(15)   ###等待bin文件加载完成
            mars.Print("send 'at+wifi=sdio_wifi_open' success")
            mars.SendAT('at+wifi=wifi_open sta', 1000, 1)
            atResp = mars.WaitAT('OK', False, 10000)
            if atResp:
                mars.Print("open sta success")
                for i in range(scan_times):
                    time.sleep(10)
                    # mars.Print('******excute {0} times , total test need {1} times.******'.format(current_test_times, scan_times))
                    while True:
                        mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                        result = mars.WaitAT()
                        result_list =result.split("scan ap=")
                        for line in result_list:
                            mars.Print(line)
                            pass
                        if heron_wifi_baseaction().check_wifi_scan(result):
                            mars.Print("Scan hotspots pass:found {0}".format(ap_name))
                            return True
                        else:
                            mars.Print("Scan hotspots fail:not found {0}".format(ap_name))
                            mars.Verdict("fail", "Scan hotspots fail:not found {0}".format(ap_name))
                            return False
            else:
                mars.Print("open sta fail")
                mars.Verdict("fail", "open sta fail")
                return False
        else:
            mars.Print("send 'at+wifi=sdio_wifi_open' fail")
            mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")
            return False

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


    def NetWork_enabled(self):
        for tmp_network in PcNetworkUtil.get_network_info():
            if 'Intel(R) Ethernet Connection' not in tmp_network['desc']:
                operate = 'enabled'
                cmd = 'netsh interface set interface name="{0}" admin={1}'.format(
                    tmp_network['name'], operate)
                subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
                # CraneFunHeronWifiEncryptionEnumAP().runAdmin(cmd)
            else:
                mars.Print("enable Ethernet Connection fail")


