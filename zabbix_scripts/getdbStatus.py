#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    (C) 21vianet Inc.
#
#    Last update: sjh 2019-12-20

""" Run CMD or SCP In Batch Mode

You can choose project type, area  to run command or upload file.
Output info will print to script.info.

"""

__authors__ = [
    '"sjh"',
]

import MySQLdb
import ConfigParser
from datetime import datetime
import re
import copy
from os import path
import sys
import time
import socket
import subprocess

sys.path.append(path.join(path.realpath(path.dirname(sys.argv[0])), "lib"))

# ----------------------------------------------------------------------------------------
# Parameter
# ----------------------------------------------------------------------------------------
# -----> Global Variables
# from global_var import *
DBSTATUS_FILE = "/opt/DBins.Info"  # db状态输出文件的路径
LAST_DBSTATUS_FILE = "/opt/.last_status.txt"  # 上一次状态数值文件的路径
dt = datetime.now()
DATETIME = dt.strftime('%Y-%m-%d %H:%M:%S')


# master/slave dba info
sock = ''
port = 3307
IP = '192.168.31.125'
user = 'root'
password = '123456'
dbschema = 'mysql'

# replication info
repl_password = '123456'

# zabbix server
zb_sender = '/usr/bin/zabbix_sender'
zb_server = '192.168.31.156'
zb_server_port = 10051

# zabbix agent
insname = 'MySQL_' + socket.gethostname()

# <----- Global Variables

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
# Some prepare work before scp or run command.
# ----------------------------------------------------------------------------------------
def own_initialize():
    """非公共初始化部分.

    """
    # 将db状态输出文件置空.
    with open(DBSTATUS_FILE, 'w') as f:
        f.write("")
        sys.exit(1)


# ----------------------------------------------------------------------------------------
# init dbs dict()
# ----------------------------------------------------------------------------------------
def init_dbins_info():
    dbins = {}  # db实例字典
    dbinfo = {}  # db信息字典
    dbinfo['global_var'] = {}  # db global variables 字典
    dbinfo['global_status'] = {}  # db global status 字典
    dbinfo['slave_status'] = {}  # db主从状态变量
    dbinfo['master_status'] = {}  # db从库对应主库状态变量
    dbinfo['last_status'] = {}  # db上一次状态数值字典
    dbinfo['cur_status_cal'] = {}  # db当前计算后状态变量
    dbinfo['server_status'] = 'on'  # dbserver 状态数值(是否active), 初始化为"on"
    dbinfo['port'] = port
    dbinfo['ip'] = IP
    dbinfo['user'] = user
    dbinfo['password'] = password
    dbinfo['dbschema'] = dbschema
    dbinfo['insname'] = insname

    dbins[insname] = copy.deepcopy(dbinfo)
    return dbins


