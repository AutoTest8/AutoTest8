#!/usr/bin/env python
# coding:utf-8
"""
Name  : sta_connected_scan.py
Author: zhf
Time  : 2021/11/17 13:58
Desc  :
        1.scan ap
        2.open sta
        3.scan at+wifi=wifi_scan,check at response
        4.connect user define ap at+wifi=wifi_open sta AP_NAME AP_PSW
        5.scan once more(6 times)
"""
import os
import mars
import time
import traceback
import subprocess
import json
from wifilib import heron_wifi
from wifilib import net_card
from wifilib import basic_fun

# user define AP_NAME AP_PSW
#AP_NAME = "bj111111111122222222223333333333"
#AP_PSW = "asr111111111122222222223333333333444444444455555555556666666666 "
ap_name = "tlwr886n"
ap_pwd = "123456789"
scan_times = 1   #自定义扫描次数（连接ap后扫描）

# def n3_wifi_on(serialN):
#     """
#     open n3 wifi
#     :param serialN: devices serial number
#     """
#
#
# def n3_wifi_scan(serialN):
#     """
#     search for visible wifi
#     :param serialN: devices serial number
#     :return: True/False
#     """


# class PcNetworkUtil(object):
#     def ExecuteOneShellCommand(cmd, timeout=None, callback_on_timeout=None, *args):
#         if timeout is None:
#             p = subprocess.Popen(
#                 str(cmd),
#                 shell=True,
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE)
#             stdout, stderr = p.communicate()
#             return (stdout, stderr, p.returncode)
#         else:
#             return ('stdout fail')
#
#     @classmethod
#     def get_network_info(cls):                 # get the info of "name, dns, ip, desc " from dos
#         '''
#             获取ipconfig数据
#             Returns:
#                 [{'name': '', 'DNS': '', 'ip': '', 'desc': ''}]
#         '''
#         net_ipconfig_list = []
#         network= subprocess.Popen('ipconfig /all', stdout=subprocess.PIPE, shell=True)
#         network_infos = network.stdout.readlines()
#         # network_infos = (temp_list).split(b'\r\n')
#         tmp_network_name = None
#         for line_byte in network_infos:
#             line = line_byte.decode('gbk').strip()
#             if line.startswith('以太网适配器'):
#                 tmp_network_name = line[7:-1]
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
#                         net_ipconfig_list[-1]['DNS'] = line.split('. . : ')[1].split('(')[0]
#                         tmp_network_name = None
#         print("====>", net_ipconfig_list)
#         return net_ipconfig_list

# class heron_wifi_baseaction():
#
#     def runAdmin(self, cmd, timeout=1800000):
#         f = None
#         try:
#             bat = os.getcwd() + r"\cmd_tool\cmd.bat"
#             f = open(bat, 'w')
#             f.write(cmd)
#         except Exception as e:
#             traceback.print_exc()
#             raise e
#         finally:
#             if f:
#                 f.close()
#         try:
#             shell = os.getcwd() + r"\cmd_tool\shell.vbs"
#             sp = subprocess.Popen(
#                 shell,
#                 shell=True,
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE
#             )
#             print("[PID] %s: %s" % (sp.pid, cmd))
#             sp.wait(timeout=timeout)
#
#             stderr = str(sp.stderr.read().decode("gbk")).strip()
#             stdout = str(sp.stdout.read().decode("gbk")).strip()
#             if "" != stderr:
#                 raise Exception(stderr)
#             if stdout.find("失败") > -1:
#                 raise Exception(stdout)
#         except Exception as e:
#             raise e
#
#     def close_sta(self):
#
#     def ip_check(self):
#
#     def check_wifi_scan(self, atResp):
#
#     def wifi_connect_encryption_ap(self):
#         """connect user define AP_NAME AP_PSW"""
#         mars.Print("wifi_connect_encryption_ap")
#
#     def wifi_connect_no_encryption_ap(self):
#         """connect user define AP_NAME AP_PSW"""
#
#     def set_apname_nonepassword(self, ap_name):
#
#     def set_apname_password(self, ap_name, ap_pwd):
#
#     def notebook_ping(self):
#
#     def wifi_scan_before_connect(self):
#         mars.Print("***********wifi_scan_before_connect*********")
class heron_wifi_baseaction():
    def wifi_scan_connected(self):

        mars.Print("************** wifi_scan_connected *********************")

        mars.SendAT('at+wifi=wifi_scan', 1000, 1)
        result = mars.WaitAT()
        result_list = result.split("scan ap=")
        for line in result_list:
            mars.Print(line)
        if heron_wifi.heron_wifi_baseaction().check_wifi_scan(result):
            mars.Print("Scan hotspots pass:found {0}".format(ap_name))
        else:
            mars.Print("wifi_scan_before_connect Scan hotspots fail:not found {0}".format(ap_name))
            mars.Verdict("fail", "wifi_scan_before_connect Scan hotspots fail:not found {0}".format(ap_name))
            return False
    #
    # def wifi_scan_before_connect_UserDefineScanTimes(self):
    #     current_test_times = 0
    #
    # def NetWork_enabled(self):
    #


def run():

    heron_wifi.heron_wifi_baseaction().close_sta()
    basic_fun.check_rndis_exist()

    serialN = basic_fun.get_N3_serial()
    mars.Print(serialN)

    heron_wifi.heron_wifi_baseaction().wifi_scan_before_connect()
    if heron_wifi.heron_wifi_baseaction.wifi_connect_encryption_ap(()):
        mars.Print("open sta pass")
        basic_fun.n3_wifi_scan(serialN)
        heron_wifi_baseaction().wifi_scan_connected()
        current_test_times = 0
        mars.Print("scan_times = %d" %scan_times)
        for i in range(scan_times):
            current_test_times= i + 1
            time.sleep(10)
            mars.Print('******excute {0} times , total test need {1} times.******'.format(current_test_times, scan_times))
            mars.Print('problem checkpoint(please ignore this print)')
            heron_wifi_baseaction().wifi_scan_connected()
    else:
        mars.Print("open sta fail")


if __name__ == '__main__':
    run()

