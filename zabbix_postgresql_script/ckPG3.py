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
DBSTATUS_FILE = "/tmp/DBins.Info"  # db状态输出文件的路径
dt = datetime.now()
DATETIME = dt.strftime('%Y-%m-%d %H:%M:%S')


#  PG info
sock = ''
port = 5433
IP = '172.25.20.14'
user = 'vmi_monitor'
password = 'vmi_mon!@##lgv11a'
dbschema = 'postgres'
pg_home = '/data/pg14data'

# keepalived 
VIP = '172.25.20.107'

#etcd
etcd_port = 2379

#patroni
patroni_port = 8008

#other
vping = '/usr/bin/ping'
vecho = '/usr/bin/echo'
vtelnet = '/usr/bin/telnet'
vdf = '/usr/bin/df'
vps = '/usr/bin/ps'
vetcdctl = '/usr/bin/etcdctl'
vcurl = '/usr/bin/curl'


# zabbix server
zb_sender = '/usr/bin/zabbix_sender'
zb_server = '172.25.10.244'
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
    dbinfo['db_alive'] = ''  # dbserver 状态数值(是否1), 1 = alive , 0 = fail
    dbinfo['port'] = port
    dbinfo['ip'] = IP
    dbinfo['user'] = user
    dbinfo['password'] = password
    dbinfo['dbschema'] = dbschema
    dbinfo['insname'] = insname
    dbinfo['vip'] = VIP

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
            except BaseException as e:
                print(str(e))
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
                    db['global_status']['UPTIME'] = str(list(row)[0]).split(',')[0].replace(' ','')
                except ValueError:
                    pass

            self.cur.close()
            self.conn.close()

    def ck_vip(self):
        # ping -c 1 127.0.0.1 &> /dev/null && echo 1 || echo 0
        ck_vip_cmd = ('%s -c 5 %s &> /dev/null && echo 1 || echo 0') % (vping, VIP)
        try:
            check_vip = runCmd(ck_vip_cmd)
        except Exception as e:
            print(str(e))

        if check_vip[1] == 0:
            for db in self.dbins.values():
                if int(check_vip[0]) == 1:
                    db['vip_status'] = 1
                else:
                    db['vip_status'] = 0
    
    def ck_port(self):
        # echo -e "\n" | telnet 192.168.71.128 5331 2>/dev/null | grep Connected | wc -l
        ck_port_cmd = ('%s -e "\\n" | %s %s %s 2>/dev/null | grep Connected | wc -l') % (vecho, vtelnet, IP, port)
        try:
            db_check_port = runCmd(ck_port_cmd)
        except Exception as e:
            print(str(e))

        if db_check_port[1] == 0:
            for db in self.dbins.values():
                if int(db_check_port[0]) == 1:
                    db['db_port'] = 1
                else:
                    db['db_port'] = 0
                
        #echo -e "\n" | telnet ip 2379 2>/dev/null | grep Connected | wc -l
        ck_etcd_port_cmd = ('%s -e "\\n" | %s %s %d 2>/dev/null | grep Connected | wc -l') % (vecho, vtelnet, IP, etcd_port)
        try:
            etcd_ck_port = runCmd(ck_etcd_port_cmd)
        except Exception as e:
            print(str(e))

        if etcd_ck_port[1] == 0:
            for db in self.dbins.values():
                if int(etcd_ck_port[0]) == 1:
                    db['etcd_port'] = 1
                else:
                    db['etcd_port'] = 0

        #echo -e "\n" | telnet ip 8008 2>/dev/null |grep Connected | wc -l
        ck_patroni_port_cmd = ('%s -e "\\n" | %s %s %d 2>/dev/null | grep Connected | wc -l') % (vecho, vtelnet, IP, patroni_port)
        try:
            patroni_ck_port = runCmd(ck_patroni_port_cmd)
        except Exception as e:
            print(str(e))

        if patroni_ck_port[1] == 0:
            for db in self.dbins.values():
                if int(patroni_ck_port[0]) == 1:
                    db['patroni_port'] = 1
                else:
                    db['patroni_port'] = 0

    def ck_tbl(self):
        # df -h /data/postgresql/data/ | awk -F " " '{print $5}' | grep -vi Use
        ck_tbl_cmd = ('%s -h %s | awk -F " " \'{print $5}\' | grep -vi Use') % (vdf, pg_home)
        try:
            ck_tbl_data = runCmd(ck_tbl_cmd)
        except Exception as e:
            print(str(e))

        if ck_tbl_data[1] == 0:
            for db in self.dbins.values():
                db['pg_data'] = int(str(ck_tbl_data[0].decode().split('%')[0]))

    def ck_process(self):
        # ps -ef |grep postgres: | wc -l
        ck_ps_cmd = ('%s -ef |grep postgres:|grep -iv grep | wc -l') % (vps)
        try:
            ck_pg_ps = runCmd(ck_ps_cmd)
        except Exception as e:
            print(str(e))

        if ck_pg_ps[1] == 0:
            for db in self.dbins.values():
                if int(ck_pg_ps[0]) >= 5:
                    db['db_process'] = 1
                else:
                    db['db_process'] = 0
        #ps -ef |grep keepalived |grep -vi grep | wc -l
        ck_keepalived_ps_cmd = ('%s -ef |grep keepalived | grep -iv grep | wc -l') % (vps)
        try:
            ck_keepalived_ps = runCmd(ck_keepalived_ps_cmd)
        except Exception as e:
            print(str(e))

        if ck_keepalived_ps[1] == 0:
            for db in self.dbins.values():
                if int(ck_keepalived_ps[0]) == 3:
                    db['keepalived_process'] = 1
                else:
                    db['keepalived_process'] = 0
        #ps -ef |grep etcd |grep -vi grep  | wc -l
        ck_etcd_ps_cmd = ('%s -ef |grep etcd |grep -vi grep | wc -l') % (vps)
        try:
            ck_etcd_ps = runCmd(ck_etcd_ps_cmd)
        except Exception as e:
            print(str(e))

        if ck_etcd_ps[1] == 0:
            for db in self.dbins.values():
                if int(ck_etcd_ps[0]) == 1:
                    db['etcd_process'] = 1
                else:
                    db['etcd_process'] = 0
        #ps -ef |grep patroni |grep -iv grep | wc -l
        ck_patroni_ps_cmd = ('%s -ef | grep patroni | grep -iv grep | wc -l') % (vps)
        try:
            ck_patroni_ps = runCmd(ck_patroni_ps_cmd)
        except Exception as e:
            print(str(e))

        if ck_patroni_ps[1] == 0:
            for db in self.dbins.values():
                if int(ck_patroni_ps[0]) >= 1:
                    db['patroni_process'] = 1
                else:
                    db['patroni_process'] = 0

    def ck_etcd_count(self):
        # etcdctl member list |wc -l
        ck_etcd_cmd = ('%s member list | wc -l') % (vetcdctl) 
        try:
            ck_etcd_cnt = runCmd(ck_etcd_cmd)
        except Exception as e:
            print(str(e))

        if ck_etcd_cnt[1] == 0:
            for db in self.dbins.values():
                if int(ck_etcd_cnt[0]) == 3:
                    db['etcd_member'] = 1
                else:
                    db['etcd_member'] = 0

    def ck_patroni_health(self):
    #/usr/bin/curl -s http://172.25.20.15:8008/leader -v 2>&1|grep '200 OK' > /dev/null;echo $?
    # 20.14, 20.15, 20.29
        ck_patroni_health_cmd = ('%s -s -s http://172.25.20.14:8008/leader -v 2>&1|grep \'200 OK\' > /dev/null;echo $?') % (vcurl)
        try:
            ck_patroni_num = runCmd(ck_patroni_health_cmd)
        except Exception as e:
            print(str(e))
        
        ck_patroni_health_cmd2 = ('%s -s -s http://172.25.20.15:8008/leader -v 2>&1|grep \'200 OK\' > /dev/null;echo $?') % (vcurl)
        try:
            ck_patroni_num2 = runCmd(ck_patroni_health_cmd2)
        except Exception as e:
            print(str(e))

        ck_patroni_health_cmd3 = ('%s -s -s http://172.25.20.29:8008/leader -v 2>&1 | grep \'200 OK\' > /dev/null;echo $?') % (vcurl)
        try:
            ck_patroni_num3 = runCmd(ck_patroni_health_cmd3)
        except Exception as e:
            print(str(e))

        if ck_patroni_num[1] == 0 and ck_patroni_num2[1] == 0 and ck_patroni_num3[1] ==0:
            s = int(ck_patroni_num[0]) + int(ck_patroni_num2[0]) + int(ck_patroni_num3[0])
            for db in self.dbins.values():
                if s == 2:
                    db['patroni_health'] = 1
                else:
                    db['patroni_health'] = 0

    def write_result_file(self):
        """将计算结果写入db状态输出文件.
        """
        with open(DBSTATUS_FILE, 'w') as f:
            f.write("#" + str(DATETIME) + "\n\n")
            f.write("start_utime =" + str(int(time.mktime(time.strptime(DATETIME, '%Y-%m-%d %H:%M:%S')))) + "\n\n")
            f.write("# " + "-"*20 + ' ' + 'global_status' + ' ' + "-"*20 + "\n")
            for (key, value) in self.dbins.items():
                for (k, v) in value['global_status'].items():
