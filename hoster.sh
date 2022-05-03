#!/usr/local/bin/bash
cd /root/pyVM/
source bin/activate

if [[ -z "$1" ]]; then
    ./hoster $@
else
    ./hoster host info
    ./hoster vm list