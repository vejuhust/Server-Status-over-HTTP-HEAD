#!/bin/sh

export SSOHH_TOKEN=abcwtf; curl http://service.yewei.me/ -I -A "$(echo "[ssohh] $SSOHH_TOKEN; [name] $(hostname); [note] dev_mac; [network] $(/sbin/ifconfig | grep en1 -A 1 | tail -1); [date] $(date); [uptime] $(uptime); [disk] $(df -h | grep / -m 1); [memory] $(top -l 1 | head -10 | grep PhysMem); " | sed -E "s/[[:space:]]+/ /gp")"
