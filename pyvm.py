#!bin/python

# System funcs
import argparse
import sys
import os
import subprocess

# 3rd party funcs

# My own funcs
sys.path.append('./extra/')
import vm_list
from vm_operations import VmOperations as vm_operations
from vm_mass_operations import VmMassOperations as vm_mass_operations
from vm_deploy import VmDeployment
from vm_backups import VmSnapshot as vm_snapshot
from vm_backups import VmReplication as vm_replicate

### Code Starts Here ###
parser = argparse.ArgumentParser()
parser.add_argument("--hostinfo", action="store_true", help="Shows host info table")
parser.add_argument("--vmlist", action="store_true", help="Shows list of VMs")
parser.add_argument("--dryrun", action="store_true", help="Skips bash helpers")

parser.add_argument("--vmkillall", action="store_true", help="Instantly kills all VMs")
parser.add_argument("--vmstartall", action="store_true", help="Instantly starts all VMs")
parser.add_argument("--vmstopall", action="store_true", help="Instantly stops all VMs")
parser.add_argument("--vmdestroyall", action="store_true", help="Instantly DELETES all VMs")

parser.add_argument("--vmstart", type=str, help="Starts one of the VMs")
parser.add_argument("--vmstop", type=str, help="Stops one of the VMs gracefully")
parser.add_argument("--vmkill", type=str, help="Instantly kills one of the VMs")
parser.add_argument("--vmdestroy", type=str, help="Instantly kills one of the VMs")
parser.add_argument("--vmedit", type=str, help="Instantly kills one of the VMs")
parser.add_argument("--vmrestart", type=str, help="Restarts one of the VMs")

parser.add_argument("--vmconsole", type=str, help="Connects you to VM console inside of a TMUX session")

parser.add_argument("--vmsnapshot", action="store_true", help="Snapshots your VM")
parser.add_argument("--vmsnapshotall", action="store_true", help="Snapshots all your VMs")
parser.add_argument("--snaptype", type=str, help="Sets the type of the snapshot")
parser.add_argument("--snapstokeep", type=int, help="Sets the number of snapshots to keep")
parser.add_argument("--vmreplicate", action="store_true", help="Replicates your VM to a backup server")
parser.add_argument("--vmreplicateall", action="store_true", help="Replicates all of your VMs to a backup server")
parser.add_argument("--endpoint", type=str, help="Sets replication endpoint")


parser.add_argument("--vmdiskexpand", type=str, help="Expands VM OS drive")
parser.add_argument("--size", type=str, help="Sets the number of gigabytes for disk expansion")

parser.add_argument("--vmdeploy", action="store_true", help="Deploys a new VM")
parser.add_argument("--vmname", type=str, help="VM name")
parser.add_argument("--ostype", type=str, help="Set OS/Distro")

parser.add_argument("--vmcireset", action="store_true", help="Renames/resets the VM with help of cloud-init")
parser.add_argument("--oldvm", type=str, help="Old VM name")
parser.add_argument("--newvm", type=str, help="New VM name")

args = parser.parse_args()

### Argument errors ###
# Throw an error when there are no args passed
# if (not args.hostinfo) and (not args.vmlist) and (not args.vmstart) and (not args.vmstop) and (not args.vmkill) and (not args.vm):
    # print("Please pass some parameters, like this:\npyvm --vmlist")
    # exit(0)

# Throw an error if there are not compatible args passed #
if args.vmstart and (args.dryrun or args.vmlist or args.hostinfo):
    print("Cannot be used with --vmstart")
    exit(0)

if args.vmstop and (args.dryrun or args.vmlist or args.hostinfo):
    print("Cannot be used with --vmstop")
    exit(0)

if args.vmkill and (args.dryrun or args.vmlist or args.hostinfo):
    print("Cannot be used with --vmkill")
    exit(0)


### Print out info ###
# Print host info
if args.hostinfo:
    if args.dryrun:
        print(vm_list.hostinfo(dryrun=True))
    else:
        print(vm_list.hostinfo())

# Print vm list
if args.vmlist:
    if args.dryrun:
        print(vm_list.vmlist(dryrun=True))
    else:
        print(vm_list.vmlist())


