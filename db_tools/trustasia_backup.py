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

def upload_filefolder(filename):
    try:
        s3_up = ('%s s3 sync %s/%s/ s3://%s/%s/') % (s3_cmd, my_backup, filename, s3_mybackup, filename)
        print s3_up
        s3_folder = runCmd(s3_up) 
        print s3_folder   
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
            pflag = self.host + " backup sucessed"
        else:
            pflag = self.host + " backup fail"
        
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
        
        mydumper_cmd = ('%s -h %s  -P %s -u %s -p %s -G -E -R -t 3 -c  -B %s -o %s/%s') % (my_dumper_cmd,self.host,self.port,self.user,self.passwd,self.database,my_backup,self.bakfile) 

        print mydumper_cmd
        try:
            mdump = runCmd(mydumper_cmd)
            print mdump
        except Exception,e:
            print str(e)

        if mdump[1] == 0:
            mflag =   " backup sucessed"
        else:
            mflag =   " backup fail"

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


## trustasia
    bakfilen = 'mybackup_' + dbins['database'][0] + '_' + td 
    mpki = bak(dbins['host'][0],dbins['port'][0],dbins['user'][0],dbins['passwd'][0],dbins['database'][0],bakfilen) 
    start = time.time()
    mpki.get_mybak()
    stop = time.time()
    print 'mpki :'
    print str(stop-start) + "秒"
    upload_filefolder(bakfilen) 
    
    print dblog
    sql = ("insert into bak_info(host,port,db,bak_create_at,bak_flag) values('%s' ,'%s' ,'%s' ,'%s' ,'%s');") % (dblog[0],dblog[1],dblog[2],dblog[3],dblog[4])
    mydeal.insrt_bak_infor(sql) 
    

def main():
    cal() 

if __name__ == '__main__':             
    main() 
