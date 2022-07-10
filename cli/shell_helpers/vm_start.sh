#!/usr/local/bin/bash

COMMAND=$1
VM_NAME=$2

# CHECK IF OLD PID EXISTS AND REMOVE IT IF IT DOES
if [[ -f /var/run/${VM_NAME}.pid ]]; then
    rm /var/run/${VM_NAME}.pid
fi

# GET OWN PID AND WRITE IT INTO VM PID FILE
# echo "$$" > /var/run/${VM_NAME}.pid
echo "${BASHPID}" > /var/run/${VM_NAME}.pid

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
    sleep 1
    echo ""
done

sleep 1

if [[ $(ifconfig | grep -c $VM_NAME) > 0 ]]
then
    if [[ -f /var/run/${VM_NAME}.pid ]]; then
        rm /var/run/${VM_NAME}.pid
    fi
    
    # PRINT OUT THE EXIT TIME/DATE AND CLEANUP EVERYTHING
    echo ""
    echo "🔶 INFO: The VM exited on $(date)" && hoster vm kill $VM_NAME > /dev/null
    echo ""
fi
