#!/bin/bash

curl http://service.yewei.me/ -I -A "$(echo "[name] $(hostname); [message] dev_mac; [ip] $(ifconfig | grep en1 -A 1 | tail -1); [date] $(date '+%Y-%m-%d %H:%M:%S %z %Z'); [uptime] $(uptime); [disk] $(df -h | grep / -m 1); [memory] $(top -l 1 | head -10 | grep PhysMem); " | sed -E "s/[[:space:]]+/ /gp")"
