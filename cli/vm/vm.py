#!bin/python

# Native Python functions
# from ipaddress import ip_address
from ipaddress import ip_address
from httplib2 import ProxiesUnavailableError
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
from generate_mac import generate_mac
from jinja2 import Template

# Own functions
from cli.host import dataset
from cli.vm import internal_classes as IC


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

    def vm_dataset(self):
        for ds in self.zfs_datasets["datasets"]:
            if exists("/" + ds["zfs_path"] + "/" + self.vm_name):
                vm_dataset = ds["zfs_path"]
                return vm_dataset
            elif ds == len(self.zfs_datasets["datasets"]) and not exists(ds["mount_path"]+self.vm_name):
                sys.exit("VM doesn't exist!")

    def vm_ip_address(self):
        """
        Get VM's IP address
        """
        vm_info_dict = self.vm_config
        vm_ip_address = vm_info_dict["networks"][0]["ip_address"]
        return vm_ip_address

    def vm_vnc_port(self):
        """
        Get VM's VNC port
        """
        vm_info_dict = self.vm_config
        vm_ip_address = vm_info_dict["vnc_port"]
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

    def existing_ip_addresses(self):
        for _vm in VmList().plainList:
            ip_address = CoreChecks(vm_name=_vm).vm_ip_address()
            self.existing_ip_addresses.append(ip_address)


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
                sys.exit(" 🚦 ERROR: Please create 2 zfs datasets: " + zfs_datasets_list)
        
        if not vmColumnNames:
            print("\n 🚦 ERROR: There are no VMs on this system. To deploy one, use:\n hoster vm deploy\n")
            sys.exit(0)

        self.plainList = vmColumnNames.copy()
        self.vmColumnNames = natsorted(vmColumnNames)

    def table_output(self):
        vmColumnNames = self.vmColumnNames

        if len(vmColumnNames) < 1:
            print("\n 🚦 ERROR: There are no VMs on this system. To deploy one, use:\n hoster vm deploy\n")
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


        vmTableHeader = [ ["Name", "State", "CPUs", "RAM", "Main IP", "VNC Port", "VNC Password", "OS Disk", "OS Comment", "Uptime", "Description", ] ]

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
    def __init__(self, vm_name:str = "test-vm", ip_address:str = "10.0.0.0", os_type:str = "ubuntu2004", vnc_port:int = 5900, dataset_id:int = 0):
        #_ Load networks config _#
        with open("./configs/networks.json", "r") as file:
            networks_file = file.read()
        networks_dict = json.loads(networks_file)
        self.networks = networks_dict["networks"][0]

        #_ Load host config _#
        with open("./configs/host.json", "r") as file:
            host_file = file.read()
        host_dict = json.loads(host_file)
        self.host_dict = host_dict

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
            sys.exit(" 🚦 ERROR: Sorry this OS is not supported. Here is the list of supported OSes:\n" + os_type_list)
        
        self.vnc_port = vnc_port

        if vm_name == "test-vm":
            self.live_status = "testing"
        else:
            self.live_status = "production"

        self.dataset_id = dataset_id

    @staticmethod
    def vm_vnc_port_generator(vnc_port):
        existing_vnc_ports = []
        allowed_vnc_ports = []
        for _port in range(5900, 6100):
            allowed_vnc_ports.append(_port)
        
        for _vm in VmList().plainList:
            _vm_vnc_port = CoreChecks(vm_name=_vm).vm_vnc_port()
            _vm_vnc_port = int(_vm_vnc_port)
            existing_vnc_ports.append(_vm_vnc_port)
        
        if vnc_port not in allowed_vnc_ports:
            sys.exit("You can't assign this port to your VM! Allowed range: 5900-6100")
        
        while vnc_port in existing_vnc_ports:
            if vnc_port >= 5900 and vnc_port <= 6100:
                vnc_port = vnc_port + 1
            else:
                sys.exit("We ran out of available VNC ports!")
        
        return vnc_port


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
    def ip_address_generator(ip_address:str, networks, existing_ip_addresses, vm_name:str):
        if ip_address in existing_ip_addresses and vm_name != "test-vm":
            print("VM with such IP exists: " + vm_name + "/" + ip_address)
        
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
    def random_password_generator(capitals:bool = False, numbers:bool = False, lenght:int = 8, specials:bool = False):
        letters_var = "asdfghjklqwertyuiopzxcvbnm"
        capitals_var = "ASDFGHJKLZXCVBNMQWERTYUIOP"
        numbers_var = "0987654321"
        specials_var = ".,-_!^*?><)(%[]=+$#"
        
        valid_chars_list = []
        for item in letters_var:
            valid_chars_list.append(item)
        if capitals:
            for c_item in capitals_var:
                valid_chars_list.append(c_item)
        if numbers:
            for n_item in numbers_var:
                valid_chars_list.append(n_item)
        if specials:
            for s_item in specials_var:
                valid_chars_list.append(s_item)
        
        password = ""
        for _i in range(0, lenght):
            password = password + random.choice(valid_chars_list)
        
        return password
    
    
    @staticmethod
    def mac_address_generator(prefix:str = "58:9C:FC"):
        mac_addess = generate_mac.vid_provided(prefix)
        mac_addess = mac_addess.lower()
        return mac_addess
    
    
    def dns_registry(self):
        dns_registry = {}
        vms_and_ips = []
        
        dns_registry["host_dns_acls"] = self.host_dict["host_dns_acls"]
        dns_registry["vms_and_ips"] = vms_and_ips
        
        for vm_index, vm_name in enumerate(self.existing_vms):
            vm_and_ip_dict = {}
            ip_address = CoreChecks(self.existing_vms[vm_index]).vm_ip_address()
            vm_and_ip_dict["vm_name"] = vm_name
            vm_and_ip_dict["ip_address"] = ip_address
            vms_and_ips.append(vm_and_ip_dict)
        
        # Read Unbound template
        with open("./templates/unbound.conf", "r") as file:
            template = file.read()
        # Render Unbound template
        template = Template(template)
        template = template.render(dns_registry=dns_registry)
        # Write Unbould template
        with open("/var/unbound/unbound.conf", "w") as file:
            file.write(template)
        # Reload the Unbound service
        command = "service local_unbound reload"
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)
        
        return


    def deploy(self):
        output_dict = {}
        output_dict["vm_name"] = VmDeploy.vm_name_generator(vm_name=self.vm_name, existing_vms=self.existing_vms)
        output_dict["ip_address"] = VmDeploy.ip_address_generator(ip_address=self.ip_address, networks=self.networks, existing_ip_addresses=self.existing_ip_addresses, vm_name=self.vm_name)
        output_dict["os_type"] = self.os_type
        output_dict["root_password"] = VmDeploy.random_password_generator(lenght=41, capitals=True, numbers=True)
        output_dict["user_password"] = VmDeploy.random_password_generator(lenght=41, capitals=True, numbers=True)
        output_dict["vnc_port"] = VmDeploy.vm_vnc_port_generator(vnc_port=self.vnc_port)
        output_dict["vnc_password"] = VmDeploy.random_password_generator(lenght=20, capitals=True, numbers=True)
        output_dict["mac_address"] = VmDeploy.mac_address_generator()
        network0 = self.networks
        network_bridge_name = network0["bridge_name"]
        network_bridge_address = network0["bridge_address"]
        output_dict["network_bridge_name"] = network_bridge_name
        output_dict["network_bridge_address"] = network_bridge_address
        output_dict["live_status"] = self.live_status

        if self.os_type == "ubuntu2004":
            output_dict["os_comment"] = "Ubuntu 20.04"
        elif self.os_type == "debian11":
            output_dict["os_comment"] = "Debian 11"
        else:
            output_dict["os_comment"] = "Unknown OS"

        # Cloud Init Section
        host_dict = self.host_dict
        vm_ssh_keys = []
        for _key in host_dict["host_ssh_keys"]:
            _ssh_key = _key["key_value"]
            vm_ssh_keys.append(_ssh_key)
        output_dict["random_instanse_id"] = VmDeploy.random_password_generator(lenght=5)
        output_dict["vm_ssh_keys"] = vm_ssh_keys

        dataset_id = self.dataset_id
        working_dataset = dataset.DatasetList().datasets["datasets"][dataset_id]["zfs_path"]
        working_dataset_path = dataset.DatasetList().datasets["datasets"][dataset_id]["mount_path"]
        
        # Clone a template using ZFS clone
        template_ds = working_dataset + "/template-" + output_dict["os_type"]
        template_folder = working_dataset_path + "template-" + output_dict["os_type"]
        if exists(template_folder):
            snapshot_name = "@deployment_" + output_dict["vm_name"] + "_" + VmDeploy.random_password_generator(lenght=7, numbers=True)
            command = "zfs snapshot " + template_ds + snapshot_name
            # print(command)
            subprocess.run(command, shell=True)
            
            command = "zfs clone " + template_ds + snapshot_name + " " + working_dataset + "/" + output_dict["vm_name"]
            # print(command)
            subprocess.run(command, shell=True)
        else:
            sys.exit(" ⛔ FATAL! Template specified doesn't exist: " + template_folder)

        new_vm_folder = working_dataset_path + output_dict["vm_name"] + "/"
        if exists(new_vm_folder):
            # Read VM template
            with open("./templates/vm_config_template.json", "r") as file:
                template = file.read()
            # Render VM template
            template = Template(template)
            template = template.render(output_dict=output_dict)
            # Write VM template
            with open(new_vm_folder + "vm_config.json", "w") as file:
                file.write(template)

            IC.CloudInit(vm_name=output_dict["vm_name"], vm_folder=new_vm_folder, vm_ssh_keys=vm_ssh_keys,
                        os_type=output_dict["os_type"], ip_address=output_dict["ip_address"],
                        network_bridge_address=output_dict["network_bridge_address"], root_password=output_dict["root_password"],
                        user_password=output_dict["user_password"], mac_address=output_dict["mac_address"]).deploy()

        else:
            sys.exit(" ⛔ FATAL! Template specified doesn't exist: " + template_folder)
        
        return {"status": "success", "vm_name": output_dict["vm_name"]}


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
            print(" 🔷 DEBUG: New snapshot was taken: " + command)
        else:
            sys.exit(" 🚫 CRITICAL: Can't snapshot! VM " + vm_name + " doesn't exist on this system!")
            
        # Remove old snapshots
        if snapshot_type != "custom":
            # Get the snapshot list
            command = "zfs list -r -t snapshot " + CoreChecks(vm_name).vm_location() + " | tail +2 | awk '{ print $1 }' | grep " + snapshot_type
            shell_command = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
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
                    print(" 🔷 DEBUG: Old snapshot was removed: " + command)
            else:
                print(" 🔷 DEBUG: VM " + vm_name + " doesn't have any '" + snapshot_type + "' snapshots to delete")

    @staticmethod
    def destroy(vm_name:str, force:bool=False):
        """
        Function responsible for completely removing VMs from the system
        """
        if force == True and CoreChecks(vm_name).vm_is_live():
            kill(vm_name=vm_name)
            time.sleep(3)

        if vm_name not in VmList().plainList:
            print(" 🔶 INFO: VM doesn't exist on this system.")
        elif CoreChecks(vm_name).vm_is_live():
            print(" 🔴 WARNING: VM is still running, you'll have to stop (or kill) it first: " + vm_name)
        else:
            command = "zfs destroy -rR " + CoreChecks(vm_name).vm_location()
            # ADD DEBUG/FAKE RUN
            shell_command = subprocess.check_output(command, shell=True)
            print(" 🔶 INFO: The VM was destroyed: " + command)

    @staticmethod
    def kill(vm_name:str):
        """
        Function that forcefully kills the VM
        """
        if vm_name not in VmList().plainList:
            sys.exit("VM doesn't exist on this system.")
        elif CoreChecks(vm_name).vm_is_live():
            # This code block is a duplicate. Another one exists in stop section.
            command = "ps axf | grep -v grep | grep 'nmdm-" + vm_name + "' | awk '{ print $1 }'"
            shell_command = subprocess.check_output(command, shell=True)
            console_list = shell_command.decode("utf-8").split()
            for _console in console_list:
                if _console:
                    command = "kill -SIGKILL " + _console
                    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Find and kill the VM process
            command = "ps axf | grep -v grep | grep " + vm_name + " | grep bhyve: | awk '{ print $1 }'"
            shell_command = subprocess.check_output(command, shell=True)
            try:
                running_vm_pid = shell_command.decode("utf-8").split()[0]
                command = "kill -SIGKILL " + running_vm_pid
                subprocess.run(command, shell=True)
            except:
                print(" 🔶 INFO: Could not find the process for the VM: " + vm_name)

            # This block is a duplicate. Creating a function would be a good idea for the future!
            command = "ifconfig | grep " + vm_name + " | awk '{ print $2 }'"
            shell_command = subprocess.check_output(command, shell=True)
            tap_interface_list = shell_command.decode("utf-8").split()

            command = "bhyvectl --destroy --vm=" + vm_name
            subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            time.sleep(1)

            if tap_interface_list:
                for tap in tap_interface_list:
                    if tap:
                        command = "ifconfig " + tap + " destroy"
                        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(" 🔶 INFO: Killed the VM: " + vm_name)
        else:
            # This block is a duplicate. Creating a function would be a good idea for the future!
            command = "ifconfig | grep " + vm_name + " | awk '{ print $2 }'"
            shell_command = subprocess.check_output(command, shell=True)
            tap_interface_list = shell_command.decode("utf-8").split()
            if tap_interface_list:
                for tap in tap_interface_list:
                    if tap:
                        command = "ifconfig " + tap + " destroy"
                        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(" 🔶 INFO: VM is already dead: " + vm_name + "!")

    @staticmethod
    def start(vm_name:str):
        if CoreChecks(vm_name).vm_is_live():
            print(" 🔶 INFO: VM is already live: " + vm_name)
        elif vm_name in VmList().plainList:
            print(" 🔶 INFO: Starting the VM: " + vm_name)
        
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
                print(" 🚦 ERROR: Loader is not supported!")

            vm_folder = CoreChecks(vm_name).vm_folder()
            command = "nohup ./cli/shell_helpers/vm_start.sh " + '"' + command + '"' + " " + vm_name + " > " + vm_folder + "/vm.log 2>&1 &"
            # print(command)
            subprocess.run(command, shell=True)

        else:
            print(" 🚦 ERROR: Such VM '" + vm_name + "' doesn't exist!")

    @staticmethod
    def stop(vm_name:str):
        """
        Gracefully stop the VM
        """
        if vm_name not in VmList().plainList:
            print(" 🚦 ERROR: VM doesn't exist on this system.")
        elif CoreChecks(vm_name).vm_is_live():
            print(" 🔶 INFO: Gracefully stopping the VM: " + vm_name)

            # This code block is a duplicate. Another one exists in kill section.
            command = "ps axf | grep -v grep | grep 'nmdm-" + vm_name + "' | awk '{ print $1 }'"
            shell_command = subprocess.check_output(command, shell=True)
            console_list = shell_command.decode("utf-8").split()
            for _console in console_list:
                if _console:
                    command = "kill -SIGKILL " + _console
                    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            

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
            subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            for tap in tap_interface_list:
                command = "ifconfig " + tap + " destroy"
                subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print(" 🔶 INFO: The VM is fully stopped now: " + vm_name)
        else:
            print(" 🔶 INFO: VM is already stopped: " + vm_name)


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
            sys.exit(" 🚦 ERROR: Sorry, could not find the disk: " + disk)
    else:
        sys.exit(" 🚦 ERROR: Sorry, could not find the VM with such name: " + vm_name)


