#!/bin/env /usr/local/bin/python
#coding=utf-8
#Creator: Jeffery.shen


import sys

#usargv = sys.argv
#print usargv


while True:
    f = raw_input("recovery db type ---->input mysql or pg or stop : ")
    
    if f == "mysql":
        my_info = "put mpki or trustasia-mysql , recovery db command will be printed : "
       # print my_info
        
        mycmd = raw_input(my_info)

        if mycmd == "mpki":
            my_cmd = "myloader -u root -p 123 -v 3 -o -d /data/mysql/backup/mybackup_mpki_release_20190215/"
            print my_cmd
        else:
            my_cmd = "mysql -uroot -p < mybackup_trustasia-mysql_20190215.sql "
            print my_cmd

    elif f == "pg":
        pg_info = "psql -U postgres -d mydb -f select_objects.sql && pg_restore --dbname=mydb --jobs=4 --verbose mydb.backup"
        print pg_info
 
    elif f == "stop":
        print "stop query!"
        break

    else:
        print "only input db type,try again!"




