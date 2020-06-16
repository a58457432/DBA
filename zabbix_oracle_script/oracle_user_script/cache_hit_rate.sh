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
select round((1-(sum(decode(name, 'physical reads',value,0))/(sum(decode(name, 'db block gets',value,0))+sum(decode(name,'consistent gets',value,0))))) * 100, 2) "Hit Ratio" from v\$sysstat;
exit;
exit;
!

