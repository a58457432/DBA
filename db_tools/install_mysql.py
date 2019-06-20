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
target_file = "/etc/init.d/mysqld"
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
	

def build_mysql():
    pass


def change_config():
    pass

def start_mysql():
    pass


def stop_mysql():
    pass


def main():
    #    get_mysql()
    init_sys_mysql()


if __name__ == '__main__':
    main()


