#!bin/python
import sys
import os
import shlex, subprocess
from os.path import exists
from os import listdir
import ast
import time
from jinja2 import Template

# Own classes
from vm_dns_registry import vm_dns_registry

class VmOperations():
    def __init__(self, vmname="None", operation="None", disk_size_plus="1",):
        self.vmname = vmname
        self.operation = operation
        self.disk_size_plus = disk_size_plus

        vmname = str(self.vmname)
        vm_name = str(self.vmname)

        operation = str(self.operation)

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
        if exists("/dev/vmm/"):
            command = "ls /dev/vmm/ || true"
            shell_command = subprocess.check_output(command, shell=True)
            runningVMs = shell_command.decode("utf-8").split()
        else:
            runningVMs = []
        vmColumnStates = []
        for vm in vmColumnNames:
            if vm in runningVMs:
                vmColumnStates.append("Running")
            else:
                vmColumnStates.append("Stopped")
        #_ EOF VM is running check _#
        
        #_ Read the config file _#
        if exists("/zroot/vm-encrypted/" + vm_name + "/vm.config"):
            vm_folder = "/zroot/vm-encrypted/" + vm_name + "/"
            with open("/zroot/vm-encrypted/" + vm_name + "/vm.config", 'r') as file_object:
                vm_info_raw = file_object.read()
            vm_info_dict = ast.literal_eval(vm_info_raw)
        elif exists("/zroot/vm-unencrypted/" + vm_name + "/vm.config"):
            vm_folder = "/zroot/vm-unencrypted/" + vm_name + "/"
            with open("/zroot/vm-unencrypted/" + vm_name + "/vm.config", 'r') as file_object:
                vm_info_raw = file_object.read()
            vm_info_dict = ast.literal_eval(vm_info_raw)
        #_ EOF Read the config file _#

        
        if operation == "vmstart":
            if vmname in vmColumnNames:
                vm_index = vmColumnNames.index(vmname)
                if vmColumnStates[vm_index] == "Running":
                    print("VM is already running!")
                    exit(0)
                print("Starting the VM: " + vmname + ". It should be up and running shortly.")
                
                macs_list = vm_info_dict["network_macs"]
                tap_interface_list = []

                for interface_index in range(0, len(macs_list)):
                    command = "ifconfig | grep -G '^tap' | awk '{ print $1 }' | sed s/://"
                    shell_command = subprocess.check_output(command, shell=True)
                    existing_tap_interfaces = shell_command.decode("utf-8").split()
                    tap_interface_number = 0
                    tap_interface = "tap" + str(tap_interface_number)
                    while tap_interface in existing_tap_interfaces:
                        tap_interface_number = tap_interface_number + 1
                        tap_interface = "tap" + str(tap_interface_number)
                    command = "ifconfig " + tap_interface + " create"
                    shell_command = subprocess.check_output(command, shell=True)
                    command = "ifconfig vm-" + vm_info_dict["network_bridges"][interface_index] + " addm " + tap_interface
                    shell_command = subprocess.check_output(command, shell=True)
                    command = "ifconfig vm-"+ vm_info_dict["network_bridges"][interface_index] + " up"
                    shell_command = subprocess.check_output(command, shell=True)
                    command = 'ifconfig ' + tap_interface + ' description ' + '"' + tap_interface + ' ' + vmname + ' ' + 'interface' + str(interface_index) + '"'
                    shell_command = subprocess.check_output(command, shell=True)
                    tap_interface_list.append(tap_interface)
                

                command1 = "bhyve -AHP -s 0:0,hostbridge -s 31,lpc "

                s1 = 2
                s2 = 0
                space = " "
                network_adaptor_type = vm_info_dict["network_adaptor_type"]
                else_macs_text = "," + network_adaptor_type + ","
                
                for mac in range(0, len(macs_list)):
                    if mac == 0:
                        mac_final = "-s " + str(s1) + ":" + str(s2) + else_macs_text + tap_interface_list[mac] + ",mac=" + macs_list[mac]
                    else:
                        s2 = s2 + 1
                        mac_final = mac_final + space + "-s " + str(s1) + ":" + str(s2) + else_macs_text + tap_interface_list[mac] + ",mac=" + macs_list[mac]

                command2 = mac_final

                s = 3
                disk_list = vm_info_dict["os_drives"]
                os_drive_type = vm_info_dict["os_drive_type"]
                else_disk_text = ":0," + os_drive_type + ","
                # if vm_info_dict["os_type"] == "rockylinux8":
                #     else_disk_text = ":0,ahci-hd,"
                # else:
                #     else_disk_text = ":0,virtio-blk,"
                
                for disk in range(0, len(disk_list)):
                    if disk == 0:
                        disk_final = " -s " + str(s) + else_disk_text + vm_folder + disk_list[disk]
                    else:
                        s = s + 1
                        disk_final = disk_final + space + "-s " + str(s) + else_disk_text + vm_folder + disk_list[disk]
                
                command3 = disk_final
                s = s + 1
                command4 = " -s " + str(s) + ":0,ahci-cd," + vm_folder + "seed.iso"
                command5 = " -c " + vm_info_dict["cpus"] + " -m " + vm_info_dict["memory"]
                s = s + 1
                command6 = " -s " + str(s) + ":" + str(s2) + ",fbuf,tcp=0.0.0.0:" + vm_info_dict["vnc_port"] + ",w=1280,h=1024,password=" + vm_info_dict["vnc_password"]
                s = s + 1

                if vm_info_dict["loader"] == "bios":
                    command7 = " -s " + str(s) + ":" + str(s2) + ",xhci,tablet -l com1,/dev/nmdm-" + vm_name + "-1A -l bootrom,/usr/local/share/uefi-firmware/BHYVE_UEFI_CSM.fd -u " + vmname
                    command = command1 + command2 + command3 + command4 + command5 + command6 + command7
                else:
                    command7 = " -s " + str(s) + ",xhci,tablet -l com1,/dev/nmdm-" + vm_name + "-1A -l bootrom,/usr/local/share/uefi-firmware/BHYVE_UEFI.fd -u " + vmname
                    command = command1 + command2 + command3 + command4 + command5 + command6 + command7
                
                command = "nohup /root/bin/startvm " + '"' + command + '"' + " " + vmname + " > " + vm_folder + "vm.log 2>&1 &"
                # print(command)
                
                shell_command = subprocess.run(command, shell=True, stderr = subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                # shell_command = subprocess.run(command, shell=True,)
            else:
                print("There is no such VM on this system")
                exit(0)


        elif operation == "vmstop":
            if vmname in vmColumnNames:
                vm_index = vmColumnNames.index(vmname)
                if vmColumnStates[vm_index] == "Stopped":
                    print("VM is not running.")
                    exit(0)
                print("Gracefully stopping the VM: " + vmname)

                command = "ps axf | grep -v grep | grep " + vmname + " | grep bhyve: | awk '{ print $1 }'"
                shell_command = subprocess.check_output(command, shell=True)
                running_vm_pid = shell_command.decode("utf-8").split()[0]
                command = "kill -SIGTERM " + running_vm_pid
                shell_command = subprocess.check_output(command, shell=True)

                command = "ifconfig | grep " + vmname + " | awk '{ print $2 }'"
                shell_command = subprocess.check_output(command, shell=True)
                running_tap_adaptor = shell_command.decode("utf-8").split()[0]
                tap_interface_list = shell_command.decode("utf-8").split()

                running_tap_adaptor_status = "active"

                while running_tap_adaptor_status == "active":
                    command = "ifconfig " + running_tap_adaptor + " | grep status | sed s/.status:.//"
                    shell_command = subprocess.check_output(command, shell=True)
                    running_tap_adaptor_status = shell_command.decode("utf-8").split("\n")[0]
                    time.sleep(2)
                
                command = "bhyvectl --destroy --vm=" + vmname
                shell_command = subprocess.check_output(command, shell=True)
                
                for tap in tap_interface_list:
                    command = "ifconfig " + tap + " destroy"
                    shell_command = subprocess.check_output(command, shell=True)
                
                print("VM " + vmname + " is fully stopped now.")
        
        
        elif operation == "vmrestart":
            if vmname in vmColumnNames:
                vm_index = vmColumnNames.index(vmname)
                if vmColumnStates[vm_index] == "Stopped":
                    print("VM is turned off, can't restart")
                    exit(0)

            VmOperations(vmname=vmname, operation="vmstop")
            VmOperations(vmname=vmname, operation="vmstart")

        
        elif operation == "vmkill":
            if vmname in vmColumnNames:
                vm_index = vmColumnNames.index(vmname)
                if vmColumnStates[vm_index] == "Stopped":
                    print("VM is already turned off.")
                    exit(0)
            
                command = "ifconfig | grep " + vmname + " | awk '{ print $2 }'"
                shell_command = subprocess.check_output(command, shell=True)
                running_tap_adaptor = shell_command.decode("utf-8").split()[0]
                tap_interface_list = shell_command.decode("utf-8").split()

                command = "bhyvectl --destroy --vm=" + vmname
                shell_command = subprocess.check_output(command, shell=True)
                
                time.sleep(1)

                for tap in tap_interface_list:
                    command = "ifconfig " + tap + " destroy"
                    shell_command = subprocess.check_output(command, shell=True)
        
        
        elif operation == "vmdestroy":
            if vmname in vmColumnNames:
                vm_index = vmColumnNames.index(vmname)
                if vmColumnStates[vm_index] == "Running":
                    print("VM is still running. You'll have to stop (or kill) it first.")
                    exit(0)
                
                if vm_folder == "/zroot/vm-encrypted/" + vm_name + "/":
                    command = "zfs destroy -rR zroot/vm-encrypted/" + vm_name
                    shell_command = subprocess.check_output(command, shell=True)
                else:
                    command = "zfs destroy -rR zroot/vm-unencrypted/" + vm_name
                    shell_command = subprocess.check_output(command, shell=True)
                
                vm_dns_registry()


        elif operation == "vmedit":
            if vmname in vmColumnNames:
                vm_index = vmColumnNames.index(vmname)
                if vmColumnStates[vm_index] == "Running":
                    print("VM appears to be running. It's a bad practice to edit the config of live VMs.")
                    exit(0)
            if exists("/zroot/vm-encrypted/" + vm_name):
                command = "nano /zroot/vm-encrypted/" + vm_name + "/vm.config"
                subprocess.run(command, shell=True)
            else:
                command = "nano /zroot/vm-unencrypted/" + vm_name + "/vm.config"
                subprocess.run(command, shell=True)

        elif operation == "vmrename":
            print("This feature is not available, and never will be. To rename your VM use this command:\npyvm --vmcireset --oldvmname test-vm-1 --newvmname production-vm-001")

        elif operation == "vmconsole":
            if vmname in vmColumnNames:
                vm_index = vmColumnNames.index(vmname)
                if vmColumnStates[vm_index] == "Stopped":
                    print("VM doesn't appear to be running, can't connect to console")
                    exit(0)
            
            command = "tmux ls | grep -c " + vmname + " || true"
            shell_command = subprocess.check_output(command, shell=True)
            tmux_sessions = shell_command.decode("utf-8").split()[0]
            if tmux_sessions != "no server running on /tmp/tmux-0/default":
                if int(tmux_sessions) > 0:
                    command = 'tmux a -t ' + '"' + vmname + '"'
                    shell_command = subprocess.check_output(command, shell=True)
                else:
                    command = 'tmux new-session -s ' + vmname + ' "cu -l /dev/nmdm-' + vm_name + '-1B"'
                    subprocess.run(command, shell=True)

        elif operation == "diskexpand":
            if vmname in vmColumnNames:
                vm_index = vmColumnNames.index(vmname)
                if vmColumnStates[vm_index] == "Running":
                    print("VM is still running. You'll have to stop (or kill) it before disk resizing.")
                    exit(0)
            
            if exists("/zroot/vm-encrypted/" + vmname + "/disk0.img"):
                folder_and_disk_image = "/zroot/vm-encrypted/" + vmname + "/disk0.img"
            else:
                folder_and_disk_image = "/zroot/vm-unencrypted/" + vmname + "/disk0.img"

            shell_command = 'truncate -s +' + disk_size_plus + "G " + folder_and_disk_image
            subprocess.run(str(shell_command), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
