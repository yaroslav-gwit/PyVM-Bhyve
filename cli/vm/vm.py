#!bin/python
import typer
from cli.vm import vmdeploy

##########################################################
# Native Python functions
import sys
import os
import subprocess
import copy
import socket
import platform
import re
from os.path import exists
from os import listdir
import ast

# Installed packages/modules
import uptime
import psutil
from tabulate import tabulate
from natsort import natsorted

# Own functions
from core import time_date_converter
from core.dataset import dataset_list

with open("/root/bin/host.info", 'r') as file_object:
    host_info_raw = file_object.read()
host_info_dict = ast.literal_eval(host_info_raw)


class VmListTable:
    def __init__(self):
        print("This will be a VmListTable class")



class VmListJson:
    def __init__(self):
        print("This will be VmListJson class")



def vmlist():
    ### VM_TABLE ###
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
        
    vmColumnNames = natsorted(vmColumnNames)

    if len(vmColumnNames) < 1:
        print("\nThere are no VMs on this system. To deploy one, use:\n pyvm --vmdeploy\n")
        exit(0)

    
    vmColumnEncryption = []
    for vm_name in vmColumnNames:
        if exists("/zroot/vm-encrypted/" + vm_name):
            vmColumnEncryption.append("Encrypted")
        else:
            vmColumnEncryption.append("Not encrypted")

    
    vmColumnStates = []
    if exists("/dev/vmm/"):
        command = "ls /dev/vmm/ || true"
        shell_command = subprocess.check_output(command, shell=True)
        runningVMs = shell_command.decode("utf-8").split()
    else:
        runningVMs = []
    for vm in vmColumnNames:
        if vm in runningVMs:
            vmColumnStates.append("Running")
        else:
            vmColumnStates.append("Stopped")
        

    vmColumnCPU = []
    for vm_name in vmColumnNames:
        if exists("/zroot/vm-encrypted/" + vm_name + "/vm.config"):
            with open("/zroot/vm-encrypted/" + vm_name + "/vm.config", 'r') as file_object:
                vm_info_raw = file_object.read()
            vm_info_dict = ast.literal_eval(vm_info_raw)
            vmColumnCPU.append(vm_info_dict["cpus"])
        elif exists("/zroot/vm-unencrypted/" + vm_name + "/vm.config"):
            with open("/zroot/vm-unencrypted/" + vm_name + "/vm.config", 'r') as file_object:
                vm_info_raw = file_object.read()
            vm_info_dict = ast.literal_eval(vm_info_raw)
            vmColumnCPU.append(vm_info_dict["cpus"])
        else:
            vmColumnCPU.append("-")

    
    vmColumnRAM = []
    for vm_name in vmColumnNames:
        if exists("/zroot/vm-encrypted/" + vm_name + "/vm.config"):
            with open("/zroot/vm-encrypted/" + vm_name + "/vm.config", 'r') as file_object:
                vm_info_raw = file_object.read()
            vm_info_dict = ast.literal_eval(vm_info_raw)
            vmColumnRAM.append(vm_info_dict["memory"])
        elif exists("/zroot/vm-unencrypted/" + vm_name + "/vm.config"):
            with open("/zroot/vm-unencrypted/" + vm_name + "/vm.config", 'r') as file_object:
                vm_info_raw = file_object.read()
            vm_info_dict = ast.literal_eval(vm_info_raw)
            vmColumnRAM.append(vm_info_dict["memory"])
        else:
            vmColumnRAM.append("-")

    
    vmColumnVncPort = []
    for vm_name in vmColumnNames:
        if exists("/zroot/vm-encrypted/" + vm_name + "/vm.config"):
            with open("/zroot/vm-encrypted/" + vm_name + "/vm.config", 'r') as file_object:
                vm_info_raw = file_object.read()
            vm_info_dict = ast.literal_eval(vm_info_raw)
            vmColumnVncPort.append(vm_info_dict["vnc_port"])
        elif exists("/zroot/vm-unencrypted/" + vm_name + "/vm.config"):
            with open("/zroot/vm-unencrypted/" + vm_name + "/vm.config", 'r') as file_object:
                vm_info_raw = file_object.read()
            vm_info_dict = ast.literal_eval(vm_info_raw)
            vmColumnVncPort.append(vm_info_dict["vnc_port"])
        else:
            vmColumnVncPort.append("-")
    
    
    vmColumnVncPassword = []
    for vm_name in vmColumnNames:
        if exists("/zroot/vm-encrypted/" + vm_name + "/vm.config"):
            with open("/zroot/vm-encrypted/" + vm_name + "/vm.config", 'r') as file_object:
                vm_info_raw = file_object.read()
            vm_info_dict = ast.literal_eval(vm_info_raw)
            vmColumnVncPassword.append(vm_info_dict["vnc_password"])
        elif exists("/zroot/vm-unencrypted/" + vm_name + "/vm.config"):
            with open("/zroot/vm-unencrypted/" + vm_name + "/vm.config", 'r') as file_object:
                vm_info_raw = file_object.read()
            vm_info_dict = ast.literal_eval(vm_info_raw)
            vmColumnVncPassword.append(vm_info_dict["vnc_password"])
        else:
            vmColumnVncPassword.append("-")


    vmColumnDiskSize = []
    for vm_name in vmColumnNames:
        if exists("/zroot/vm-encrypted/" + vm_name + "/disk0.img"):
            command = "ls -ahl /zroot/vm-encrypted/" + vm_name + "/ | grep disk0.img | awk '{ print $5 }'"
            shell_command = subprocess.check_output(command, shell=True)
            disk_size = shell_command.decode("utf-8").split()[0]
            vmColumnDiskSize.append(disk_size)
        elif exists("/zroot/vm-unencrypted/" + vm_name + "/disk0.img"):
            command = "ls -ahl /zroot/vm-unencrypted/" + vm_name + "/ | grep disk0.img | awk '{ print $5 }'"
            shell_command = subprocess.check_output(command, shell=True)
            disk_size = shell_command.decode("utf-8").split()[0]
            vmColumnDiskSize.append(disk_size)
        else:
            vmColumnDiskSize.append("-")
   
   
    vmColumnDiskUsed = []
    for vm_name in vmColumnNames:
        if exists("/zroot/vm-encrypted/" + vm_name + "/disk0.img"):
            command = "du -h /zroot/vm-encrypted/" + vm_name + "/disk0.img | awk '{ print $1 }'"
            shell_command = subprocess.check_output(command, shell=True)
            disk_size = shell_command.decode("utf-8").split()[0]
            vmColumnDiskUsed.append(disk_size)
        elif exists("/zroot/vm-unencrypted/" + vm_name + "/disk0.img"):
            command = "du -h /zroot/vm-encrypted/" + vm_name + "/disk0.img | awk '{ print $1 }'"
            shell_command = subprocess.check_output(command, shell=True)
            disk_size = shell_command.decode("utf-8").split()[0]
            vmColumnDiskUsed.append(disk_size)
        else:
            vmColumnDiskUsed.append("-")

    
    vmColumnIpAddress = []
    for vm_name in vmColumnNames:
        if exists("/zroot/vm-encrypted/" + vm_name + "/vm.config"):
            with open("/zroot/vm-encrypted/" + vm_name + "/vm.config", 'r') as file_object:
                vm_info_raw = file_object.read()
            vm_info_dict = ast.literal_eval(vm_info_raw)
            vmColumnIpAddress.append(vm_info_dict["ip_address"])
        elif exists("/zroot/vm-unencrypted/" + vm_name + "/vm.config"):
            with open("/zroot/vm-unencrypted/" + vm_name + "/vm.config", 'r') as file_object:
                vm_info_raw = file_object.read()
            vm_info_dict = ast.literal_eval(vm_info_raw)
            vmColumnIpAddress.append(vm_info_dict["ip_address"])
        else:
            vmColumnIpAddress.append("-")

    
    vmColumnOsType = []
    for vm_name in vmColumnNames:
        if exists("/zroot/vm-encrypted/" + vm_name + "/vm.config"):
            with open("/zroot/vm-encrypted/" + vm_name + "/vm.config", 'r') as file_object:
                vm_info_raw = file_object.read()
            vm_info_dict = ast.literal_eval(vm_info_raw)
            vmColumnOsType.append(vm_info_dict["os_type"])
        elif exists("/zroot/vm-unencrypted/" + vm_name + "/vm.config"):
            with open("/zroot/vm-unencrypted/" + vm_name + "/vm.config", 'r') as file_object:
                vm_info_raw = file_object.read()
            vm_info_dict = ast.literal_eval(vm_info_raw)
            vmColumnOsType.append(vm_info_dict["os_type"])
        else:
            vmColumnOsType.append("-")
    vmColumnOsType = ["Debian 10" if var == "debian10" else var for var in vmColumnOsType]
    vmColumnOsType = ["Debian 11" if var == "debian11" else var for var in vmColumnOsType]
    vmColumnOsType = ["Ubuntu 20.04" if var == "ubuntu2004" else var for var in vmColumnOsType]
    vmColumnOsType = ["FreeBSD 13 ZFS" if var == "freebsd13zfs" else var for var in vmColumnOsType]
    vmColumnOsType = ["FreeBSD 13 UFS" if var == "freebsd13ufs" else var for var in vmColumnOsType]
    vmColumnOsType = ["AlmaLinux 8" if var == "almalinux8" else var for var in vmColumnOsType]
    vmColumnOsType = ["RockyLinux 8" if var == "rockylinux8" else var for var in vmColumnOsType]
    vmColumnOsType = ["Fedora 34" if var == "fedora34" else var for var in vmColumnOsType]
    vmColumnOsType = ["Windows 10" if var == "windows10" else var for var in vmColumnOsType]

    
    vmColumnUptime = []
    for vm_name in vmColumnNames:
        if vm_name in runningVMs:
            command = "ps axwww -o etime,command > /tmp/bhyve_vms_uptime.txt"
            subprocess.run(command, shell=True)
            command = "grep 'bhyve: " + vm_name + "' /tmp/bhyve_vms_uptime.txt | grep -v grep | awk '{print $1}'"
            shell_command = subprocess.check_output(command, shell=True)
            vm_uptime = shell_command.decode("utf-8").split()[0]
            vmColumnUptime.append(vm_uptime)
        else:
            vmColumnUptime.append("-")

    vmColumnDescription = []
    for vm_name in vmColumnNames:
        if exists("/zroot/vm-encrypted/" + vm_name + "/vm.config"):
            with open("/zroot/vm-encrypted/" + vm_name + "/vm.config", 'r') as file_object:
                vm_info_raw = file_object.read()
            vm_info_dict = ast.literal_eval(vm_info_raw)
            vmColumnDescription.append(vm_info_dict["description"])
        elif exists("/zroot/vm-unencrypted/" + vm_name + "/vm.config"):
            with open("/zroot/vm-unencrypted/" + vm_name + "/vm.config", 'r') as file_object:
                vm_info_raw = file_object.read()
            vm_info_dict = ast.literal_eval(vm_info_raw)
            vmColumnDescription.append(vm_info_dict["description"])
        else:
            vmColumnDescription.append("-")


    vmTableHeader = [["Name", "State", "Encryption", "CPUs", "RAM", "VncPort", "VncPassword", "DiskSize", "DiskUsed", "VmIpAddr", "OsType", "VmUptime", "VmDescription", ]]

    for vm_index in range(len(vmColumnNames)):
        vmTableHeader.append([ vmColumnNames[vm_index], vmColumnStates[vm_index], vmColumnEncryption[vm_index], vmColumnCPU[vm_index], vmColumnRAM[vm_index], vmColumnVncPort[vm_index], vmColumnVncPassword[vm_index], vmColumnDiskSize[vm_index], vmColumnDiskUsed[vm_index], vmColumnIpAddress[vm_index], vmColumnOsType[vm_index], vmColumnUptime[vm_index], vmColumnDescription[vm_index], ])

    return tabulate(vmTableHeader, headers="firstrow", tablefmt="fancy_grid", showindex=range(1, len(vmColumnNames) + 1))
    ### EOF_VM_TABLE ###

##############################################################

""" Section below is responsible for the CLI input/output """
app = typer.Typer(context_settings=dict(max_content_width=800))
# app.add_typer(vmlist.app, name="list")
app.add_typer(vmdeploy.app, name="deploy", help="Manage users in the app.")

@app.command()
def list(json: bool = typer.Option(False, help="Output json instead of a table")):
    """
    Example: hoster vm list
    """
    if json:
        vm_list.VmListJson()
    else:
        vm_list.VmListTable()

""" If this file is executed from the command line, activate Typer """
if __name__ == "__main__":
    app()