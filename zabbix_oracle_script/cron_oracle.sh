#!/bin/bash
#


sh_cmd=`which sh`
python_cmd=`which python`

script_home='/usr/local/webserver/DBA/zabbix_oracle_script'

$sh_cmd /usr/local/webserver/DBA/zabbix_oracle_script/create_dbstatus.sh

$python_cmd /usr/local/webserver/DBA/zabbix_oracle_script/get_oracle_status.py


