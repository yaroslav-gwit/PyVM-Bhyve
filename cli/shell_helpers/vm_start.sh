#!/usr/local/bin/bash
COMMAND=$1
VM_NAME=$2

echo ""
echo "__NEW_START__"
echo "Time and date: $(date)"
echo "This bhyve command was executed:"
echo $COMMAND

echo ""

echo "VM name: $VM_NAME"
echo ""

$COMMAND

while [[ $? == 0 ]]
do
    $COMMAND
    sleep 5
done

sleep 3

if [[ $(ifconfig | grep -c $VM_NAME) > 0 ]]
then
    echo ""
    hoster vm kill $VM_NAME
    echo ""
fi

echo "The VM exited at $(date)"
echo ""