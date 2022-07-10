#!/usr/local/bin/bash

func_stop() {
    echo "Stopping CHILD_PROCESS: $!"
    kill -s SIGTERM $!
}

func_kill() {
    echo "Stopping CHILD_PROCESS: $!"
    kill -SIGTERM $!
}

# LISTEN FOR KILL -1 AND IF IT HAPPENS SHUTDOWN THE VM
PRID=
trap '[[ $PRID ]] && Stopping CHILD_PROCESS $PRID && kill -s SIGTERM $PRID' 34
# trap func_stop SIGHUP

# LISTEN FOR KILL -2 AND IF IT HAPPENS KILL THE VM
# trap func_kill SIGINT

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
$COMMAND & PRID=$!
wait
PRID=

# echo ""
# PARENT_PID=$$
# CHILD_PID=$!
# echo "PARENT_PID=${PARENT_PID}"
# echo "CHILD_PID=${CHILD_PID}"
# echo ""


while [[ $? == 0 ]]
do
    echo ""
    echo "VM has been restarted at: $(date)"
    $COMMAND & PRID=$!
    wait
    PRID=
    sleep 1
    echo ""
done

sleep 1

if [[ $(ifconfig | grep -c $VM_NAME) > 0 ]]
then
    echo ""
    hoster vm kill $VM_NAME
    echo ""
    
    if [[ -f /var/run/${VM_NAME}.pid ]]; then
        rm /var/run/${VM_NAME}.pid
    fi
fi

echo "The VM exited at $(date)"
echo ""