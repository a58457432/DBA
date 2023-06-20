#!/usr/local/python3/bin/python3
# -*- coding:utf-8 -*-

import sys
sys.path.append('/usr/local/webserver/DBA/zabbix_alert')

import mydeal
from data_deal import session_db,select_tbl_id
from queue import Queue

# 根据主机,alerttype,apptype 获取用户名
def get_alert_user(hostname,alerttype,apptype):
#SELECT
#    a. NAME
#FROM
#    USER a,
#    Alert_List_Table b,
#    HostName c,
#    AppType d,
#    AlertType e
#WHERE
#    a.id = b.user_id
#AND c.id = b.hostname_id
#AND d.id = b.apptype_id
#AND e.id = b.alerttype_id
#AND c.`name` = 'WTCCN-NHDC-HV01'
#AND d.`name` = 'ping'
#AND e.`name` = 'wechat';
#
    q = []
    mydb = session_db()
    sql = ("""select  
                    a.name 
              from 
                    User a, 
                    Alert_List_Table b,
                    HostName c, 
                    AppType d, 
                    AlertType e
              where a.id = b.user_id
              AND c.id = b.hostname_id
              AND d.id = b.apptype_id
              AND e.id = b.alerttype_id
              AND c.`name` = '%s'
              AND d.`name` = '%s'
              AND e.`name` = '%s';
            """ % (hostname, apptype, alerttype)) 
    result = mydb.executeSql(sql)
    for i in result:
        for j in i:
            q.append(j)
    if q: return q

# 获取email
def get_emai():
    pass

if __name__ == "__main__":
    result = get_alert_user('WTCCN-NHDC-HV01', 'wechat', 'ping')
    print(result)
