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
select  name,round((total_mb-free_mb)/total_mb*100) as used_percent from v\$asm_diskgroup;
exit;
exit;
!

