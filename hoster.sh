#!/usr/local/bin/bash
cd /root/pyVM/
source bin/activate

if [[ -z "$1" ]]; then
    ./hoster host info
    ./hoster vm list
else
    ./hoster $@
fi