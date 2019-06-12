#!/bin/env /usr/local/bin/python
#coding=utf-8
#Creator: Jeffery.shen
#UpdateTime: 2019-03-12 11:00:05

from ftplib import FTP
import time
import tarfile
import os
import sys
import socket


class MyFTP:

    def __init__(self, host):
        
        self.host = host
#        self.port = port
        self.ftp = FTP()
        self.ftp.encoding ='utf8'
        self.log_file = open('/tmp/log.txt', "a")
        self.file_list = []

    def login(self, username, password):

        try:
            timeout = 60
            socket.setdefaulttimeout(timeout)
            self.ftp.set_pasv(True)

            self.debug_print('begin connect %s' % self.host)
            self.ftp.connect(self.host, 5021)
            self.debug_print('sucess connect %s' % self.host)

            self.debug_print('begin login %s' % self.host)
            self.ftp.login(username, password)
            self.debug_print('sucess login %s' % self.host)

            self.debug_print(self.ftp.welcome)
        except Exception as e:
            self.deal_error("ftp fail")
            pass

    
    def download_file(self, local_file, remote_file):
        
        self.debug_print('download_file() --> local_path = %s,remote_path = %s' % (local_file, remote_file))

        try:
            buf_size = 1024
            file_handler = open(local_file, "wb")
            self.ftp.retrbinary('RETR %s' % remote_file, file_handler.write, buf_size)
            file_handler.close()
        except Exception as e:
            self.debug_print("ftp download %s " % e)
            return

    
    def download_file_tree(self, local_path, remote_path):
        
        try:
            self.ftp.cwd(remote_path)
        except Exception as e:
            self.debug_print('remote_path is null , %s' % e)
            return

        self.debug_print('cmd folder %s' % self.ftp.pwd())

        self.file.list = []

        self.ftp.dir(self.get_file_list)

        remote_names = self.file_list
        self.debug_print()

        for item in remote_names:
            file_type = item[0]
            file_name = item[1]
            local = os.path.join(local_path, file_name)
            if file_type == 'd':
                print("download_file_tree() --> download : %s" % file_name)
                self.download_file_tree(local, file_name)
            elif file_type == '-':
                print("download_file() --> download file: %s" % file_name)
                self.download_file(local, file_name)

            self.ftp.cwd("..")
            self.debug_print('return %s' % self.ftp.pwd())
        return True


    def upload_file(self, local_file, remote_file):
        
        if not os.path.isfile(local_file):
            self.debug_print('%s is null' % local_file)
            return
        
        buf_size = 1024
        file_handler = open(local_file, 'rb')
        self.ftp.storbinary('STOR %s' % remote_file, file_handler, buf_size)
        file_handler.close()
        self.debug_print('upload %s' % local_file + ' sucess')


    def upload_file_tree(self, local_path, remote_path):
        
        if not os.path.isdir(local_path):
            self.debug_print('%s is null' % local_path)
            return

        self.ftp.cwd(remote_path)
        
        local_name_list = os.listdir(local_path)
        for local_name in local_name_list:
            src = os.path.join(local_path, local_name)
            if os.path.isdir(src):
                try:
                    self.ftp.mkd(local_name)
                except Exception as e:
                    self.debug_print('%s is existence, %s' % (loacl_name,e))
                self.upload_file_tree(src, local_name)

            else:
                self.upload_file(src, local_name)
        self.ftp.cwd("..")


    def close(self):
        self.debug_print("close()---> ftp out")
        self.ftp.quit()
        self.log_file.close()


    def debug_print(self, s):
        self.write_log(s)

    def deal_error(self, e):
        
        log_str = 'error: %s' % e
        self.write_log(log_str)
        sys.exit()


    def write_log(self, log_str):
        
        time_now = time.localtime()
        date_now = time.strftime('%Y-%m-%d', time_now)
        format_log_str = "%s ---> %s \n" % (date_now, log_str)
        print(format_log_str)
        self.log_file.write(format_log_str)

    def get_file_list(self, line):
        
        file_arr = self.get_file_name(line)

        if file_arr[1] not in ['.','..']:
            self.file_list.append(file_arr)

    def get_file_name(self, line):
        
        pos = line.rfind(':')
        while (line[pos] != ''):
            pos += 1
        while (line[pos] == ''):
            pos += 1
        file_arr = [line[0], line[pos:]]
        return file_arr

    

if __name__ == "__main__":
    my_ftp = MyFTP("dsm.xxx.cn")
    my_ftp.login("xxx","xxx")

    my_ftp.upload_file_tree("/data/mysql/backup","/home/mysqlbackup")
#    my_ftp.upload_file_tree("/data/pg/backup","/home/pgbackup")
    
    my_ftp.close()


