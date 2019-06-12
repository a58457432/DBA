#!/bin/env /usr/local/bin/python
#coding=utf-8
#Creator: shenjinhong
#UpdateTime: 2019-06-10 09:30:05

import psycopg2

dbconfig = {}
dbconfig['host'] = '127.0.0.1'
dbconfig['port'] = 5432
dbconfig['user'] = 'postgres'
dbconfig['passwd'] = 'postgres'
dbconfig['db'] = 'yashu'
dbconfig['charset'] = 'utf8'                                                                                                      


# db class

class Postgresql:
    u'''pg class'''
    _conn=None
    _usr=None
    
    def __init__(self,dbconfig):
        try:
            self._conn = psycopg2.connect(dbname=dbconfig['db'], user=dbconfig['user'], password=dbconfig['passwd'], host=dbconfig['host'], port=dbconfig['port'])

        except psycopg2.Error as e:
            print "Unable to connect!"
            print e.pgerror
            print e.diag.message_detail
            sys.exit(1)
        
        self._cur = self._conn.cursor()


    def query(self,sql):
        try:
            self._cur.execute("set client_encoding=utf8")
            result = self._cur.execute(sql)
        
        except psycopg2.Error as e:
            print e.pgerror
            print e.diag.message_detail
            result = False

        return result

    def insert(self,sql):
        try:
            self._cur.execute("set client_encoding=utf8")
            self._cur.execute(sql)
            self._conn.commit()

        except psycopg2.Error as e:
            print e.pgerror
            print e.diag.message_detail

    def update(self,sql):
        try:
            self._cur.execute("set client_encoding=utf8")
            self._cur.execute(sql)
            self._conn.commit()

        except psycopg2.Error as e:
            print e.pgerror
            print e.diag.message_detail

    def fetchAllRows(self):

        return self._cur.fetchall()

    def fetchOneRow(self):

        return self._cur.fetchone()
    
    def __del__(self): 
        try:
            self._cur.close()
            self._conn.close()
        
        except:
            pass


    def close(self):

        self.__del__()


def cal():
    
    pger = Postgresql(dbconfig)
    sql = "insert into test1 values(3,'yashulolo');"
    pger.insert(sql)
#    result = pger.fetchAllRows()
#    print result

    pger.close()

if __name__ == '__main__':
    cal()

