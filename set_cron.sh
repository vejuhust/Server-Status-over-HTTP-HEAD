#!/bin/sh

SSOHH_TAG=YOUR_PRIVATE_TAG_FOR_SSOHH
ENDPOINT=http://status.YourCustomDomain.com/
INTERVAL=5

if [ $# -ge 1 ];
then
    ARCH="$1"
else
    ARCH=linux
fi

case $ARCH in
    p|pi)
        MONITOR='"[ssohh] '$SSOHH_TAG'; [name] $(hostname); [note] regular_'$INTERVAL'min_pi; [network] $(/sbin/ifconfig | grep eth0 -A 1 | tail -1); [date] $(date); [uptime] $(uptime); [disk] $(df -h | grep / -m 1); [memory] $(cat /proc/meminfo | grep MemFree) / $(cat /proc/meminfo | grep MemTotal); [temperature] $(cat /sys/class/thermal/thermal_zone0/temp); "'
        ;;
    b|bbb)
        MONITOR='"[ssohh] '$SSOHH_TAG'; [name] $(hostname); [note] regular_'$INTERVAL'min_bbb; [network] $(/sbin/ifconfig | grep eth0 -A 1 | tail -1); [date] $(date); [uptime] $(uptime); [disk] $(df -h | grep / -m 1); [memory] $(cat /proc/meminfo | grep MemFree) / $(cat /proc/meminfo | grep MemTotal); [temperature] $(cat /sys/class/hwmon/hwmon0/device/temp1_input); "'
        ;;
    l|linux)
        MONITOR='"[ssohh] '$SSOHH_TAG'; [name] $(hostname); [note] regular_'$INTERVAL'min_linux; [network] $(/sbin/ifconfig | grep eth0 -A 1 | tail -1); [date] $(date); [uptime] $(uptime); [disk] $(df -h | grep / -m 1); [memory] $(cat /proc/meminfo | grep MemFree) / $(cat /proc/meminfo | grep MemTotal); "'
        ;;
    m|mac)
        MONITOR='"[ssohh] '$SSOHH_TAG'; [name] $(hostname); [note] regular_'$INTERVAL'min_mac; [network] $(/sbin/ifconfig | grep en1 -A 1 | tail -1); [date] $(date); [uptime] $(uptime); [disk] $(df -h | grep / -m 1); [memory] $(top -l 1 | head -10 | grep PhysMem); "'
        ;;
    *)
        echo "Invalid ARCH: "$ARCH
        exit 1
        ;;
esac

COMMAND='curl '$ENDPOINT' -I -A "$(echo '$MONITOR' | sed -E "s/[[:space:]]+/ /gp")"'

(crontab -l ; echo "*/"$INTERVAL" * * * * $COMMAND") | uniq - | crontab -
