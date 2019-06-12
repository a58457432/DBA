#!/bin/env /usr/local/bin/python
#coding=utf-8
#Creator: Jeffery.shen
#UpdateTime: 2019-01-11 11:00:05

from ftplib import FTP
import time
import tarfile
import os
import glob
import datetime


def ftpconnect(host, username, password):
    ftp = FTP()
    ftp.connect(host,5021)
    ftp.login(username, password)
    return ftp


def downloadfile(ftp, remotepath, localpath):
    bufsize = 1024
    fp = open(localpath, 'wb')
    ftp.retrbinary('RETR ' + remotepath, fp.write, bufsize)
    ftp.set_debuglevel(0)
    fp.close()


def uploadfile(ftp, remotepath, localpath):
    bufsize = 1024
    fp = open(localpath, 'rb')
    ftp.storbinary('STOR ' + remotepath, fp, bufsize)
    ftp.set_debuglevel(0)
    fp.close()

def get_time():
    try:
        t_day = datetime.datetime.now()
        td = t_day.strftime('%Y%m%d')
    
    except BaseException,e:
        print e

    return td


def get_filesize(filepath):
    filepath = unicode(filepath, 'utf8')
    fsize = os.path.getsize(filepath)
    fsize = fsize/float(1024*1024*1024)
    return round(fsize,1)

def cal():
    ftp = ftpconnect("dsm.xxx.cn","xxx","xxx")
    td = get_time()
    up_file =  glob.glob('/data/pg/backup/*result*.sql') 
    for i in up_file:
        str = os.path.basename(i)
        if str.find(td) != -1:
            print str    
            fs = get_filesize(i)
            print fs
            if fs < 16:
                print "backup file %s  is not ok !" % str

            else:
                print "backup file %s is ok" % str
                uploadfile(ftp, "/home/check_result/" + str, i)
                
    ftp.quit()


if __name__ == "__main__":
    cal()
#    downloadfile(ftp, "/home/pgbackup_myssl_ee_20190211.sql","/opt/pgbackup_myssl_ee_20190211.sql")
#    uploadfile(ftp, "/home/pgbackup_check_result_20190211.sql", "/data/pg/backup/pgbackup_check_result_20190211.sql")
