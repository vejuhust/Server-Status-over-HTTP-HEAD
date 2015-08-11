#!/bin/sh

curl http://service.yewei.me/ -I -A "[ssohh] $SSOHH_TOKEN; $(echo "[name] $(hostname); [note] dev_bbb; [network] $(/sbin/ifconfig | grep eth0 -A 1 | tail -1); [date] $(date); [uptime] $(uptime); [disk] $(df -h | grep / -m 1); [memory] $(cat /proc/meminfo | grep MemFree) / $(cat /proc/meminfo | grep MemTotal); [temperature] $(cat /sys/class/hwmon/hwmon0/device/temp1_input); " | sed -E "s/[[:space:]]+/ /gp")"
