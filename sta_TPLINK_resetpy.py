import os
# import mars
import time
import traceback
import subprocess
import json
from abc import ABCMeta, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver as Chrome
from selenium.webdriver.common.action_chains import ActionChains
import random
from wifilib import heron_wifi
from wifilib import net_card
from wifilib import basic_fun

router = "tlwr886n"
# 路由器登录相关信息
router_username = "admin"
router_password = "AAbbcc123"
host = "192.168.1.1"
# host = "tplogin.cn"
wireless_setting = "2.4G"
# ap热点名字
ap_name = "tlwr886n"
ap_pwd = "123456789"
# tplink 待设置参数
channel=[1, 6, 11] # 1--13
# mode=["0","1","2","3","4"] # bgn  bg n g b
mode=["0"] # bgn  bg n g b
bandwidth=["1"]  #自动/20
ssidbrd=[1]  # 0为隐藏  1为可见


class router_process(object):
    def __init__(self, router_password, username, password,wlan_channel,wlan_mode, wlan_width):
        self.username = username
        self.password = password
        self.router_password = router_password
        self.wlan_channel = wlan_channel
        self.wlan_mode = wlan_mode
        self.wlan_width = wlan_width

        self.driver = Chrome(executable_path='C:\Program Files\Google\Chrome\Application\chromedriver.exe')
        self.my_action = ActionChains(self.driver)

    def process_all(self):
        self.log_in()
        time.sleep(0.5)

        # mars.Print(" add_encryption mode ")
        time.sleep(2)
        self.wlan_set_encryption()
        self.mode_slete()
        # mars.Print("setting success")

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
        # mars.Print(" log in setting")
        self.driver.find_element(By.ID, "wlanPwd").clear()
        time.sleep(1)
        self.driver.find_element(By.ID, "wlanPwd").click()
        self.driver.find_element(By.ID, "wlanPwd").send_keys(self.password)  # 登录密码
        time.sleep(2)
        # mars.Print("password has set done")
        self.driver.find_element(By.ID, "saveBasic").click()  # 点击保存

    # def wlan_no_encryption(self):
    #     self.driver.find_element(By.ID, "routerSetMbtn").click()  # 路由设置
    #     time.sleep(0.5)
    #     self.driver.find_element(By.ID, "wireless2G_rsMenu").click()  # 无线设置
    #
    #     time.sleep(1)
    #     mars.Print(" log in setting")
    #     self.driver.find_element(By.ID, "wlanPwd").clear()
    #     time.sleep(1)
    #     self.driver.find_element(By.ID, "saveBasic").click()  # 点击保存

    def box_click(self, type, id_str, idx1):

        str1 = "// *[ @ id = '{0}'] / li[{1}]".format(id_str, idx1)
        # mars.Print(str1)
        self.driver.find_element(By.ID, type).click()
        # time.sleep(5)
        time.sleep(2)
        # mars.Print("click end ")
        my_error_element = self.driver.find_element(By.XPATH, str1)
        # time.sleep(6)
        time.sleep(2)
        self.my_action.move_to_element(my_error_element).perform()  # 将鼠标移动到点击的位置
        time.sleep(2)
        # mars.Print("move end")
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
            # mars.Print("move save")
            time.sleep(10)
            self.driver.find_element(By.ID, "save").click()  # 点击保存
            time.sleep(10)
            # mars.Print("save success")
        except:
            print("a")
            # mars.Print("errior")

def run():
    time1 = 0
    while time1<=3:
        try:
            r = router_process(router_password, ap_name, ap_pwd, 12, 1, 1)
            r.process_all()
            r.driver.quit()
            time.sleep(10)
            break
        except:
            time1 = time1 + 1
            continue

if __name__ == '__main__':
    run()