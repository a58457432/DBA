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

import psycopg2
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
dt = datetime.now()
DATETIME = dt.strftime('%Y-%m-%d %H:%M:%S')


#  PG info
sock = ''
port = 5432
IP = '192.168.31.125'
user = 'wwg'
password = 'wwg'
dbschema = 'pgsql_zabbix'


# zabbix server
zb_sender = '/usr/bin/zabbix_sender'
zb_server = '192.168.31.156'
zb_server_port = 10051

# zabbix agent
insname = 'PG_' + socket.gethostname()

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
def own_initialize():
    """非公共初始化部分.

    """
    # 将db状态输出文件置空.
    with open(DBSTATUS_FILE, 'w') as f:
        f.write("")
        sys.exit(1)



# ----------------------------------------------------------------------------------------
# init dbs dict()
# ----------------------------------------------------------------------------------------
def init_dbins_info():
    dbins = {}  # db实例字典
    dbinfo = {}  # db信息字典
    dbinfo['global_status'] = {}  # db global status 字典
    dbinfo['processlist'] = {}
    dbinfo['db_alive'] = ''  # dbserver 状态数值(是否1), 1 = alive , 0 = fail
    dbinfo['port'] = port
    dbinfo['ip'] = IP
    dbinfo['user'] = user
    dbinfo['password'] = password
    dbinfo['dbschema'] = dbschema
    dbinfo['insname'] = insname

    dbins[insname] = copy.deepcopy(dbinfo)
    return dbins

# ----------------------------------------------------------------------------------------
# Class for DBStatus.
# ----------------------------------------------------------------------------------------
class DBStatus(object):
    def __init__(self):
        self.dbins = init_dbins_info()
        self.global_status = ('ALL_SESSION','ACTIVE_SESSION','NEW_5_SESSION','UPTIME')
        
    def get_status_var(self):
        for db in self.dbins.values():
            try:
                self.conn = psycopg2.connect(dbname=db['dbschema'], user=db['user'], password=db['password'],host=db['ip'],port=db['port'])
            except BaseException, e:
                print str(e)
                continue
            self.cur = self.conn.cursor()
            sql = "select 10*10;"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            if rows[0][0] != 100:
                db['db_alive'] = 0
            else:
                db['db_alive'] = 1
            
            self.cur.close()
            
            #获取PG状态
            self.cur = self.conn.cursor()
            sql = "select count(*) from pg_stat_activity ;"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            for row in rows:
                try:
                    db['global_status']['ALL_SESSION'] = float(list(row)[0])
                except ValueError:
                    pass

            self.cur.close()

            self.cur = self.conn.cursor()
            sql = "select count(*) from pg_stat_activity where state='active'; "
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            for row in rows:
                try:
                    db['global_status']['ACTIVE_SESSION'] = float(list(row)[0])
                except ValueError:
                    pass

            self.cur.close()

            self.cur = self.conn.cursor()
            sql = "select count(*) from pg_stat_activity where now()-backend_start > '5 second'; "
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            for row in rows:
                try:
                    db['global_status']['NEW_5_SESSION'] = float(list(row)[0])
                except ValueError:
                    pass

            self.cur.close()

            self.cur = self.conn.cursor()
            sql = "select date_trunc('second',current_timestamp - pg_postmaster_start_time()) as uptime;"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            for row in rows:
                try:
                    db['global_status']['UPTIME'] = str(list(row)[0])
                except ValueError:
                    pass

            self.cur.close()
            self.conn.close()

    def write_result_file(self):
        """将计算结果写入db状态输出文件.
        """
        with open(DBSTATUS_FILE, 'w') as f:
            f.write("#" + str(DATETIME) + "\n\n")
            f.write("start_utime =" + str(int(time.mktime(time.strptime(DATETIME, '%Y-%m-%d %H:%M:%S')))) + "\n\n")
            dbs = self.dbins.values()
            dbs.sort()
            f.write("# " + "-"*20 + ' ' + 'global_status' + ' ' + "-"*20 + "\n")
            for (key, value) in dbs[0]['global_status'].items():
                f.write(str(key) + '=' + str(value) + "\n")
            f.write('db_alive' + '=' + str(dbs[0]['db_alive']) + "\n")

    def push_zabbix_items(self):
    #  zabbix_sender -z 192.168.31.156 -p 10051 -s "MySQL_mysql2" -k "QPS" -o 1000
        dbs = self.dbins.values()
        dbs.sort()
        print str(DATETIME) + " * "*20 + " push item " + " * "*20
        for (key, value) in dbs[0]['global_status'].items():
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

        zb_sender_cmd2 = ('%s -z %s -p %d -s %s -k "DB_ALIVE" -o %s') % (zb_sender, zb_server, zb_server_port, insname, dbs[0]['db_alive'])        
        print zb_sender_cmd2
        sender_cmd2 = runCmd(zb_sender_cmd2)
        if sender_cmd2[1] == 0:
            print "db_alive" + "    sucessed"
        else:
            print "db_alive" + "     failed"



if __name__ == '__main__':
    db = DBStatus()
    db.get_status_var()
    db.write_result_file()
    db.push_zabbix_items()
