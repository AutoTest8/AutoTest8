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

class heron_wifi_baseaction():

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

    def wifi_connect_encryption_ap(self):
        """connect user define AP_NAME AP_PSW"""
        mars.Print("wifi_connect_encryption_ap")

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
                atResp = mars.WaitAT()
                mars.Print(" scan result %s " % atResp)
                if heron_wifi_baseaction().check_wifi_scan(atResp):
                    mars.Print("wifi_scan {0} success".format(ap_name))
                else:
                    mars.Print("wifi_scan {0} fail".format(ap_name))

            mars.SendAT('at+wifi=wifi_open sta {0} {1}'.format(ap_name, ap_pwd), 1000, 1)
            atResp = mars.WaitAT('OK', False, 10000)
            mars.Print(atResp)
            if atResp:
                mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                atResp = mars.WaitAT()
                mars.Print(" scan result %s " % atResp)
                if heron_wifi_baseaction().check_wifi_scan(atResp):
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
                    mars.Print("Scan hotspots fail:not found {0}".format(ap_name))
                    mars.Verdict("fail", "Scan hotspots fail:not found {0}".format(ap_name))
                    return False
            else:
                mars.Print('Scan hotspots fail:not found tlwr886n')
                mars.Verdict("fail", "Scan hotspots fail:not found tlwr886n")
                return False
        else:
            mars.Print("send 'at+wifi=sdio_wifi_open' fail")
            mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")

    def wifi_connect_no_encryption_ap(self):
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
                            atResp = mars.WaitAT('OK', False, 360000)
                            if atResp:
                                mars.Print("send AT success: AT+wifi=wifi_get_ip")
                                mars.SendAT('at+wifi=wifi_open sta {0} {1}'.format(ap_name, ap_pwd), 1000,
                                            1)  ###验证脚本用，后续需要去除
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
                mars.Print('Scan hotspots fail:not found tlwr886n')
                mars.Verdict("fail", "Scan hotspots fail:not found tlwr886n")
                return False
        else:
            mars.Print("send 'at+wifi=sdio_wifi_open' fail")
            mars.Verdict("fail", "send 'at+wifi=sdio_wifi_open' fail")

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
        scan_fail = 0
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


    def wifi_scan_connected(self):

        mars.Print("************** wifi_scan_connected *********************")

        mars.SendAT('at+wifi=wifi_scan', 1000, 1)
        result = mars.WaitAT()
        mars.Print("result %s {0}" % result)
        if heron_wifi_baseaction().check_wifi_scan(result):
            mars.Print("Scan hotspots pass:found {0}".format(ap_name))
        else:
            mars.Print("wifi_scan_before_connect Scan hotspots fail:not found {0}".format(ap_name))
            mars.Verdict("fail", "wifi_scan_before_connect Scan hotspots fail:not found {0}".format(ap_name))
            return False


    def wifi_scan_before_connect_UserDefineScanTimes(self):
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
                    time.sleep(10)
                    current_test_times = i + 1
                    mars.Print('******excute {0} times , total test need {1} times.******'.format(current_test_times,scan_times))
                    mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                    time.sleep(2)
                    result = mars.WaitAT()
                    mars.Print("XH-1 result: {0}".format(len(result)))
                    mars.Print("result %s {0}" % result)
                    if HeronWifiBaseaction().check_wifi_scan(result):
                        mars.Print("wifi_scan {0} success".format(ap_name))
                    else:
                        mars.Print("wifi_scan {0} fail".format(ap_name))
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



def run():
    basic_fun.check_rndis_exist()
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
    heron_wifi_baseaction().close_sta()
    n3_wifi_scan(serialN)
    heron_wifi_baseaction().wifi_scan_before_connect()
    if heron_wifi_baseaction().wifi_connect_encryption_ap():
        mars.Print("open sta pass")
        n3_wifi_scan(serialN)
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

