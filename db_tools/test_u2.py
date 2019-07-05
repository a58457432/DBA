#!/usr/bin/env python
## coding=utf-8
# Creator: shenjinhong
# UpdateTime:2019.6.10

from urllib import request

proxy_handler = request.ProxyHandler({'http':'http://172.20.20.65:10080'})
url = 'http://10.6.2.235:10080/dbbridge/uid/get?num=4'

opener = request.build_opener(proxy_handler)
r = opener.open(url)
print(str(r.read(), encoding='utf-8'))

print(dir(opener))
