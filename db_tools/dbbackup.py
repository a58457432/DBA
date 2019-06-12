#!/bin/env /usr/local/bin/python
#coding=utf-8
#Creator: Jeffery.shen
#UpdateTime: 2019-01-10 09:30:05


import datetime
#from datetime import datetime
import re
import copy
from os import path
import sys
import time
import socket
import os
try:
    import json
except:
    import simplejson as json
import subprocess
import calendar 
import boto3

sys.path.append('/usr/local/webserver/scripts/mydeal.py')

import mydeal

##ftp


def runCmd(cmd):
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    except:
        return None, p.returncode
    else:
        output, err = p.communicate()
        return output, p.returncode


def get_db_config():
    dbsource = {}
    dbsource['host'] = source_host
    dbsource['port'] = source_port
    dbsource['user'] = source_user
    dbsource['passwd'] = source_passwd
    dbsource['database'] = source_database

    return dbsource
    

def get_time():
    try: 
        t_day = datetime.datetime.now()    
        td = t_day.strftime('%Y%m%d')
                                             
    except BaseException,e:
        pass

    return td

def upload_file(filename,bucket,key):
    try:
        s3 = boto3.resource('s3')
        s3.meta.client.upload_file(filename,bucket,key)
            
    except BaseException,e:
        print str(e)

# ===class bak===

class bak(object):
     

    def __init__(self,host,port,user,passwd,database,bakfile):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.database = database
        self.bakfile = bakfile

    def get_pgbak(self):
            
        pgdump_cmd = ('PGPASSWORD=%s  %s -U %s -h %s -p %s -d %s -O > %s/%s') % (self.passwd,pg_dump_cmd,self.user,self.host,self.port,self.database,pg_backup,self.bakfile)
        print pgdump_cmd

        try:
            pdump = runCmd(pgdump_cmd)
        except Exception, e:
            print str(e)

        if pdump[1] == 0:
            pflag =  " backup sucessed"
        else:
            pflag =  " backup fail"
        
        plog['host'] = self.host
        plog['port'] = self.port
        plog['database'] = self.database
        plog['dtime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        plog['flag'] = pflag

        dblog.append(plog['host'])
        dblog.append(plog['port'])
        dblog.append(plog['database'])
        dblog.append(plog['dtime'])
        dblog.append(plog['flag'])
        

    def get_mybak(self):
        
        mydump_cmd = ('%s -u %s -p%s  -h %s -P %s --single-transaction --set-gtid-purged=OFF  --quick --extended-insert -B %s  > %s/%s') % (my_dump_cmd,self.user,self.passwd,self.host,self.port,self.database,my_backup,self.bakfile) 

        print mydump_cmd
        try:
            mdump = runCmd(mydump_cmd)
        except Exception,e:
            print str(e)

        if mdump[1] ==0:
            mflag =  " backup sucessed"
        else:
            mflag =  " backup fail"

        plog['host'] = self.host
        plog['port'] = self.port
        plog['database'] = self.database
        plog['dtime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        plog['flag'] = mflag

        dblog.append(plog['host'])
        dblog.append(plog['port'])
        dblog.append(plog['database'])
        dblog.append(plog['dtime'])
        dblog.append(plog['flag'])



def cal():
    dbins = get_db_config()
    td = get_time()

## freessl
    bakfilen = 'pgbackup_' + dbins['database'][0] + '_' + td + '.sql'
    freessl = bak(dbins['host'][0],dbins['port'][0],dbins['user'][0],dbins['passwd'][0],dbins['database'][0],bakfilen)
    freessl.get_pgbak()
    filename = pg_backup + '/' + bakfilen
    upload_file(filename,s3_pgbackup,bakfilen)
    
### trustasia-mysql

    bakfilen1 = 'mybackup_' + 'trustasia-mysql' + '_' + td + '.sql'
    db = ' '.join(dbins['database'][2])
    zhuzhan = bak(dbins['host'][2],dbins['port'][1],dbins['user'][0],dbins['passwd'][0],db,bakfilen1)
    zhuzhan.get_mybak()
    filename1 = my_backup + '/' + bakfilen1
    upload_file(filename1,s3_mybackup,bakfilen1)

    
## mysslee
    bakfilen3 = 'pgbackup_' + dbins['database'][3] + '_' + td + '.sql'
    mysslee = bak(dbins['host'][3],dbins['port'][0],dbins['user'][0],dbins['passwd'][0],dbins['database'][3],bakfilen3)
    mysslee.get_pgbak()
    filename3 = pg_backup + '/' + bakfilen3
    upload_file(filename3,s3_pgbackup,bakfilen3)

## tshield
    bakfilen4 = 'pgbackup_' + dbins['database'][4] + '_' + td + '.sql'
    tshield = bak(dbins['host'][4],dbins['port'][0],dbins['user'][0],dbins['passwd'][0],dbins['database'][4],bakfilen4)
    tshield.get_pgbak()
    filename4 = pg_backup + '/' + bakfilen4
    upload_file(filename4,s3_pgbackup,bakfilen4)
    
## sslchina
    bakfilen5 = 'mybackup_' + dbins['database'][5] + '_' + td + '.sql'
    sslchina = bak(dbins['host'][5],dbins['port'][1],dbins['user'][0],dbins['passwd'][0],dbins['database'][5],bakfilen5)
    sslchina.get_mybak()
    filename5 = my_backup + '/' + bakfilen5
    upload_file(filename5,s3_mybackup,bakfilen5)


    step = 5
    lg = [dblog[i:i+step] for i in range(0,len(dblog),step)]

    for i in lg:
        sql = ("insert into bak_info(host,port,db,bak_create_at,bak_flag) values('%s' ,'%s' ,'%s' ,'%s' ,'%s');") % (i[0],i[1],i[2],i[3],i[4])
        mydeal.insrt_bak_infor(sql)

def main():
    cal() 

if __name__ == '__main__':             
    main() 
