#!/bin/bash
#
# mongodb backup
#
# author: shenjinhong 
# Date created: 2025-03-04



# Export directory
EXPORT_DIR="/data/backup/*" 

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
    done | sort -rn | head -n 7 | while read -r line; do
    # 提取目录名
        dir=$(echo "$line" | cut -d' ' -f 2-)
        echo "$dir"
    done
}




main(){
find_the_latest_dir
}

main
