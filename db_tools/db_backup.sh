#!/bin/bash
#
# db backup

backup_cmd = `which mysqldump`
user='root'
passwd='MaH@iy2n'
host='127.0.0.1'
port='3306'
dtime=`date "+%Y%m%d-%H-%M-%S"`

db_backup(){
$backup_cmd -u$user -p$passwd -h$host -P$port  --master-data=2 --single-transaction -A > /usr/local/webserver/backup/'dbbackup' + dtime + '.sql'

}



