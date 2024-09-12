#!/usr/bin/env python
## coding=utf-8
# Creator: sjh
# UpdateTime:2019.7.1

import platform
import socket
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
import paramiko
import yaml

def runCmd(cmd):
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    except:
        return None, p.returncode
    else:
        output, err = p.communicate()
        return output, p.returncode

def yamllist(filename):
    f = open(filename)
    x = yaml.load(f, Loader=yaml.FullLoader)

    return x

class sshd:

    def __init__(self, host, port, user, passwd):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd

    def to_do(self, cmd):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=self.host, port=self.port, username=self.user, password=self.passwd)
            stdin, stdout, stderr = client.exec_command(cmd)
            print(stdout.read().decode('utf-8'))
            client.close()
        except(Exception, e):
            print(str(e))

def main():
    ylist = yamllist('/usr/local/webserver/scripts/db_tools/host.yaml')
    for i in ylist['ip_list']:
        print(i)
        a = sshd(i['host'], ylist['port'], ylist['sysuser']['user'], ylist['sysuser']['passwd'])
        a.to_do('hostname')
#        a.to_do('cat /etc/redhat-release')
#        a.to_do('yum install https://repo.saltstack.com/yum/redhat/salt-repo-latest.el6.noarch.rpm -y')
#        a.to_do('yum install salt-minion -y')
#        a.to_do("echo 'main: 172.20.20.187' > /etc/salt/minion")
        a.to_do('service salt-minion start')

if __name__ == '__main__':
    main()
