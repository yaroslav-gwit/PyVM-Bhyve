#!/usr/local/bin/bash
cd /root/pyVM/

if [[ $1 == "-h" ]] || [[ $1 == "--help" ]]
then
   bin/python3 pyvm.py --hostinfo
elif [[ -z $1 ]]
then
   bin/python3 pyvm.py --vmlist --hostinfo
else
   bin/python3 pyvm.py $@
fi