#!/bin/bash
#
# mysql backup
#
# author: shenjinhong 
# Date created: 2025-03-05

backup_cmd='/usr/local/mysql/bin/mysqldump'
mysql_host="192.168.217.129"
mysql_port=3306
mysql_user="uor_mutms"
mysql_password="M36tVomW*IsknA8"
mysql_database="mutms"

table01="basic_data"
table02="session_info"
table03="user_icon"

dump_name="three_tables_no_data"


dtime=`date "+%Y%m%d-%H-%M"`

# dump collections
COLLECTIONS=("APPVersionUpgradeRecord" "BizVersionUpgradeRecord" "OtaChannelAdminInfo" "OtaChannelInfo" "OtaChannelRecord" "PlatformVersionControlRuleConfig" "ProductZone")

# Export directory
EXPORT_DIR="/data/backup/mysql/" 

# mysqldump -u uor_mutms -p'M36tVomW*IsknA8' -h 192.168.217.129 -P3306  mutms --ignore-table=mutms.session_info --ignore-table=mutms.basic_data --ignore-table=mutms.user_icon --set-gtid-purged=OFF > /data/backup/mutms20250305.sql

mysql_backup(){
$backup_cmd -u $mysql_user -p$mysql_password -h $mysql_host -P$mysql_port  $mysql_database --ignore-table=$mysql_database.$table01 --ignore-table=$mysql_database.$table02 --ignore-table=$mysql_database.$table03 --set-gtid-purged=OFF > $EXPORT_DIR$mysql_database$dtime.sql
}

#mysqldump -u uor_mutms -p'M36tVomW*IsknA8' -h 192.168.217.129 -P3306  mutms  session_info basic_data user_icon --set-gtid-purged=OFF  --no-data > /data/backup/three_tables_no_data.sql

mysql_backup_three_table_nodata(){
$backup_cmd -u $mysql_user -p$mysql_password -h $mysql_host -P$mysql_port  $mysql_database  $table01 $table02 $table03  --no-data --set-gtid-purged=OFF > $EXPORT_DIR$dump_name$dtime.sql
}



del_dir(){
find "$EXPORT_DIR" -type d -mtime +7 -exec rm -rf {} \;
}


main(){
    mysql_backup
    mysql_backup_three_table_nodata
    del_dir
}

main
