import sys
import os
import subprocess
from os.path import exists
from os import listdir

# Own classes
from vm_dns_registry import vm_dns_registry
from vm_operations import VmOperations as vm_operations
from vm_backups import VmSnapshot as vm_snapshot
from vm_backups import VmReplication as vm_replicate

class VmMassOperations():
    def __init__(self, operation="None", snapshot_type="None", endpoint="None"):
        self.operation = operation
        
        if snapshot_type == "None":
            snapshot_type = "custom"
        else:
            snapshot_type = snapshot_type
        self.snapshot_type = snapshot_type

        self.endpoint = endpoint

        #_ VM List _#
        vmColumnNames = []
        zfs_datasets = ["zroot/vm-encrypted", "zroot/vm-unencrypted"]
        for dataset in zfs_datasets:
            if exists("/" + dataset + "/"):
                _dataset_listing = listdir("/" + dataset + "/")
                for vm_directory in _dataset_listing:
                    if exists("/" + dataset + "/" + vm_directory + "/vm.config"):
                        vmColumnNames.append(vm_directory)
            else:
                print("Please create 2 zfs datasets: " + zfs_datasets)
        vmColumnNames.sort()
        #_ EOF VM List _#

        #_ VM is running check _#
        vmRunningList = []
        vmStoppedList = []
        if exists("/dev/vmm/"):
            command = "ls /dev/vmm/ || true"
            shell_command = subprocess.check_output(command, shell=True)
            runningVMs = shell_command.decode("utf-8").split()
        else:
            runningVMs = []
        for vm in vmColumnNames:
            if vm in runningVMs:
                vmRunningList.append(vm)
            else:
                vmStoppedList.append(vm)
        #_ EOF VM is running check _#

        if operation == "vmstartall":
            for vm in vmStoppedList:
                vm_operations(vmname=vm, operation="vmstart")

        elif operation == "vmstopall":
            for vm in vmRunningList:
                vm_operations(vmname=vm, operation="vmstop")

        elif operation == "vmkillall":
            for vm in vmRunningList:
                vm_operations(vmname=vm, operation="vmkill")

        elif operation == "vmdestroyall":
            for vm in vmStoppedList:
                vm_operations(vmname=vm, operation="vmdestroy")
            # This will clean up all ZFS snapshots to free up space
            command = "for SNAPSHOT in $(zfs list -H -o name -t snapshot); do zfs destroy $SNAPSHOT; done"
            subprocess.run(command, shell=True)
            # EOF This will clean up all ZFS snapshots to free up space
            vm_dns_registry()
        
        elif operation == "vmsnapshotall":
            for vm in vmColumnNames:
                vm_snapshot(vmname=vm, snapshot_type=snapshot_type)
        
        elif operation == "vmreplicateall":
            for vm in vmColumnNames:
                vm_replicate(vmname=vm, endpoint=endpoint)