#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    (C) 21vianet Inc.
#
#    Last update: sjh 2019-12-20

""" Run CMD or SCP In Batch Mode

You can choose project type, area  to run command or upload file.
Output info will print to script.info.

"""

__authors__ = [
    '"sjh"',
]

import MySQLdb
import ConfigParser
from datetime import datetime
import re
import copy
from os import path
import sys
import time
import socket
import subprocess

#sys.path.append(path.join(path.realpath(path.dirname(sys.argv[0])), "lib"))

# ----------------------------------------------------------------------------------------
# Parameter
# ----------------------------------------------------------------------------------------
# -----> Global Variables
# from global_var import *
DBSTATUS_FILE = "/opt/DBins.Info"  # db状态输出文件的路径
LAST_DBSTATUS_FILE = "/opt/.last_status.txt"  # 上一次状态数值文件的路径
dt = datetime.now()
DATETIME = dt.strftime('%Y-%m-%d %H:%M:%S')


# master/slave dba info
sock = ''
port = 3306
IP = ['172.21.102.8','172.21.120.6']

port_list = [3306, 3307, 3308, 3309]
IP_list = ['172.21.101.9','172.21.101.10','172.21.101.11','172.21.101.12','172.21.101.13','172.21.101.14','172.21.101.17','172.21.101.15']

user = 'zabbix_reader'
password = 'zabbix_reader2021'
dbschema = 'mysql'


# zabbix server
zb_sender = '/usr/bin/zabbix_sender'
zb_server = '10.21.3.60'
zb_server_port = 10051


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
    dbinfo['slave_status'] = {}  # db主从状态变量
    dbinfo['port'] = port
    dbinfo['ip'] = IP
    dbinfo['user'] = user
    dbinfo['password'] = password
    dbinfo['dbschema'] = dbschema
    dbinfo['insname'] = insname
    dbins[insname] = copy.deepcopy(dbinfo)
    return dbins


# ------------------
# mysql init
# -----------------
def init_connect(ip,port,user,passwd,dbschema):

    db = MySQLdb.connect(host=ip, port=port, user=user, passwd=passwd, db=dbschema,charset='utf8')
    slaveinfo = {}  
    slave_status_template = ('Seconds_Behind_Master','Slave_SQL_Running','Slave_IO_Running',)

    cur = db.cursor()
    sql = "select 10*10;"
    cur.execute(sql)
    rows = cur.fetchall()
    if rows[0][0] != 100:
        slaveinfo['server_status'] = 'off'
    else:
        slaveinfo['server_status'] = 'on'
   
    try:
        slave_cur = db.cursor(MySQLdb.cursors.DictCursor)
        sql = "show slave status;"
        slave_cur.execute(sql)
        rows = slave_cur.fetchall()
        slaveinfo[insname] = rows[0].copy()
        for key in rows[0]:
            if key not in slave_status_template:
                del slaveinfo[insname][key]
        for (key, value) in slaveinfo[insname].items():
            if value == '' :
                db['slave_status'][key] = 'something'

    except IndexError:
        pass    
   
    if slaveinfo[insname]['Slave_SQL_Running'] == 'Yes' and slaveinfo[insname]['Slave_IO_Running'] == 'Yes' :
        slaveinfo['slave_replication'] = 1
    else:
        slaveinfo['slave_repliaction'] = 0

        

    
    db.close()
    return slaveinfo


def push_zabbix_items(key,insname,val):
    
    # zabbix_sender -z 192.168.31.156 -p 10051 -s "MySQL_mysql2" -k "QPS" -o 1000
    zb_sender_cmd2 = ('%s -z %s -p %d -s %s -k %s -o %s') % (zb_sender, zb_server, zb_server_port, insname, key, val)    
    
    print zb_sender_cmd2
    sender_cmd2 = runCmd(zb_sender_cmd2)
    if sender_cmd2[1] == 0:
        print "server_status" + "    sucessed"
    else:
        print "server_status" + "     failed"


if __name__ == '__main__':
#    slaveinfo = init_connect(IP,port,user,password,dbschema)
#    print slaveinfo

    for i in IP_list:
        for j in port_list:
            insname = 'MySQL_' + i + '_' + str(j)
            slaveinfo = init_connect(i,j,user,password,dbschema)
            if slaveinfo.get('slave_replication') == None:
                slaveinfo['slave_replication'] = 0
            push_zabbix_items('slave_replication', insname, slaveinfo['slave_replication'])
            push_zabbix_items('server_status', insname, slaveinfo['server_status'])
#            print type(slaveinfo.get('slave_replication'))
#            print slaveinfo.get('slave_replication')
#            print slaveinfo.keys()

    for i in IP:
        insname = 'MySQL_' + i + '_' + str(port)
        slaveinfo = init_connect(i,port,user,password,dbschema)
        if slaveinfo.get('slave_replication') == None:
            slaveinfo['slave_replication'] = 0
        push_zabbix_items('slave_replication', insname, slaveinfo['slave_replication'])
        push_zabbix_items('server_status', insname, slaveinfo['server_status'])
