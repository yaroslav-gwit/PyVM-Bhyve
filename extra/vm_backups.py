from time import strftime,localtime
import subprocess
from os.path import exists
from os import listdir
import re

class VmSnapshot():
    def __init__(self, vmname="None", snapshot_type="custom", snapshot_list=False, snapshots_to_keep="None"):
        snapshot_type_list = [ "replication", "custom", "hourly", "daily", "weekly", "monthly", "yearly"]
        vm_exclude_list = []
        self.vmname = vmname
        
        if snapshot_type in snapshot_type_list:
            self.snapshot_type = snapshot_type
        else:
            self.snapshot_type = "custom"
        
        self.snapshot_list = snapshot_list


        vmColumnNames = []
        vmZfsDatasets = []
        zfs_datasets = ["zroot/vm-encrypted", "zroot/vm-unencrypted"]
        for dataset in zfs_datasets:
            if exists("/" + dataset + "/"):
                _dataset_listing = listdir("/" + dataset + "/")
                for vm_name in _dataset_listing:
                    if exists("/" + dataset + "/" + vm_name + "/vm.config"):
                        vmColumnNames.append(vm_name)
                        vmZfsDatasets.append(dataset + "/" + vm_name)

        if self.vmname not in vmColumnNames:
            print("Can't find such VM on this system")
            exit(1)


        date_now = strftime("%Y-%m-%d_%H-%M-%S", localtime())
        snapshot_name = self.snapshot_type + "_" + date_now
        zfs_dataset = vmZfsDatasets[vmColumnNames.index(vmname)]

        # If snapshots to keep was specified, delete the snapshots that are exceeding the number that was set
        if isinstance(snapshots_to_keep, int) and self.snapshot_type != "custom":
            self.snapshots_to_keep = snapshots_to_keep
            # Get the snapshot list
            command = "zfs list -r -t snapshot " + vmZfsDatasets[vmColumnNames.index(vmname)] + " | tail +2 | awk '{ print $1 }'"
            shell_command = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL)
            vm_zfs_snapshot_list = shell_command.decode("utf-8").split()
            
            # Generate list of snapshots to delete
            vm_zfs_snapshots_to_delete = vm_zfs_snapshot_list.copy()
            if len(vm_zfs_snapshots_to_delete) > 0:
                for zfs_snapshot in range(0, snapshots_to_keep):
                    del vm_zfs_snapshots_to_delete[-1]
                # Remove the old snapshots
                for vm_zfs_snapshot_to_delete in vm_zfs_snapshots_to_delete:
                    command = "zfs destroy " + vm_zfs_snapshot_to_delete
                    print(command)

        else:
            command = "zfs snapshot " + zfs_dataset + "@" + snapshot_name
            subprocess.run(command, shell=True, stderr = subprocess.DEVNULL, stdout=subprocess.DEVNULL)

