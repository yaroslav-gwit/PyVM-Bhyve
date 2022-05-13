#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]
  then echo "ERROR: Only root can control VMs"
  exit 1
fi


if [[ ! -z $HOSTER_RED_WD ]]; then
    cd $HOSTER_RED_WD
else
    cd /root/pyVM/
fi

if [[ $VENV == "yes" ]]; then
    source bin/activate
fi


if [[ -z "$1" ]]; then
    ./hoster host info
    ./hoster vm list
elif [[ $1 == "init" ]]; then
    ./hoster host init
    ./hoster network init
else
    ./hoster $@
fi
