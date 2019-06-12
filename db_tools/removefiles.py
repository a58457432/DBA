#!/bin/env /usr/local/bin/python
#coding=utf-8

import os
import datetime
import time
import shutil

pg_backup = '/data/pg/backup/'
my_backup = '/data/mysql/backup/'

def removefiles(file_path):
    f = list(os.listdir(file_path))

    for i in range(len(f)):
        fpath = file_path + f[i]
        filedate = os.path.getmtime(file_path + f[i])
        time1 = datetime.datetime.fromtimestamp(filedate).strftime('%Y-%m-%d')
        date1 = time.time()
        num_day = (date1-filedate)/60/60/24


        if num_day >=1:
            try:
                if os.path.isfile(fpath):

                    os.remove(file_path + f[i])
                    print (u"已删除: %s : %s " % (time1,f[i]))
                
                elif os.path.isdir(fpath):                                 
                    shutil.rmtree(fpath)
#                    os.removedirs(fpath)                  
                    print (u"已删除文件夹: %s : %s " % (time1,f[i]))      
                else:
                             
                    os.remove(fpath)

                           
            except Exception as e:
                print(e)
        else:
            print ("no expire day file")




removefiles(pg_backup)
removefiles(my_backup)
