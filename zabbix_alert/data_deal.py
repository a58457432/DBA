#!/usr/local/python3/bin/python3
# -*- coding:utf-8 -*-

import sys
sys.path.append('/usr/local/webserver/DBA/zabbix_alert')

import excel_operation
import mydeal
from configparser import ConfigParser
import json
from collections import defaultdict

excel_path = '/root/monitor_server_list_20230405.xlsx'
alert_relationship_sheet_name = 'Server List'
alert_first_header = '编号'
alert_headerlist = {
    'name':'Nost Name',
    'ip':'IP Address',
    'ping_wechat_users':'PING微信联系人',
    'ping_email_users':'PING邮件联系人',
    'ping_sms_users':'PING短信联系人',
    'performance_wechat_users': 'PERFORMANCE微信联系人',
    'performance_email_users': 'PERFORMANCE邮件联系人',
    'performance_sms_users': 'PERFORMANCE短信联系人',
    'application_wechat_users': 'APPLICATION微信联系人',
    'application_email_users': 'APPLICATION邮件联系人',
    'application_sms_users': 'APPLICATION短信联系人',
    'snmp_wechat_users': 'SNMP微信联系人',
    'snmp_email_users': 'SNMP邮件联系人',
    'snmp_sms_users': 'SNMP短信联系人',
}


def list_execl_data():
    alert_xl = excel_operation.excel_operation(excel_path, alert_relationship_sheet_name)
    alert_xl.first_header = alert_first_header
    alert_xl.headerlist = alert_headerlist
    
    alert_datas_list = alert_xl.get_excel_data()
    if alert_datas_list: return alert_datas_list

def session_db():
    conf = ConfigParser()
    conf.read('dbconfig.ini')
    host = conf.get("mysql", "host")
    port = conf.getint("mysql", "port")
    user = conf.get("mysql", "user")
    passwd = conf.get("mysql", "password")
    db = conf.get("mysql", "db")
    charset = conf.get("mysql", "charset")

    dbconfig = {}
    dbconfig['host'] = host
    dbconfig['port'] = port
    dbconfig['user'] = user
    dbconfig['passwd'] = passwd
    dbconfig['db'] = db
    dbconfig['charset'] = charset
    mydb = mydeal.MySQL(dbconfig)
    if mydb: return mydb
    
def select_user_id(username):
    id = ''
    table_name = 'User'
    mydb = session_db()
    cond_dict = {'name':'%s' % (username)}
    result = mydb.select(table_name, cond_dict, fields=["id"])
    
    for item in iter(result):
        for index, value in enumerate(item):
            id = value
    if id != '': return id


def select_hostname_id(hostname):
    host_id = ''
    table_name = 'HostName'
    mydb = session_db()
    cond_dict = {'name':'%s' % (hostname)}
    result = mydb.select(table_name, cond_dict, fields=["id"])
    
    for item in iter(result):
        for index, value in enumerate(item):
            host_id = value
    if host_id != '': return host_id

def select_tbl_id(tablename,name_value):
    table_id = ''
    table_name = '%s' % (tablename)
    mydb = session_db()
    cond_dict = {'name':'%s' % (name_value)}
    result = mydb.select(table_name, cond_dict, fields=["id"])
    
    for item in iter(result):
        for index, value in enumerate(item):
            table_id = value 
    if table_id != '': return table_id 


def insert_hostname_tbl():
    alert_datas_list = list_execl_data()
    list_name = []
    list_ip = []
    dict_name_ip = {}
    list_dict_ni = []
    tablename = 'HostName'
    
    mydb = session_db()

    for data_dict in alert_datas_list:
        if data_dict['name']: list_name.append(data_dict['name'])
        if data_dict['ip']: list_ip.append(data_dict['ip'])
        dict_name_ip['name'] = data_dict['name']
        dict_name_ip['ip'] = data_dict['ip']
        list_dict_ni.append(dict_name_ip)
        mydb.insert(tablename,dict_name_ip)

def insert_user_tbl():
    alert_datas_list = list_execl_data() 
    list_user = []
    dict_user = {}
    tablename = 'User'
    
    mydb = session_db()
    
    for data_dict in alert_datas_list:
        for key in data_dict:
            if key == 'name' or key == 'ip':
                continue
#            print(data_dict[key])
            list = data_dict[key].split(",")
            for i in list:
                list_user.append(i)
    myset = set(list_user)
    myset.discard('')
    for i in myset:
        dict_user['name'] = i
        mydb.insertone(tablename, dict_user)
#        print(dict_user)
#        print(alert_datas_list[data_dict])
#        list = alert_datas_list[data_dict].split(",")
#        for i in list:
#            list_user.append(i)
#    print(list_user)

def insert_tag_tbl():
    alert_datas_list = list_execl_data()
    list_tag = []
    dict_tag = {}
    tablename = 'UserTag'
    
    mydb = session_db()
    
    for data_dict in alert_datas_list:
#        print(data_dict)
        for key in data_dict:
            if key == 'name' or key == 'ip':
                continue
#            print(data_dict[key])
            list = data_dict[key].split(",")
            for i in list:
                if '_Tag' in i:
                    list_tag.append(i)
    myset = set(list_tag)
    myset.discard('')
    for i in myset:
        dict_tag['name'] = i
        mydb.insertone(tablename, dict_tag) 


def countstat():
    count = 0
    def inc():
        nonlocal count
        count += 1
        return count
    return inc


def insert_alert_list_table_tbl():
    alert_list_table_dict = {}
    single_lst = ''
    singleone_lst = []
    alert_all_lst = []
    alert_list_table_key = ["hostname_id", "user_id", "apptype_id", "alerttype_id"]
    table_name = 'Alert_List_Table'
    c = countstat()
    
    mydb = session_db()
    alert_datas_list = list_execl_data()        
    for alert_item in alert_datas_list: 
        for k,v in alert_item.items():
#            print(k,'=',v)
#            print("=======================================")
            if k == 'name':single_lst=v
            if k == 'ip' or k == 'name':
                continue
            lst = v.split(",")
#            print(lst)
            if len(lst) >= 1:
                for i in lst:
#                    print(k,'=',i)
#                    print(i,'=',k)
                    k_lst = k.split("_")
                    del k_lst[2]
#                    print(k_lst,i,single_lst)
                    s_str = single_lst
                    hostid = select_tbl_id('HostName',s_str)
                    userid = select_tbl_id('User', i)
                    appid = select_tbl_id('AppType', k_lst[0])
                    alertid = select_tbl_id('AlertType',k_lst[1])
                    idlst = [hostid,userid,appid,alertid]
                    alert_list_table_dict[alert_list_table_key[0]] = hostid
                    alert_list_table_dict[alert_list_table_key[1]] = userid
                    alert_list_table_dict[alert_list_table_key[2]] = appid
                    alert_list_table_dict[alert_list_table_key[3]] = alertid
#                    print(alert_list_table_dict)
#                    print(idlst)
                    n_list = [s_str,i,k_lst[0],k_lst[1]]
#                    print([s_str,i,k_lst[0],k_lst[1]])
                    mydb.insert(table_name, alert_list_table_dict)
                    
                    
        print("**********************%s**********************" % (c()))
                



if __name__ == "__main__":
#    insert_hostname_tbl()
#    insert_user_tbl()
#    insert_alert_list_table_tbl()
#    insert_tag_tbl()
