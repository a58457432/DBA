#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    (C) China Eastern Airlines
#
#    Last update: sjh 2025-03-04

""" Run CMD or SCP In Batch Mode

You can choose project type, area  to run command or upload file.
Output info will print to script.info.

"""

__authors__ = [
    '"sjh"',
]

import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from datetime import datetime
import re
import copy
from os import path
import sys
import time
import socket
import subprocess
import copy
import os
import re

#sys.path.append(path.join(path.realpath(path.dirname(sys.argv[0])), "lib"))

dt = datetime.now()
DATETIME = dt.strftime('%Y-%m-%d %H:%M:%S')

# mongodb information
target_user = 'test'
target_passwd = 'test2025'
target_host = '192.168.217.129'
target_port = '27017'
target_database_name = 'mutms'


# call find dir shell
bash='/usr/bin/bash'
find_dir_shell='/usr/local/webserver/DBA/mongodb/find_the_latest_dir.sh'



# hostname
insname = 'Mongodb_' + socket.gethostname()

# collection_list
col_list = ["APPVersionUpgradeRecord","BizVersionUpgradeRecord","OtaChannelAdminInfo","OtaChannelInfo","OtaChannelRecord","PlatformVersionControlRuleConfig","ProductZone"]


# ----------------------------------------------------------------------------------------
# run bash cmd 
# ----------------------------------------------------------------------------------------
def runCmd(cmd):
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    except:
        return None, p.returncode
    else:
        output, err = p.communicate()
    return output, p.returncode


# ----------------------------------------------------------------------------------------
# init dbs dict()
# ----------------------------------------------------------------------------------------
def init_dbins_info():
    dbins = {}  # db实例字典
    dbinfo = {}  # db信息字典
    dbinfo['mongodb'] = {}
    dbinfo['target_user'] = target_user
    dbinfo['target_passwd'] = target_passwd
    dbinfo['target_host'] = target_host
    dbinfo['target_port'] = target_port
    dbinfo['target_database_name'] = target_database_name
    dbinfo['insname'] = insname

    dbins[insname] = copy.deepcopy(dbinfo)
    return dbins

#-------------------------
# mongodb class
#-------------------------
class MongoDBConnector:
    def __init__(self, username, password, host, port, database_name):
        """
        初始化 MongoDB 连接
        :param username: 数据库用户名
        :param password: 数据库密码
        :param host: 数据库主机地址
        :param port: 数据库端口号
        :param database_name: 要连接的数据库名
        """
        try:
            # 构建连接字符串
            connection_string = f"mongodb://{username}:{password}@{host}:{port}/{database_name}"
            # 连接到 MongoDB 服务器
            self.client = MongoClient(connection_string)
            # 选择数据库
            self.db = self.client[database_name]
        except ConnectionFailure:
            print("无法连接到 MongoDB 服务器，请检查连接信息。")
            self.client = None
            self.db = None

    def insert_document(self, collection_name, document):
        """
        向指定集合插入单个文档
        :param collection_name: 集合名称
        :param document: 要插入的文档（字典形式）
        :return: 插入文档的 ID
        """
        if self.client and self.db is not None:
            try:
                collection = self.db[collection_name]
                result = collection.insert_one(document)
                return result.inserted_id
            except OperationFailure as e:
                print(f"插入文档失败: {e}")
        return None

    def find_document(self, collection_name, query):
        """
        在指定集合中查找符合条件的单个文档
        :param collection_name: 集合名称
        :param query: 查询条件（字典形式）
        :return: 查找到的文档，如果未找到则返回 None
        """
        if self.client and self.db is not None:
            try:
                collection = self.db[collection_name]
                return collection.find_one(query)
            except OperationFailure as e:
                print(f"查找文档失败: {e}")
        return None

    def update_document(self, collection_name, query, update):
        """
        在指定集合中更新符合条件的单个文档
        :param collection_name: 集合名称
        :param query: 查询条件（字典形式）
        :param update: 更新内容（使用 MongoDB 更新操作符，如 $set）
        :return: 更新的文档数量
        """
        if self.client and self.db is not None:
            try:
                collection = self.db[collection_name]
                result = collection.update_one(query, update)
                return result.modified_count
            except OperationFailure as e:
                print(f"更新文档失败: {e}")
        return 0

    def delete_document(self, collection_name, query):
        """
        在指定集合中删除符合条件的单个文档
        :param collection_name: 集合名称
        :param query: 查询条件（字典形式）
        :return: 删除的文档数量
        """
        if self.client and self.db is not None:
            try:
                collection = self.db[collection_name]
                result = collection.delete_one(query)
                return result.deleted_count
            except OperationFailure as e:
                print(f"删除文档失败: {e}")
        return 0
    
    def count_document(self, collection_name):

        if self.client and self.db is not None:
            try:
                collection = self.db[collection_name]
                return collection.count_documents({})
            except OperationFailure as e:
                print(f"统计文档失败: {e}")
        return None

    def del_all_document(self, collection_name):

        if self.client and self.db is not None:
            try:
                collection = self.db[collection_name]
                return collection.drop()
            except OperationFailure as e:
                print(f"统计文档失败: {e}")
        return None

    def close_connection(self):
        """
        关闭 MongoDB 连接
        """
        if self.client:
            self.client.close()

