#!/usr/bin/env python
## coding=utf-8
# Creator: sjh
# UpdateTime:2019.6.13

import os
import sys

try:
    import json
except:
    import simplejson as json
import subprocess
import shutil
import re
import configparser
import time

softdir = "/usr/local/webserver/software/"
mysql_url = "wget -c https://cdn.mysql.com//Downloads/MySQL-8.0/mysql-8.0.16-linux-glibc2.12-x86_64.tar.xz"
mysql_pkg = "mysql-8.0.16-linux-glibc2.12-x86_64.tar.xz"
profile = "/root/.bash_profile"
groupadd_cmd = "groupadd mysql"
useradd_cmd = "useradd -r -g mysql mysql"
chown_mysql = "chown -R mysql:mysql "
port = "3306"
mysql_root_dir = "/data/"
data_dir = "/data/mysql/mysql_" + port + "/data"
logs_dir = "/data/mysql/mysql_" + port + "/logs"
tmp_dir = "/data/mysql/mysql_" + port + "/tmp"
config_dir = "/etc/"
mysql_dir = "/usr/local/mysql/"
mkdir_cmd = "mkdir -p "
cp_cmd = "cp "
chmod_cmd = "chmod +x "
mysqld_cmd = mysql_dir + "bin/mysqld " + "--initialize   --user=mysql  --datadir=%s --basedir=%s" % (data_dir, mysql_dir) 
target_file = "/etc/init.d/mysqld"
mysql_start_cmd = target_file + " " + "start"
mysql_stop_cmd = target_file + " " + "stop"
source_file = "support-files/mysql.server"
mysql_server_file = mysql_dir + source_file
move_server_file = cp_cmd + mysql_dir + source_file + " " + target_file 

chown_mysql_dir = chown_mysql + mysql_dir
chown_mysql_data = chown_mysql + mysql_root_dir
chmod_mysqld = chmod_cmd + target_file



def runCmd(cmd):
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    except:
        return None, p.returncode
    else:
        output, err = p.communicate()
        return output, p.returncode


def untar(fname, dirs):
    t = tarfile.open(fname)
    t.extractall(path=dirs)


# wget mysql && install mysql 

def get_mysql():
    if os.path.exists(softdir) == True:
        print("softdir is exists")
    else:
        os.makedirs(softdir)
        os.chdir(softdir)
    download_mysql = runCmd(mysql_url)[1]
    if download_mysql == 0:
        untar(mysql_pkg, softdir)
        print("tar sucess")
    else:
        print("download fail")


def init_sys_mysql():
    os.chdir(softdir)
    groupadd_tag = runCmd(groupadd_cmd)[1]
    useradd_tag = runCmd(useradd_cmd)[1]

    if groupadd_tag == 0 and useradd_tag == 0:
        print("add mysql user sucessd")
    else:
        print("add user fail")

    create_dir = runCmd(mkdir_cmd + data_dir)[1] + runCmd(mkdir_cmd + logs_dir)[1] + runCmd(mkdir_cmd + tmp_dir)[1]

    if create_dir == 0:
        print("add data dir sucess")
    else:
        print("add data dir fail")

    chown_dir_flag = runCmd(chown_mysql_dir)[1] + runCmd(chown_mysql_data)[1]
    if chown_dir_flag == 0:
        print("chown dir sucess ")
    else:
        print("chown dir fail")

    if os.path.exists(target_file) == True:
        print("mysqld exists")
    else:
        shutil.copyfile(mysql_server_file, target_file)

    file = open(target_file, 'r')
    con = file.read()
    count = re.findall('datadir=/data', con)
    if len(count) == 1:
        print(" mysqld datadir is right")
    else:
        f1 = open(target_file, 'r')
        con = f1.read()
        f1.close()
        t = con.replace("datadir=", "datadir=%s", 1) % (data_dir)
        with open(target_file, "w") as f2:
            f2.write(t)

    runCmd(chmod_mysqld)
	

# 
# /usr/local/mysql/bin/mysqld --initialize   --user=mysql  --datadir=/data/mysql/mysql_3306/data/ --basedir=/usr/local/mysql/
# cat /data/mysql/mysql_3306/logs/mysql-error-log.err  |grep password | awk -F 'localhost: ' '{print $2}'
# update user set password_expired="N" where user="root";
# ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123' EXPIRE NEVER;
# flush privilegs;
def build_mysql():
    try:
        if len(os.listdir(data_dir)) > 0:
            print('data_dir has something')
        else:
            init_mysql_data = runCmd(mysqld_cmd)[1]
            if init_mysql_data == 0:
                print("init mysql sucesss")
            else:
                print("init mysql fail")
    except(BaseException,e):
        print(str(e))

