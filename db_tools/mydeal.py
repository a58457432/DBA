#!/bin/env /usr/local/bin/python
#coding=utf-8
#Creator: Jeffery.shen
#UpdateTime: 2019-01-21 09:30:05

import MySQLdb


dbconfig = {}
dbconfig['host'] = '127.0.0.1'
dbconfig['port'] = 5501
dbconfig['user'] = 'wwg1'
dbconfig['passwd'] = 'wwg2019'
dbconfig['db'] = 'bak_infor'
dbconfig['charset'] = 'utf8'                                                                                                      


# db class

class MySQL:
    u'''mysqldb class'''
    error_code=''
    _instance=None
    _conn=None
    _cur=None
    _TIMEOUT=30
    _timecount=0
    error_code=''
    _instance=None
    _conn=None
    _cur=None
    _TIMEOUT=30
    _timecount=0

    def __init__(self,dbconfig):
        try:
            self._conn = MySQLdb.connect(host=dbconfig['host'],port=dbconfig['port'],user=dbconfig['user'],passwd=dbconfig['passwd'],db=dbconfig['db'],charset=dbconfig['charset'])

        except MySQLdb.Error, e:
            self.error_code=e.args[0]
            error_msg = 'MySQL error!', e.args[0],e.args[1]
            print error_msg


            if self._timecount < self._TIMEOUT:
                interval = 5
                self._timeout += interval
                time.sleep(interval)
                return self.__init__(dbconfig)
            else:
                raise Exception(error_msg)
        
        self._cur = self._conn.cursor()
        self._instance = MySQLdb

    def query(self,sql):
        try:
            self._cur.execute("set NAMES utf8")
            result = self._cur.execute(sql)

        except MySQLdb.Error,e:
            self.error_code = e.args[0]
            print "DB error:" ,e.args[0],e.args[1]
            result = False

        return result

    def insert(self,sql):
        try:
            self._cur.execute("set NAMES utf8")
            self._cur.execute(sql)
            self._conn.commit()
        
        except MySQLdb.Error,e:
            self.error_code = e.args[0]

    def update(self,sql):
        try:
            self._cur.execute("set NAMES utf8")
            self._cur.execute(sql)
            self._conn.commit()

        except MySQLdb.Error,e:
            self.error_code = e.args[0]


        return False

    def fetchAllRows(self):
        
        return self._cur.fetchall()

    def fetchOneRow(self):
        
        return self._cur.fetchone()

    def getRowCount(self):
        
        return self._cur.rowcount

    def commit(self):
        
        self._conn.rollback()

    def __del__(self):
        
        try:
            self._cur.close()
            self._conn.close()

        except:
            pass

    def close(self):
        
        self.__del__()



def insrt_bak_infor(sql):
    db = MySQL(dbconfig)
    insert_sql = sql
    db.insert(insert_sql)
    result = db.fetchAllRows()


    db.close()

    return result


#insrt_bak_infor("insert into bak_info(host,port,db,bak_create_at,bak_flag) values('172.31.19.69','5432','freessl','2019-01-21 15:38:10','backup sucessed');")

