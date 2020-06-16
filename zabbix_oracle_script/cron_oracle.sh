#!/bin/bash
#


sh_cmd=`which sh`
python_cmd=`which python`

script_home='/usr/local/webserver/zabbix_oracle_script'

$sh_cmd $script_home/create_dbstatus.sh

$python_cmd $script_home/get_oracle_status.py


