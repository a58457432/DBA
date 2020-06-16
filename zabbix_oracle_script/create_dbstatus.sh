#!/bin/bash
#

sudo su - oracle <<EOF> /usr/local/webserver/zabbix_oracle_script/dbstatus.log    
sh /usr/local/webserver/zabbix_oracle_script/oracle_user_script/check_ora.sh
EOF
