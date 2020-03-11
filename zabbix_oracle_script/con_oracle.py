#!/bin/env /usr/bin/python
#coding=utf-8
#Creator: Sjh

import cx_Oracle
conn = cx_Oracle.connect('system', 'oracle','192.168.31.173:1521/wwg')
cursor = conn.cursor()
sql='''SELECT UPPER(F.TABLESPACE_NAME) "tablespace_name",
       D.TOT_GROOTTE_MB "tablespace_size_M",
       D.TOT_GROOTTE_MB - F.TOTAL_BYTES "used_size_M",
       TO_CHAR(ROUND((D.TOT_GROOTTE_MB - F.TOTAL_BYTES) / D.TOT_GROOTTE_MB * 100,
                     2),
               '990.99') "used_ percent",
       F.TOTAL_BYTES "free_size_M"
  FROM (SELECT TABLESPACE_NAME,
               ROUND(SUM(BYTES) / (1024 * 1024), 2) TOTAL_BYTES,
               ROUND(MAX(BYTES) / (1024 * 1024), 2) MAX_BYTES
          FROM SYS.DBA_FREE_SPACE
         GROUP BY TABLESPACE_NAME) F,
       (SELECT DD.TABLESPACE_NAME,
               ROUND(SUM(DD.BYTES) / (1024 * 1024), 2) TOT_GROOTTE_MB
          FROM SYS.DBA_DATA_FILES DD
         GROUP BY DD.TABLESPACE_NAME) D
 WHERE D.TABLESPACE_NAME = F.TABLESPACE_NAME
 ORDER BY 4 DESC;'''
cursor.execute(sql)
result = cursor.fetchone()
print 'Oracle Database time:%s' % result
cursor.close()
conn.close()

