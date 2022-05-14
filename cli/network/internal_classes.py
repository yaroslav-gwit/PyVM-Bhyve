#!/usr/bin/env python3
import json
import os
import subprocess
import sys

class FileLocations:
    def __init__(self, network_config_location:str = "./configs/networks.json"):
        # if os._exists(network_config_location):
        #     self.network_config_location = network_config_location
        # else:
        #     print("File was not found!")
        #     sys.exit(1)

        self.network_config_location = network_config_location
        
        with open(self.network_config_location, "r") as file:
            network_config_location_dict = file.read()
        
        self.network_config_location_dict = json.loads(network_config_location_dict)


class NetworkInit:
    def __init__(self):
        self.network_config_location_dict = FileLocations().network_config_location_dict
    
    def init(self):
        for _network in self.network_config_location_dict["networks"]:
            
            _network_name = _network["bridge_name"]
            
            command = "ifconfig | grep -c vm-" + _network_name + " || true"
            output = subprocess.check_output(command, shell=True)
            output = output.decode("utf-8").split()[0]
            
            if output != "1":
                command = "ifconfig bridge create name vm-" + _network_name
                subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)
                print(" 🔷 DEBUG: " + command)
                
                if _network["bridge_interface"] and _network["bridge_interface"] != "None":
                    command = "ifconfig vm-external addm " + _network["bridge_interface"]
                    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)
                    print(" 🔷 DEBUG: " + command)

                if _network["apply_bridge_address"] == True:
                    command = "ifconfig vm-" +  _network_name + " inet " + _network["bridge_address"] + "/" + str(_network["bridge_subnet"])
                    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)
                    print(" 🔷 DEBUG: " + command)
            
            elif output == "1":
                print(" 🔷 DEBUG: Network " + _network_name + " is already configured!")
            
            else:
                print(" 🚫 ERROR: Something unexpected happened!")
        