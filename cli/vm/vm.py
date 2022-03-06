#!bin/python

# Native Python functions
import typer
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
import json
import time
import datetime
from datetime import timedelta

# Installed packages/modules
import uptime
import psutil
from tabulate import tabulate
from natsort import natsorted

# Own functions
from cli.vm import vmdeploy
from cli.host import dataset

with open("/root/bin/host.info", 'r') as file_object:
    host_info_raw = file_object.read()
host_info_dict = ast.literal_eval(host_info_raw)

class CoreChecks:
    def __init__(self, vm_name, disk_image_name="disk0.img"):
        if not vm_name:
            print("Please supply a VM name!")
            sys.exit(1)
        self.vm_name = vm_name
        self.zfs_datasets = dataset.DatasetList().datasets
        self.disk_image_name = disk_image_name


    def vm_is_live(self):
        if exists("/dev/vmm/" + self.vm_name):
            return True
        else:
            return False
    

    def vm_is_encrypted(self):
        for ds in self.zfs_datasets["datasets"]:
            if exists(ds["mount_path"]+self.vm_name):
                return ds["encrypted"]

    
    def vm_in_production(self):
        vm_info_dict = VmConfigs(self.vm_name).vm_config_read()
        if vm_info_dict["live_status"] == "Production" or vm_info_dict["live_status"] == "production":
            return True
        else:
            return False
    
    
    def disk_exists(self):
        for ds in self.zfs_datasets["datasets"]:
            if exists(ds["mount_path"]+self.vm_name+"/"+self.disk_image_name):
                return True
    
    def disk_location(self):
        for ds in self.zfs_datasets["datasets"]:
            image_path = ds["mount_path"]+self.vm_name+"/"+self.disk_image_name
            if exists(image_path):
                return image_path


class VmConfigs:
    def __init__(self, vm_name):
        self.vm_name = vm_name
        self.zfs_datasets = dataset.DatasetList().datasets
        self.vm_config = "/vm_config.json"

    
    def vm_config_read(self):
        for ds in self.zfs_datasets["datasets"]:
            vm_config = ds["mount_path"]+self.vm_name+self.vm_config
            if exists(vm_config):
                with open(vm_config, 'r') as file:
                    vm_info_raw = file.read()
                vm_info_dict = json.loads(vm_info_raw)
                return vm_info_dict
            elif ds == self.zfs_datasets["datasets"][-1] and not exists(vm_config):
                print("Sorry, config file was not found for " + self.vm_name + " path: " + vm_config)
                sys.exit(1)
        
    
    def vm_config_wrire(self):
        print("This function will write config files to the required directories")