@app.command()
def rename(vm_name:str = typer.Argument(..., help="VM Name"),
    new_name:str = typer.Option(..., help="New VM Name"),
    ):
    """
    Rename the VM
    """
    if vm_name not in VmList().plainList:
        sys.exit(" 🚦 ERROR: This VM doesn't exist: " + vm_name)
    elif CoreChecks(vm_name=vm_name).vm_is_live():
        sys.exit(" 🚦 ERROR: VM is live! Please turn it off first: hoster vm stop " + vm_name)
    
    vm_folder = CoreChecks(vm_name=vm_name).vm_folder()
    vm_dataset = CoreChecks(vm_name=vm_name).vm_dataset()
    old_zfs_ds = vm_dataset + "/" + vm_name
    new_zfs_ds = vm_dataset + "/" + new_name

    vm_ssh_keys = []
    os_type = ""
    ip_address = ""
    network_bridge_address = ""
    root_password = ""
    user_password = ""
    mac_address = ""

    cloud_init = IC.CloudInit(vm_name=vm_name, vm_folder=vm_folder, vm_ssh_keys=vm_ssh_keys, os_type=os_type, ip_address=ip_address,
    network_bridge_address=network_bridge_address, root_password=root_password, user_password=user_password, mac_address=mac_address,
    new_vm_name=new_name, old_zfs_ds=old_zfs_ds, new_zfs_ds=new_zfs_ds)
    
    cloud_init.rename()
    
    # Reload DNS
    VmDeploy().dns_registry()
    

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
    
    # Reload DNS 
    VmDeploy().dns_registry()

