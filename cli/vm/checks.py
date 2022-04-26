#!bin/python3

# Native Python functions
import typer
import sys
import os
import subprocess
from os.path import exists
from os import listdir
import json
import time

# Installed packages/modules
from tabulate import tabulate
from natsort import natsorted

# Own functions
from cli.host import dataset


class CoreChecks:
    def __init__(self, vm_name, disk_image_name="disk0.img"):
        if not vm_name:
            print("Please supply a VM name!")
            sys.exit(1)
        self.vm_name = vm_name
        self.zfs_datasets = dataset.DatasetList().datasets
        self.disk_image_name = disk_image_name
        self.vm_config = VmConfigs(vm_name).vm_config_read()


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
        vm_info_dict = self.vm_config
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
    
    def vm_location(self):
        for ds in self.zfs_datasets["datasets"]:
            if exists(ds["mount_path"]+self.vm_name):
                vm_location = ds["zfs_path"] + "/" + self.vm_name
                return vm_location
            elif ds == len(self.zfs_datasets["datasets"]) and not exists(ds["mount_path"]+self.vm_name):
                sys.exit("VM doesn't exist!")
    
    def vm_folder(self):
        for ds in self.zfs_datasets["datasets"]:
            if exists(ds["mount_path"]+self.vm_name):
                vm_folder = ds["mount_path"] + self.vm_name
                return vm_folder
            elif ds == len(self.zfs_datasets["datasets"]) and not exists(ds["mount_path"]+self.vm_name):
                sys.exit("VM doesn't exist!")


    #_ VM START PORTION _#
    def vm_network_interfaces(self):
        vm_config = self.vm_config
        vm_network_interfaces = vm_config["networks"]
        return vm_network_interfaces

    def vm_disks(self):
        vm_config = self.vm_config
        vm_disks = vm_config["disks"]
        return vm_disks
    
    def vm_cpus(self):
        vm_config = self.vm_config
        vm_cpu = {}
        vm_cpu["cpu_sockets"] = vm_config.get("cpu_sockets", 1)
        vm_cpu["cpu_cores"] = vm_config.get("cpu_cores", 2)
        vm_cpu["memory"] = vm_config.get("memory", "1G")
        vm_cpu["vnc_port"] = vm_config.get("vnc_port", 5100)
        vm_cpu["vnc_password"] = vm_config.get("vnc_password", "NakHkX09a7pgZUQoEJzI")
        vm_cpu["loader"] = vm_config.get("loader", "uefi")
        vm_cpu["live_status"] = vm_config.get("live_status", "testing")
        return vm_cpu
    
    def vm_os_type(self):
        vm_config = self.vm_config
        os_type = vm_config.get("os_type", "default_os_type")
        return os_type


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
    
    
    def vm_config_manual_edit(self):
        for ds in self.zfs_datasets["datasets"]:
            vm_config = ds["mount_path"]+self.vm_name+self.vm_config
            if exists(vm_config):
                command = "nano " + vm_config
                shell_command = subprocess.run(command, shell=True)
                return
            elif ds == self.zfs_datasets["datasets"][-1] and not exists(vm_config):
                print("Sorry, config file was not found for " + self.vm_name + " path: " + vm_config)
                sys.exit(1)
    
    
    def vm_config_wrire(self):
        print("This function will write config files to the required directories")
