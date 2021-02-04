#!/usr/bin/env python
## coding=utf-8
# Creator: shenjinhong
# UpdateTime:2021.2.1

import sys
import os
import subprocess
import pymssql

# client

ip = '172.21.117.2'
user = 'db_reader'
passwd = 'vHmWDCzi6iXCW3jC'
database = 'master'
insname = 'sqlserver_uat'

# zabbix server
zb_sender = '/usr/bin/zabbix_sender'
zb_server = '10.21.3.60'
zb_server_port = 10051

def runCmd(cmd):
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    except:
        return None, p.returncode
    else:
        output, err = p.communicate()
        return output, p.returncode

def mssql_con(sql):
    connect = pymssql.connect(ip, user, passwd, database)
    if connect:
        print("connect success!")
    else:
        print("connect fail!")

    cursor = connect.cursor()
    cursor.execute(sql)
    res = cursor.fetchall()
    connect.commit()
    cursor.close()
    connect.close()

    return res

def create_map():
    dbinfo = {} 

    sql1 = "select 1* 10";
    res1 = mssql_con(sql1)
    if int(res1[0][0]) == 10:
        dbinfo['alive'] = 1
    else:
        dbinfo['alive'] = 0

    sql2 = "select cntr_value from sys.dm_os_performance_counters where counter_name = 'User Connections';"
    res2 = mssql_con(sql2)
    dbinfo['connections'] = int(res2[0][0])

    sql3 = "select cntr_value from sys.dm_os_performance_counters where counter_name = 'Transactions/sec' and instance_name = '_Total';"
    res3 = mssql_con(sql3)
    res32 = mssql_con(sql3)
    dbinfo['transactions'] = int(res32[0][0] - res3[0][0])

    sql4 = "select cntr_value from sys.dm_os_performance_counters where counter_name = 'Lock Waits/sec'and instance_name = '_Total';"
    res4 = mssql_con(sql4)
    res42 = mssql_con(sql4)
    dbinfo['lock_wait_num'] = int(res42[0][0] - res4[0][0])

    sql5 = '''SELECT (a.cntr_value * 1.0 / b.cntr_value) * 100.0 as BufferCacheHitRatio
    FROM sys.dm_os_performance_counters a
    JOIN (SELECT cntr_value, OBJECT_NAME
    FROM sys.dm_os_performance_counters
    WHERE counter_name = 'Buffer cache hit ratio base'
    AND OBJECT_NAME = 'SQLServer:Buffer Manager') b ON a.OBJECT_NAME = b.OBJECT_NAME
    WHERE a.counter_name = 'Buffer cache hit ratio'
    AND a.OBJECT_NAME = 'SQLServer:Buffer Manager';'''

    res5 = mssql_con(sql5)
    dbinfo['cache_hit'] = int(res5[0][0])
#    print(dbinfo)
    return dbinfo

def push_zabbix_items():
    dbinfo = create_map()
    for (key, value) in dbinfo.items():
        zb_sender_cmd = ('%s -z %s -p %d -s %s -k %s -o %s') % (zb_sender, zb_server, zb_server_port, insname, str(key), str(value))
        print(zb_sender_cmd)

        try:
            sender_cmd = runCmd(zb_sender_cmd)
        except Exception, e:
            print str(e)

        if sender_cmd[1] == 0:
            print str(key) + "    sucessed"
        else:
            print str(key) + "     failed"


def main():
#    create_map()
    push_zabbix_items()

if __name__ == '__main__':
    main()