def write_config():
    config = configparser.ConfigParser()
    config['client'] = {'loose_prompt': '\\u@\\h \\d >','loose_default-character-set': 'utf8','port': port,'socket': '/tmp/mysql.sock' ,'default-character-set': 'utf8'}
    config['mysqld'] = {}
    config['mysqld']['default_authentication_plugin'] = 'mysql_native_password'
    config['mysqld']['server-id'] = str(int(time.time()))
    config['mysqld']['user'] = 'mysql'
    config['mysqld']['basedir'] = mysql_dir
    config['mysqld']['datadir'] = data_dir
    config['mysqld']['socket'] = config['client']['socket']
    config['mysqld']['pid-file'] = data_dir + '/mysql.pid'
    config['mysqld']['event_scheduler'] = '0'
    config['mysqld']['lower_case_table_names'] = '1'
    config['mysqld']['character-set-server'] = 'utf8mb4'
    config['mysqld']['transaction-isolation'] = 'REPEATABLE-READ'
    config['mysqld']['max_connect_errors'] = '100000'
    config['mysqld']['max_connections'] = '2048'
    config['mysqld']['max_allowed_packet'] = '1G'
    config['mysqld']['wait_timeout'] = '3600'
    config['mysqld']['interactive_timeout'] = '3600'
    config['mysqld']['explicit_defaults_for_timestamp'] = '1'
    # innodb
    config['mysqld']['innodb_buffer_pool_size'] = '1G'
    config['mysqld']['innodb_file_per_table'] = '1'
    config['mysqld']['innodb_data_home_dir'] = data_dir
    config['mysqld']['innodb_data_file_path'] = 'ibdata1:1G:autoextend'
    config['mysqld']['innodb_log_group_home_dir'] = data_dir
    config['mysqld']['innodb_log_files_in_group'] = '3'
    config['mysqld']['innodb_log_file_size'] = '1G'
    config['mysqld']['innodb_log_buffer_size'] = '32M'
    config['mysqld']['innodb_flush_log_at_trx_commit'] = '2'
    config['mysqld']['innodb_lock_wait_timeout'] = '50'
    config['mysqld']['innodb_io_capacity'] = '2000'
    config['mysqld']['innodb_io_capacity_max'] = '4000'
    config['mysqld']['innodb_flush_method'] = 'O_DIRECT'
    config['mysqld']['innodb_max_dirty_pages_pct'] = '40'
    config['mysqld']['innodb_flush_neighbors'] = '0'
    config['mysqld']['innodb_thread_concurrency'] = '40'
    config['mysqld']['innodb_sort_buffer_size'] = '64M'
    # buffer and cache
    config['mysqld']['key_buffer_size'] = '256M'
    config['mysqld']['bulk_insert_buffer_size'] = '64M'
    config['mysqld']['myisam_sort_buffer_size'] = '128M'
    config['mysqld']['myisam_max_sort_file_size'] = '10G'
    config['mysqld']['read_buffer_size'] = '4M'
    config['mysqld']['read_rnd_buffer_size'] = '8M'
    config['mysqld']['sort_buffer_size'] = '8M'
    config['mysqld']['join_buffer_size'] = '8M'
    config['mysqld']['open_files_limit'] = '65535'
    config['mysqld']['table_open_cache'] = '512'
    config['mysqld']['tmp_table_size'] = '256M'
    config['mysqld']['max_heap_table_size'] = '256M'
    config['mysqld']['thread_cache_size'] = '1024'
    config['mysqld']['thread_stack'] = '256K'
    # log
    config['mysqld']['slow_query_log'] = '1'
    config['mysqld']['slow_query_log_file'] = logs_dir + '/mysql-slow.log'
    config['mysqld']['long_query_time'] = '2'
    config['mysqld']['log-error'] = logs_dir + '/mysql-error-log.err'
    config['mysqld']['expire_logs_days'] = '7'
    # replication
    config['mysqld']['subordinate-skip-errors'] = '1032'
    config['mysqld']['replicate_ignore_db'] = 'performance_schema'
    config['mysqld']['replicate_ignore_db'] = 'mysql'
    config['mysqld']['log-bin'] = logs_dir + '/mysql-bin'
    config['mysqld']['max_binlog_size'] = '1G'
    config['mysqld']['binlog_cache_size'] = '4M'
    config['mysqld']['max_binlog_cache_size'] = '2G'
    config['mysqld']['binlog_format'] = 'row'
    config['mysqld']['relay_log'] = logs_dir + '/mysql-relay-bin'
    config['mysqld']['max_relay_log_size'] = '1G'
    config['mysqld']['relay_log_purge'] = '1'
    config['mysqld']['log_subordinate_updates'] = '1'
    config['mysqld']['sync_binlog'] = '10'
    config['mysqld']['gtid_mode'] = 'off'
    config['mysqld']['symbolic-links'] = '0'
    config['mysqld_safe'] = {'log-error': config['mysqld']['log-error'], 'pid-file' : config['mysqld']['pid-file']}
    with open('/etc/my.cnf', 'w') as configfile:
        config.write(configfile)


def start_mysql():
    if os.path.exists(target_file) == True:
        mysql_start_info = runCmd(mysql_start_cmd)[1]
        if mysql_start_info == 0:
            print("start mysql sucess")
        else:
            print("start mysql fail")
    else:
        print("mysqld file is lose")

def stop_mysql():
    if os.path.exists(target_file) == True:
        mysql_stop_info = runCmd(mysql_stop_cmd)[1]
        if mysql_stop_info == 0:
            print("stop mysql sucess")
        else:
            print("stop mysql fail")

def alter_user():
    pass

def main():
#    get_mysql()
    init_sys_mysql()
    write_config()
    build_mysql()
    start_mysql()

if __name__ == '__main__':
    main()
