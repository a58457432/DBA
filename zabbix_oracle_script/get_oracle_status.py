#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    (C) 21vianet Inc.
#
#    Last update: sjh 2020-03-06

""" Run CMD or SCP In Batch Mode

You can choose project type, area  to run command or upload file.
Output info will print to script.info.

"""

__authors__ = [
    '"sjh"',
]

import ConfigParser
from datetime import datetime
import re
import copy
from os import path
import sys
import time
import socket
import commands
import subprocess

#sys.path.append(path.join(path.realpath(path.dirname(sys.argv[0])), "lib"))

dt = datetime.now()
DATETIME = dt.strftime('%Y-%m-%d %H:%M:%S')




# zabbix server
zb_sender = '/usr/bin/zabbix_sender'
zb_server = '172.25.10.244'
zb_server_port = 10051

# zabbix agent
insname = 'RAC_' + socket.gethostname()

# <----- Global Variables

# ----------------------------------------------------------------------------------------
# run bash cmd 
# ----------------------------------------------------------------------------------------
def runCmd(cmd):
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    except:
        return None, p.returncode
    else:
        output, err = p.communicate()
    return output, p.returncode




# ----------------------------------------------------------------------------------------
# init dbs dict()
# ----------------------------------------------------------------------------------------
def init_dbins_info():
    dbins = {}  # db实例字典
    dbinfo = {}  # db信息字典
    dbinfo['lsnrctl_status'] = {}
    dbinfo['listen_status'] = {}
    dbinfo['tns_status'] = {}
    dbinfo['db_status'] = {}
    dbinfo['tbl_status'] = {}
    dbinfo['test'] = {}
    dbinfo['insname'] = insname
    dbinfo['asm_status'] = {}
    dbinfo['scan_ip'] = {}
    dbins[insname] = copy.deepcopy(dbinfo)
    return dbins

#--------------------------------
# get oracle status
#--------------------------------
def get_oracle_status():
    dbins = init_dbins_info() 
    for db in dbins.values():
        with open('/usr/local/webserver/zabbix_oracle_script/dbstatus.log','r') as f:
            for line in f.readlines():
                if line[0:4] == 'Last':
                    continue    
            
                linelist = re.split('=',line.strip())
                if "lsnrctl" in line:
                    db['lsnrctl_status'][linelist[0]] = linelist[1]
                if "listen" in line:
                    db['listen_status'][linelist[0]] = linelist[1]
                if "tns" in line:
                    db['tns_status'][linelist[0]] = linelist[1]
                if "db" in line:
                    db['db_status'][linelist[0]] = linelist[1]
                if "tbl" in line:
                    db['tbl_status'][linelist[0]] = linelist[1]
                if "asm" in line:
                    db['asm_status'][linelist[0]] = linelist[1]
                if "scan" in line:
                    db['scan_ip'][linelist[0]] = linelist[1]
#    print dbins
    return dbins



# ----------------------------------------------------------------------------------------
# push zabbix items
# ----------------------------------------------------------------------------------------
# zabbix_sender -z 192.168.31.156 -p 10051 -s "MySQL_mysql2" -k "QPS" -o 1000

def push_zabbix_items():
    dbins = get_oracle_status()
    dbs = dbins.values()
    dbs.sort()
    
    for status_type in ('lsnrctl_status', 'listen_status', 'tns_status', 'db_status', 'tbl_status', 'asm_status','scan_ip'):
        for (key, value) in dbs[0][status_type].items():
            zb_sender_cmd = ('%s -z %s -p %d -s %s -k %s -o %s') % (zb_sender, zb_server, zb_server_port, insname, str(key), str(value))
            print zb_sender_cmd
            try:
                sender_cmd = runCmd(zb_sender_cmd)
            except Exception, e:
                print str(e)

            if sender_cmd[1] == 0:
                print str(key) + "    sucessed"
            else:
                print str(key) + "     failed"


if __name__ == '__main__':
    push_zabbix_items()