#----------------
# get restore dir
#----------------
def get_restore_dir():
    dir_list_cmd = bash + " " + find_dir_shell 
    try:
        dir_list = runCmd(dir_list_cmd)
    except Exception as e:
        print(str(e))

    data = copy.deepcopy(dir_list)
    if isinstance(data[0], bytes):
        split_bytes = data[0].split(b'\n')
        decoded_list = [item.decode('utf-8') for item in split_bytes if item]
    else:
        decoded_list = []

    return decoded_list


def check_target_document(collection):

    connector = MongoDBConnector(target_user, target_passwd, target_host, target_port, target_database_name)
    
    collection_name = collection
    
    find_doc = connector.count_document(collection_name)
    
    if find_doc > 0:
        print(f"{collection_name} 文档存在,准备删除在导入")
        del_all_doc = connector.del_all_document(collection_name)
    else:
        print(f"{collection_name} 文档不存在")
        pass

def get_split_str(path):
    path = path
    filename = path.split("/")[-1]  # 获取文件名部分
    result = filename.split("20")[0]  # 以 "20" 为分隔符，取第一部分
    return result

# mongorestore --host 192.168.217.129 --port 27017 --username test --password test2025 --authenticationDatabase mutms --db=mutms  /data/backup/APPVersionUpgradeRecord20250303-04/mutms/

def restore_mongodb():
    restore_dir_list = get_restore_dir()
    mongores_cmd = "/usr/local/mongodb-tools/bin/mongorestore" 

    if len(restore_dir_list) == 7: 
        for i in restore_dir_list:
            #print(get_split_str(i))
            check_target_document(get_split_str(i))
            mr_cmd = ('%s --host %s --port %s --username %s --password %s --authenticationDatabase %s --db=%s  %s/%s > /dev/null 2>&1') % (mongores_cmd, target_host, target_port, target_user, target_passwd , target_database_name, target_database_name, i, target_database_name)

            try:
                restore_cmd = runCmd(mr_cmd)
            except Exception as e:
                print(str(e))            

            connector = MongoDBConnector(target_user, target_passwd, target_host, target_port, target_database_name)
            count_doc = connector.count_document(get_split_str(i))

            if restore_cmd[1] == 0:
                print(i + "  成功导入 " + str(count_doc) + "条数据" , end='\n\n')
            else:
                print(i + "  导入失败", end='\n\n')
    else:
        pass 



if __name__ == '__main__':
    restore_mongodb()
