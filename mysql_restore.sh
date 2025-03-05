#!/bin/bash
#
# mysql backup
#
# author: shenjinhong 
# Date created: 2025-03-05

#target mysql
mysql_cmd="/usr/local/mysql/bin/mysql"
target_mysql_host="192.168.217.129"
target_mysql_port=3306
target_mysql_database="mutms"
target_mysql_user="uws_mutms"
target_mysql_password="G8?d9_ZZh2jn"



# Export directory
EXPORT_DIR="/data/backup/mysql/*" 

find_the_latest_dir(){

    # 用于存储目录及其修改时间的数组
    declare -A dir_times

    # 遍历当前目录下的所有目录
    for dir in $EXPORT_DIR; do
    # 获取目录的修改时间
        mtime=$(stat -c %Y "$dir")
    # 将目录及其修改时间存入关联数组
        dir_times["$dir"]=$mtime
    done

    # 对关联数组按照修改时间进行排序
    for dir in "${!dir_times[@]}"; do
        echo "${dir_times[$dir]} $dir"
    done | sort -rn | head -n 2 | while read -r line; do
    # 提取目录名
        dir=$(echo "$line" | cut -d' ' -f 2-)
        echo "$dir"
    done
}

# mysql -uuws_mutms -p"G8?d9_ZZh2jn" -h 192.168.217.129 -P3306 mutms < /data/backup/mysql/mutms20250304-21-55.sql
restore_mysql(){
# 调用函数并将结果存储到数组中
latest_dirs=($(find_the_latest_dir))

#打印数组元素进行验证
for dir in "${latest_dirs[@]}"; do
    result=$(echo "$dir" | awk -F '/mysql/|202' '{print $2}')
    if [ "$result" = "mutms" ]; then
        echo $result
        echo $dir
        $mysql_cmd -u$target_mysql_user -p$target_mysql_password -h $target_mysql_host -P$target_mysql_port $target_mysql_database < $dir
    fi
done
}


# mysql -uuws_mutms -p"G8?d9_ZZh2jn" mutms < three_tables_no_data20250304-21-55.sql  
restore_mysql_nodata(){
# 调用函数并将结果存储到数组中
latest_dirs=($(find_the_latest_dir))

#打印数组元素进行验证
for dir in "${latest_dirs[@]}"; do
    #echo "$dir"
    result=$(echo "$dir" | awk -F '/mysql/|202' '{print $2}')
    if [ "$result" = "three_tables_no_data" ]; then
        echo $result
        echo "$dir"
        $mysql_cmd -u$target_mysql_user -p$target_mysql_password -h $target_mysql_host -P$target_mysql_port $target_mysql_database < $dir
    fi
done
}




# 检查是否提供了命令行参数
if [ $# -eq 0 ]; then
    echo "Error: You must specify a function to call. Valid options are 'restore_mysql', 'restore_mysql_nodata'."
    exit 1
fi

# 获取命令行参数
function_choice=$1

# 检查参数值是否合法
if [ "$function_choice" != "restore_mysql" ] && [ "$function_choice" != "restore_mysql_nodata" ] ; then
    echo "Error: Invalid function choice. Valid options are 'restore_mysql', 'restore_mysql_nodata'."
    exit 1
fi

# 根据参数值调用相应的函数
case $function_choice in
    restore_mysql)
        restore_mysql
        ;;
    restore_mysql_nodata)
        restore_mysql_nodata
        ;;
esac