@app.command()
def destroy_all(force:bool = typer.Option(False, help="Kill and destroy all VMs, even if they are running")):
    """
    Completely remove all VMs from this system!
    """
    vm_list = VmList().plainList
    for _vm in vm_list:
        Operation.destroy(vm_name=_vm, force=force)
    
    # Let user know that he can remove deployment snapshots
    print()
    print(" 🔶 INFO: Execute this command to find and manually remove old deployment snapshots:")
    print("          zfs list -t all | grep \"@deployment_\" | awk '{ print $1 }'")
    print(" 🔶 INFO: Or execute this command to find and automatically remove old test deployment snapshots:")
    print("          for ITEM in $(zfs list -t all | grep \"@deployment_\" | awk '{ print $1 }' | grep test-vm-); do zfs destroy $ITEM; done")
    print()
    
    # Reload DNS 
    VmDeploy().dns_registry()


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
        _vm_live_status = CoreChecks(vm_name=_vm).vm_cpus()["live_status"]
        if _vm_live_status == "production":
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
        os_type:str = typer.Option("ubuntu2004", help="OS Type, for example: debian11 or ubuntu2004"),
        # ip_address:str = typer.Option("10.0.0.0", help="Specify the IP address or leave at default to generate a random address"),
        ds_id:int = typer.Option(0, help="Dataset ID to which this VM will be deployed"),
        ):
        """
        New VM deployment
        """
        deployment_output = VmDeploy(vm_name=vm_name, os_type=os_type, dataset_id=ds_id).deploy()
        
        # Reload DNS 
        VmDeploy().dns_registry()

        # Let user know, that everything went well
        print (" 🟢 INFO: VM was deployed successfully: " + deployment_output["vm_name"])

