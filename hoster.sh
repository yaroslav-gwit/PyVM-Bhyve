#!/usr/local/bin/bash
cd /root/pyVM/
source bin/activate

if [[ -z "$1" ]]; then
    ./hoster host info
    ./hoster vm list
elif [[ $1 == "init" ]]; then
    ./hoster host init
    ./hoster network init
else
    ./hoster $@
fi