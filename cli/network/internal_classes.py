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
            command = "ifconfig | grep -c vm-" + _network_name
            output = subprocess.check_output(command, shell=True)
            output = output.decode("utf-8").split()[0]
            if output != "1":
                return "Result is not 1!"
            elif output != "1":
                return "Result is 1 :)"
