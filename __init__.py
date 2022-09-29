# -*- coding: utf-8 -*-
from ctypes import *
import os
import sys

__version__ = "V1.1.0.1"
__package__name_ = "Falcon N3"
__description__ = "Falcon N3 pacakge,20211224"

# "strVersion",strTestPackageName", "strDescription"
def GetTestPackageDetails():
    return (__version__, __package__name_, __description__ )

#Test Case Details in dict:tuple format
# "filename":("strVersion","strCaseName", "strSubTitle", "strDescription", "strComments")
def GetTestCaseDetails():
    return {
        "ap_reconnect_N3.py":("V1.0.0.1","ap_connect_N3","ap_connect_N3 test ap","proc for sample","proc for sample"),
        "ap_connect_N3_data_recovery.py":("V1.0.0.1","ap_connect_N3_data_recovery","ap_connect_N3_data_recovery test ap","proc for sample","proc for sample"),
        "ap_connect_N3_data_reset.py":("V1.0.0.1", "ap_connect_N3_data_reset", "ap_connect_N3_data_reset test ap", "proc for sample","proc for sample"),
        "ap_connect_N3_recovery.py":("V1.0.0.1", "ap_connect_N3_recovery", "ap_connect_N3_recovery test ap", "proc for sample","proc for sample"),
        "ap_connect_N3_reset.py":("V1.0.0.1", "ap_connect_N3_reset", "ap_connect_N3_reset test ap", "proc for sample","proc for sample"),
        "ap_reconnect_data_N3.py":("V1.0.0.1", "ap_reconnect_data_N3", "ap_reconnect_data_N3 test ap", "proc for sample","proc for sample"),
        "Lock_LTE_N3_Data.py": ("V1.0.0.1", "Lock_LTE_N3_Data", "Lock_LTE_N3_Data", "n3 ping and falcon call test LTE","n3 ping and falcon call LTE"),
        "Lock_WCDMA_N3_Data.py": ("V1.0.0.1", "Lock_WCDMA_N3_Data", "Lock_WCDMA_N3_Data", "n3 ping and falcon call test WCDMA","n3 ping and falcon call WCDMA"),
        "Lock_GSM_N3_Data.py": ("V1.0.0.1", "Lock_GSM_N3_Data", "Lock_GSM_N3_Data", "n3 ping and falcon call test GSM","n3 ping and falcon call GSM"),
        "CSPS_query_stainfo.py": ("V1.0.0.1", "CSPS_query_stainfo", "CSPS_query_stainfo", "do cs or ps event and query stainfo test", "do cs or ps event and query stainfo"),
        "CSPS_query_version.py": ("V1.0.0.1", "CSPS_query_version", "CSPS_query_version", "do cs or ps event and query version", "do cs or ps event and query version"),
        "Idle_query_stainfo.py": ("V1.0.0.1", "Idle_query_stainfo", "Idle_query_stainfo", "keep idle and query stainfo test", "keep idle and query stainfo"),
        "Idle_query_version.py": ("V1.0.0.1", "Idle_query_version", "Idle_query_version", "keep idle and query version test", "keep idle and query version"),
        "Search_network_query_stainfo.py": ("V1.0.0.1", "Search_network_query_stainfo", "Search_network_query_stainfo", "search network and query stainfo test", "search network and query stainfo"),
        "Search_network_query_version.py": ("V1.0.0.1", "Search_network_query_version", "Search_network_query_version", "search network and query version test", "search network and query version"),
        "N3_DKB_Reboot.py": ("V1.0.0.1", "N3_DKB_Reboot", "N3_DKB_Reboot test ap", "N3_DKB_Reboot", "N3_DKB_Reboot"),
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