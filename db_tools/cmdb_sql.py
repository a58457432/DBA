#!/usr/bin/env python
## coding=utf-8
# Creator: shenjinhong
# UpdateTime:2019.7.5


import datetime
#from datetime import datetime
import re
import copy
from os import path
import sys
import time
import socket
import os
try:
    import json
except:
    import simplejson as json
from urllib import request
from urllib import parse





class dosql():
    
    def __init__(self,p_host,p_port,t_host,t_port):
        self.p_host = p_host
        self.p_port = p_port
        self.t_host = t_host
        self.t_port = t_port

    def commit_sql(self,sql):
        proxy_handler = request.ProxyHandler({'http':'http://172.20.20.65:10080'})
        opener = request.build_opener(proxy_handler)
        url = "http://10.6.2.235:10080/dbbridge/sql/dosql"
        data = bytes(sql, encoding='utf-8')
    
        req = request.Request(url, data=data)
        page = request.urlopen(req).read()
        page = page.decode('utf-8')
        print(page)

a = dosql('172.20.20.65','10080','10.6.2.235','10080')
a.commit_sql('select now();')
