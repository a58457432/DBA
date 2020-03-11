#!/bin/bash
#
# get oracle value

lsnr_status=`lsnrctl status|grep -v grep| grep -c READY`
lsnr_process=`ps -ef |grep tnslsnr |grep -v grep | wc -l`
IP=192.168.31.173
PORT=1521
lsnr_num=`echo -n "\n"|telnet $IP $PORT|grep Connected|wc -l`

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

TNS=wwg


#check lsnrctl; 1 is ok, 0  is fail
ora_lsnrctl_status(){
    if [ ${lsnr_status} -lt 1 ]; then
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
        echo "tns_status_$TNS=1"
    else
        echo "tns_status_$TNS=0"
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
tbl_name=`sh /home/oracle/script/tblspace.sh |awk -F ' ' '{print $1}'`
tbl_percent=`sh /home/oracle/script/tblspace.sh |awk -F ' ' '{print $4}'`

tbl_name1=($tbl_name)
tbl_percent1=($tbl_percent)
num=${#tbl_name1[*]}
num1=$[$num-1]

for i in `seq 0 $num1`;
do 
    echo tbl_${tbl_name1[$i]}=${tbl_percent1[$i]}
done 

}

main(){
ora_lsnrctl_status
ora_check_listen_port
ora_tns_status
ora_check_DBalive
ora_active_session
ora_all_process
#ora_check_tablespace
ora_get_tblspace
}

main
