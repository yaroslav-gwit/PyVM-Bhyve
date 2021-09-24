#!/usr/local/bin/bash
COMMAND=$1
VM_NAME=$2
echo "This bhyve command was executed:"
echo $COMMAND
echo ""
echo "VM name was:"
echo $VM_NAME
echo ""

$COMMAND

while [[ $? == 0 ]]; do
$COMMAND
done

sleep 5

if [[ $(ifconfig | grep -c $VM_NAME) > 0 ]]; then
pyvm --vmkill $VM_NAME
fi