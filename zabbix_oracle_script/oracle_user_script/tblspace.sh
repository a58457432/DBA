#!/bin/bash
#
# get db_status
sqlplus -S "/ as sysdba" << !
set heading off
col tablespace_name,tablespace_size_M,used_size_M,used_percent noprint
column tablespace_name new_val v_tablespace_name
column tablespace_size_M new_val v_tablespace_size_M
column used_size_M  new_val v_used_size_M
column used_percent new_val v_used_percent
SELECT
UPPER (F.TABLESPACE_NAME) "tablespace_name",
D .TOT_GROOTTE_MB "tablespace_size_M",
D .TOT_GROOTTE_MB - F.TOTAL_BYTES "used_size_M",
TO_CHAR(ROUND((D .TOT_GROOTTE_MB - F.TOTAL_BYTES) / D .TOT_GROOTTE_MB * 100,2),'990.99') "used_percent",
F.TOTAL_BYTES "free_size_M"
FROM
(SELECT TABLESPACE_NAME,                                                                                                                      ROUND (SUM(BYTES) /(1024 * 1024), 2) TOTAL_BYTES,
        ROUND (MAX(BYTES) /(1024 * 1024), 2) MAX_BYTES                                                                                        FROM  SYS.DBA_FREE_SPACE where tablespace_name not in('SYSAUX','SYSTEM','USERS','UNDOTBS2','UNDOTBS1')
        GROUP BY TABLESPACE_NAME
         ) F,
(SELECT    DD.TABLESPACE_NAME,
           ROUND (SUM (DD.BYTES) / (1024 * 1024),2) TOT_GROOTTE_MB                                                                               FROM  SYS.DBA_DATA_FILES DD
           GROUP BY   DD.TABLESPACE_NAME
           ) D
WHERE D .TABLESPACE_NAME = F.TABLESPACE_NAME
ORDER BY 4 DESC;
exit;
exit;
!