class VmList:
    def __init__(self):
        self.zfs_datasets = dataset.DatasetList().datasets
        
        vmColumnNames = []
        zfs_datasets_list = []
        for ds in self.zfs_datasets["datasets"]:
            if ds["type"] == "zfs":
                zfs_datasets_list.append(ds["zfs_path"])

        for ds in zfs_datasets_list:
            if exists("/" + ds + "/"):
                _dataset_listing = listdir("/" + ds + "/")
                for vm_directory in _dataset_listing:
                    if exists("/" + ds + "/" + vm_directory + "/vm_config.json"):
                        vmColumnNames.append(vm_directory)
            else:
                print("Please create 2 zfs datasets: " + zfs_datasets_list)
                sys.exit(1)
            
        self.vmColumnNames = natsorted(vmColumnNames)

    def table_output(self):
        vmColumnNames = self.vmColumnNames

        if len(vmColumnNames) < 1:
            print("\nThere are no VMs on this system. To deploy one, use:\n pyvm --vmdeploy\n")
            sys.exit(0)

        
        vmColumnState = []
        for vm_name in vmColumnNames:
            if CoreChecks(vm_name).vm_is_live():
                state = "🟢"
            else:
                state = "🔴"
            if CoreChecks(vm_name).vm_is_encrypted():
                state = state + "🔒"
            if CoreChecks(vm_name).vm_in_production():
                state = state + "🔁"
                #This is the icon to display if the VM is backed up 💾!
            vmColumnState.append(state)


        vmColumnCPU = []
        for vm_name in vmColumnNames:
            vm_config = VmConfigs(vm_name).vm_config_read()
            vm_config = vm_config.get("cpus", "-")
            vmColumnCPU.append(vm_config)

        
        vmColumnRAM = []
        for vm_name in vmColumnNames:
            vm_config = VmConfigs(vm_name).vm_config_read()
            vm_config = vm_config.get("memory", "-")
            vmColumnRAM.append(vm_config)
        

        vmColumnVncPort = []
        for vm_name in vmColumnNames:
            vm_config = VmConfigs(vm_name).vm_config_read()
            vm_config = vm_config.get("vnc_port", "-")
            vmColumnVncPort.append(vm_config)
        
        vmColumnVncPassword = []
        for vm_name in vmColumnNames:
            vm_config = VmConfigs(vm_name).vm_config_read()
            vm_config = vm_config.get("vnc_password", "-")
            vmColumnVncPassword.append(vm_config)


        vmColumnOsDisk = []
        for vm_name in vmColumnNames:
            vm_config = VmConfigs(vm_name).vm_config_read()
            vm_config = vm_config.get("disks", "-")
            disk_image_name = vm_config[0].get("disk_image", "-")
            if CoreChecks(vm_name, disk_image_name).disk_exists():
                image_path = CoreChecks(vm_name, disk_image_name).disk_location()
                command_size = "ls -ahl " + image_path + " | awk '{ print $5 }'"
                command_used = "du -h " + image_path + " | awk '{ print $1 }'"
                shell_command_size = subprocess.check_output(command_size, shell=True)
                shell_command_used = subprocess.check_output(command_used, shell=True)
                disk_size = shell_command_size.decode("utf-8").split()[0]
                disk_used = shell_command_used.decode("utf-8").split()[0]
                final_output = disk_used + "/" + disk_size
                vmColumnOsDisk.append(final_output)
            else:
                vmColumnOsDisk.append("-")
    
    
        vmColumnIpAddress = []
        for vm_name in vmColumnNames:
            vm_config = VmConfigs(vm_name).vm_config_read()
            vm_config = vm_config.get("networks", "-")
            vm_config = vm_config[0].get("ip_address", "-")
            vmColumnIpAddress.append(vm_config)

        
        vmColumnOsType = []
        for vm_name in vmColumnNames:
            vm_config = VmConfigs(vm_name).vm_config_read()
            vm_config = vm_config.get("os_comment", "-")
            vmColumnOsType.append(vm_config)
        # vmColumnOsType = ["Debian 10" if var == "debian10" else var for var in vmColumnOsType]
        # vmColumnOsType = ["Debian 11" if var == "debian11" else var for var in vmColumnOsType]
        # vmColumnOsType = ["Ubuntu 20.04" if var == "ubuntu2004" else var for var in vmColumnOsType]
        # vmColumnOsType = ["FreeBSD 13 ZFS" if var == "freebsd13zfs" else var for var in vmColumnOsType]
        # vmColumnOsType = ["FreeBSD 13 UFS" if var == "freebsd13ufs" else var for var in vmColumnOsType]
        # vmColumnOsType = ["AlmaLinux 8" if var == "almalinux8" else var for var in vmColumnOsType]
        # vmColumnOsType = ["RockyLinux 8" if var == "rockylinux8" else var for var in vmColumnOsType]
        # vmColumnOsType = ["Fedora 34" if var == "fedora34" else var for var in vmColumnOsType]
        # vmColumnOsType = ["Windows 10" if var == "windows10" else var for var in vmColumnOsType]

        
        vmColumnUptime = []
        for vm_name in vmColumnNames:
            if CoreChecks(vm_name).vm_is_live():
                timestamp = time.mktime((datetime.datetime.now() + timedelta(seconds=10)).timetuple())
                if timestamp < os.path.getmtime("/tmp/bhyve_vms_uptime.txt"):
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
            vm_config = VmConfigs(vm_name).vm_config_read()
            vm_config = vm_config.get("description", "-")
            vmColumnDescription.append(vm_config)


        vmTableHeader = [["Name", "State", "CPUs", "RAM", "Main IP", "VNC Port", "VNC Password", "OS Disk", "OS Comment", "Uptime", "Description", ]]

        for vm_index in range(len(vmColumnNames)):
            vmTableHeader.append([ vmColumnNames[vm_index], vmColumnState[vm_index], vmColumnCPU[vm_index], vmColumnRAM[vm_index], vmColumnIpAddress[vm_index], vmColumnVncPort[vm_index], vmColumnVncPassword[vm_index], vmColumnOsDisk[vm_index], vmColumnOsType[vm_index], vmColumnUptime[vm_index], vmColumnDescription[vm_index], ])

        return tabulate(vmTableHeader, headers="firstrow", tablefmt="fancy_grid", showindex=range(1, len(vmColumnNames) + 1))

    
    def json_output(self):
        vm_list_dict = {}
        vm_list_dict["vm_list"] = self.vmColumnNames
        vm_list_json = json.dumps(vm_list_dict, indent=2)
        return vm_list_json


""" Section below is responsible for the CLI input/output """
app = typer.Typer(context_settings=dict(max_content_width=800))
app.add_typer(vmdeploy.app, name="deploy", help="Manage users in the app.")
# app.add_typer(vmlist.app, name="list")

@app.command()
def list(json: bool = typer.Option(False, help="Output json instead of a table")):
    """
    Example: hoster vm list
    """
    if json:
        print(VmList().json_output())
    else:
        print(VmList().table_output())

@app.command()
def info(vmname: str = typer.Argument(..., help="Print VM config file to the screen")):
    """
    Example: hoster vm info test-vm-1
    """
    if json:
        print(VmList().json_output())
    else:
        print(VmList().table_output())



""" If this file is executed from the command line, activate Typer """
if __name__ == "__main__":
    app()