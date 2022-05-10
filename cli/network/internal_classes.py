import json
import os
import subprocess

class FileLocations:
    def __init__(self, network_config_location:str = "./configs/networks.json") -> None:
        self.network_config_location = network_config_location

        with open(self.network_config_location, "r") as file:
            network_config_location_dict = file.read()
        
        self.network_config_location_dict = json.loads(network_config_location_dict)


class NetworkInit:
    def __init__(self) -> None:
        self.network_config_location_dict = FileLocations().network_config_location_dict
        
    def init(self):
        for _network in self.network_config_location_dict["networks"]:
            _network_name = _network["bridge_name"]
            command = "ifconfig | grep -c vm-" + _network_name
            output = subprocess.check_output(command, shell=True).split()[0]
            if output != "0":
                print("Output is not 1!" + _network_name)

NetworkInit().init