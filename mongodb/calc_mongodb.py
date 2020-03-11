#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    (C) 21vianet Inc.
#
#    Last update: sjh 2020-03-05

""" Run CMD or SCP In Batch Mode

You can choose project type, area  to run command or upload file.
Output info will print to script.info.

"""

__authors__ = [
    '"sjh"',
]

import pymongo
from pymongo import MongoClient
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


# master/slave dba info
sock = ''
port = 3307
IP = '192.168.31.125'
user = 'root'
password = '123456'
dbschema = 'mysql'


# zabbix server
zb_sender = '/usr/bin/zabbix_sender'
zb_server = '192.168.31.156'
zb_server_port = 10051

# zabbix agent
insname = 'MySQL_' + socket.gethostname()

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
# Some prepare work before scp or run command.
# ----------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------
# init dbs dict()
# ----------------------------------------------------------------------------------------
def init_dbins_info():
    dbins = {}  # db实例字典
    dbinfo = {}  # db信息字典
    dbinfo['global_var'] = {}  # db global variables 字典
    dbinfo['global_status'] = {}  # db global status 字典
    dbinfo['slave_status'] = {}  # db主从状态变量
    dbinfo['master_status'] = {}  # db从库对应主库状态变量
    dbinfo['last_status'] = {}  # db上一次状态数值字典
    dbinfo['cur_status_cal'] = {}  # db当前计算后状态变量
    dbinfo['processlist'] = {}
    dbinfo['server_status'] = ''  # dbserver 状态数值(是否active), 初始化为"on"
    dbinfo['port'] = port
    dbinfo['ip'] = IP
    dbinfo['user'] = user
    dbinfo['password'] = password
    dbinfo['dbschema'] = dbschema
    dbinfo['insname'] = insname

    dbins[insname] = copy.deepcopy(dbinfo)
    return dbins

#-------------------------
# conn mongodb
#-------------------------
def conn_mongodb():
    myclient = pymongo.MongoClient('mongodb://admin:admin@192.168.31.156:27017/')
    c = myclient.database_names()
    a = myclient["school"]
    b = a['col']
    print b.find().count()
    for i in c:
        print "database_name : " +  i
        print myclient[i].list_collection_names(session=None)
        print myclient[i].list_collection_names(session=None)[0]

# ----------------------------------------------------------------------------------------
# Class for DBStatus.
# ----------------------------------------------------------------------------------------

if __name__ == '__main__':
    conn_mongodb()
