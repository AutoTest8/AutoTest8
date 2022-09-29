import sys
from ctypes import *
import os
import threading
import time
from datetime import datetime
import mars
import subprocess
import re
import random
import uiautomator2 as u2

#
class heron_baseaction_fun():
    def __init__(self,AP_NAME, KEY):
        self.AP_NAME = AP_NAME
        self.KEY = KEY

    def close_ap(self):
        mars.Print("close ap ,send AT")
        mars.SendAT('at+wifi=wifi_close', 1)
        atRespCops = mars.WaitAT('OK', False, 20000)
        mars.Print(atRespCops)
        if atRespCops:
            time.sleep(10)
            return 1
        else:
            return 0

    def recovery_ap(self):
        mars.Print("recovery ,send AT")
        mars.SendAT('AT+RSTSET', 1)
        atRespCops = mars.WaitAT('OK', False, 200000)
        mars.Print(atRespCops)
        if atRespCops:
            time.sleep(30)
            return 1
        else:
            return 0

    def open_ap(self):
        mars.Print('at+wifi=wifi_open ap {0} {1} 11'.format(self.AP_NAME, self.KEY))
        mars.SendAT('at+wifi=wifi_open ap {0} {1} 11'.format(self.AP_NAME, self.KEY), 1)
        atRespCops = mars.WaitAT('wifi_softap_open_done', False, 20000)
        if atRespCops:
            mars.Print(atRespCops)
            time.sleep(10)
        else:
            time.sleep(10)
            mars.Print("open ap ,resend AT")
            mars.SendAT('at+wifi=wifi_open ap {0} {1} 11'.format(self.AP_NAME, self.KEY), 1)
            atRespCops1 = mars.WaitAT('wifi_softap_open_done', False, 20000)
            if atRespCops1:
                mars.Print(atRespCops1)
                time.sleep(10)
            else:
                mars.Print("send open ap AT fail")
                return 0
        return 1

    def ip_check(self):
        mars.SendAT('at + wifi =wifi_get_peer_sta_info', 1)
        atRespCops = mars.WaitAT('OK', False, 20000)
        mars.Print(atRespCops)
        if atRespCops:
            return 1
        else:
            return 0

    def reset_ap(self):
        mars.Print("reset ap ,send AT")
        mars.SendAT('at+reset', 1)
        atRespCops = mars.WaitAT('OK', False, 20000)
        mars.Print(atRespCops)
        if atRespCops:
            time.sleep(60)
            return 1
        else:
            return 0

    def check_sta_information(self):
        """
        check sta information
        :return: True/False
        """
        mars.Print("query sta information")
        mars.Print("send AT command: at+wifi=wifi_get_peer_sta_info")
        mars.SendAT('at+wifi=wifi_get_peer_sta_info', 1000, 1)
        atResp = mars.WaitAT('OK', False, 10000)
        if atResp:
            mars.Print("send AT command:at+wifi=wifi_get_peer_sta_info success")
        else:
            mars.Print("send AT command:at+wifi=wifi_get_peer_sta_info failed")
            mars.Verdict("fail", "send AT command:at+wifi=wifi_get_peer_sta_info failed")

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