#                    print (str(k) + '=' + str(v))
                    f.write(str(k) + '=' + str(v) + "\n")
                for db in value.keys():
#                    print(str(db) + '=' + str(value[db]))
                    f.write(str(db) + '=' + str(value[db]) + "\n")

    def push_zabbix_items(self):
    #  zabbix_sender -z 192.167.123.5 -p 10051 -s "MySQL_mysql2" -k "QPS" -o 1000
        dbs = self.dbins.values()
        dbs = list(dbs)
        print(str(DATETIME) + " * "*20 + " push item " + " * "*20)
        for (key, value) in dbs[0]['global_status'].items():
            zb_sender_cmd = ('%s -z %s -p %d -s %s -k %s -o %s') % (zb_sender, zb_server, zb_server_port, insname, str(key), str(value))
            print(zb_sender_cmd)
            
            try:
                sender_cmd = runCmd(zb_sender_cmd)
            except Exception as e:
                print(str(e))
            if sender_cmd[1] == 0:
                print(str(key) + "    sucessed")
            else:
                print(str(key) + "     failed")

        zb_sender_cmd2 = ('%s -z %s -p %d -s %s -k "DB_ALIVE" -o %s') % (zb_sender, zb_server, zb_server_port, insname, dbs[0]['db_alive'])        
        print(zb_sender_cmd2)
        sender_cmd2 = runCmd(zb_sender_cmd2)
        if sender_cmd2[1] == 0:
            print("db_alive" + "    sucessed")
        else:
            print("db_alive" + "     failed")

        zb_sender_cmd3 = ('%s -z %s -p %d -s %s -k "VIP_STATUS" -o %s') % (zb_sender, zb_server, zb_server_port, insname, dbs[0]['vip_status'])
        print(zb_sender_cmd3)
        sender_cmd3 = runCmd(zb_sender_cmd3)
        if sender_cmd3[1] == 0:
            print("vip_status" + "  sucessed")
        else:
            print("vip_status" + "  failed")

        zb_sender_cmd4 = ('%s -z %s -p %d -s %s -k "DB_PORT" -o %s') % (zb_sender, zb_server, zb_server_port, insname, dbs[0]['db_port'])
        print(zb_sender_cmd4)
        sender_cmd4 = runCmd(zb_sender_cmd4)
        if sender_cmd4[1] == 0:
            print("db_port" + "  sucessed")
        else:
            print("db_port" + "  failed")

        zb_sender_cmd5 = ('%s -z %s -p %d -s %s -k "ETCD_PORT" -o %s') % (zb_sender, zb_server, zb_server_port, insname, dbs[0]['etcd_port'])
        print(zb_sender_cmd5)
        sender_cmd5 = runCmd(zb_sender_cmd5)
        if sender_cmd5[1] == 0:
            print("etcd_port" + "  sucessed")
        else:
            print("etcd_port" + "  failed")

        zb_sender_cmd6 = ('%s -z %s -p %d -s %s -k "PATRONI_PORT" -o %s') % (zb_sender, zb_server, zb_server_port, insname, dbs[0]['patroni_port'])
        print(zb_sender_cmd6)
        sender_cmd6 = runCmd(zb_sender_cmd6)
        if sender_cmd6[1] == 0:
            print("patroni_port" + "  sucessed")
        else:
            print("patroni_port" + "  failed")

        zb_sender_cmd7 = ('%s -z %s -p %d -s %s -k "PG_DATA" -o %s') % (zb_sender, zb_server, zb_server_port, insname, dbs[0]['pg_data'])
        print(zb_sender_cmd7)
        sender_cmd7 = runCmd(zb_sender_cmd7)
        if sender_cmd7[1] == 0:
            print("pg_data" + "  sucessed")
        else:
            print("pg_data" + "  failed")

        zb_sender_cmd8 = ('%s -z %s -p %d -s %s -k "DB_PROCESS" -o %s') % (zb_sender, zb_server, zb_server_port, insname, dbs[0]['db_process'])
        print(zb_sender_cmd8)
        sender_cmd8 = runCmd(zb_sender_cmd8)
        if sender_cmd8[1] == 0:
            print("db_process" + "  sucessed")
        else:
            print("db_process" + "  failed")

        zb_sender_cmd9 = ('%s -z %s -p %d -s %s -k "KEEPALIVED_PROCESS" -o %s') % (zb_sender, zb_server, zb_server_port, insname, dbs[0]['keepalived_process'])
        print(zb_sender_cmd9)
        sender_cmd9 = runCmd(zb_sender_cmd9)
        if sender_cmd9[1] == 0:
            print("keepalived_process" + "  sucessed")
        else:
            print("keepalived_process" + "  failed")

        zb_sender_cmd10 = ('%s -z %s -p %d -s %s -k "ETCD_PROCESS" -o %s') % (zb_sender, zb_server, zb_server_port, insname, dbs[0]['etcd_process'])
        print(zb_sender_cmd10)
        sender_cmd10 = runCmd(zb_sender_cmd10)
        if sender_cmd10[1] == 0:
            print("etcd_process" + "  sucessed")
        else:
            print("etcd_process" + "  failed")

        zb_sender_cmd11 = ('%s -z %s -p %d -s %s -k "PATRONI_PROCESS" -o %s') % (zb_sender, zb_server, zb_server_port, insname, dbs[0]['patroni_process'])
        print(zb_sender_cmd11)
        sender_cmd11 = runCmd(zb_sender_cmd11)
        if sender_cmd11[1] == 0:
            print("patroni_process" + "  sucessed")
        else:
            print("patroni_process" + "  failed")

        zb_sender_cmd12 = ('%s -z %s -p %d -s %s -k "ETCD_MEMBER" -o %s') % (zb_sender, zb_server, zb_server_port, insname, dbs[0]['etcd_member'])
        print(zb_sender_cmd12)
        sender_cmd12 = runCmd(zb_sender_cmd12)
        if sender_cmd12[1] == 0:
            print("etcd_member" + "  sucessed")
        else:
            print("etcd_member" + "  failed")

        zb_sender_cmd13 = ('%s -z %s -p %d -s %s -k "PATRONI_HEALTH" -o %s') % (zb_sender, zb_server, zb_server_port, insname, dbs[0]['patroni_health'])
        print(zb_sender_cmd13)
        sender_cmd13 = runCmd(zb_sender_cmd13)
        if sender_cmd13[1] == 0:
            print("patroni_health" + "  sucessed")
        else:
            print("patroni_health" + "  failed")


if __name__ == '__main__':
    db = DBStatus()
    db.get_status_var()
    db.ck_vip()
    db.ck_port()
    db.ck_tbl()
    db.ck_process()
    db.ck_etcd_count()
    db.ck_patroni_health()
#    print(db.dbins)
    db.write_result_file()
    db.push_zabbix_items()