# ----------------------------------------------------------------------------------------
# Class for DBStatus.
# ----------------------------------------------------------------------------------------
class DBStatus(object):
    """DB状态类.

    """

    def __init__(self):

        self.dbins = init_dbins_info()

        self.global_status = ('KEY_READS', 'KEY_READ_REQUESTS', 'KEY_WRITES', 'KEY_WRITE_REQUESTS', 'KEY_BLOCKS_UNUSED',
                              'INNODB_BUFFER_POOL_READS', 'INNODB_BUFFER_POOL_READ_REQUESTS',
                              'INNODB_BUFFER_POOL_READ_AHEAD', 'INNODB_BUFFER_POOL_PAGES_DATA',
                              'INNODB_BUFFER_POOL_PAGES_TOTAL', 'INNODB_BUFFER_POOL_WAIT_FREE', 'QCACHE_HITS',
                              'QCACHE_INSERTS',
                              'QCACHE_FREE_BLOCKS', 'QCACHE_TOTAL_BLOCKS', 'QCACHE_FREE_MEMORY', 'QUERY_CACHE_SIZE',
                              'BINLOG_CACHE_USE', 'BINLOG_CACHE_DISK_USE', 'OPEN_TABLES', 'OPENED_TABLES',
                              'CONNECTIONS', 'THREADS_CREATED', 'UPTIME',
                              'QUERIES', 'OPENED_TABLES', 'TABLE_LOCKS_IMMEDIATE', 'TABLE_LOCKS_WAITED',
                              'INNODB_ROW_LOCK_WAITS', 'INNODB_ROW_LOCK_TIME', 'CREATED_TMP_TABLES',
                              'CREATED_TMP_DISK_TABLES', 'SLOW_QUERIES', 'THREADS_CONNECTED',
                              'INNODB_ROWS_DELETED', 'INNODB_ROWS_INSERTED', 'INNODB_ROWS_READ', 'INNODB_ROWS_UPDATED',
                              'CREATED_TMP_DISK_TABLES', 'CREATED_TMP_FILES', 'CREATED_TMP_TABLES',
                              'MAX_USED_CONNECTIONS', 'COM_ROLLBACK', 'COM_COMMIT', 'COM_ROLLBACK_TO_SAVEPOINT',
                              'HANDLER_ROLLBACK')

        self.slave_status = (
            'Last_Error', 'Seconds_Behind_Master', 'Master_Host', 'Master_User', 'Master_Port', 'Master_Log_File',
            'Read_Master_Log_Pos', 'Replicate_Do_DB', 'Exec_Master_Log_Pos', 'Master_Server_Id',
            'Last_SQL_Error', 'Relay_Master_Log_File', 'Relay_Log_File', 'Replicate_Ignore_DB',
            'Last_IO_Error', 'Last_Errno', 'Master_Host', 'Slave_SQL_Running', 'Relay_Log_Pos',
            'Last_IO_Errno', 'Slave_IO_Running', 'Last_SQL_Errno')

        self.master_status = ('File', 'Position', 'Executed_Gtid_Set')

        self.master_slave_info = ('Master_id', 'Server_id')

        self.trycount = 5

    # ------------------------------------------------------------------------------------
    # Get last db status
    # ------------------------------------------------------------------------------------
    def get_last_status(self):
        """获取前一时间点的状态数据
        """
        try:
            with open(LAST_DBSTATUS_FILE, 'r') as f:
                for row in f:
                    if not re.match(r"#.*|^$", row):
                        # 如果不是空行或注释行
                        db = row.split('.')[0]
                        var = row.split('.')[1].split('=')[0]
                        value = row.split('=')[1]

                        try:
                            self.dbins[db]['last_status'][var] = float(value)
                        except ValueError:
                            self.dbins[db]['last_status'][var] = value
                        except KeyError:
                            raise IOError
        except IOError:
            # 处理上一次状态数值文件不存在的情况，缺省将上一次的状态数值都置为0.
            for db in self.dbins:
                for var in self.global_status:
                    self.dbins[db]['last_status'][var] = 0

    # ------------------------------------------------------------------------------------
    # Get global variables, global status, slave status.
    # ------------------------------------------------------------------------------------
    def get_status_var(self):
        """获取全局状态变量,系统变量,复制状态变量,从库对应主库状态变量.
        """
        for db in self.dbins.values():
            is_master = ""
            try:
                self.conn = MySQLdb.connect(host=db['ip'], port=db['port'], user=db['user'], passwd=db['password'], db=db['dbschema'],
                                            charset='utf8') 
            except MySQLdb.OperationalError, e:
                print e
                continue
            # 判断实例是否存活
            self.cur = self.conn.cursor()
            sql = "select 10*10;"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            if rows[0][0] != 100:
                db['server_status'] = 'off'    

            # 全局状态变量
            # 
            self.cur = self.conn.cursor(MySQLdb.cursors.DictCursor)
