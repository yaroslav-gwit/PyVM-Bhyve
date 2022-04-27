#!bin/python

# Native Python functions
# from ipaddress import ip_address
import typer
import sys
import os
import subprocess
from os.path import exists
from os import listdir
import json
import time
import random

# Installed packages/modules
from tabulate import tabulate
from natsort import natsorted

# Own functions
# from cli.vm import vmdeploy
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
    
    def vm_ip_address(self):
        """
        Get VM's IP address
        """
        vm_info_dict = self.vm_config
        vm_ip_address = vm_info_dict["networks"][0]["ip_address"]
        return vm_ip_address


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
        
        if not vmColumnNames:
            print("\nThere are no VMs on this system. To deploy one, use:\n pyvm --vmdeploy\n")
            sys.exit(0)

        self.plainList = vmColumnNames.copy()
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
            vm_config = vm_config.get("cpu_cores", "-")
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
                if not exists("/tmp/bhyve_vms_uptime.txt"):
                    command = "ps axwww -o etime,command > /tmp/bhyve_vms_uptime.txt"
                    subprocess.run(command, shell=True)
                elif (time.time() - os.path.getmtime("/tmp/bhyve_vms_uptime.txt")) > 10:
                    command = "ps axwww -o etime,command > /tmp/bhyve_vms_uptime.txt"
                    subprocess.run(command, shell=True)
                command = "grep 'bhyve: " + vm_name + "' /tmp/bhyve_vms_uptime.txt | grep -v grep | awk '{print $1}'"
                shell_command = subprocess.check_output(command, shell=True)
                try:
                    vm_uptime = shell_command.decode("utf-8").split()[0]
                    vmColumnUptime.append(vm_uptime)
                except:
                    vmColumnUptime.append("-")
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
        # vm_list_dict = {}
        # vm_list_dict["vm_list"] = self.vmColumnNames
        vm_list_dict = self.vmColumnNames
        vm_list_json = json.dumps(vm_list_dict, indent=2)
        return vm_list_json


# class Generators:



class VmDeploy:
    def __init__(self, vm_name:str = "test-vm", ip_address:str = "10.0.0.0", os_type:str = "debian11"):
        #_ Load networks config _#
        with open("./configs/networks.json", "r") as file:
            networks_file = file.read()
        networks_dict = json.loads(networks_file)
        self.networks = networks_dict["networks"][0]

        #_ Load host config _#
        with open("./configs/host.json", "r") as file:
            host_file = file.read()
        host_dict = json.loads(host_file)
        self.host = host_dict

        self.vm_name = vm_name
        self.ip_address = ip_address
        
        self.existing_ip_addresses = []
        for _vm in VmList().plainList:
            ip_address = CoreChecks(vm_name=_vm).vm_ip_address()
            self.existing_ip_addresses.append(ip_address)
        
        self.existing_vms = VmList().plainList

        # OS Type Settings
        os_type_list = ["debian11", "ubuntu2004"]
        if os_type in os_type_list:
            self.os_type = os_type
        else:
            os_type_list = " ".join(os_type_list)
            sys.exit("Sorry this OS is not supported. Here is the list of supported OSes:\n" + os_type_list)

    @staticmethod
    def vm_name_generator(vm_name:str, existing_vms):
        # Generate test VM name and number
        number = 1
        if vm_name in existing_vms:
            print("VM with this name exists: " + vm_name)
            sys.exit(0)
        elif vm_name == "test-vm":
            vm_name = "test-vm-" + str(number)
            while vm_name in existing_vms:
                number = number + 1
                vm_name = "test-vm-" + str(number)
        else:
            vm_name = vm_name
        return vm_name
    
    @staticmethod
    def ip_address_generator(ip_address:str, networks, existing_ip_addresses):
        if ip_address in existing_ip_addresses and vm_name != "test-vm":
            print("VM with such IP exists: " + vm_name + "/" + self.ip_address)
        elif ip_address == "10.0.0.0":
            bridge_address = networks["bridge_address"]
            range_start = networks["range_start"]
            range_end = networks["range_end"]
            
            # Generate full list of IPs for the specified range
            bridge_split = bridge_address.split(".")
            del bridge_split[-1]
            bridge_join = ".".join(bridge_split) + "."

            ip_address_list = []
            for number in range(range_start, range_end+1):
                _ip_address = bridge_join + str(number)
                ip_address_list.append(_ip_address)
            
            ip_address = ip_address_list[0]
            number = range_start
            while ip_address in existing_ip_addresses:
                number = number + 1
                if number > range_end:
                    sys.exit("There are no free IPs left!")
                else:
                    ip_address = bridge_join + str(number)

        return ip_address
    
    @staticmethod
    def random_password_generator(capitals:bool = False, numbers:bool = False, lenght:int = 8):
        letters_var = "asdfghjklqwertyuiopzxcvbnm"
        capitals_var = "ASDFGHJKLZXCVBNMQWERTYUIOP"
        numbers_var = "0987654321"
        
        valid_chars_list = []
        for item in letters_var:
            valid_chars_list.append(item)
        if capitals:
            for item in capitals_var:
                valid_chars_list.append(item)
        if numbers:
            for item in numbers_var:
                valid_chars_list.append(item)
        
        password = ""
        for iteration in range(0, lenght):
            password = password + random.choice(valid_chars_list)
        
        return password
    

    def output_dict(self):
        output_dict = {}
        output_dict["vm_name"] = VmDeploy.vm_name_generator(vm_name=self.vm_name, existing_vms=self.existing_vms)
        output_dict["ip_address"] = VmDeploy.ip_address_generator(ip_address=self.ip_address, networks=self.networks, existing_ip_addresses=self.existing_ip_addresses)
        output_dict["os_type"] = self.os_type
        output_dict["root_password"] = VmDeploy.random_password_generator(lenght=12, capitals=True)
        return output_dict
    
    def deploy(self):
        pass

    

