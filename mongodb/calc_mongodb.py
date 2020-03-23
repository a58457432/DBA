#!/usr/bin/env python
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

import pymongo
from pymongo import MongoClient
import ConfigParser
from datetime import datetime
import re
import copy
from os import path
import sys
import time
import socket
import commands
import subprocess

#sys.path.append(path.join(path.realpath(path.dirname(sys.argv[0])), "lib"))

dt = datetime.now()
DATETIME = dt.strftime('%Y-%m-%d %H:%M:%S')



# hostname
insname = 'Mongodb_' + socket.gethostname()

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
# init dbs dict()
# ----------------------------------------------------------------------------------------
def init_dbins_info():
    dbins = {}  # db实例字典
    dbinfo = {}  # db信息字典
    dbinfo['mongodb'] = {}
    dbinfo['insname'] = insname

    dbins[insname] = copy.deepcopy(dbinfo)
    return dbins

#-------------------------
# conn mongodb
#-------------------------
def calc_mongodb():
    dbins = init_dbins_info()
    database_list = []
    for dbi in dbins.values():
        myclient = pymongo.MongoClient('mongodb://admin:admin@192.168.31.156:27017/')
        c = myclient.database_names()
        for i in c:
            if i in ['config','admin','local']:
                continue
            dbi['mongodb'][i] = {}
            print "database_name : " +  i
            db_name =  myclient[i].list_collection_names(session=None)
            for x in db_name:
                dbi['mongodb'][i][x] = myclient[i][x].find().count()
                print str(x) + "=" + str(myclient[i][x].find().count())
            print "\n"
            print 'db_count:' + str(sum(dbi['mongodb'][i].values()))
            print "\n"
            database_list.append(sum(dbi['mongodb'][i].values()))
        #print dbi['mongodb']
        print  'instance_cnt = ' + str(sum(database_list))
            


if __name__ == '__main__':
    calc_mongodb()