#            sql = """SELECT * FROM performance_schema.GLOBAL_STATUS a 
#                     WHERE a.VARIABLE_NAME in %s""" % str(self.global_status)
            sql = "show global status;"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            for row in rows:
                try:
                    db['global_status'][row['Variable_name'].upper()] = float(row['Value'])
                except ValueError:
                    db['global_status'][row['Variable_name'].upper()] = row['Value']
                if row['Variable_name'].upper() not in self.global_status:
                    del db['global_status'][row['Variable_name'].upper()]
            
            self.cur.close()

            # 获取复制的状态变量
            try:
                self.cur = self.conn.cursor(MySQLdb.cursors.DictCursor)
                sql = "show slave status;"
                self.cur.execute(sql)
                rows = self.cur.fetchall()
                db['slave_status'] = rows[0].copy()
                for key in rows[0]:
                    if key not in self.slave_status:
                        del db['slave_status'][key]
                for (key, value) in db['slave_status'].items():
                    if value == '' :
                        db['slave_status'][key] = 'something'
            except IndexError:
                # 处理数据库不是从库(不存在复制状态变量)的情况
                is_master = 1
                pass
            self.cur.close()

            # 获取全局系统变量
            self.cur = self.conn.cursor()
            sql = "SELECT * FROM performance_schema.GLOBAL_VARIABLES"
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            for row in rows:
                try:
                    db['global_var'][row[0].upper()] = float(row[1])
                except ValueError:
                    db['global_var'][row[0].upper()] = row[1]
            self.cur.close()
            self.conn.close()

            # 获取主库状态变量
            if not is_master:
                mip = db['slave_status']['Master_Host']
                muser = db['slave_status']['Master_User']
                mport = db['slave_status']['Master_Port']

                try:
                    # 复制用户密码
                    self.conn1 = MySQLdb.connect(mip, muser, repl_password, port=mport, compress=1, charset='utf8')

                except MySQLdb.OperationalError, e:
                    print e
                    continue
                # 获取对应主库状态变量
                try:
                    self.cur = self.conn1.cursor(MySQLdb.cursors.DictCursor)
                    master_sql = "show master status;"
                    master_slave_host = "show slave hosts;"
                    self.cur.execute(master_sql)
                    rows = self.cur.fetchall()
                    db['master_status'] = rows[0].copy()
                    for key in rows[0]:
                        if key not in self.master_status:
                            del db['master_status'][key]
                except Exception, e:
                    print e
                self.cur.close()
                self.conn1.close()

    # -----------------------------------------------------------------------------
    # Calculate current status value
    # -----------------------------------------------------------------------------
    def cal_cur_status(self):
        """计算当前状态变量数值
        """
        for db in self.dbins.values():
            db['cur_status_cal']['ip'] = db['ip']
            db['cur_status_cal']['port'] = db['port']
            db['cur_status_cal']['insname'] = db['insname']

            # other calculate
            # 计算当前从库传输的二进制日志与主库日志的差值
            try:
                db['slave_status']['Binlog_File_Diff'] = \
                    int(db['master_status']['File'][10:]) - int(db['slave_status']['Master_Log_File'][10:])
            except KeyError:
                pass

            # 性能参数
            try:
                try:
                    # 键缓存读命中率
                    db['cur_status_cal']['Key_buffer_read_hits'] = \
                        1 - (db['global_status']['KEY_READS'] - db['last_status']['KEY_READS']) / \
                        ((db['global_status']['KEY_READ_REQUESTS'] - db['last_status']['KEY_READ_REQUESTS']))
                except ZeroDivisionError:
                    db['cur_status_cal']['Key_buffer_read_hits'] = 1

                try:
                # 键缓存写命中率
                    db['cur_status_cal']['Key_buffer_write_hits'] = \
                    1 - (db['global_status']['KEY_WRITES'] - db['last_status']['KEY_WRITES'] / \
                         ((db['global_status']['KEY_WRITE_REQUESTS'] - db['last_status']['KEY_WRITE_REQUESTS']) + (db['global_status']['KEY_WRITES'] - db['last_status']['KEY_WRITES'])))
                except ZeroDivisionError:
                    db['cur_status_cal']['Key_buffer_write_hits'] = 1

                # 键缓存使用百分比
                db['cur_status_cal']['Key_buffer_used_pct'] = 1 - (db['global_status']['KEY_BLOCKS_UNUSED'] * db['global_var']['KEY_CACHE_BLOCK_SIZE']) / db['global_var']['KEY_BUFFER_SIZE']

                try:
                    # innodb 缓冲池读命中率
                    db['cur_status_cal']['Innodb_buffer_pool_hits'] = \
                        1 - (db['global_status']['INNODB_BUFFER_POOL_READS'] - db['last_status'][
                            'INNODB_BUFFER_POOL_READS']) / \
                        ((db['global_status']['INNODB_BUFFER_POOL_READ_REQUESTS'] - db['last_status'][
                            'INNODB_BUFFER_POOL_READ_REQUESTS'] +
                          (db['global_status']['INNODB_BUFFER_POOL_READS'] - db['last_status'][
                              'INNODB_BUFFER_POOL_READS']) +
                          (db['global_status']['INNODB_BUFFER_POOL_READ_AHEAD'] - db['last_status'][
                              'INNODB_BUFFER_POOL_READ_AHEAD'])))
                except ZeroDivisionError:
                    db['cur_status_cal']['Innodb_buffer_pool_hits'] = 1

                # innodb 缓冲池已使用百分比
                db['cur_status_cal']['Innodb_buffer_pool_used_pct'] = \
                    db['global_status']['INNODB_BUFFER_POOL_PAGES_DATA'] / db['global_status'][
                        'INNODB_BUFFER_POOL_PAGES_TOTAL']

                # innodb缓冲池等待干净页次数
                db['cur_status_cal']['Innodb_buffer_pool_wait_free'] = int(
                    db['global_status']['INNODB_BUFFER_POOL_WAIT_FREE'] - db['last_status'][
                        'INNODB_BUFFER_POOL_WAIT_FREE'])

                try:
                    # 查询缓存命中率
                    db['cur_status_cal']['Qcache_hits'] = \
                        (db['global_status']['QCACHE_HITS'] - db['last_status']['QCACHE_HITS']) / \
                        ((db['global_status']['QCACHE_HITS'] - db['last_status']['QCACHE_HITS']) + (
                                db['global_status']['QCACHE_INSERTS'] - db['last_status']['QCACHE_INSERTS']))
                except ZeroDivisionError:
                    db['cur_status_cal']['Qcache_hits'] = 0

                try:
                    # 查询缓存碎片百分比
                    db['cur_status_cal']['Qcache_fragments'] = \
                        round(db['global_status']['QCACHE_FREE_BLOCKS'] / db['global_status']['QCACHE_TOTAL_BLOCKS'], 2)
                except ZeroDivisionError:
                    db['cur_status_cal']['Qcache_fragments'] = 0

                try:
                    # 查询缓存已使用百分比
                    db['cur_status_cal']['Qcache_used_pct'] = \
                        1 - db['global_status']['QCACHE_FREE_MEMORY'] / db['global_var']['QUERY_CACHE_SIZE']
                except ZeroDivisionError:
                    db['cur_status_cal']['Qcache_used_pct'] = 0

                try:
                    # 二进制日志缓冲的命中率
                    db['cur_status_cal']['Binlog_buffer_hits'] = \
                        (db['global_status']['BINLOG_CACHE_USE'] - db['last_status']['BINLOG_CACHE_USE']) / \
                        ((db['global_status']['BINLOG_CACHE_USE'] - db['last_status']['BINLOG_CACHE_USE']) +
                         (db['global_status']['BINLOG_CACHE_DISK_USE'] - db['last_status']['BINLOG_CACHE_DISK_USE']))
                except ZeroDivisionError:
                    db['cur_status_cal']['Binlog_buffer_hits'] = 1

                # 表打开百分比
                db['cur_status_cal']['Open_tables_pct'] = int(db['global_status']['OPEN_TABLES']) / int(
                    db['global_status']['OPENED_TABLES'])

                # 打开过多少表
                db['cur_status_cal']['Opened_tables'] = int(
                    db['global_status']['OPENED_TABLES'] - db['last_status']['OPENED_TABLES'])

                try:
                    # 线程失败的缓存命中率
                    db['cur_status_cal']['Thread_cache_hits'] = \
                        ((db['global_status']['CONNECTIONS'] - db['last_status']['CONNECTIONS']) - (
                                db['global_status']['THREADS_CREATED'] - db['last_status']['THREADS_CREATED'])) / \
                        (db['global_status']['CONNECTIONS'] - db['last_status']['CONNECTIONS'])
                except ZeroDivisionError:
                    db['cur_status_cal']['Thread_cache_hits'] = 1

                try:
                    # QPS
                    db['cur_status_cal']['QPS'] = \
                        (db['global_status']['QUERIES'] - db['last_status']['QUERIES']) / (
                                db['global_status']['UPTIME'] - db['last_status']['UPTIME'])
                except ZeroDivisionError:
                    db['cur_status_cal']['QPS'] = "Warning: interval should larger than 1 second"

                try:
                    # TPS
                    db['cur_status_cal']['TPS'] = \
                        (db['global_status']['COM_COMMIT'] - db['last_status']['COM_COMMIT']) + (
                                db['global_status']['COM_ROLLBACK'] - db['last_status']['COM_ROLLBACK']) \
                        + (db['global_status']['COM_ROLLBACK_TO_SAVEPOINT']) - db['last_status'][
                            'COM_ROLLBACK_TO_SAVEPOINT'] / (db['global_status']['UPTIME'] - db['last_status']['UPTIME'])
                except ZeroDivisionError:
                    db['cur_status_cal']['TPS'] = "Warning: interval should larger than 1 second"

                # 立即获得表锁的次数
                db['cur_status_cal']['Table_locks_immediate'] = int(
                    db['global_status']['TABLE_LOCKS_IMMEDIATE'] - db['last_status']['TABLE_LOCKS_IMMEDIATE'])

                # 需要等待获得表锁的数量
                db['cur_status_cal']['Table_locks_waited'] = int(
                    db['global_status']['TABLE_LOCKS_WAITED'] - db['last_status']['TABLE_LOCKS_WAITED'])

                # 当前等待过的行锁数量
                db['cur_status_cal']['Innodb_row_lock_current_waited'] = int(
                    db['global_status']['INNODB_ROW_LOCK_WAITS'] - db['last_status']['INNODB_ROW_LOCK_WAITS'])

                try:
                    # 当前行锁锁定的平均时间
                    db['cur_status_cal']['Innodb_row_lock_cur_avg_time'] = \
                        (db['global_status']['INNODB_ROW_LOCK_TIME'] - db['last_status']['INNODB_ROW_LOCK_TIME']) / \
                        db['cur_status_cal']['Innodb_row_lock_current_waited'] / 1000
                except ZeroDivisionError:
                    db['cur_status_cal']['Innodb_row_lock_cur_avg_time'] = 0

                # 内存中创建的临时表数量
                db['cur_status_cal']['Created_mem_tmp_tables'] = int(
                    db['global_status']['CREATED_TMP_TABLES'] - db['last_status']['CREATED_TMP_TABLES'])

                # 使用内存创建临时表的百分比
                db['cur_status_cal']['Created_mem_tmp_tables_pct'] = \
                    db['cur_status_cal']['Created_mem_tmp_tables'] / (
                            db['cur_status_cal']['Created_mem_tmp_tables'] + db['global_status'][
                        'CREATED_TMP_DISK_TABLES'] - db['last_status']['CREATED_TMP_DISK_TABLES'])

                # 慢查询数量
                db['cur_status_cal']['Slow_queries'] = int(db['global_status']['SLOW_QUERIES'] - db['last_status']['SLOW_QUERIES'])

                # 当前连接数
                db['cur_status_cal']['Threads_connected'] = int(db['global_status']['THREADS_CONNECTED'])

                # 已使用连接数百分比
                db['cur_status_cal']['Threads_connected_pct'] = float(db['global_status']['THREADS_CONNECTED']) / float(db['global_var']['MAX_CONNECTIONS']) 

                # innodb删除行数量
                db['cur_status_cal']['Innodb_rows_deleted'] = \
                    (db['global_status']['INNODB_ROWS_DELETED'] - db['last_status']['INNODB_ROWS_DELETED']) / (db['global_status']['UPTIME'] - db['last_status']['UPTIME'])

                # innodb插入行数量
                db['cur_status_cal']['Innodb_rows_inserted'] = \
                    (db['global_status']['INNODB_ROWS_INSERTED'] - db['last_status']['INNODB_ROWS_INSERTED']) / (db['global_status']['UPTIME'] - db['last_status']['UPTIME'])

                # innodb读取行数量
                db['cur_status_cal']['Innodb_rows_read'] = \
                    (db['global_status']['INNODB_ROWS_READ'] - db['last_status']['INNODB_ROWS_READ']) / (db['global_status']['UPTIME'] - db['last_status']['UPTIME'])

                # innodb更新行数量
                db['cur_status_cal']['Innodb_rows_updated'] = \
                    (db['global_status']['INNODB_ROWS_UPDATED'] - db['last_status']['INNODB_ROWS_UPDATED']) / (db['global_status']['UPTIME'] - db['last_status']['UPTIME'])

                # 创建磁盘临时表数
                db['cur_status_cal']['Created_tmp_disk_tables'] = \
                    db['global_status']['CREATED_TMP_DISK_TABLES'] - db['last_status']['CREATED_TMP_DISK_TABLES']

                # 创建临时文件数
                db['cur_status_cal']['Created_tmp_files'] = \
                    db['global_status']['CREATED_TMP_FILES'] - db['last_status']['CREATED_TMP_FILES']

                # 创建基于内存临时表数
                db['cur_status_cal']['Created_tmp_tables'] = \
                    db['global_status']['CREATED_TMP_TABLES'] - db['last_status']['CREATED_TMP_TABLES']

                # 曾经最高连接数
                db['cur_status_cal']['Max_used_connections'] = db['global_status']['MAX_USED_CONNECTIONS']

                # 主动执行rollback语句数
                db['cur_status_cal']['Com_rollback'] = \
                    db['global_status']['COM_ROLLBACK'] - db['last_status']['COM_ROLLBACK']

                # 内部rollback语句数
                db['cur_status_cal']['Handler_rollback'] = \
                    db['global_status']['HANDLER_ROLLBACK'] - db['last_status']['HANDLER_ROLLBACK']
            except KeyError:
                print   db['insname'] + " hasn't last_status and it's db_status will be calculated next time,\n or db is infinidb."