class Operation:
    @staticmethod
    def snapshot(vm_name:str, stype:str="custom", keep:int=3):
        """
        Function responsible for taking VM Snapshots
        """

        snapshot_type = stype
        snapshots_to_keep = keep
        snapshot_type_list = [ "replication", "custom", "hourly", "daily", "weekly", "monthly", "yearly" ]
        if vm_name in VmList().plainList:
            date_now = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
            snapshot_name = snapshot_type + "_" + date_now
            command = "zfs snapshot " + CoreChecks(vm_name).vm_location() + "@" + snapshot_name
            subprocess.run(command, shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            # DEBUG
            # print(command)
            print("New snapshot was taken: " + command)
        else:
            sys.exit("VM doesn't exist on this system.")
            
        # Remove old snapshots
        if snapshot_type != "custom":
            # Get the snapshot list
            command = "zfs list -r -t snapshot " + CoreChecks(vm_name).vm_location() + " | tail +2 | awk '{ print $1 }' | grep " + snapshot_type
            shell_command = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL)
            vm_zfs_snapshot_list = shell_command.decode("utf-8").split()

            # Generate list of snapshots to delete
            vm_zfs_snapshots_to_delete = vm_zfs_snapshot_list.copy()
            if len(vm_zfs_snapshots_to_delete) > 0 and len(vm_zfs_snapshots_to_delete) > snapshots_to_keep:
                for zfs_snapshot in range(0, snapshots_to_keep):
                    del vm_zfs_snapshots_to_delete[-1]
                # Remove the old snapshots
                for vm_zfs_snapshot_to_delete in vm_zfs_snapshots_to_delete:
                    command = "zfs destroy " + vm_zfs_snapshot_to_delete
                    subprocess.run(command, shell=True)
                    print("Old snapshot was removed: " + command)
            else:
                print("VM " + vm_name + " doesn't have any '" + snapshot_type + "' snapshots to delete")

    @staticmethod
    def destroy(vm_name:str, force:bool=False):
        """
        Function responsible for completely removing VMs from the system
        """
        if force == True and CoreChecks(vm_name).vm_is_live():
            kill(vm_name=vm_name)
            time.sleep(3)

        if vm_name not in VmList().plainList:
            sys.exit("VM doesn't exist on this system.")
        elif CoreChecks(vm_name).vm_is_live():
            print("VM is still running. You'll have to stop (or kill) it first.")
        else:
            command = "zfs destroy -rR " + CoreChecks(vm_name).vm_location()
            # ADD DEBUG/FAKE RUN
            shell_command = subprocess.check_output(command, shell=True)
            print("The VM was destroyed: " + command)

    @staticmethod
    def kill(vm_name:str):
        """
        Function that forcefully kills the VM
        """
        if vm_name not in VmList().plainList:
            sys.exit("VM doesn't exist on this system.")
        elif CoreChecks(vm_name).vm_is_live():
            # This block is a duplicate. Creating a function would be a good idea for the future!
            command = "ifconfig | grep " + vm_name + " | awk '{ print $2 }'"
            shell_command = subprocess.check_output(command, shell=True)
            tap_interface_list = shell_command.decode("utf-8").split()

            command = "bhyvectl --destroy --vm=" + vm_name
            shell_command = subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            time.sleep(1)

            if tap_interface_list:
                for tap in tap_interface_list:
                    if tap:
                        command = "ifconfig " + tap + " destroy"
                        shell_command = subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("Killed the VM: " + vm_name)
        else:
            # This block is a duplicate. Creating a function would be a good idea for the future!
            command = "ifconfig | grep " + vm_name + " | awk '{ print $2 }'"
            shell_command = subprocess.check_output(command, shell=True)
            tap_interface_list = shell_command.decode("utf-8").split()
            if tap_interface_list:
                for tap in tap_interface_list:
                    if tap:
                        command = "ifconfig " + tap + " destroy"
                        shell_command = subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("VM is already dead: " + vm_name + "!")

    @staticmethod
    def start(vm_name:str):
        if CoreChecks(vm_name).vm_is_live():
            print("VM is already live: " + vm_name)
        elif vm_name in VmList().plainList:
            print("Starting the VM: " + vm_name)
        
            #_ NETWORKING - Create required TAP interfaces _#
            vm_network_interfaces = CoreChecks(vm_name).vm_network_interfaces()
            tap_interface_number = 0
            tap_interface_list = []
        
            for interface in range(len(vm_network_interfaces)):
                command = "ifconfig | grep -G '^tap' | awk '{ print $1 }' | sed s/://"
                shell_command = subprocess.check_output(command, shell=True)
                existing_tap_interfaces = shell_command.decode("utf-8").split()
                tap_interface = "tap" + str(tap_interface_number)
                while tap_interface in existing_tap_interfaces:
                    tap_interface_number = tap_interface_number + 1
                    tap_interface = "tap" + str(tap_interface_number)
                # print(tap_interface)
                
                command = "ifconfig " + tap_interface + " create"
                # print(command)
                subprocess.run(command, shell=True)
                
                command = "ifconfig vm-" + vm_network_interfaces[interface]["network_bridge"] + " addm " + tap_interface
                # print(command)
                subprocess.run(command, shell=True)
                
                command = "ifconfig vm-"+ vm_network_interfaces[interface]["network_bridge"] + " up"
                # print(command)
                subprocess.run(command, shell=True)
                
                command = 'ifconfig ' + tap_interface + ' description ' + '"' + tap_interface + ' ' + vm_name + ' ' + 'interface' + str(interface) + '"'
                # print(command)
                subprocess.run(command, shell=True)
                
                tap_interface_list.append(tap_interface)
        
            #_ NEXT SECTION _#
            command1 = "bhyve -HAw -s 0:0,hostbridge -s 31,lpc "

            bhyve_pci_1 = 2
            bhyve_pci_2 = 0
            space = " "
            if len(vm_network_interfaces) > 1:
                for interface in range(len(vm_network_interfaces)):
                    network_adaptor_type = vm_network_interfaces[interface]["network_adaptor_type"]
                    generic_network_text = "," + network_adaptor_type + ","
                    if interface == 0:
                        network_final = "-s " + str(bhyve_pci_1) + ":" + str(bhyve_pci_2) + generic_network_text + tap_interface_list[interface] + ",mac=" + vm_network_interfaces[interface]["network_mac"]
                    else:
                        bhyve_pci_2 = bhyve_pci_2 + 1
                        network_final = network_final + space + "-s " + str(bhyve_pci_1) + ":" + str(bhyve_pci_2) + generic_network_text + tap_interface_list[interface] + ",mac=" + vm_network_interfaces[interface]["network_mac"]
            else:
                network_adaptor_type = vm_network_interfaces[0]["network_adaptor_type"]
                generic_network_text = "," + network_adaptor_type + ","
                network_final = "-s " + str(bhyve_pci_1) + ":" + str(bhyve_pci_2) + generic_network_text + tap_interface_list[0] + ",mac=" + vm_network_interfaces[0]["network_mac"]

            command2 = network_final

            bhyve_pci = 3
            vm_disks = CoreChecks(vm_name).vm_disks()
            if len(vm_disks) > 1:
                for disk in range(len(vm_disks)):
                    generic_disk_text = ":0," + vm_disks[disk]["disk_type"] + ","
                    disk_image = vm_disks[disk]["disk_image"]
                    if disk == 0:
                        disk_final = " -s " + str(bhyve_pci) + generic_disk_text + CoreChecks(vm_name=vm_name, disk_image_name=disk_image).disk_location()
                    else:
                        bhyve_pci = bhyve_pci + 1
                        disk_final = disk_final + " -s " + str(bhyve_pci) + generic_disk_text + CoreChecks(vm_name=vm_name, disk_image_name=disk_image).disk_location()
            else:
                generic_disk_text = ":0," + vm_disks[0]["disk_type"] + ","
                disk_image = vm_disks[0]["disk_image"]
                disk_final = " -s " + str(bhyve_pci) + generic_disk_text + CoreChecks(vm_name=vm_name, disk_image_name=disk_image).disk_location()

            command3 = disk_final


            os_type = CoreChecks(vm_name).vm_os_type()
            vm_cpus = CoreChecks(vm_name).vm_cpus()
            command5 = " -c sockets=" + vm_cpus["cpu_sockets"] + ",cores=" + vm_cpus["cpu_cores"] + " -m " + vm_cpus["memory"]

            bhyve_pci = bhyve_pci + 1
            command6 = " -s " + str(bhyve_pci) + ":" + str(bhyve_pci_2) + ",fbuf,tcp=0.0.0.0:" + vm_cpus["vnc_port"] + ",w=1280,h=1024,password=" + vm_cpus["vnc_password"]
            
            bhyve_pci = bhyve_pci + 1
            if vm_cpus["loader"] == "bios":
                command7 = " -s " + str(bhyve_pci) + ":" + str(bhyve_pci_2) + ",xhci,tablet -l com1,/dev/nmdm-" + vm_name + "-1A -l bootrom,/usr/local/share/uefi-firmware/BHYVE_UEFI_CSM.fd -u " + vm_name
                # command = command1 + command2 + command3 + command4 + command5 + command6 + command7
                command = command1 + command2 + command3 + command5 + command6 + command7
            elif vm_cpus["loader"] == "uefi":
                command7 = " -s " + str(bhyve_pci) + ",xhci,tablet -l com1,/dev/nmdm-" + vm_name + "-1A -l bootrom,/usr/local/share/uefi-firmware/BHYVE_UEFI.fd -u " + vm_name
                # command = command1 + command2 + command3 + command4 + command5 + command6 + command7
                command = command1 + command2 + command3 + command5 + command6 + command7
            else:
                print("Loader is not supported!")

            vm_folder = CoreChecks(vm_name).vm_folder()
            # command = "nohup /root/bin/startvm " + '"' + command + '"' + " " + vm_name + " > " + vm_folder + "vm.log 2>&1 &"
            command = "nohup ./cli/shell_helpers/vm_start.sh " + '"' + command + '"' + " " + vm_name + " &> " + vm_folder + "/vm.log &"
            # print(command)
            subprocess.run(command, shell=True, stderr = subprocess.DEVNULL, stdout=subprocess.DEVNULL)

        else:
            print("Such VM '" + vm_name + "' doesn't exist!")

    @staticmethod
    def stop(vm_name:str):
        """
        Gracefully stop the VM
        """
        if vm_name not in VmList().plainList:
            sys.exit("VM doesn't exist on this system.")
        elif CoreChecks(vm_name).vm_is_live():
            print("Gracefully stopping the VM: " + vm_name)

            command = "ps axf | grep -v grep | grep " + vm_name + " | grep bhyve: | awk '{ print $1 }'"
            shell_command = subprocess.check_output(command, shell=True)
            running_vm_pid = shell_command.decode("utf-8").split()[0]
            command = "kill -SIGTERM " + running_vm_pid
            subprocess.run(command, shell=True)

            command = "ifconfig | grep " + vm_name + " | awk '{ print $2 }'"
            shell_command = subprocess.check_output(command, shell=True)
            running_tap_adaptor = shell_command.decode("utf-8").split()[0]
            tap_interface_list = shell_command.decode("utf-8").split()

            running_tap_adaptor_status = "active"
            while running_tap_adaptor_status == "active":
                command = "ifconfig " + running_tap_adaptor + " | grep status | sed s/.status:.//"
                shell_command = subprocess.check_output(command, shell=True)
                running_tap_adaptor_status = shell_command.decode("utf-8").split("\n")[0]
                time.sleep(2)
            
            command = "bhyvectl --destroy --vm=" + vm_name
            subprocess.run(command, shell=True)
            
            for tap in tap_interface_list:
                command = "ifconfig " + tap + " destroy"
                subprocess.run(command, shell=True)
            
            print("The VM is fully stopped now: " + vm_name)
        else:
            print("VM is already stopped: " + vm_name)