### VM operations ###
# Start VM
if args.vmstart:
    vmname = args.vmstart
    vm_operations(vmname, "vmstart")

if args.vmstartall:
    vm_mass_operations(operation = "vmstartall")
    print("DONE!")

# Stop VM
if args.vmstop:
    vmname = args.vmstop
    vm_operations(vmname, "vmstop")

if args.vmstopall:
    vm_mass_operations(operation = "vmstopall")
    print("DONE!")

# Restart VM
if args.vmrestart:
    vmname = args.vmrestart
    vm_operations(vmname, "vmrestart")

# Kill VM
if args.vmkill:
    vmname = args.vmkill
    vm_operations(vmname, "vmkill")
    print("VM " + vmname + " was just killed!")

if args.vmkillall:
    vm_mass_operations(operation = "vmkillall")
    print("DONE!")

# Destroy (delete/remove) VM
if args.vmdestroy:
    vmname = args.vmdestroy
    vm_operations(vmname, "vmdestroy")
    print("VM " + vmname + " was just completely removed from this host!")

if args.vmdestroyall:
    vm_mass_operations(operation = "vmdestroyall")
    print("DONE!")

# Edit VM Config
if args.vmedit:
    vmname = args.vmedit
    vm_operations(vmname, "vmedit")
    print("VM " + vmname + " config was edited succesfully! Now start the VM again to apply new config.")

# Connect to VM's console
if args.vmconsole:
    vmname = args.vmconsole
    vm_operations(vmname, "vmconsole")

# VM Snapshot
if args.vmsnapshot:
    vmname = args.vmname
    if args.snaptype:
        snapshot_type = args.snaptype
    else:
        snapshot_type = "custom"
    if args.snapstokeep:
        snapshots_to_keep = args.snapstokeep
    else:
        snapshots_to_keep = "None"
    vm_snapshot(vmname=vmname, snapshot_type=snapshot_type, snapshots_to_keep=snapshots_to_keep)

if args.vmsnapshotall:
    if args.snaptype:
        snapshot_type = args.snaptype
    else:
        snapshot_type = "custom"
    if args.snapstokeep:
        snapshots_to_keep = args.snapstokeep
    else:
        snapshots_to_keep = "None"
    vm_mass_operations(operation = "vmsnapshotall", snapshot_type=snapshot_type, snapshots_to_keep=snapshots_to_keep)
    print("DONE!")

# VM replication
if args.vmreplicate:
    vmname = args.vmname
    endpoint = args.endpoint
    vm_replicate(vmname=vmname, endpoint=endpoint)

if args.vmreplicateall:
    endpoint = args.endpoint
    vm_mass_operations(operation = "vmreplicateall", endpoint=endpoint)
    print("DONE!")

# Expand VM OS disk
if args.vmdiskexpand:
    vmname = args.vmdiskexpand
    disk_size_plus = args.size
    vm_operations(vmname=vmname, disk_size_plus=disk_size_plus, operation="diskexpand")
    print("VM " + vmname + " disk was expanded succesfully. Start the VM now to apply the changes.")


### VM deployment ###
if args.vmdeploy:
    if not args.vmname:
        vmname = "None"
    else:
        vmname = args.vmname

    if not args.ostype:
        ostype = "debian10"
    else:
        ostype = args.ostype

    vm_deploy = VmDeployment(new_vm_name=vmname, vm_os_type=ostype)
    #command = "vmdeploy " + vm_deploy.new_vm_name + " " + vm_deploy.vm_ipaddress + " " + vm_deploy.vm_os_type + " " + vm_deploy.vm_encryption
    #print(command)
    #subprocess.run(command, shell=True, stderr = subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    vm_deploy.vm_deploy_command()

### VM deployment ###
if args.vmcireset:
    if not args.oldvm:
        oldvm = "None"
    else:
        oldvm = args.oldvm

    if not args.newvm:
        newvm = "None"
    else:
        newvm = args.newvm

    vm_deploy = VmDeployment(new_vm_name=newvm, old_vm_name=oldvm)
    vm_deploy.vm_ci_reset_command()