#!/bin/env /usr/bin/python
# -*- coding: utf-8 -*-
#
#    (C) 21vianet Inc.
#
#    Last update: sjh 2021-02-04

""" Run CMD or SCP In Batch Mode

You can choose project type, area  to run command or upload file.
Output info will print to script.info.

"""

__authors__ = [
    '"sjh"',
    ]

import os
import sys
import redis
import subprocess

dbconfig = {}
dbconfig['host'] = '172.21.107.8'
dbconfig['port'] = 6379
dbconfig['passwd'] = 'Ecology2020!'
insname = 'redis_107_8_6379'

#zabbix
zb_sender = '/usr/bin/zabbix_sender'
zb_server = '10.21.3.60'
zb_server_port = 10051



def runCmd(cmd):
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    except:
        return None, p.returncode
    else:
        output, err = p.communicate()
        return output, p.returncode


def calc_redis_status():
    redis_info = {}
    conn = redis.Redis(host=dbconfig['host'],port=dbconfig['port'],password=dbconfig['passwd'])
    redis_status = conn.info()
    # status
    redis_info['instantaneousopsper_sec'] = redis_status['instantaneous_ops_per_sec']
    redis_info['hit_rate'] = (redis_status['keyspace_hits']/(redis_status['keyspace_hits']+redis_status['keyspace_misses'])) * 100
    redis_info['used_memory_M'] = redis_status['used_memory_rss']/1024/1024
    redis_info['total_net_input_M'] = round(float(redis_status['total_net_input_bytes'])/1024/1024,2)
    redis_info['total_net_output_M'] = round(float(redis_status['total_net_output_bytes'])/1024/1024,2)
    redis_info['connected_clients'] = redis_status['connected_clients']
    redis_info['rejected_connections'] = redis_status['rejected_connections']
    redis_info['keyspace_misses'] = redis_status['keyspace_misses']

    print(redis_info)

    return redis_info


def push_zabbix_items():
    redis_info = calc_redis_status()
    for (key, value) in redis_info.items():
        zb_sender_cmd = ('%s -z %s -p %d -s %s -k %s -o %s') % (zb_sender, zb_server, zb_server_port, insname, str(key), str(value))
        print(zb_sender_cmd)
    
        try:
            sender_cmd = runCmd(zb_sender_cmd)
        except Exception, e:
            print str(e)

        if sender_cmd[1] == 0:
            print str(key) + "    sucessed"
        else:
            print str(key) + "     failed"


if __name__ == '__main__':             
#    calc_redis_status()
    push_zabbix_items()
