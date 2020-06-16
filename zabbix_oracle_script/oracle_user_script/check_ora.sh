#!/bin/bash
#
# get oracle value

lsnr_status=`lsnrctl status|grep -v grep| grep -c READY`
lsnr_process=`ps -ef |grep tnslsnr |grep -v grep | wc -l`
IP=172.25.20.3
PORT=1521
lsnr_num=`echo -n "\n"|telnet $IP $PORT|grep Connected|wc -l`
SCAN_IP=172.25.20.101
scan_ip_num=`ping -w 2 -c 3 $SCAN_IP | grep packet | awk -F" " '{print $6}'| awk -F"%" '{print $1}'| awk -F' ' '{print $1}'`

script_home='/usr/local/webserver/zabbix_oracle_script/oracle_user_script'

db_alive=`sqlplus -silent "/ as sysdba" <<END
set pagesize 0 feedback off verify off heading off echo off
select status from v\\\$instance;
exit;
END`

db_active_session=`sqlplus -silent "/ as sysdba" <<END
set pagesize 0 feedback off verify off heading off echo off
select trim(count(*)) from v\\\$session where status='ACTIVE';
exit;
END`


db_max_processes=`sqlplus -silent "/ as sysdba" <<END
set pagesize 0 feedback off verify off heading off echo off
select trim(value) from v\\\$parameter where name ='processes';
exit;
END`

TNS=ORCL


#check lsnrctl; 1 is ok, 0  is fail
ora_lsnrctl_status(){
    if [ ${lsnr_status} -lt 3 ]; then
        lsnrctl_status_flag=0
        echo 'lsnrctl_status_flag='$lsnrctl_status_flag
    else
        lsnrctl_status_flag=1
        echo 'lsnrctl_status_flag='$lsnrctl_status_flag
    fi
}


#check listen port;  1 is  ok, 0 is fail
ora_check_listen_port(){
    if [ $lsnr_num == 1 ]; then
        echo "listen_$PORT=1"
    else 
        echo "listen_$PORT=0"
    fi
}

#check tns,  1 is ok, 0 is fail
ora_tns_status(){
    tnschk=`tnsping $TNS |grep -c OK `
    if [ ${tnschk} -eq 1 ]; then
        echo "tns_status=1"
    else
        echo "tns_status=0"
    fi
}

#check scan ip, 1 is ok, 0 is fail
ora_scan_ip_status(){
    if [ ${scan_ip_num} -eq 0 ]; then
        echo "scan_ip=1"
    else
        echo "scan_ip=0"
    fi
}



# grep ORA- alert.log

# check database status
ora_check_DBalive(){
    if [ $db_alive == 'OPEN' ]; then
        echo "db_status=1"
    else
        echo "db_status=0"
    fi
}

# active session
ora_active_session(){
    echo 'db_active_session='$db_active_session
}

# All processes
ora_all_process(){
    echo 'db_all_process='$db_max_processes
}

# check  tablespace
ora_check_tablespace(){
sqlplus -S "/ as sysdba" <<  EOF
set linesize 200
set pagesize 200
spool /tmp/ora_tablespace.txt
SELECT UPPER(F.TABLESPACE_NAME) "tablespace_name",
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
 ORDER BY 4 DESC;
spool off
set linesize 100
set pagesize 100
spool /tmp/ora_autex.txt
select tablespace_name,autoextensible from dba_data_files;
spool off
quit
EOF
};

# get tbl
ora_get_tblspace(){
tbl_name=`sh $script_home/tblspace.sh | grep -iv selected |awk -F ' ' '{print $1}'`
tbl_percent=`sh $script_home/tblspace.sh | grep -iv selected |awk -F ' ' '{print $4}'`

tbl_name1=($tbl_name)
tbl_percent1=($tbl_percent)
num=${#tbl_name1[*]}
num1=$[$num-1]

for i in `seq 0 $num1`;
do 
    echo tbl_${tbl_name1[$i]}=${tbl_percent1[$i]}
done 

}

# get asm
ora_asm_used_per(){
asm_name=`sh $script_home/asm_used.sh | grep -iv rows |awk -F ' ' '{print $1}'`
asm_percent=`sh $script_home/asm_used.sh | grep -iv rows |awk -F ' ' '{print $2}'`

asm_name1=($asm_name)
asm_percent1=($asm_percent)
num=${#asm_name1[*]}
num1=$[$num-1]

for i in `seq 0 $num1`;
do
    echo asm_${asm_name1[$i]}=${asm_percent1[$i]}
done

}

# get cache hit rate
ora_cache_hit_rate(){
cache_hit_name=`sh $script_home/cache_hit_rate.sh`
echo "db_cache_hit_rate="$cache_hit_name
}

# get archivelog_increase_size.sh
ora_archivelog_increase(){
archivelog_size=`sh $script_home/archivelog_increase_size.sh`
echo 'db_archivelog_size_MB='$archivelog_size
}

#process_usage
sys_process_usage(){
process_usage=`ps aux  |grep pmon |grep ora_ | grep -iv grep |awk -F ' ' '{print $3}'`
echo 'sys_process_usage='$process_usage
}

# sys app home size
sys_app_home_size(){
app_home_size=`df -h /app |grep -iv Use |awk -F ' ' '{print $5}' | awk -F '%' '{print $1}'`
echo 'sys_app_home_size='$app_home_size
}

main(){
ora_lsnrctl_status
ora_check_listen_port
ora_tns_status
ora_scan_ip_status
ora_check_DBalive
ora_active_session
ora_all_process
#ora_check_tablespace
ora_get_tblspace
ora_asm_used_per
ora_cache_hit_rate
ora_archivelog_increase
sys_process_usage
sys_app_home_size
}

main
