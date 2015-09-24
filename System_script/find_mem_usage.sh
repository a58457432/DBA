#!/bin/bash
#
# find mem usage

usage() {
echo "Usage: $0 [ types... ] [ limit ] "
echo ""
echo "Types are:"
echo "[ Size ] [ Rss ] [ Swap ] [ Private ] [ Shared ]"
echo ""
printf "%-12s%-12s\n" "[ Size ]" "程序映射的内存大小，非实际占用"
printf "%-12s%-12s\n" "[ Rss ]" "实际使用内存大小（包括独占+共享）"
printf "%-12s%-12s\n" "[ Swap ]" "使用的虚拟内存大小"
printf "%-12s%-12s\n" "[ Private ]" "程序独占内存大小"
printf "%-12s%-12s\n" "[ Shared ]" "程序与其他进程共享内存大小"
echo ""
echo "For example : $0 Swap 10"
echo ""
}


mem() {
printf "%-20s%-100s%-20s%-20s\n" "PID" "PRO_NAME" "SIZE(m)" "%RATIO"
for pid in `ls /proc/ |grep ^[0-9]`
do

  if [ ${pid} -eq 1 ];then
    continue
  fi

grep -q $1 /proc/${pid}/smaps 2>/dev/null

  if [ $? -eq 0 ];then
    memsize=`free -m |grep "Mem" |awk '{print $2}'`
    swapsize=`free -m |grep "Swap" |awk '{print $2}'`
    size=`cat /proc/$pid/smaps |grep $1 |awk '{sum+=$2;} END{print sum/1024}'`
    pro_name=`ps aux | grep -w "$pid" | grep -v grep  |awk '{print $11}'`
    ratioval() {
    if [ '$1' = Swap ];then
      ratio=`awk "BEGIN{print $size/$swapsize*100 \"%\"}"`
    else
      ratio=`awk "BEGIN{print $size/$memsize*100 \"%\"}"`
    fi
      echo $ratio
    }
    ratioval
    printf "%-20s%-100s%-20s%-20s\n" "${pid}" "${pro_name}" "${size}" "$ratio"

  fi
done | sort -n -r -k 3  | head -$2
}


if [ $# -eq 0 ]; then  
    usage  
 else
    mem $1 $2
fi