@app.command()
def cireset(vm_name:str = typer.Argument(..., help="VM name"),
        # os_type:str = typer.Option(..., help="OS type"),
        # os_comment:str = typer.Option(..., help="OS Comment")
        ):
        """
        Reset the VM settings, including passwords, network settings, user keys, etc.
        """
        if vm_name not in VmList().plainList:
            sys.exit(" 🚦 ERROR: This VM doesn't exist: " + vm_name)
        elif CoreChecks(vm_name=vm_name).vm_is_live():
            sys.exit(" 🚦 ERROR: VM is live! Please turn it off first: hoster vm stop " + vm_name)

        vm_config_dict = VmConfigs(vm_name).vm_config_read()
        print(vm_config_dict)
        print()
        vm_folder = CoreChecks(vm_name=vm_name).vm_folder()
        print(vm_folder)
        print()
        #_ Load host config _#
        with open("./configs/host.json", "r") as file:
            host_file = file.read()
        host_dict = json.loads(host_file)
        print(host_dict)
        print()

        # host_dict = VmDeploy().host_dict
        # vm_ssh_keys = []
        # for _key in host_dict["host_ssh_keys"]:
        #     _ssh_key = _key["key_value"]
        #     vm_ssh_keys.append(_ssh_key)

        # networks = VmDeploy().networks
        # existing_ip_addresses = VmDeploy().existing_ip_addresses
        # ip_address = VmDeploy().ip_address_generator(ip_address="10.0.0.0", networks=networks, existing_ip_addresses=existing_ip_addresses, vm_name=vm_name)

        # network_bridge_address = networks["bridge_address"]
        # root_password = IC.random_password_generator(capitals=True, numbers=True, lenght=53)
        # user_password = IC.random_password_generator(capitals=True, numbers=True, lenght=53)
        # mac_address = IC.mac_address_generator()

        # old_zfs_ds = ""
        # new_zfs_ds = ""

        # cloud_init = IC.CloudInit(vm_name=vm_name, vm_folder=vm_folder, vm_ssh_keys=vm_ssh_keys, os_type=os_type, ip_address=ip_address,
        # network_bridge_address=network_bridge_address, root_password=root_password, user_password=user_password, mac_address=mac_address,
        # new_vm_name=vm_name, old_zfs_ds=old_zfs_ds, new_zfs_ds=new_zfs_ds, os_comment=os_comment)

        # cloud_init.reset()

        # Reload DNS 
        VmDeploy().dns_registry()

        # Let user know, that everything went well
        print (" 🟢 INFO: VM was reset successfully: " + vm_name)


""" If this file is executed from the command line, activate Typer """
if __name__ == "__main__":
    app()
