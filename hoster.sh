#!/usr/bin/env bash

# ICONS USED IN THIS LIBRARY. USED AS A REFERENCE.
# 🚫 ⛔ 🚦 🟢 🔒 🔁 🔴 🔶 🔷 💾 ⏩

#_ CHECK IF USER IS ROOT _#
if [ "$EUID" -ne 0 ]
  then echo " 🚦 ERROR: Only root can control VMs!"
  exit 1
fi

#_ CHECK THE DEPLOYMENT FOLDER _#
if [[ ! -z $HOSTER_RED_WD ]]; then
    cd $HOSTER_RED_WD
else
    cd /root/pyVM/
fi
#_ CHECK IF VENV IS USED _#
if [[ $VENV == "yes" ]]; then
    source bin/activate
elif [[ -z $VENV ]]; then
    source bin/activate
fi

#_ EXECUTION BID _#
if [[ -z "$1" ]]; then
    ./hoster host info
    ./hoster vm list
elif [[ $1 == "init" ]]; then
    ./hoster host init
    ./hoster network init
else
    ./hoster $@
fi
