#!/bin/bash
#

sudo su - oracle <<EOF> /usr/local/webserver/DBA/zabbix_oracle_script/dbstatus.log    
sh /home/oracle/script/check_ora.sh
EOF
