#!/usr/bin/env python
## coding=utf-8
# Creator: shenjinhong
# UpdateTime:2019.6.11

import sys
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
from chardet import detect
import tarfile

command = "sysctl -p"
command_se = "getenforce"
stop_firewall_cmd = "systemctl stop firewalld.service"
disable_firewall_cmd = "systemctl status firewalld"
pt_list = "yum install perl-IO-Socket-SSL perl-DBD-MySQL perl-Time-HiRes perl-DBI  -y"
wget_pt_tools = "wget -c https://www.percona.com/downloads/percona-toolkit/3.0.13/binary/tarball/percona-toolkit-3.0.13_x86_64.tar.gz"
tools_pkg = "percona-toolkit-3.0.13_x86_64.tar.gz"
softdir = "/usr/local/webserver/software/"
profile = "/root/.bash_profile"

def runCmd(cmd):
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    except:
        return None, p.returncode
    else:
        output, err = p.communicate()
        return output, p.returncode

def check(dstStr, fn):
    with open(fn, 'rb') as fp:
        content = fp.read()
    encoding = detect(content)['encoding']
    try:
        content = content.decode(encoding)
        return dstStr in content
    except:
        return False

def untar(fname, dirs):
	t = tarfile.open(fname)
	t.extractall(path = dirs)
	

#liunx init

def modify_file():
	file_limit="fs.file-max = 6553560"
	swap="vm.swappiness = 0"
	soft_limit_nofile="* soft nofile 204800" + "\n"
	soft_limit_nproc="* soft nproc 204800" + "\n"
	hard_limit_nofile="* hard nofile 204800" + "\n"
	hard_limit_nproc="* hard nproc 204800" + "\n"
	file_ulimits = [soft_limit_nofile, soft_limit_nproc, hard_limit_nofile, hard_limit_nproc]
	 
	sysctl_file_name="/etc/sysctl.conf"
	limits_file_name="/etc/security/limits.conf"

	if check(file_limit, sysctl_file_name) == False:
		with open(sysctl_file_name,'a+') as f:
			f.write(file_limit + "\n")
	else:
		print("has file-max!")	

	if check(swap, sysctl_file_name) == False:
		with open(sysctl_file_name, 'a+') as f:
			f.write(swap + "\n") 
	else:
		print("has swap !")

	if check(hard_limit_nproc, limits_file_name) == False:
		with open(limits_file_name, 'a+') as f:
			f.writelines(file_ulimits)
	else:
		print("set ulimit 204800")
	
	flag = runCmd(command)
	if flag[1] == 0:
		print("limits.conf has being changed")
	else:
		print("limits.conf has not being changed")	

#  seliunx && firewall
def check_params():
	flag = "SELINUX=disabled"
	file_name = "/etc/selinux/config"
	seliunx_flag = runCmd(command_se)[0]
	sflag = seliunx_flag.decode('utf-8', 'ignore')
	sflag = sflag.strip()

	if sflag == 'Disabled':
		print("seliunx  is Disabled")
	else:
		with open(file_name, "r") as f:
			lines = f.readlines()
		with open(file_name, "w+") as f_w:
			for line in lines:
				if "SELINUX" in line:
					continue
				f_w.write(line)
				f_w.write(flag)
	
	check_firewall = runCmd(stop_firewall_cmd)[1]
	disable_firewall = runCmd(disable_firewall_cmd)[1]
	if check_firewall == 0 and disable_firewall == 0:
		print("firewall is stop")
	else:
		print("firewall is on")		

	

#check && install pt-tools
def install_pt_tools():
	if os.path.exists(softdir) == True:
		print("softdir is exists")
	else:
		os.makedirs(softdir)
	os.chdir(softdir)
	check_pt_list = runCmd(pt_list)[1]
	check_pt_tools = runCmd(wget_pt_tools)[1]
	if check_pt_list == 0 and check_pt_tools == 0:
	#解压&& 配置.bash_profile&& source	
		untar(tools_pkg, softdir)
		print("tar sucess")
	else:
		print("pt_tools is not ready")
	
	for i in os.listdir():
		if i.find('percona') == 0 and os.path.isdir(i):
			pt_dir = i
			
	pt_bin = softdir + pt_dir + '/bin'
	pro = "export PATH=$PATH:" + pt_bin
	with open(profile, "a+") as f:
		f.write(pro + "\n")
	
	profile_flag = runCmd('source ' + profile)[1]
	if profile_flag == 0:
		print "source profile sucessd"
	
def main():
	modify_file()
	check_params()
	install_pt_tools()

if __name__ == '__main__':
    main()
