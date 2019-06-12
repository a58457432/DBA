#!/bin/env /usr/local/bin/python
#coding=utf-8


import os
import sys

sys.path.append('/usr/local/webserver/scripts/mydeal.py')

import mydeal
dbconfig['charset'] = 'utf8'

def pki_ddl(sql):
    db = mydeal.MySQL(dbconfig)
    ddl_sql = sql
    db.insert(ddl_sql)
    result = db.fetchAllRows()

    print result
    db.close()
    return result



def main():
    pki_ddl("alter table pkilogs add index idx_CreateTime_PKI_ID_IP(CreateTime,PKI_ID,IP);") 

if __name__ == '__main__':             
    main() 
