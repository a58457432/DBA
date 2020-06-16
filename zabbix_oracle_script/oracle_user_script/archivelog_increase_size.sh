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
SELECT  round(SUM(BLOCK_SIZE * BLOCKS)/1024/1024,2) "SIZE(MB)" FROM V\$ARCHIVED_LOG where to_char(TRUNC(FIRST_TIME),'yyyy-mm-dd') = to_char(sysdate,'yyyy-mm-dd')  GROUP BY TRUNC(FIRST_TIME);
exit;
exit;
!

