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


config = {}
config['http'] = 'http://172.20.20.65:10080'
config['url'] = 'http://10.6.2.235:10080/dbbridge/sql/dosql'

class dosql():

    def commit_sql(self,sql):
        proxy_handler = request.ProxyHandler({'http':config['http']})
        opener = request.build_opener(proxy_handler)
        url = config['url']
        data = bytes(sql, encoding='utf-8')
    
        req = request.Request(url, data=data)
        page = request.urlopen(req).read()
        page = page.decode('utf-8')
        print(page)

def main():
    a = dosql()
    a.commit_sql('select now();')

if __name__ == '__main__':             
    main()