""" Section below is responsible for the CLI input/output """
app = typer.Typer(context_settings=dict(max_content_width=800))
# app.add_typer(vmdeploy.app, name="deploy", help="Manage users in the app.")
# app.add_typer(vmlist.app, name="list")


@app.command()
def list(json:bool = typer.Option(False, help="Output json instead of a table")):
    """
    List the VMs using table or JSON output
    """
    if json:
        print(VmList().json_output())
    else:
        print(VmList().table_output())


@app.command()
def info(vm_name:str = typer.Argument(..., help="Print VM config file to the screen")):
    """
    Show VM info in the form of JSON output
    """
    vm_info_dict = VmConfigs(vm_name).vm_config_read()
    vm_info_json = json.dumps(vm_info_dict, indent=2)
    print(vm_info_json)


@app.command()
def edit(vm_name:str = typer.Argument(..., help="Edit VM config file with nano")):
    """
    Manually edit the VM config file (with 'nano')
    """
    VmConfigs(vm_name).vm_config_manual_edit()


@app.command()
def diskexpand(vm_name:str = typer.Argument(..., help="VM name"),
        size:int = typer.Option(10, help="Number or Gigabytes to add"),
        disk:str = typer.Option("disk0.img", help="Disk image file name"),
    ):
    """
    Make VM disks larger. Example: hoster vm diskexpand test_vm_1 --disk disk1.img --size 100
    """
    if vm_name in VmList().plainList:
        # DEBUG
        # print("All good. VM exists.")
        if CoreChecks(vm_name=vm_name, disk_image_name=disk).disk_exists():
            # DEBUG
            # print("All good. Disk exists.")
            disk_location = CoreChecks(vm_name=vm_name, disk_image_name=disk).disk_location()
            shell_command = "truncate -s +" + str(size) + "G " + disk_location
            subprocess.run(shell_command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("Disk was enlarged by " + str(size) + "G. Reboot or start the VM now to apply new settings.")
        else:
            sys.exit("Sorry, could not find the disk: " + disk)
    else:
        sys.exit("Sorry, could not find the VM with such name: " + vm_name)


@app.command()
def rename(vm_name:str = typer.Argument("Default", help="VM Name")):
    """
    Rename the VM
    """
    print("This feature is not available. To rename your VM use cireset, like so: 'hoster vm cireset old_vm_name --new-name new_vm_name'.")


@app.command()
def console(vm_name:str = typer.Argument(..., help="VM Name")):
    """
    Connect to VM's console
    """
    if vm_name not in VmList().plainList:
        sys.exit("VM doesn't exist on this system.")
    elif CoreChecks(vm_name).vm_is_live():
        command = "tmux ls | grep -c " + vm_name + " || true"
        shell_command = subprocess.check_output(command, shell=True)
        tmux_sessions = shell_command.decode("utf-8").split()[0]
        if tmux_sessions != "no server running on /tmp/tmux-0/default":
            if int(tmux_sessions) > 0:
                command = 'tmux a -t ' + '"' + vm_name + '"'
                shell_command = subprocess.check_output(command, shell=True)
            else:
                command = 'tmux new-session -s ' + vm_name + ' "cu -l /dev/nmdm-' + vm_name + '-1B"'
                subprocess.run(command, shell=True)
    else:
        sys.exit("VM is not running. Start the VM first to connect to it's console.")


@app.command()
def destroy(vm_name:str = typer.Argument(..., help="VM Name"),
    force:bool = typer.Option(False, help="Kill and destroy the VM, even if it's running"),
    ):
    """
    Completely remove the VM from this system!
    """
    Operation.destroy(vm_name=vm_name)

@app.command()
def destroy_all(force:bool = typer.Option(False, help="Kill and destroy all VMs, even if they are running")):
    """
    Completely remove all VMs from this system!
    """
    vm_list = VmList().plainList
    for _vm in vm_list:
        Operation.destroy(vm_name=_vm, force=force)


@app.command()
def snapshot(vm_name:str = typer.Argument(..., help="VM Name"),
    stype:str = typer.Option("custom", help="Snapshot type: daily, weekly, etc"),
    keep:int = typer.Option(3, help="How many snapshots to keep")
    ):
    """
    Snapshot the VM (RAM snapshots are not supported). Snapshot will be taken at the storage level: ZFS or GlusterFS.
    Example: hoster vm snapshot test-vm-1 --type weekly --keep 5
    """
    Operation.snapshot(vm_name=vm_name, stype=stype, keep=keep)

@app.command()
def snapshot_all(stype:str = typer.Option("custom", help="Snapshot type: daily, weekly, etc"),
    keep:int = typer.Option(3, help="How many snapshots to keep")
    ):
    """
    Snapshot all VMs
    """
    vm_list = VmList().plainList
    for _vm in vm_list:
        Operation.snapshot(vm_name=_vm, keep=keep, stype=stype)


@app.command()
def kill(vm_name:str = typer.Argument(..., help="VM Name")):
    """
    Kill the VM immediately!
    """
    Operation.kill(vm_name=vm_name)

@app.command()
def kill_all():
    """
    Kill all VMs on this system!
    """
    vm_list = VmList().plainList
    for _vm in vm_list:
        Operation.kill(vm_name=_vm)


@app.command()
def start(vm_name:str = typer.Argument(..., help="VM name"),
    ):
    """
    Power on the VM
    """
    Operation.start(vm_name=vm_name)

@app.command()
def start_all(wait:int = typer.Option(5, help="Seconds to wait before starting next VM on the list")
    ):
    """
    Power on all production VMs
    """
    vm_list = VmList().plainList
    for _vm in vm_list:
        if not CoreChecks(vm_name=_vm).vm_is_live():
            _vm_live_status = CoreChecks(vm_name=_vm).vm_cpus()["live_status"]
            if _vm_live_status == "production":
                Operation.start(vm_name=_vm)
                time.sleep(wait)
        else:
            print("VM is already live: " + _vm)

@app.command()
def stop(vm_name:str = typer.Argument(..., help="VM name"),
        
        ):
        """
        Gracefully stop the VM
        """
        Operation.stop(vm_name=vm_name)

@app.command()
def stop_all(wait:int = typer.Option(5, help="Seconds to wait before stopping next VM on the list")
    ):
    """
    Gracefully stop all VMs running on this system
    """
    vm_list = VmList().plainList
    for _vm in vm_list:
        if CoreChecks(vm_name=_vm).vm_is_live():
            Operation.stop(vm_name=_vm)
            time.sleep(wait)
        else:
            print("VM is already stopped: " + _vm)

@app.command()
def deploy(vm_name:str = typer.Argument("test-vm", help="New VM name"),
        os_type:str = typer.Option("debian11", help="OS Type, for example: debian11 or ubuntu2004"),
        ip_address:str = typer.Option("10.0.0.0", help="Specify the IP address or leave at default to generate a random address")
        ):
        """
        New VM deployment
        """
        printout = VmDeploy(vm_name=vm_name, ip_address=ip_address, os_type=os_type).output_dict()
        print(printout)


""" If this file is executed from the command line, activate Typer """
if __name__ == "__main__":
    app()
