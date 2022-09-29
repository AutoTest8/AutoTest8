import os
import mars
import time
import traceback
import subprocess
import json
from urllib import request
from abc import ABCMeta, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver as Chrome
from selenium.webdriver.common.action_chains import ActionChains
import random
from wifilib import heron_wifi
from wifilib import net_card
from wifilib import basic_fun


# from selenium import webdriver
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
channel = [12]  # 1--13
mode = [2, 4, 1]  # bgn  bg n g b
bandwidth = ["1"]  # 20
encryption = [0, 1]  # 0为不加密  1为加密


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
            time.sleep(2)
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
            time.sleep(5)  ###等待bin文件加载完成
            mars.Print("send 'at+wifi=sdio_wifi_open' success")
            mars.SendAT('at+wifi=wifi_open sta', 1000, 1)
            atResp = mars.WaitAT('OK', False, 10000)
            if atResp:
                # time.sleep(10)
                time.sleep(3)
                mars.Print("open sta success")
                mars.SendAT('at+wifi=wifi_scan', 1000, 1)
                result = mars.WaitAT()
                mars.Print("result %s " % result)
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


    def wifi_connect_add_encryption(self):
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
                    mars.SendAT('at+wifi=wifi_open sta {0} {1}'.format(ap_name, ap_pwd), 1000, 1)
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


    def wifi_connect_no_encryption(self):
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
        try:
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
        except:
            mars.Print("n3 scan innoc")
            return True

        if scan_num > 4:
            mars.Print("N3 cannot find this ap in 3 times")
            # return False




class router_process(object):
    def __init__(self, router_password, username, password,wlan_channel,wlan_mode, wlan_width, wlan_encryption):
        self.username = username
        self.password = password
        self.router_password = router_password
        self.wlan_channel = wlan_channel
        self.wlan_mode = wlan_mode
        self.wlan_width = wlan_width
        self.wlan_encryption = wlan_encryption

        self.driver = Chrome(executable_path='C:\Program Files\Google\Chrome\Application\chromedriver.exe')
        self.my_action = ActionChains(self.driver)

    def process_all(self):
        self.log_in()
        time.sleep(0.5)
        if self.wlan_encryption:
            mars.Print(" add_encryption mode ")
            time.sleep(2)
            self.wlan_set_encryption()
            self.mode_slete()
        else:
            mars.Print(" no encryption mode ")
            time.sleep(2)
            self.wlan_no_encryption()
            self.mode_slete()

        mars.Print("setting success")

    def log_in(self):
        self.driver.maximize_window()
        url = "http://192.168.1.1/"
        self.driver.get(url)
        # self.driver.find_element(By.ID, "inputPwd").click()
        time.sleep(2)
        self.driver.find_element(By.ID, "lgPwd").send_keys("AAbbcc123")
        time.sleep(1)
        self.driver.find_element(By.ID, "loginSub").click()


    def wlan_set_encryption(self):
        self.driver.find_element(By.ID, "routerSetMbtn").click()  # 路由设置
        time.sleep(1)
        self.driver.find_element(By.ID, "wireless2G_rsMenu").click()  # 无线设置
        time.sleep(2)
        mars.Print(" log in setting")
        self.driver.find_element(By.ID, "wlanPwd").clear()
        time.sleep(1)
        self.driver.find_element(By.ID, "wlanPwd").click()
        self.driver.find_element(By.ID, "wlanPwd").send_keys(self.password)  # 登录密码
        time.sleep(2)
        mars.Print("password has set done")
        self.driver.find_element(By.ID, "saveBasic").click()  # 点击保存

    def wlan_no_encryption(self):
        self.driver.find_element(By.ID, "routerSetMbtn").click()  # 路由设置
        time.sleep(0.5)
        self.driver.find_element(By.ID, "wireless2G_rsMenu").click()  # 无线设置

        time.sleep(1)
        mars.Print(" log in setting")
        self.driver.find_element(By.ID, "wlanPwd").clear()
        time.sleep(1)
        self.driver.find_element(By.ID, "saveBasic").click()  # 点击保存

    def box_click(self, type, id_str, idx1):

        str1 = "// *[ @ id = '{0}'] / li[{1}]".format(id_str, idx1)
        mars.Print(str1)
        self.driver.find_element(By.ID, type).click()
        # time.sleep(5)
        time.sleep(2)
        mars.Print("click end ")
        my_error_element = self.driver.find_element(By.XPATH, str1)
        # time.sleep(6)
        time.sleep(2)
        self.my_action.move_to_element(my_error_element).perform()  # 将鼠标移动到点击的位置
        time.sleep(2)
        mars.Print("move end")
        self.driver.find_element(By.XPATH, str1).click()

    def mode_slete(self):
        time.sleep(6)
        self.box_click("channel", "selOptsUlchannel", self.wlan_channel)
        time.sleep(3)
        self.box_click("wlanMode", "selOptsUlwlanMode", self.wlan_mode)
        time.sleep(5)
        try:
            target = self.driver.find_element(By.ID, "save")
            self.driver.execute_script("arguments[0].scrollIntoView();", target)  # 拖动到可见的元素去
            mars.Print("move save")
            time.sleep(10)
            self.driver.find_element(By.ID, "save").click()  # 点击保存
            time.sleep(10)
            mars.Print("save success")
        except:
            mars.Print("errior")

def serialN_get():
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


def run():
    basic_fun.check_rndis_exist()
    serialN = serialN_get()
    n3_wifi_scan(serialN)
    heron_wifi_baseaction().wifi_scan_before_connect()
    obj_json = []
    for c in channel:
        for m in mode:
            for b in bandwidth:
                for e in encryption:
                    list = [c, m, b, e]
                    obj_json.append(list)
    mars.Print("sta_TPLink_channel_encryption test begin")
    for list in obj_json:
        mars.Print("list:{}".format(list))
        time.sleep(3)
        timess = 0
        while timess <= 3:
            r = router_process(router_password, ap_name, ap_pwd, list[0], list[1], list[2], list[3])
            try:
                r.process_all()
                r.driver.quit()
                time.sleep(3)
                break
            except:
                mars.Print("*********")
                r.driver.quit()
                time.sleep(3)
                timess = timess + 1
                mars.Print("Failed to access mode three times")
        time.sleep(60)

        mars.Print("*****************************************************")
        if heron_wifi_baseaction().close_sta():
            mars.Print(" close wifi successful ")
            if list[3] == 0:
                if heron_wifi_baseaction().wifi_connect_no_encryption():
                    mars.Print("*** connect ap success")
                    try:
                        n3_wifi_scan(serialN)
                        # heron_wifi_baseaction().wifi_scan_connected(ap_name)
                        time.sleep(20)
                    except:
                        time.sleep(20)  ####验证脚本用，后续需要去除
                    time.sleep(2)
                    cs_ps_event_random()
                    time.sleep(20)
                    query_version()
                else:
                    mars.Print("**** connect ap fail")
            else:
                if heron_wifi_baseaction().wifi_connect_add_encryption():
                    mars.Print("*** connect ap success")
                    try:
                        n3_wifi_scan(serialN)
                        # heron_wifi_baseaction().wifi_scan_connected(ap_name)
                        time.sleep(20)
                    except:
                        time.sleep(20)  ####验证脚本用，后续需要去除
                    time.sleep(2)
                    cs_ps_event_random()
                    time.sleep(20)
                    query_version()
                else:
                    mars.Print("**** connect ap fail")
        else:
            mars.Print("** close fail ")
    mars.Print("case have ended")


if __name__ == '__main__':
    run()