#!/usr/bin/env python
## coding=utf-8
# Creator: shenjinhong
# UpdateTime:2019.6.10

from urllib import request
from urllib import parse

#proxies = {'http':'http://172.20.20.65:10080'}
proxy_handler = request.ProxyHandler({'http':'http://172.20.20.65:10080'})
opener = request.build_opener(proxy_handler)

sql = 'select now();'
#sql = "insert into school values(2,'wwg');"
url = "http://10.6.2.235:10080/dbbridge/sql/dosql"
data = bytes(sql, encoding='utf-8')

req = request.Request(url, data=data)
page = request.urlopen(req).read()
page = page.decode('utf-8')

print(page)
