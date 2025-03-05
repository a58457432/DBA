#!/bin/bash
#
# mongodb backup
#
# author: shenjinhong 
# Date created: 2025-03-03

backup_cmd='/usr/local/mongodb-tools/bin/mongodump'
mongodb_host="192.168.217.129"
mongodb_port=27017
mongodb_user="test"
mongodb_password="test2025"
mongodb_database="mutms"
dtime=`date "+%Y%m%d-%H-%M"`

# dump collections
COLLECTIONS=("APPVersionUpgradeRecord" "BizVersionUpgradeRecord" "OtaChannelAdminInfo" "OtaChannelInfo" "OtaChannelRecord" "PlatformVersionControlRuleConfig" "ProductZone")

# Export directory
EXPORT_DIR="/data/backup/" 


# mongodump --host 192.168.217.129 --port 27017 --username test --password test2025 --db mutms --collection APPVersionUpgradeRecord --out /data/backup/APPVersionUpgradeRecord_20250303

mongodb_backup(){
for collection in "${COLLECTIONS[@]}";do
    echo $collection
    $backup_cmd --host $mongodb_host --port $mongodb_port --username $mongodb_user --password $mongodb_password --db $mongodb_database --collection $collection  --out $EXPORT_DIR$collection$dtime
done
}

del_dir(){
find "$EXPORT_DIR" -type d -mtime +7 -exec rm -rf {} \;
}


main(){
    mongodb_backup
    del_dir
}

main