class N3_operator():
    def __init__(self, AP_NAME, KEY):
        self.AP_NAME = AP_NAME
        self.KEY = KEY
        self.heron_baseaction = heron_baseaction_fun(AP_NAME, KEY)

    def adb_devcies(self):
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

    def quit_send_key(self):
        d = u2.connect_usb(serialN)
        time_send_key = 0
        while time_send_key < 3:
            d(text='取消').click()
            time.sleep(5)
            d(text=self.AP_NAME).click()
            time.sleep(5)
            d(resourceId="com.android.settings:id/password").click()
            try:
                d.send_keys("asr123456", clear=True)
                return True
            except:
                time_send_key = time_send_key + 1
                continue
        return False

    def N3_screen(self, serialN):
        tasktime = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')  # output the current time
        # open serialN to operate phone, and save picture in "/system/bin/screencap"
        subprocess.Popen(
            'adb -s {0} shell /system/bin/screencap -p /sdcard/{1}_{2}.png'.format(serialN, self.AP_NAME,
                                                                                   tasktime),
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, shell=True)

    def N3_wifi_off(self, serialN):
        obj = subprocess.Popen('adb -s %s shell' % serialN, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, shell=True)
        obj.communicate(input='svc wifi disable'.encode())

    def N3_wifi_on(self, serialN):
        # 建立一个子进程以及子进程与主进程之间的管道，执行“adb -s serialN shell”命令
        obj = subprocess.Popen('adb -s %s shell' % serialN, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, shell=True)
        # 等待“svc wifi enable”
        obj.communicate(input='svc wifi enable'.encode())

    def wifi_scan(self, serialN):
        for scan_num in range(1, 4):
            obj = subprocess.Popen(['adb', '-s', '{0}'.format(serialN), 'shell'], shell=True, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            obj.stdin.write('su\n'.encode('utf-8'))
            time.sleep(1)
            obj.stdin.write('wpa_cli -i wlan0 scan\n'.encode('utf-8'))
            time.sleep(15)
            obj.stdin.write('wpa_cli -i wlan0 scan_results\n'.encode('utf-8'))
            time.sleep(15)
            obj.stdin.write('exit\n'.encode('utf-8'))  # 重点，一定要执行exit
            info, err = obj.communicate()
            if err.decode('gbk'):
                mars.Print("the {0} N3 wifi cannot work well!!".format(scan_num))
                mars.Print(err.decode('gbk'))
            else:
                if self.AP_NAME in info.decode('gbk'):
                    mars.Print("ap find in list")
                    return True
                else:
                    mars.Print("the {0} ap not find in list".format(scan_num))
                    mars.Print(info.decode('gbk'))
            if scan_num > 4:
                mars.Print("N3 cannot find this ap in 3 times")
                return False

    def N3_re_run(self):
        serialN = ''
        sn = os.popen('adb devices').readlines()
        num = len(sn)
        mars.Print("N3_wifi_run")
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
            mars.Print("daemon not running")
        self.N3_wifi_off(serialN)
        time.sleep(5)
        self.N3_wifi_on(serialN)
        time.sleep(5)


    def N3_run(self):
        serialN = ''
        sn = os.popen('adb devices').readlines()
        mars.Print("os = %s" % sn)
        num = len(sn)
        if num < 3:
            mars.Print("No Devices,please connect the device")
            # mars.Verdict("fail", "NO N3 connect to PC")
            return
        else:
            if '* daemon not running' in sn[1]:
                for i in range(3, (num - 1)):
                    serialN = sn[i].split("\t")[0]
            else:
                for i in range(1, (num - 1)):
                    serialN = sn[i].split("\t")[0]
        self.N3_wifi_on(serialN)
        time.sleep(10)
        if self.wifi_scan(serialN):
            mars.Print("N3 cli_supplicant command can find ap pass,will connect this ap...")
            if self.N3_con_ap(serialN) == 1:
                time.sleep(10)
                if self.N3_ping(serialN):
                    return 1
                else:
                    return 0
        else:
            mars.Verdict("fail", "N3 cli_supplicant command can not find ap , fail")

    def N3_send_keys(self, serialN):
        d = u2.connect_usb(serialN)
        try:
            # d(resourceId="com.android.settings: id / password").click()
            d.send_keys("asr123456", clear=True)
            mars.Print("first send key successful")
        except:
            if self.quit_send_key():
                mars.Print("send key successful")
            else:
                mars.Verdict("fail", "send key, fail")
        if d(text="连接").exists:  # 判断“连接”是否存在， 正常界面也是通过一些标识符进行区分的，通过查找“text”标识符 = “连接”所在位置
            d(text="连接").click()  # 点击
            time.sleep(15)
            if d(text=self.AP_NAME).exists:  # 判断是否“AP_NAME”存在
                d(resourceId="android:id/title", text=self.AP_NAME).click()  # 找到AP_NAME对应的位置点击
                time.sleep(5)
                if d(text="已连接").exists:
                    mars.Print('n3 connect pass')
                else:
                    mars.Verdict("fail", "N3 connect ap, fail")
            else:
                mars.Verdict("fail", "N3 cannot find ap, fail")
                return False
        else:
            d(text="CONNECT").click()
            time.sleep(15)
            if d(text=self.AP_NAME).exists:
                d(resourceId="android:id/title", text=self.AP_NAME).click()
                time.sleep(5)
                if d(text="Connected").exists:
                    mars.Print('n3 connect pass')
                else:
                    mars.Verdict("fail", "N3 connect ap, fail")
            else:
                mars.Verdict("fail", "N3 cannot find ap, fail")
                return False

    def reconnect_wifi(self):
        d(text == '开启').click()  # 关闭wifi
        time.sleep(20)
        d(text == '开启').click()  # 开启wifi
        time.sleep(30)
        if d(text == self.AP_NAME).exists():
            mars.Print("{0} is exists".format(self.AP_NAME))
            if d(text == '已连接').exists():
                mars.Print("已连接")
                return True
            else:
                return False
        else:
            return False

    def N3_con_ap(self, serialN):
        d = u2.connect_usb(serialN)
        mars.Print("home")
        d.press("home")  # 按下home键
        # 打开设置
        d.app_start("com.android.settings")
        time.sleep(1)
        # 打开N3网络
        d(scrollable=True).scroll.toBeginning()  # 滚动到页面顶部
        net_name = ["网络和互联网", "Network & Internet", "Network & internet"]
        net_result = ''
        for net in net_name:  # 寻找Network & Internet并点击
            if d(text=net).exists:
                d(text=net).click()
                net_result = 1
        time.sleep(1)
        # 打开N3网络-wlan
        if net_result:
            wlan_name = ["WLAN", "Wi‑Fi"]
            wlan_result = ''
            for wlan in wlan_name:  # 寻找wlan_name并点击
                if d(text=wlan).exists:
                    d(text=wlan).click()
                    wlan_result = 1
                    time.sleep(5)
            if wlan_result:
                ap_find_result = ''

                ## 查找wlan位置

                for scan_num in range(1, 4):
                    if ap_find_result == 1:
                        break
                    if scan_num > 1:
                        mars.Print("close N3 WIFI,and rescan ap...")
                        self.N3_wifi_off(serialN)
                        time.sleep(2)
                        self.N3_wifi_on(serialN)
                        time.sleep(15)
                    # p判断 ap是否存在
                    if d(text=self.AP_NAME).exists:
                        mars.Print("ap in UI")
                        ap_find_result = 1
                        break
                    else:
                        mars.Print("ap not in UI,scroll to find")
                        if scan_num > 1:
                            self.N3_screen(serialN)
                        d(scrollable=True).scroll.toBeginning()  # 滑倒顶部
                        for i in range(1, 100):
                            d.swipe(0.5, 0.8, 0.5, 0.6)
                            time.sleep(5)
                            if d(text=self.AP_NAME).exists:
                                ap_find_result = 1
                                break
                            elif d(text="Add network").exists and d(text=self.AP_NAME).exists is not True:
                                mars.Print('swipe end,not find ap')
                                if scan_num > 1:
                                    self.N3_screen(serialN)
                                # 没有找到ap，结束连接，返回false
                                mars.Print("not this ap")
                                break
                    if scan_num == 3:
                        mars.Print("N3 cannot find ap in 3 times,please check picture")
                        return 0
                if ap_find_result:
                    # ap 连接
                    time.sleep(3)
                    mars.Print("prepare to connect")
                    d(text=self.AP_NAME).click()
                    if d(text="FORGET").exists:
                        mars.Print("connected")
                    elif d(text="取消保存").exists:
                        mars.Print("connected")
                    elif d(text="WLAN").exists:
                        mars.Print("connected")
                    elif d(text="Wi‑Fi").exists:
                        mars.Print("connected")
                    else:
                        try:
                            # d(resourceId="com.android.settings: id / password").click()
                            d.send_keys("asr123456", clear=True)
                        except:
                            if self.quit_send_key():
                                mars.Print("send key successful")
                            else:
                                mars.Verdict("fail", "send key, fail")

                        if d(text="连接").exists:
                            d(text="连接").click()
                            time.sleep(25)
                            if d(text=self.AP_NAME).exists:
                                d(resourceId="android:id/title", text=self.AP_NAME).click()
                                time.sleep(5)
                                if d(text="已连接").exists:
                                    mars.Print('n3 connect pass')
                                else:
                                    # mars.Verdict("fail", "N3 connect ap, fail")
                                    mars.Print("已连接 is not exists")
                                    self.N3_send_keys(serialN)
                            elif self.reconnect_wifi():
                                mars.Print('n3 connect pass')
                            else:
                                mars.Verdict("fail", "N3 cannot find ap, fail")
                                return False
                        else:
                            d(text="CONNECT").click()
                            time.sleep(15)
                            if d(text=self.AP_NAME).exists:
                                d(resourceId="android:id/title", text=self.AP_NAME).click()
                                time.sleep(5)
                                if d(text="Connected").exists:
                                    mars.Print('n3 connect pass')
                                else:
                                    mars.Verdict("fail", "N3 connect ap, fail")
                            else:
                                mars.Verdict("fail", "N3 cannot find ap, fail")
                                return False
                    # 结束连接返回true
                    return 1
                else:
                    mars.Verdict("fail", "find ap, fail")
            else:
                mars.Verdict("fail", "into wlan, fail")
        else:
            mars.Verdict("fail", "into net  setting, fail")

    def N3_ping(self, SerialN):
        mars.Print('ping baidu')
        ping_str = '192.168.0.100'
        p_result = ''
        pi = subprocess.Popen('adb -s {0} shell ping -c 4 {1}'.format(SerialN, ping_str), shell=True,
                              stdout=subprocess.PIPE)
        for i in iter(pi.stdout.readline, 'b'):
            mars.Print('adb ping record: {0}'.format(i.decode()))
            if "time=" in i.decode():
                p_result = 'pingPASS'
                print("ping www.baidu.com pass!!!!")
                mars.Print('ping baidu pass')
                mars.Print("pass,ping baidu,pass")
                break
            elif "" == i.decode():
                print("ping www.baidu.com fail!!!!")
                mars.Print('ping baidu fail')
                mars.Verdict("fail", "ping baidu,fail")
                break
        return p_result

    def N3_delete_WLAN(self, serialN):
        d = u2.connect_usb(serialN)
        d.press("home")
        # 打开设置
        d.app_start("com.android.settings")
        time.sleep(1)
        try:
            # 打开N3网络
            if d(text="网络和互联网").exists:
                d(text="网络和互联网").click()
            else:
                if d(text="Network & Internet").exists:
                    d(text="Network & Internet").click()
                else:
                    d(text="Network & internet").click()
            time.sleep(1)
            # 打开N3网络-wlan
            if d(text="WLAN").exists:
                d(text="WLAN").click()
            else:
                d(text="Wi‑Fi").click()
            # 打开已保存的网络删除指定ap
            d(scrollable=True).scroll.to(description="已保存的网络")
            if d(text="已保存的网络").exists:
                d(text="已保存的网络").click()
            else:
                d(text="Saved networks").click()

            time.sleep(1)
            d(text=self.AP_NAME).click()
            if d(text="取消保存").exists:
                d(text="取消保存").click()
            else:
                d(text="FORGET").click()
        except Exception:
            # U2 can not find click point
            mars.Print("U2 can not find click point")
            mars.Verdict("fail", "U2 can not find click point,fail")

    def open_ap_N3_checkIP(self):
        if self.heron_baseaction.open_ap() == 1:
            mars.Print("pass,open ap, pass")
            if self.N3_run() == 1:
                mars.Print("pass,n3 connect, pass")
                if self.heron_baseaction.ip_check() == 1:
                    mars.Print("pass,ip check, pass")
                    return 1
                else:
                    mars.Verdict("fail", "ip check, fail")
            else:
                mars.Verdict("fail", "n3 connect, fail")
        else:
            mars.Verdict("fail", "open ap, fail")
        return 0

    def n3_unsave_ap(self):
        serialN = ''
        sn = os.popen('adb devices').readlines()
        num = len(sn)
        if num < 3:
            mars.Print("No Devices,please connect the device")
            # mars.Verdict("fail", "NO N3 connect to PC")
            return
        else:
            if '* daemon not running' in sn[1]:
                for i in range(3, (num - 1)):
                    serialN = sn[i].split("\t")[0]
            else:
                for i in range(1, (num - 1)):
                    serialN = sn[i].split("\t")[0]
        d = u2.connect_usb(serialN)
        if d(text="取消保存").exists:
            d(resourceId="com.android.settings:id/button1_negative").click()
            # d(text="取消保存").click()
        else:
            # d(resourceId="android:id/title", text=AP_NAME).click()
            # time.sleep(5)
            # d(resourceId="com.android.settings:id/button1_negative").click()
            mars.Print('claer saved wifi-network failed')

    def open_ap_n3_check_ip_without_ping(self):
        """
        open ap
        n3_run_without_ping
        ip_check
        :return: True/False
        """
        if self.heron_baseaction.open_ap():
            mars.Print("pass,open ap, pass")
            self.n3_run_without_ping()
            if self.heron_baseaction.ip_check():
                mars.Print("pass,ip check, pass")
                return True
            else:
                mars.Verdict("fail", "ip check, fail")
        else:
            mars.Verdict("fail", "open ap, fail")
        return False

    def n3_run_without_ping(self):
        """
        n3 open wifi
        n3 scan wifi
        n3 connect ap
        :return: True/False
        """
        serialN = ''
        sn = os.popen('adb devices').readlines()
        num = len(sn)
        if num < 3:
            print("No Devices,please connect the device")
            return
        else:
            if '* daemon not running' in sn[1]:
                for i in range(3, (num - 1)):
                    serialN = sn[i].split("\t")[0]
            else:
                for i in range(1, (num - 1)):
                    serialN = sn[i].split("\t")[0]
        self.N3_wifi_on(serialN)
        if self.n3_wifi_scan(serialN):
            mars.Print("N3 cli_supplicant command can find ap pass,will connect this ap...")
            if self.N3_con_ap(serialN) == 1:
                time.sleep(5)
                mars.Print("N3 connect ap success")
            else:
                mars.Verdict("fail", "N3 connect ap failed")
        else:
            mars.Verdict("fail", "N3 cli_supplicant command can not find ap , fail")

    def n3_wifi_scan(self, serialN):
        """
        search for visible wifi
        :param serialN: devices serial number
        :return: True/False
        """
        for scan_num in range(1, 4):
            obj = subprocess.Popen(['adb', '-s', '{0}'.format(serialN), 'shell'], shell=True, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            obj.stdin.write('su\n'.encode('utf-8'))
            time.sleep(1)
            # search for visible wifi
            obj.stdin.write('wpa_cli -i wlan0 scan\n'.encode('utf-8'))
            time.sleep(15)
            # search for visible wifi results
            obj.stdin.write('wpa_cli -i wlan0 scan_results\n'.encode('utf-8'))
            time.sleep(15)
            # exit
            obj.stdin.write('exit\n'.encode('utf-8'))
            info, err = obj.communicate()
            if err.decode('gbk'):
                mars.Print("the {0} N3 wifi cannot work well!!".format(scan_num))
                mars.Print(err.decode('gbk'))
            else:
                if self.AP_NAME in info.decode('gbk'):
                    mars.Print("ap find in list")
                    return True
                else:
                    mars.Print("the {0} ap not find in list".format(scan_num))
                    mars.Print(info.decode('gbk'))
            # search four times
            if scan_num > 4:
                mars.Print("N3 cannot find this ap in 3 times")
                return False

    def open_ap_n3_check_ip(self):
        """
        open ap
        n3_run
        ip_check
        :return: True/False
        """
        if self.heron_baseaction.open_ap():
            mars.Print("pass,open ap, pass")
            if self.N3_run():
                mars.Print("pass,n3 connect, pass")
                if self.heron_baseaction.ip_check():
                    mars.Print("pass,ip check, pass")
                    return True
                else:
                    mars.Verdict("fail", "ip check, fail")
            else:
                mars.Verdict("fail", "n3 connect, fail")
        else:
            mars.Verdict("fail", "open ap, fail")
        return False
