#!/bin/env /usr/bin/python
# -*- coding: utf-8 -*-
#
#    (C) 21vianet Inc.
#
#    Last update: sjh 2020-02-28

""" Run CMD or SCP In Batch Mode

You can choose project type, area  to run command or upload file.
Output info will print to script.info.

"""

__authors__ = [
    '"sjh"',
    ]

import os
import sys
import MySQLdb

sys.path.append('/usr/local/webserver/DBA/mysql_script/mydeal.py')
dbconfig = {}
dbconfig['host'] = '192.168.31.156'
dbconfig['port'] = 3307
dbconfig['user'] = 'root'
dbconfig['passwd'] = '123456'
dbconfig['db'] = 'information_schema'
dbconfig['charset'] = 'utf8'

import mydeal
dbconfig['charset'] = 'utf8'

dbins = {}

def pki_ddl(sql):
    db = mydeal.MySQL(dbconfig)
    ddl_sql = sql
    db.insert(ddl_sql)
    result = db.fetchAllRows()

    db.close()
    return result



def get_db_info():
    table_schema = pki_ddl('''select distinct table_schema from information_schema.tables where table_schema not in ('information_schema','mysql','performance_schema','sys');''')
    for i in table_schema:
        tbl_schema = i[0].encode('utf8')
        dbins[tbl_schema] = {}
        get_table_name = ('''select table_name from information_schema.tables where table_schema not in ('information_schema','mysql','performance_schema','sys') and table_schema = '%s';''') % (i[0].encode('utf8'))
        table_name = pki_ddl(get_table_name)

        for n in table_name:
            tbl_name = n[0].encode('utf8')
            tbl_sch_name = tbl_schema + '.' + tbl_name
            tbl_cnt_sql = ('select count(*) from %s;') % (tbl_sch_name)
            tbl_cnt = pki_ddl(tbl_cnt_sql)
            dbins[tbl_schema][tbl_name] = int(tbl_cnt[0][0])
    return dbins

def calc_db_cnt():
    dbins = get_db_info()
    for i in dbins.keys():
        print str(i) + '=' + str(sum(dbins[i].values()))

def calc_db_pro_fun():
    sql = 'select db,type,count(*) from mysql.proc group by type,db;'
    pro_fun = pki_ddl(sql)
    for i in pro_fun:
        print i


if __name__ == '__main__':             
    calc_db_cnt() 
    calc_db_pro_fun()
