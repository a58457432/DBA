#!/usr/bin/env python
## coding=utf-8
# Creator: shenjinhong
# UpdateTime:2019.6.10

import platform
import socket
import psutil
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
import subprocess

slat_cmd="salt-run manage.up |awk -F '-' '{ print $2}'"
alive_list={}

def runCmd(cmd):
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    except:
        return None, p.returncode
    else:
        output, err = p.communicate()
        return output, p.returncode


def scan_list():
    b = []
    salt_list = runCmd(slat_cmd)
    lists = str((list(salt_list)[0]), encoding="utf-8")
    nlist = lists.split('\n')
    if salt_list[1] == 0:
        for i in nlist:    
            b.append(i.strip())
    if '' in b:
        b.remove('')
    print(b)
    return b

def main():
    scan_list()


if __name__ == '__main__':
    main()
