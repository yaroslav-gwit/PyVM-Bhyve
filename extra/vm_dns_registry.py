import os
import sys
import subprocess
from os.path import exists
from jinja2 import Template
import re
import ast
from os import listdir

def vm_dns_registry():
    #_ VM List _#
    vmColumnNames = []
    zfs_datasets = ["zroot/vm-encrypted", "zroot/vm-unencrypted"]
    for dataset in zfs_datasets:
        if exists("/" + dataset + "/"):
            _dataset_listing = listdir("/" + dataset + "/")
            for vm_directory in _dataset_listing:
                if exists("/" + dataset + "/" + vm_directory + "/vm.config"):
                    vmColumnNames.append(vm_directory)
    vmColumnNames.sort()
    #_ EOF VM List _#

    #_ IP addresses _#
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
    #_ EOF IP addresses _#

    # Code is here 2 times because it doesn't delete the item, if it's last in the list :(
    for old_ip_address in vmColumnIpAddress:
        if old_ip_address == "-":
            ip_address_index = vmColumnIpAddress.index(old_ip_address)
            del vmColumnIpAddress[ip_address_index]
            del vmColumnNames[ip_address_index]
    for old_ip_address in vmColumnIpAddress:
        if old_ip_address == "-":
            ip_address_index = vmColumnIpAddress.index(old_ip_address)
            del vmColumnIpAddress[ip_address_index]
            del vmColumnNames[ip_address_index]


    read_from_file = "./templates/unbound.conf"

    with open(read_from_file, 'r') as file_object:
        contents = file_object.read()

    # Read values from a given host, to support dynamic config
    with open("/root/bin/host.info", 'r') as file_object:
        host_info_raw = file_object.read()
    host_info_dict = ast.literal_eval(host_info_raw)
    host_dns_acls = host_info_dict["host_dns_acls"]
    # EOF Read values from a given host, to support dynamic config

    tm = Template(contents)
    msg_unbound_template = tm.render(vmColumnNames=vmColumnNames, vmColumnIpAddress=vmColumnIpAddress, host_dns_acls = host_dns_acls)

    write_to_file = "/var/unbound/unbound.conf"
    
    with open(write_to_file, 'w') as file_object:
        file_object.write(msg_unbound_template)

    command = "service local_unbound reload"
    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)