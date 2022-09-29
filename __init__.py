# -*- coding: utf-8 -*-
from ctypes import *
import os
import sys

__version__ = "V1.1.0.1"
__package__name_ = "CraneG "
__description__ = "CraneG  pacakge,20211224"

# "strVersion",strTestPackageName", "strDescription"
def GetTestPackageDetails():
    return (__version__, __package__name_, __description__ )

#Test Case Details in dict:tuple format
# "filename":("strVersion","strCaseName", "strSubTitle", "strDescription", "strComments")
def GetTestCaseDetails():
    return {
        "sta_TPLINK_resetpy.py": ("V1.0.0.1", "sta_TPLINK_resetpy", "sta_TPLINK_resetpy test ap", "proc for sample", "proc for sample"),
        "sta_connect_ap.py":("V1.0.0.1","sta_connect_ap","sta_connect_ap test ap","proc for sample","proc for sample"),
        "sta_connect_standby.py":("V1.0.0.1","sta_connect_standby","sta_connect_standby test ap","proc for sample","proc for sample"),
        "sta_connected_close.py":("V1.0.0.1","sta_connected_close","sta_connected_close test ap","proc for sample","proc for sample"),
        "sta_scan_connect_ap.py":("V1.0.0.1","sta_scan_connect_ap","sta_scan_connect_ap test ap","proc for sample","proc for sample"),
        "sta_scan_without_connect_ap.py":("V1.0.0.1","sta_scan_without_connect_ap","sta_scan_without_connect_ap test ap","proc for sample","proc for sample"),
        "sta_TPLink_channel_encryption.py":("V1.0.0.1","sta_TPLink_channel_encryption","sta_TPLink_channel_encryption test ap","proc for sample","proc for sample"),
        "sta_press_scan_test.py":("V1.0.0.1","sta_press_scan_test","sta_press_scan_test test ap","proc for sample","proc for sample"),
        "Sta_idle_query_version.py": ("V1.0.0.1", "Sta_idle_query_version", "Sta_idle_query_version", "sta keep idle and query version test", "sta keep idle and query version"),
        "Sta_idle_query_version_connect_ap.py": ("V1.0.0.1", "Sta_idle_query_version_connect_ap", "Sta_idle_query_version_connect_ap", "sta connect ap keep idle and query version test", "sta connect ap keep idle and query version"),
        "Sta_search_network_query_version.py": ("V1.0.0.1", "Sta_search_network_query_version", "Sta_search_network_query_version", "sta search network and query version test", "sta search network and query version"),
        "Sta_search_network_query_version_connect_ap.py": ("V1.0.0.1", "Sta_search_network_query_version_connect_ap", "Sta_search_network_query_version_connect_ap", "sta connect ap search network and query version test", "sta connect ap search network and query version"),
        "Sta_CSPS_query_version.py": ("V1.0.0.1", "Sta_CSPS_query_version", "Sta_CSPS_query_version", "sta do csps event and query version test", "sta do csps event and query version"),
        "Sta_CSPS_query_version_connect_ap.py": ("V1.0.0.1", "Sta_CSPS_query_version_connect_ap", "Sta_CSPS_query_version_connect_ap", "sta connect ap do csps event and query version test", "sta connect ap do csps event and query version"),

        "sta_scan_direct_connect.py": ("V1.0.0.1", "sta_scan_direct_connect", "sta_scan_direct_connect","sta connect ap do ping or call event and query version test", "sta connect ap do ping or call event and query version"),
        "sta_wifi_reconnect.py": ("V1.0.0.1", "sta_wifi_reconnect", "sta_wifi_reconnect","sta connect close and reconnect test", "sta connect close and reconnect"),
        "sta_TPLink_mode_serch_network.py": ("V1.0.0.1", "sta_TPLink_mode_serch_network", "sta_TPLink_mode_serch_network","sta connect encryption and disencryption at diff mode test", "sta connect encryption and disencryption at diff mode")

    }
if __name__ =='__main__': 
    cmd=''
    try:
        cmd = sys.argv[1:1]
    except Exception as e:
        print(GetTestPackageDetails()) 
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd =='GetTestCaseDetails':
        print(GetTestCaseDetails()) 
    elif cmd =='GetTestPackageDetails':
        print(GetTestPackageDetails()) 
    else: 
        print(GetTestPackageDetails()) 