class VmReplication():
    def __init__(self, vmname="None", endpoint="None"):
        self.vmname = vmname
        if endpoint == "None":
            print("Please specify an endpoint")
        else:
            self.endpoint = endpoint

        vmColumnNames = []
        vmZfsDatasets = []
        zfs_datasets = ["zroot/vm-encrypted", "zroot/vm-unencrypted"]
        for dataset in zfs_datasets:
            if exists("/" + dataset + "/"):
                _dataset_listing = listdir("/" + dataset + "/")
                for vm_name in _dataset_listing:
                    if exists("/" + dataset + "/" + vm_name + "/vm.config"):
                        vmColumnNames.append(vm_name)
                        vmZfsDatasets.append(dataset + "/" + vm_name)
        
        endpoint_dataset = vmZfsDatasets[vmColumnNames.index(vmname)]
        # print(endpoint_dataset)

        if self.vmname not in vmColumnNames:
            print("Can't find such VM on this system")
            exit(1)

        else:
            # Create temporary replication snapshot
            VmSnapshot(vmname=vmname, snapshot_type="replication")
            
            # Local snapshot list
            command = "zfs list -r -t snapshot " + vmZfsDatasets[vmColumnNames.index(vmname)] + " | tail +2 | awk '{ print $1 }'"
            shell_command = subprocess.check_output(command, shell=True)
            vm_zfs_snapshot_list = shell_command.decode("utf-8").split()
            # print("Local snap list: " + str(vm_zfs_snapshot_list))
            # print()

            # Leave only 2 replication snapshots
            _local_snaps_to_delete = []
            for item in vm_zfs_snapshot_list:
                if re.match(".*replication.*", item):
                    _local_snaps_to_delete.append(item)
            _local_snaps_to_delete.pop()
            if len(_local_snaps_to_delete) > 1:
                for item in range(0, len(_local_snaps_to_delete)-1):
                    vm_zfs_snapshot_list.remove(_local_snaps_to_delete[item])
                    command = "zfs destroy " + _local_snaps_to_delete[item]
                    subprocess.run(command, shell=True)

            # Remote snapshot list
            command = 'echo "if [[ -d /' + endpoint_dataset + ' ]]; then zfs list -r -t snapshot ' + endpoint_dataset + '; fi" | ssh ' + endpoint + ' /usr/local/bin/bash | tail +2 | ' + "awk '{ print $1 }'"
            shell_command = subprocess.check_output(command, shell=True)
            remote_zfs_snapshot_list = shell_command.decode("utf-8").split()
            # print("Remote snap list: " + str(remote_zfs_snapshot_list))
            # print(command)

            # Revert to a last snapshot to avoid dealing with differences
            if len(remote_zfs_snapshot_list) >= 1:
                command = "ssh " + endpoint + " zfs rollback -r " + remote_zfs_snapshot_list[len(remote_zfs_snapshot_list) - 1]
                subprocess.run(command, shell=True)
            # print("Reverted to a last snapshot " + command)
            # print()

            if vm_zfs_snapshot_list == remote_zfs_snapshot_list:
                print("The backup system is already up to date!")
                exit(0)

            # Difference list
            _to_delete_snapshot_list = []
            _to_delete_snapshot_list.extend(remote_zfs_snapshot_list)
            for zfs_snapshot in vm_zfs_snapshot_list:
                if zfs_snapshot in _to_delete_snapshot_list:
                    _to_delete_snapshot_list.remove(zfs_snapshot)
            # print("To delete list: " + str(_to_delete_snapshot_list))
            if len(_to_delete_snapshot_list) != 0:
                for item in _to_delete_snapshot_list:
                    command = "ssh " + endpoint + " zfs destroy " + item
                    subprocess.run(command, shell=True)
                print("Some old snapshots were removed from the backup system: " + str(_to_delete_snapshot_list))

            for remote_zfs_snapshot in remote_zfs_snapshot_list:
                if remote_zfs_snapshot_list.index(remote_zfs_snapshot) != len(remote_zfs_snapshot_list) - 1:
                    if remote_zfs_snapshot in vm_zfs_snapshot_list:
                        vm_zfs_snapshot_list.remove(remote_zfs_snapshot)
            # print("Updated snapshot list: " + str(vm_zfs_snapshot_list))
            # print()
        
        if len(remote_zfs_snapshot_list) >= 1:
            for snapshot in range(0, len(vm_zfs_snapshot_list)-1):
                command = "zfs send -vi " + vm_zfs_snapshot_list[snapshot] + " " + vm_zfs_snapshot_list[snapshot + 1] + " | ssh " + endpoint + " zfs receive " + endpoint_dataset
                subprocess.run(command, shell=True)
            print("Replication job for " + vmname +" is done!")
            print()

        elif len(remote_zfs_snapshot_list) == 0:
            command = "zfs send -v " + vm_zfs_snapshot_list[0] + " | ssh " + endpoint + " zfs receive " + endpoint_dataset
            subprocess.run(command, shell=True)
            print("Replication job for " + vmname +" is done!")
            print()
