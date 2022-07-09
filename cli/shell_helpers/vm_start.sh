#!/usr/local/bin/bash
COMMAND=$1
VM_NAME=$2

echo ""
echo "__NEW_START__"
echo "Time and date: $(date)"

echo ""
echo "This bhyve command was executed to start the VM:"
echo $COMMAND

echo ""
$COMMAND

while [[ $? == 0 ]]
do
    echo ""
    echo "VM has been restarted at: $(date)"
    $COMMAND
    sleep 5
    echo ""
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