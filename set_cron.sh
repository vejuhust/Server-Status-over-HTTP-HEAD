#!/bin/sh

SSOHH_TAG=YOUR_PRIVATE_TAG_FOR_SSOHH

if [ $# -ge 1 ];
then
    ARCH="$1"
else
    ARCH=linux
fi

case $ARCH in
pi)
    MONITOR='"[ssohh] '$SSOHH_TAG'; [name] $(hostname); [note] regular_5min_pi; [network] $(/sbin/ifconfig | grep eth0 -A 1 | tail -1); [date] $(date); [uptime] $(uptime); [disk] $(df -h | grep / -m 1); [memory] $(cat /proc/meminfo | grep MemFree) / $(cat /proc/meminfo | grep MemTotal); [temperature] $(cat /sys/class/thermal/thermal_zone0/temp); "'
    ;;
bbb)
    MONITOR='"[ssohh] '$SSOHH_TAG'; [name] $(hostname); [note] regular_5min_bbb; [network] $(/sbin/ifconfig | grep eth0 -A 1 | tail -1); [date] $(date); [uptime] $(uptime); [disk] $(df -h | grep / -m 1); [memory] $(cat /proc/meminfo | grep MemFree) / $(cat /proc/meminfo | grep MemTotal); [temperature] $(cat /sys/class/hwmon/hwmon0/device/temp1_input); "'
    ;;
linux)
    MONITOR='"[ssohh] '$SSOHH_TAG'; [name] $(hostname); [note] regular_5min_linux; [network] $(/sbin/ifconfig | grep eth0 -A 1 | tail -1); [date] $(date); [uptime] $(uptime); [disk] $(df -h | grep / -m 1); [memory] $(cat /proc/meminfo | grep MemFree) / $(cat /proc/meminfo | grep MemTotal); "'
    ;;
mac)
    MONITOR='"[ssohh] '$SSOHH_TAG'; [name] $(hostname); [note] regular_5min_mac; [network] $(/sbin/ifconfig | grep en1 -A 1 | tail -1); [date] $(date); [uptime] $(uptime); [disk] $(df -h | grep / -m 1); [memory] $(top -l 1 | head -10 | grep PhysMem); "'
    ;;
*)
    echo "Invalid ARCH"
    exit 1
    ;;
esac

COMMAND='curl http://service.yewei.me/ -I -A "$(echo '$MONITOR' | sed -E "s/[[:space:]]+/ /gp")"'

(crontab -l ; echo "*/5 * * * * $COMMAND") | uniq - | crontab -
