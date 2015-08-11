#!/bin/sh

curl http://service.yewei.me/ -I -A "[ssohh] $SSOHH_TOKEN; $(echo "[name] $(hostname); [note] dev_pi; [network] $(/sbin/ifconfig | grep eth0 -A 1 | tail -1); [date] $(date); [uptime] $(uptime); [disk] $(df -h | grep / -m 1); [memory] $(cat /proc/meminfo | grep MemFree) / $(cat /proc/meminfo | grep MemTotal); [temperature] $(cat /sys/class/thermal/thermal_zone0/temp); " | sed -E "s/[[:space:]]+/ /gp")"
