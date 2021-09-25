#!bin/python
import os
import sys
import subprocess
import wget
from os.path import exists
from generate_mac import generate_mac
import random
from jinja2 import Template
import ast
from os import listdir

# Own classes
from vm_dns_registry import vm_dns_registry


class VmDeployment():
    def __init__(self, new_vm_name = "None", old_vm_name = "None", vm_ipaddress = "None", vm_os_type = "debian10", vm_encryption = "encrypted", vm_start = "No", vm_macaddress = "None"):
        self.new_vm_name = new_vm_name
        self.vm_ipaddress = vm_ipaddress
        self.vm_os_type = vm_os_type
        self.vm_encryption = vm_encryption
        self.vm_start = vm_start
        self.vm_macaddress = vm_macaddress
        self.old_vm_name = old_vm_name

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
        self.vmColumnNames = vmColumnNames
        #_ EOF VM List _#

        #_ VM is running check _#
        runningVMs = []
        stoppedVMs = []
        if exists("/dev/vmm/"):
            command = "ls /dev/vmm/ || true"
            shell_command = subprocess.check_output(command, shell=True)
            runningVMs = shell_command.decode("utf-8").split()
        else:
            runningVMs = []
        for vm in vmColumnNames:
            if vm not in runningVMs:
                stoppedVMs.append(vm)
        
        self.stoppedVMs = stoppedVMs
        #_ EOF VM is running check _#

        #_ IP Addresses _#
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
        #_ EOF IP Addresses _#

        #_ VNC Port list _#
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
        
        vmColumnVncPort = list(map(int, vmColumnVncPort))
        vm_vnc_port = 5900
        while vm_vnc_port in vmColumnVncPort:
            vm_vnc_port = vm_vnc_port + 1
        
        self.vm_vnc_port = str(vm_vnc_port)
        #_ EOF VNC Port list _#

        # Read values from a given host, to support dynamic config
        with open("/root/bin/host.info", 'r') as file_object:
            host_info_raw = file_object.read()
        host_info_dict = ast.literal_eval(host_info_raw)

        host_internal_switch_subnet = host_info_dict["host_internal_switch_subnet"]
        self.host_internal_switch_subnet = host_internal_switch_subnet

        host_gateway = host_info_dict["host_gateway"]
        self.host_gateway = host_gateway

        host_ssh_keys = host_info_dict["host_ssh_keys"]
        self.host_ssh_keys = host_ssh_keys

        host_internal_switch_name = host_info_dict["host_internal_switch_name"]
        self.host_internal_switch_name = host_internal_switch_name
        # EOF Read values from a given host, to support dynamic config
        
        ip_address_list = []
        for ip in range(1, 254):
            ip_address_list.append(host_internal_switch_subnet + str(ip))

        vm_os_type_list = [ "debian10", "debian11", "freebsd13zfs", "freebsd13ufs", "ubuntu2004", "almalinux8", "fedora34", "openbsd6", "rockylinux8", "windows10"]
        
        if new_vm_name == "None":
            random_vm_number = 1
            random_vm_name = "test-vm-"
            
            new_vm_name = random_vm_name + str(random_vm_number)
            
            while new_vm_name in vmColumnNames:
                random_vm_number = random_vm_number + 1
                new_vm_name = random_vm_name + str(random_vm_number)
            
            self.new_vm_name = new_vm_name

        elif new_vm_name in vmColumnNames:
            print("VM with that name already exists!")
            exit(1)

        
        if vm_ipaddress == "None":
            for ip in vmColumnIpAddress:
                if ip in ip_address_list:
                    ip_address_list.remove(ip)
            self.vm_ipaddress = ip_address_list[0]
           
        elif vm_ipaddress == host_gateway:
            print("IP address is assigned to internal router!")
            exit(1)
        elif vm_ipaddress not in ip_address_list:
            print("This is not an IP address, or the IP doesn't belong to this pool of addresses")
            exit(1)
        elif vm_ipaddress in vmColumnIpAddress:
            print("IP address is in use!")
            exit(1)


        if vm_macaddress == "None":
            vm_macaddress = generate_mac.vid_provided('58:9C:FC')
            self.vm_macaddress = vm_macaddress.lower()
        elif generate_mac.is_mac_address(vm_macaddress) != True:
            print("Please make sure you use a proper MAC address!")
            exit(1)


        if vm_os_type in vm_os_type_list:
            # Rocky Linux 8 (CentOS Clone)
            if vm_os_type == "rockylinux8":
                folders = ["zroot/vm-encrypted/rockylinux8-template", "zroot/vm-unencrypted/rockylinux8-template",]
                qcow_disk_file = "rockylinux8.vdi"
                disk_file = "disk0.img"
                local_file = "/root/pyVM/vm_images/" + qcow_disk_file
                
                if not exists("/root/pyVM/vm_images/" + qcow_disk_file):
                    print("Can't find Rocky Linux 8 image locally, downloading now!")
                    
                    remote_url = "https://gateway-it.com/wp-content/uploads/2021/09/Arch-Linux-x86_64-cloudimg-20210906.0.qcow2"
                    wget.download(remote_url, local_file)
                    print("")
                
                for folder in folders:
                    if not exists("/" + folder):
                        command = "zfs create " + folder
                        subprocess.run(command, shell=True, stdout=None)
                    
                    if not exists("/" + folder + "/" + disk_file):
                        print("\nDisk image in " + folder + " was not found, copying it now!")
                        
                        command = "qemu-img convert -p " + local_file + " /" + folder + "/" + disk_file
                        subprocess.run(command, shell=True, stdout=None)

                        command = "truncate -s +5G " + "/" + folder + "/" + disk_file
                        subprocess.run(command, shell=True, stdout=None)
                        
                        print("Done!")
                        print("")

            # AlmaLinux 8 (CentOS Clone)
            if vm_os_type == "almalinux8":
                folders = ["zroot/vm-encrypted/almalinux8-template", "zroot/vm-unencrypted/almalinux8-template",]
                qcow_disk_file = "almalinux8.vdi"
                disk_file = "disk0.img"
                local_archive = "/root/pyVM/vm_images/almalinux8.zip"
                local_file = "/root/pyVM/vm_images/" + qcow_disk_file
                
                if not exists("/root/pyVM/vm_images/" + qcow_disk_file):
                    print("Can't find AlmaLinux 8 image locally, downloading now!")
                    
                    remote_url = "https://github.com/yaroslav-gwit/PyVM-Bhyve/releases/download/202109/almalinux8.zip"
                    wget.download(remote_url, local_archive)
                    command = "unzip " + local_archive + " -d /root/pyVM/vm_images/"
                    subprocess.run(command, shell=True, stdout=None)
                    command = "mv '/root/pyVM/vm_images/AlmaLinux 8.vdi' " + local_file
                    subprocess.run(command, shell=True, stdout=None)

                    print("")
                
                for folder in folders:
                    if not exists("/" + folder):
                        command = "zfs create " + folder
                        subprocess.run(command, shell=True, stdout=None)
                    
                    if not exists("/" + folder + "/" + disk_file):
                        print("\nDisk image in " + folder + " was not found, copying it now!")
                        
                        command = "qemu-img convert -p " + local_file + " /" + folder + "/" + disk_file
                        subprocess.run(command, shell=True, stdout=None)

                        command = "truncate -s +5G " + "/" + folder + "/" + disk_file
                        subprocess.run(command, shell=True, stdout=None)
                        
                        print("Done!")
                        print("")

            # Fedora 34
            if vm_os_type == "fedora34":
                folders = ["zroot/vm-encrypted/fedora34-template", "zroot/vm-unencrypted/fedora34-template",]
                qcow_disk_file = "fedora34.vdi"
                disk_file = "disk0.img"
                local_file = "/root/pyVM/vm_images/" + qcow_disk_file
                
                if not exists("/root/pyVM/vm_images/" + qcow_disk_file):
                    print("Can't find Fedora 34 image locally, downloading now!")
                    
                    remote_url = "https://gateway-it.com/wp-content/uploads/2021/09/Fedora-Cloud-Base-34-1.2.x86_64.qcow2"
                    wget.download(remote_url, local_file)
                    print("")
                
                for folder in folders:
                    if not exists("/" + folder):
                        command = "zfs create " + folder
                        subprocess.run(command, shell=True, stdout=None)
                    
                    if not exists("/" + folder + "/" + disk_file):
                        print("\nDisk image in " + folder + " was not found, copying it now!")
                        
                        command = "qemu-img convert -p " + local_file + " /" + folder + "/" + disk_file
                        subprocess.run(command, shell=True, stdout=None)

                        command = "truncate -s +5G " + "/" + folder + "/" + disk_file
                        subprocess.run(command, shell=True, stdout=None)
                        
                        print("Done!")
                        print("")
            
            # FreeBSD 13 ZFS
            if vm_os_type == "freebsd13zfs":
                folders = ["zroot/vm-encrypted/freebsd13zfs-template", "zroot/vm-unencrypted/freebsd13zfs-template",]
                qcow_disk_file = "freebsd13zfs.qcow2"
                disk_file = "disk0.img"
                local_file = "/root/pyVM/vm_images/" + qcow_disk_file
                
                if not exists("/root/pyVM/vm_images/" + qcow_disk_file):
                    print("Can't find FreeBSD 13 ZFS image locally, downloading now!")
                    
                    remote_url = "https://gateway-it.com/wp-content/uploads/2021/09/freebsd-13.0-zfs.qcow2"
                    wget.download(remote_url, local_file)
                    print("")
                
                for folder in folders:
                    if not exists("/" + folder):
                        command = "zfs create " + folder
                        subprocess.run(command, shell=True, stdout=None)
                    
                    if not exists("/" + folder + "/" + disk_file):
                        print("\nDisk image in " + folder + " was not found, copying it now!")
                        
                        command = "qemu-img convert -p " + local_file + " /" + folder + "/" + disk_file
                        subprocess.run(command, shell=True, stdout=None)

                        command = "truncate -s +12G " + "/" + folder + "/" + disk_file
                        subprocess.run(command, shell=True, stdout=None)
                        
                        print("Done!")
                        print("")

            # FreeBSD 13 UFS
            if vm_os_type == "freebsd13ufs":
                folders = ["zroot/vm-encrypted/freebsd13ufs-template", "zroot/vm-unencrypted/freebsd13ufs-template",]
                qcow_disk_file = "freebsd13ufs.img"
                disk_file = "disk0.img"
                local_file = "/root/pyVM/vm_images/" + qcow_disk_file
                local_archive = "/root/pyVM/vm_images/freebsd13ufs.zip"
                
                if not exists("/root/pyVM/vm_images/" + qcow_disk_file):
                    print("Can't find FreeBSD13 image locally, downloading now!")
                    
                    remote_url = "https://github.com/yaroslav-gwit/PyVM-Bhyve/releases/download/202109/debian11.zip"
                    wget.download(remote_url, local_archive)
                    print("")
                    command = "unzip " + local_archive + " -d /root/pyVM/vm_images"
                    subprocess.run(command, shell=True, stdout=None)
                    command = "rm " + local_archive
                    subprocess.run(command, shell=True, stdout=None)

                    print("")
                
                for folder in folders:
                    if not exists("/" + folder):
                        command = "zfs create " + folder
                        subprocess.run(command, shell=True, stdout=None)
                    
                    if not exists("/" + folder + "/" + disk_file):
                        print("\nDisk image in " + folder + " was not found, copying it now!")
                        
                        command = "pv " + local_file + " > /" + folder + "/" + disk_file
                        subprocess.run(command, shell=True, stdout=None)

                        command = "truncate -s +5G " + "/" + folder + "/" + disk_file
                        subprocess.run(command, shell=True, stdout=None)
                        
                        print("Done!")
                        print("")
            
            # Debian 10
            if vm_os_type == "debian10":
                folders = ["zroot/vm-encrypted/debian10-template", "zroot/vm-unencrypted/debian10-template",]
                qcow_disk_file = "debian10.qcow2"
                disk_file = "disk0.img"
                local_file = "/root/pyVM/vm_images/" + qcow_disk_file
                
                if not exists("/root/pyVM/vm_images/" + qcow_disk_file):
                    print("Can't find Debian 10 image locally, downloading now!")
                    
                    remote_url = "https://gateway-it.com/wp-content/uploads/2021/04/debian-10.qcow2"
                    wget.download(remote_url, local_file)
                    print("")
                
                for folder in folders:
                    if not exists("/" + folder):
                        command = "zfs create " + folder
                        subprocess.run(command, shell=True, stdout=None)
                    
                    if not exists("/" + folder + "/" + disk_file):
                        print("\nDisk image in " + folder + " was not found, copying it now!")
                        
                        command = "qemu-img convert -p " + local_file + " /" + folder + "/" + disk_file
                        subprocess.run(command, shell=True, stdout=None)

                        command = "truncate -s +13G " + "/" + folder + "/" + disk_file
                        subprocess.run(command, shell=True, stdout=None)
                        
                        print("Done!")
                        print("")
            
            # Debian 11
            if vm_os_type == "debian11":
                folders = ["zroot/vm-encrypted/debian11-template", "zroot/vm-unencrypted/debian11-template",]
                qcow_disk_file = "debian11.img"
                disk_file = "disk0.img"
                local_file = "/root/pyVM/vm_images/" + qcow_disk_file
                local_archive = "/root/pyVM/vm_images/debian11.zip"
                
                if not exists("/root/pyVM/vm_images/" + qcow_disk_file):
                    print("Can't find Debian 11 image locally, downloading now!")
                    
                    remote_url = "https://github.com/yaroslav-gwit/PyVM-Bhyve/releases/download/202109/debian11.zip"
                    wget.download(remote_url, local_archive)
                    print("")
                    command = "unzip " + local_archive + " -d /root/pyVM/vm_images"
                    subprocess.run(command, shell=True, stdout=None)
                    command = "rm " + local_archive
                    subprocess.run(command, shell=True, stdout=None)

                    print("")
                
                for folder in folders:
                    if not exists("/" + folder):
                        command = "zfs create " + folder
                        subprocess.run(command, shell=True, stdout=None)
                    
                    if not exists("/" + folder + "/" + disk_file):
                        print("\nDisk image in " + folder + " was not found, copying it now!")
                        
                        command = "pv " + local_file + " > /" + folder + "/" + disk_file
                        subprocess.run(command, shell=True, stdout=None)

                        command = "truncate -s +5G " + "/" + folder + "/" + disk_file
                        subprocess.run(command, shell=True, stdout=None)
                        
                        print("Done!")
                        print("")

            # OpenBSD 6
            if vm_os_type == "openbsd6":
                folders = ["zroot/vm-encrypted/openbsd6-template", "zroot/vm-unencrypted/openbsd6-template",]
                qcow_disk_file = "openbsd6.raw"
                disk_file = "disk0.img"
                local_file = "/root/pyVM/vm_images/" + qcow_disk_file

                if not exists("/root/pyVM/vm_images/" + qcow_disk_file):
                    print("Can't find OpenBSD 6 image locally, downloading now!")

                    remote_url = "https://gateway-it.com/wp-content/uploads/2021/09/openbsd-6.9.qcow2"
                    wget.download(remote_url, local_file)
                    print("")
                
                for folder in folders:
                    if not exists("/" + folder):
                        command = "zfs create " + folder
                        subprocess.run(command, shell=True, stdout=None)
                    
                    if not exists("/" + folder + "/" + disk_file):
                        print("\nDisk image in " + folder + " was not found, copying it now!")
                        
                        command = "qemu-img convert -p " + local_file + " /" + folder + "/" + disk_file
                        subprocess.run(command, shell=True)

                        command = "truncate -s +11G " + "/" + folder + "/" + disk_file
                        subprocess.run(command, shell=True, stdout=None)
                        
                        print("Done!")
                        print("")
            
            # Ubuntu 20.04
            if vm_os_type == "ubuntu2004":
                folders = ["zroot/vm-encrypted/ubuntu2004-template", "zroot/vm-unencrypted/ubuntu2004-template",]
                qcow_disk_file = "ubuntu2004.vmdk"
                disk_file = "disk0.img"
                local_file = "/root/pyVM/vm_images/" + qcow_disk_file

                if not exists("/root/pyVM/vm_images/" + qcow_disk_file):
                    print("Can't find Ubuntu 20.04 image locally, downloading now!")

                    remote_url = "https://gateway-it.com/wp-content/uploads/2021/09/focal-server-cloudimg-amd64.vmdk"
                    wget.download(remote_url, local_file)
                    print("")
                
                for folder in folders:
                    if not exists("/" + folder):
                        command = "zfs create " + folder
                        subprocess.run(command, shell=True, stdout=None)
                    
                    if not exists("/" + folder + "/" + disk_file):
                        print("\nDisk image in " + folder + " was not found, copying it now!")
                        
                        command = "qemu-img convert -p " + local_file + " /" + folder + "/" + disk_file
                        subprocess.run(command, shell=True)

                        command = "truncate -s +5G " + "/" + folder + "/" + disk_file
                        subprocess.run(command, shell=True, stdout=None)
                        
                        print("Done!")
                        print("")

            # Windows 10
            if vm_os_type == "windows10":
                folders = ["zroot/vm-encrypted/windows10-template", "zroot/vm-unencrypted/windows10-template",]
                qcow_disk_file = "windows10.vdi"
                disk_file = "disk0.img"
                local_file = "/root/pyVM/vm_images/" + qcow_disk_file

                if not exists("/root/pyVM/vm_images/" + qcow_disk_file):
                    print("Can't find Windows 10 image locally, downloading now!")

                    remote_url = "https://gateway-it.com/wp-content/uploads/2021/09/focal-server-cloudimg-amd64.vmdk"
                    wget.download(remote_url, local_file)
                    print("")
                
                for folder in folders:
                    if not exists("/" + folder):
                        command = "zfs create " + folder
                        subprocess.run(command, shell=True, stdout=None)
                    
                    if not exists("/" + folder + "/" + disk_file):
                        print("\nDisk image in " + folder + " was not found, copying it now!")
                        
                        command = "qemu-img convert -p " + local_file + " /" + folder + "/" + disk_file
                        subprocess.run(command, shell=True)

                        # command = "truncate -s +20G " + "/" + folder + "/" + disk_file
                        # subprocess.run(command, shell=True, stdout=None)
                        
                        print("Done!")
                        print("")

        else:
            print("We don't support this OS for a quick deploy. Please choose another one from the list:")
            vm_os_type_list.sort()
            for os_type in vm_os_type_list:
                print(os_type)
            exit(1)

        
        if vm_encryption == ("encrypted" or "Encrypted"):
            self.vm_encryption = "encrypted"
        else:
            self.vm_encryption = "unecrypted"


    def password_generator(number=10, capitals="no"):
        def split(word):
            return [char for char in word]

        valid_letters = "asdfghjklqwertyuiopzxcvbnm"
        valid_letters = split(valid_letters)

        if capitals == "yes":
            capitals = "ASDFGHJKLZXCVBNMQWERTYUIOP"
            capitals = split(capitals)
            valid_letters = valid_letters + capitals
        
        valid_numbers = "0987654321"
        valid_numbers = split(valid_numbers)
        valid_characters = valid_letters + valid_numbers

        password_final = ""

        for password in range(0, number):
            password_final = password_final + random.choice(valid_characters)
            
        return password_final
    
    
    def vm_deploy_command(self):
        ### ZFS Clone section ###
        if self.vm_os_type == "rockylinux8" and self.vm_encryption == "encrypted":
            zfs_dataset = "zroot/vm-encrypted/rockylinux8-template"
        elif self.vm_os_type == "rockylinux8" and self.vm_encryption == "unencrypted":
            zfs_dataset = "zroot/vm-unencrypted/rockylinux8-template"

        if self.vm_os_type == "fedora34" and self.vm_encryption == "encrypted":
            zfs_dataset = "zroot/vm-encrypted/fedora34-template"
        elif self.vm_os_type == "fedora34" and self.vm_encryption == "unencrypted":
            zfs_dataset = "zroot/vm-unencrypted/fedora34-template"

        if self.vm_os_type == "almalinux8" and self.vm_encryption == "encrypted":
            zfs_dataset = "zroot/vm-encrypted/almalinux8-template"
        elif self.vm_os_type == "almalinux8" and self.vm_encryption == "unencrypted":
            zfs_dataset = "zroot/vm-unencrypted/almalinux8-template"

        if self.vm_os_type == "freebsd13ufs" and self.vm_encryption == "encrypted":
            zfs_dataset = "zroot/vm-encrypted/freebsd13ufs-template"
        elif self.vm_os_type == "freebsd13ufs" and self.vm_encryption == "unencrypted":
            zfs_dataset = "zroot/vm-unencrypted/freebsd13ufs-template"

        if self.vm_os_type == "freebsd13zfs" and self.vm_encryption == "encrypted":
            zfs_dataset = "zroot/vm-encrypted/freebsd13zfs-template"
        elif self.vm_os_type == "freebsd13zfs" and self.vm_encryption == "unencrypted":
            zfs_dataset = "zroot/vm-unencrypted/freebsd13zfs-template"

        if self.vm_os_type == "debian10" and self.vm_encryption == "encrypted":
            zfs_dataset = "zroot/vm-encrypted/debian10-template"
        elif self.vm_os_type == "debian10" and self.vm_encryption == "unencrypted":
            zfs_dataset = "zroot/vm-unencrypted/debian10-template"

        if self.vm_os_type == "debian11" and self.vm_encryption == "encrypted":
            zfs_dataset = "zroot/vm-encrypted/debian11-template"
        elif self.vm_os_type == "debian11" and self.vm_encryption == "unencrypted":
            zfs_dataset = "zroot/vm-unencrypted/debian11-template"

        if self.vm_os_type == "openbsd6" and self.vm_encryption == "encrypted":
            zfs_dataset = "zroot/vm-encrypted/openbsd6-template"
        elif self.vm_os_type == "openbsd6" and self.vm_encryption == "unencrypted":
            zfs_dataset = "zroot/vm-unencrypted/openbsd6-template"

        if self.vm_os_type == "ubuntu2004" and self.vm_encryption == "encrypted":
            zfs_dataset = "zroot/vm-encrypted/ubuntu2004-template"
        elif self.vm_os_type == "ubuntu2004" and self.vm_encryption == "unencrypted":
            zfs_dataset = "zroot/vm-unencrypted/ubuntu2004-template"

        if self.vm_os_type == "windows10" and self.vm_encryption == "encrypted":
            zfs_dataset = "zroot/vm-encrypted/windows10-template"
        elif self.vm_os_type == "windows10" and self.vm_encryption == "unencrypted":
            zfs_dataset = "zroot/vm-unencrypted/windows10-template"

        if self.vm_encryption == "encrypted":
            zfs_dataset_vm = "zroot/vm-encrypted/"
        else:
            zfs_dataset_vm = "zroot/vm-unencrypted/"

        random_snapshot_name = VmDeployment.password_generator()
        random_vnc_password = VmDeployment.password_generator(20, "yes")

        command = "zfs snapshot " + zfs_dataset + "@" + random_snapshot_name
        # print(command)
        subprocess.run(command, shell=True, stdout=None)
        
        command = "zfs clone " + zfs_dataset + "@" + random_snapshot_name + " " + zfs_dataset_vm + self.new_vm_name
        subprocess.run(command, shell=True, stdout=None)

        ### Cloud Init READ Section ###
        to_save_dir = "./templates/cloudinit/"

        # NETWORK CONFIG #
        filename = "network-config"
        full_path = to_save_dir + filename

        with open(full_path, 'r') as file_object:
            contents = file_object.read()

        tm = Template(contents)
        msg_network = tm.render(gateway=self.host_gateway, mac_address=self.vm_macaddress, ip_address=self.vm_ipaddress, vm_os_type=self.vm_os_type)

        # USER DATA #
        filename = "user-data"
        full_path = to_save_dir + filename

        with open(full_path, 'r') as file_object:
            contents = file_object.read()

        sshkeys = self.host_ssh_keys

        root_password = VmDeployment.password_generator(51, "yes")
        debian_user_password = VmDeployment.password_generator(51, "yes")

        tm = Template(contents)
        msg_user = tm.render(root_password=root_password, sshkeys=sshkeys, os_type=self.vm_os_type, debian_user_password=debian_user_password)

        # META DATA #
        filename = "meta-data"
        full_path = to_save_dir + filename

        with open(full_path, 'r') as file_object:
            contents = file_object.read()

        random_instanse_id = VmDeployment.password_generator()

        tm = Template(contents)
        msg_meta = tm.render(random_instanse_id=random_instanse_id, vm_name=self.new_vm_name)

        ### Cloud Init WRITE Section ###
        write_to_dir = "/" + zfs_dataset_vm + self.new_vm_name + "/cloudinit/"

        if not exists(write_to_dir):
            command = "mkdir " + write_to_dir
            subprocess.run(command, shell=True, stdout=None)

        full_path = write_to_dir + "network-config"
        with open(full_path, 'w') as file_object:
            file_object.write(msg_network)
        
        full_path = write_to_dir + "user-data"
        with open(full_path, 'w') as file_object:
            file_object.write(msg_user)

        full_path = write_to_dir + "meta-data"
        with open(full_path, 'w') as file_object:
            file_object.write(msg_meta)

        ### VM Config Section ###
        os_without_virtio_block_drivers = [ "rockylinux8", "almalinux8", "windows10", "fedora34" ]
        if self.vm_os_type in os_without_virtio_block_drivers:
            read_from_file = "./templates/vm_conf_generic_legacy_drivers.conf"
        else:
            read_from_file = "./templates/vm_conf_generic.conf"
        write_to_file = "/" + zfs_dataset_vm + self.new_vm_name + "/vm.config"

        with open(read_from_file, 'r') as file_object:
            contents = file_object.read()

        tm = Template(contents)
        live_status = "Production"
        msg_vmtemplate = tm.render(cpus="2", memory="1G", switch=self.host_internal_switch_name, mac_address=self.vm_macaddress, vnc_port=self.vm_vnc_port, vnc_password=random_vnc_password, ip_address=self.vm_ipaddress, os_type=self.vm_os_type, live_status=live_status)

        with open(write_to_file, 'w') as file_object:
            file_object.write(msg_vmtemplate)

        write_to_dir = "/" + zfs_dataset_vm + self.new_vm_name + "/cloudinit/"
        vm_dir = "/" + zfs_dataset_vm + self.new_vm_name + "/"

        command = "genisoimage -output " + vm_dir + "seed.iso -volid cidata -joliet -rock " + write_to_dir + "user-data " + write_to_dir + "meta-data " + write_to_dir + "network-config"
        subprocess.run(command, shell=True, stderr = subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        ### EOF VM Config Section ###

        vm_dns_registry()

        if self.vm_start == "Yes":
            command = "pyvm --vmstart " + self.new_vm_name
            subprocess.run(command, shell=True, stderr = subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        
        print("VM " + self.new_vm_name + " was deployed!")


    def vm_ci_reset_command(self):
        new_vm_name = self.new_vm_name
        old_vm_name = self.old_vm_name

        if old_vm_name == "None":
            print("Invalid parameters. Hint:")
            print("pyvm --vmcireset --oldvm test-vm-1 --newvm production-vm-2")
            exit(0)
        elif new_vm_name == "None":
            print("Invalid parameters. Hint:")
            print("pyvm --vmcireset --oldvm test-vm-1 --newvm production-vm-2")
            exit(0)

        if old_vm_name not in self.vmColumnNames:
            print("Can't find such VM on the system, make sure you didn't make a typo")
            exit(0)
        elif old_vm_name not in self.stoppedVMs:
            print("VM is still running. You'll have to stop (or kill) it before resetting the config.")
            exit(0)

        
        #_ Read the config file _#
        if exists("/zroot/vm-encrypted/" + old_vm_name + "/vm.config"):
            with open("/zroot/vm-encrypted/" + old_vm_name + "/vm.config", 'r') as file_object:
                vm_info_raw = file_object.read()
            vm_info_dict = ast.literal_eval(vm_info_raw)
        elif exists("/zroot/vm-unencrypted/" + old_vm_name + "/vm.config"):
            with open("/zroot/vm-unencrypted/" + old_vm_name + "/vm.config", 'r') as file_object:
                vm_info_raw = file_object.read()
            vm_info_dict = ast.literal_eval(vm_info_raw)
        #_ EOF Read the config file _#
        
        os_type = vm_info_dict["os_type"]
        ip_address = vm_info_dict["ip_address"]
        network_mac = vm_info_dict["network_macs"][0]

        ### Cloud Init READ Section ###
        to_save_dir = "./templates/cloudinit/"

        # NETWORK CONFIG #
        filename = "network-config"
        full_path = to_save_dir + filename

        with open(full_path, 'r') as file_object:
            contents = file_object.read()

        tm = Template(contents)
        msg_network = tm.render(gateway=self.host_gateway, mac_address=network_mac, ip_address=ip_address, vm_os_type=os_type)
        # EOF NETWORK CONFIG #

        # USER DATA #
        filename = "user-data"
        full_path = to_save_dir + filename

        with open(full_path, 'r') as file_object:
            contents = file_object.read()

        sshkeys = self.host_ssh_keys

        root_password = VmDeployment.password_generator(51, "yes")
        debian_user_password = VmDeployment.password_generator(51, "yes")

        tm = Template(contents)
        msg_user = tm.render(root_password=root_password, sshkeys=sshkeys, os_type=os_type, debian_user_password=debian_user_password)
        # EOF USER DATA #

        # META DATA #
        filename = "meta-data"
        full_path = to_save_dir + filename

        with open(full_path, 'r') as file_object:
            contents = file_object.read()

        random_instanse_id = VmDeployment.password_generator()

        tm = Template(contents)
        msg_meta = tm.render(random_instanse_id=random_instanse_id, vm_name=new_vm_name)
        # EOF META DATA #

        if exists("/zroot/vm-encrypted/" + old_vm_name + "/vm.config"):
            zfs_dataset_current = "zroot/vm-encrypted/" + old_vm_name
            zfs_dataset_new = "zroot/vm-encrypted/" + new_vm_name
        else:
            zfs_dataset_current = "zroot/vm-unencrypted/" + old_vm_name
            zfs_dataset_new = "zroot/vm-unencrypted/" + new_vm_name

        command = "rm /" + zfs_dataset_current + "/cloudinit/*"
        subprocess.run(command, shell=True)
        command = "rm /" + zfs_dataset_current + "/seed.iso"
        subprocess.run(command, shell=True)

        command = "zfs rename " + zfs_dataset_current + " " + zfs_dataset_new
        subprocess.run(command, shell=True)
        
        ### Cloud Init WRITE Section ###
        write_to_dir = "/" + zfs_dataset_new + "/cloudinit/"

        if not exists(write_to_dir):
            command = "mkdir " + write_to_dir
            subprocess.run(command, shell=True, stdout=None)

        full_path = write_to_dir + "network-config"
        with open(full_path, 'w') as file_object:
            file_object.write(msg_network)
        
        full_path = write_to_dir + "user-data"
        with open(full_path, 'w') as file_object:
            file_object.write(msg_user)

        full_path = write_to_dir + "meta-data"
        with open(full_path, 'w') as file_object:
            file_object.write(msg_meta)

        # Generate ISO
        command = "genisoimage -output /" + zfs_dataset_new + "/seed.iso -volid cidata -joliet -rock " + write_to_dir + "user-data " + write_to_dir + "meta-data " + write_to_dir + "network-config"
        subprocess.run(command, shell=True, stderr = subprocess.DEVNULL, stdout=subprocess.DEVNULL)

        vm_dns_registry()