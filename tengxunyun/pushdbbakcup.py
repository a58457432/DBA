#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    (C) YGF.
#
#    Last update: sjh 2024-11-24G

""" Run CMD or SCP In Batch Mode

You can choose project type, area  to run command or upload file.
Output info will print to script.info.

"""

__authors__ = [
    '"sjh"',
]

#import MySQLdb
#import ConfigParser
from datetime import datetime, timedelta
import re
import copy
from os import path
import os
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
one_day_age = dt - timedelta(days=1)
DATETIME = dt.strftime('%Y-%m-%d')
one_datetime = one_day_age.strftime('%Y-%m-%d')


# Pos-营销中台-Prod
port = 3306
IP = '172.17.16.58'
user = 'DB_Backup_ygf'
password = 'P@ssw0rd'
bussiness = 'Pos-营销中台-Prod'
backup_dir = '/data/mysql/'
yxzt_file = backup_dir + bussiness + '_' + DATETIME + '.sql.gz'


# Pos-Cpos-Prod
Cops_IP = '172.17.16.185'
bussiness02 = 'Pos-Cpos-Prod'
cpos_file = backup_dir + bussiness02 + '_' + DATETIME + '.sql.gz'

# Pos-业务中台-Prod
ywzt_IP = '172.17.16.158'
bussiness03 = 'Pos-业务中台-Prod'
ywzt_file = backup_dir + bussiness03 + '_' + DATETIME + '.sql.gz'

# Pos-营销中台CRM-Prod
yxztcrm_IP = '172.17.16.237'
bussiness04 = 'Pos-营销中台CRM-Prod'
yxztcrm_file = backup_dir + bussiness04 + '_' + DATETIME + '.sql.gz'

# Pos-业务中台-订单-Prod
ywzt_dd_IP = '172.17.16.133'
bussiness05 = 'Pos-业务中台-订单-Prod'
ywzt_dd_file = backup_dir + bussiness05 + '_' + DATETIME + '.sql.gz'

# MSY-生命周期-Prod
smzq_IP = '172.17.32.7'
bussiness06 = 'MSY-生命周期-Prod'
smzq_file = backup_dir + bussiness06 + '_' + DATETIME + '.sql.gz'

#存储桶
bucket = 'mysql' + DATETIME + '/'

#coscmd upload /data/mysql/MSY-生命周期-Prod_2024-11-26.sql.gz  mysql-2024-11-26/

# dump
mysql_dump_cmd = '/usr/local/mysql8.4/bin/mysqldump'

# cos
coscmd_cmd = '/usr/local/bin/coscmd'

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
# init dbs dict()
# ----------------------------------------------------------------------------------------
def init_dbins_info():
    dbins = {}  # db实例字典
    dbinfo = {}  # db信息字典
    dbinfo['port'] = port
    dbinfo['ip'] = IP
    dbinfo['user'] = user
    dbinfo['password'] = password
    dbinfo['bussiness'] = bussiness
    dbinfo['yxzt_file'] = yxzt_file
    dbinfo['backup_dir'] = backup_dir
    dbinfo['Cops_IP'] = Cops_IP
    dbinfo['bussiness02'] = bussiness02
    dbinfo['cpos_file'] = cpos_file
    dbinfo['ywzt_IP'] = ywzt_IP
    dbinfo['bussiness03'] = bussiness03
    dbinfo['ywzt_file'] = ywzt_file
    dbinfo['yxztcrm_IP'] = yxztcrm_IP
    dbinfo['bussiness04'] = bussiness04
    dbinfo['yxztcrm_file'] = yxztcrm_file
    dbinfo['ywzt_dd_IP'] = ywzt_dd_IP
    dbinfo['bussiness05'] = bussiness05
    dbinfo['ywzt_dd_file'] = ywzt_dd_file
    dbinfo['smzq_IP'] = smzq_IP
    dbinfo['bussiness06'] = bussiness06
    dbinfo['smzq_file'] = smzq_file

    dbins[bussiness] = copy.deepcopy(dbinfo)
    return dbins

#mysqldump -h 172.17.16.58 -P3306 -u DB_Backup_ygf -pP@ssw0rd -A --single-transaction > all02.sql
#
# mysqldump -h 172.17.16.58 -P3306 -u DB_Backup_ygf -pP@ssw0rd -A --single-transaction | gzip > /d# ata/mysql/all02.sql.gz

# dump mysql data