#            print "=============global_var"
#            print db['global_var']
#            print "=============last_status"
#            print db['last_status']
#            print "=============global_status"
#            print db['global_status']
#            print "=============slave_status"
#            print db['slave_status']
#            print "===================cur_status_cal"
#            print db['cur_status_cal']
    # ------------------------------------------------------------------------
    # Write calculated result into  db status file.
    # ------------------------------------------------------------------------
    def write_result_file(self):
        """将计算结果写入db状态输出文件.
        """
        with open(DBSTATUS_FILE, 'w') as f:
            f.write("#" + str(DATETIME) + "\n\n")
            f.write("start_utime =" + str(int(time.mktime(time.strptime(DATETIME, '%Y-%m-%d %H:%M:%S')))) + "\n\n") 
            dbs = self.dbins.values() # 获取db实例名字
            dbs.sort()
            for status_type in ('cur_status_cal','slave_status'):
                f.write("# " + "-"*20 + ' ' + status_type + ' ' + "-"*20 + "\n")
                for (key, value) in dbs[0][status_type].items():
                    f.write(insname + '.' + str(key) + '=' + str(value) + "\n")
            f.write("# " + "-"*20 + ' ' + 'server_status' + ' ' + "-"*20 + "\n")
            f.write(insname + "." + 'server_status' + "=" + dbs[0]['server_status'] + "\n")
            print "\n"


    # ------------------------------------------------------------------------
    # Write global status  into last status file.
    # ------------------------------------------------------------------------
    def write_before_file(self):
        """将global status写入上一次db状态数值文件.
        """
        with open(LAST_DBSTATUS_FILE, 'w') as f:
            f.write("# " + str(DATETIME) + "\n\n")
            for db in self.dbins:
                f.write("# " + "-"*50 + "\n")
                for (key, value) in self.dbins[db]['global_status'].items():
                    f.write(db + "." + str(key) + "=" + str(value) + "\n")
            f.write("\n\n")

    # ------------------------------------------------------------------------
    # Push zabbix
    # ------------------------------------------------------------------------
    def push_zabbix_items(self):
        """zabbix sender into  zb template items
        """
        # zabbix_sender -z 192.168.31.156 -p 10051 -s "MySQL_mysql2" -k "QPS" -o 1000
        dbs = self.dbins.values()
        dbs.sort()
        print "push ********************************"
        for status_type in ('cur_status_cal','slave_status'):
            for (key, value) in dbs[0][status_type].items():
                zb_sender_cmd = ('%s -z %s -p %d -s %s -k %s -o %s') % (zb_sender, zb_server, zb_server_port, insname, str(key), str(value))
                print zb_sender_cmd
                try:
                    sender_cmd = runCmd(zb_sender_cmd)
                except Exception, e:
                    print str(e)

                if sender_cmd[1] == 0:
                    print str(key) + "    sucessed"
                else:
                    print str(key) + "     failed"

        zb_sender_cmd2 = ('%s -z %s -p %d -s %s -k "server_status" -o %s') % (zb_sender, zb_server, zb_server_port, insname, dbs[0]['server_status'])
        print zb_sender_cmd2
        sender_cmd2 = runCmd(zb_sender_cmd2)
        if sender_cmd2[1] == 0:
            print "server_status" + "    sucessed"
        else:
            print "server_status" + "     failed"


    # ------------------------------------------------------------------------
    # Write cur_status_cal, slave status , master status , into DB tables
    # ------------------------------------------------------------------------
    def write_status_tbl():
        pass

if __name__ == '__main__':
    # dbins = init_dbins_info()
    moniter = DBStatus()
    moniter.get_status_var()
    moniter.get_last_status()
    moniter.cal_cur_status()
    moniter.write_result_file()
    moniter.write_before_file()
    moniter.push_zabbix_items()
