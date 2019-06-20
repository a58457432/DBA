#!/usr/bin/env python
## coding=utf-8
# Creator: shenjinhong
# UpdateTime:2019.6.10


import psutil
import datetime
#from datetime import datetime
import re
import copy
from os import path
import sys
import time
import socket
import os
try:
    import json
except:
    import simplejson as json
import subprocess


pt_hostname="/usr/local/bin/pt-summary | grep Hostname | awk -F '|' '{print $2}'"
pt_platform="/usr/local/bin/pt-summary |grep -iv System| grep Platform | awk -F '|' '{print $2}'"
pt_release="/usr/local/bin/pt-summary | grep Release | awk -F '|' '{print $2}'"
pt_kernel="/usr/local/bin/pt-summary | grep Kernel | awk -F '|' '{print $2}'"
pt_system="/usr/local/bin/pt-summary | grep System | awk -F '|' '{print $2}'"

def runCmd(cmd):
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    except:
        return None, p.returncode
    else:
        output, err = p.communicate()
        return output, p.returncode

def get_sys_info():
	sys_info={}
	sys_info['hostname']=str(list(runCmd(pt_hostname))[0])
	sys_info['platform']=str(list(runCmd(pt_platform))[0])
	sys_info['release']=str(list(runCmd(pt_release))[0])
	sys_info['kernel']=str(list(runCmd(pt_kernel))[0])
	sys_info['system']=str(list(runCmd(pt_system))[0])
	print(sys_info)
	return sys_info

def get_cpu_info():
	cpu_info={}
	data=psutil.cpu_times_percent(3)
	cpu_info['user']=data[0]
	cpu_info['system']=data[2]
	cpu_info['idle']=data[3]
	cpu_info['iowait']=data[4]
	cpu_info['hardirq']=data[5]
	cpu_info['softirq']=data[6]
	cpu_info['cpu_cores']=psutil.cpu_count()
	print(cpu_info)
	return cpu_info
	

def get_mem_info():
	mem_info={}
	data=psutil.virtual_memory()
	mem_info['mem_total']=data[0]/1024/1024/1024
	mem_info['mem_avariable']=data[1]/1024/1024/1024
	mem_info['mem_percent']=data[2]
	print(mem_info)
	return mem_info

def get_disk_info():
	disk_info={}
	partitions=psutil.disk_partitions()
	for i in partitions:
		disk_info[i[0]]={}
		disk_info[i[0]]['mountpoint']=i[1]
		disk_info[i[0]]['fstype']=i[2]		
		disk_info[i[0]]['total_size']=psutil.disk_usage(i[1])[0]/1024/1024/1024
		disk_info[i[0]]['used_percent']=psutil.disk_usage(i[1])[3]		

	print(disk_info)
	return disk_info

def cal():
	get_sys_info()
	get_cpu_info()
	get_mem_info()
	get_disk_info()	

def main():
    cal()


if __name__ == '__main__':
    main()