def dump_mysql_data():
    dbins = init_dbins_info()
    dbins = dbins.values()
    dbins = list(dbins)[0]
    mysqldump_cmd = ('%s -h %s -P%d -u %s -p%s -A --single-transaction | gzip > %s ') % (mysql_dump_cmd,dbins['ip'],dbins['port'],dbins['user'],dbins['password'],dbins['yxzt_file'])
    print(mysqldump_cmd)
    try:
        mysqldump_cmd = runCmd(mysqldump_cmd)
    except Exception as e:
        print(str(e))
    
    if mysqldump_cmd[1] == 0:
        print(bussiness + "    sucessed")
    else:
        print(bussiness + "     failed")

    # business02
    mysqldump_cmd02 = ('%s -h %s -P%d -u %s -p%s -A --single-transaction | gzip > %s ') % (mysql_dump_cmd,dbins['Cops_IP'],dbins['port'],dbins['user'],dbins['password'],dbins['cpos_file'])        
    print(mysqldump_cmd02)
    try:
        mysqldump_cmd02 = runCmd(mysqldump_cmd02)
    except Exception as e:
        print(str(e))

    if mysqldump_cmd02[1] == 0:
        print(bussiness02 + " sucessed")
    else:
        print(bussiness02 + " failed")

    # business03
    mysqldump_cmd03 = ('%s -h %s -P%d -u %s -p%s -A --single-transaction | gzip > %s ') % (mysql_dump_cmd,dbins['ywzt_IP'],dbins['port'],dbins['user'],dbins['password'],dbins['ywzt_file'])
    print(mysqldump_cmd03)
    try:
        mysqldump_cmd03 = runCmd(mysqldump_cmd03)
    except Exception as e:
        print(str(e))
    

    # business04
    mysqldump_cmd04 = ('%s -h %s -P%d -u %s -p%s -A --single-transaction | gzip > %s ') % (mysql_dump_cmd,dbins['yxztcrm_IP'],dbins['port'],dbins['user'],dbins['password'],dbins['yxztcrm_file'])
    print(mysqldump_cmd04)
    try:
        mysqldump_cmd04 = runCmd(mysqldump_cmd04)
    except Exception as e:
        print(str(e))

    # business05
    mysqldump_cmd05 = ('%s -h %s -P%d -u %s -p%s -A --single-transaction | gzip > %s ') % (mysql_dump_cmd,dbins['ywzt_dd_IP'],dbins['port'],dbins['user'],dbins['password'],dbins['ywzt_dd_file'])
    print(mysqldump_cmd05)
    try:
        mysqldump_cmd05 = runCmd(mysqldump_cmd05)
    except Exception as e:
        print(str(e))


    # business06
    mysqldump_cmd06 = ('%s -h %s -P%d -u %s -p%s -A --single-transaction | gzip > %s ') % (mysql_dump_cmd,dbins['smzq_IP'],dbins['port'],dbins['user'],dbins['password'],dbins['smzq_file'])
    print(mysqldump_cmd06)
    try:
        mysqldump_cmd06 = runCmd(mysqldump_cmd06)
    except Exception as e:
        print(str(e))


#    print(list(dbins)[0]['ip'])

# coscmd upload /data/mysql/MSY-生命周期-Prod_2024-11-26.sql.gz  mysql-2024-11-26/
def push_mysql_to_bucket():
#    dbins = init_dbins_info()
#    dbins = dbins.values()

    coscmd_cmd01 = ('%s upload %s %s') % (coscmd_cmd, yxzt_file, bucket)
    print(coscmd_cmd01)
    try:
        coscmd_cmd01 = runCmd(coscmd_cmd01)
    except Exception as e:
        print(str(e))

    coscmd_cmd02 = ('%s upload %s %s') % (coscmd_cmd, cpos_file, bucket)
    print(coscmd_cmd02)
    try:
        coscmd_cmd02 = runCmd(coscmd_cmd02)
    except Exception as e:
        print(str(e))

    coscmd_cmd03 = ('%s upload %s %s') % (coscmd_cmd, ywzt_file, bucket)
    print(coscmd_cmd03)
    try:
        coscmd_cmd03 = runCmd(coscmd_cmd03)
    except Exception as e:
        print(str(e))

    coscmd_cmd04 = ('%s upload %s %s') % (coscmd_cmd, yxztcrm_file, bucket)
    print(coscmd_cmd04)
    try:
        coscmd_cmd04 = runCmd(coscmd_cmd04)
    except Exception as e:
        print(str(e))

    coscmd_cmd05 = ('%s upload %s %s') % (coscmd_cmd, ywzt_dd_file, bucket)
    print(coscmd_cmd05)
    try:
        coscmd_cmd05 = runCmd(coscmd_cmd05)
    except Exception as e:
        print(str(e))

    coscmd_cmd06 = ('%s upload %s %s') % (coscmd_cmd, smzq_file, bucket)
    print(coscmd_cmd06)
    try:
        coscmd_cmd06 = runCmd(coscmd_cmd06)
    except Exception as e:
        print(str(e))

def remove_mysql_files():
    yxzt_file_one_day_ago = backup_dir + bussiness + '_' + one_datetime + '.sql.gz' 
    cpos_file_one_day_ago = backup_dir + bussiness02 + '_' + one_datetime + '.sql.gz'
    ywzt_file_one_day_ago = backup_dir + bussiness03 + '_' + one_datetime + '.sql.gz'
    yxztcrm_file_one_day_ago = backup_dir + bussiness04 + '_' + one_datetime + '.sql.gz'
    ywzt_dd_file_one_day_ago = backup_dir + bussiness05 + '_' + one_datetime + '.sql.gz'
    smzq_file_one_day_ago = backup_dir + bussiness06 + '_' + one_datetime + '.sql.gz'

    if os.path.isfile(yxzt_file_one_day_ago):
        os.remove(yxzt_file_one_day_ago)

    if os.path.isfile(cpos_file_one_day_ago):
        os.remove(cpos_file_one_day_ago)

    if os.path.isfile(ywzt_file_one_day_ago):
        os.remove(ywzt_file_one_day_ago)

    if os.path.isfile(yxztcrm_file_one_day_ago):
        os.remove(yxztcrm_file_one_day_ago)

    if os.path.isfile(ywzt_dd_file_one_day_ago):
        os.remove(ywzt_dd_file_one_day_ago)

    if os.path.isfile(smzq_file_one_day_ago):
        os.remove(smzq_file_one_day_ago)


if __name__ == '__main__':
    dump_mysql_data()
    push_mysql_to_bucket()
    remove_mysql_files()
