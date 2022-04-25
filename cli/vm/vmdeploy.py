#!bin/python3

import os
import sys
import subprocess
import wget
from os.path import exists
from generate_mac import generate_mac
import random
from jinja2 import Template
from os import listdir
import re
import json

from cli.vm.vm import CoreChecks
from cli.vm.vm import VmConfigs

class Deploy:
    def __init__(self):
        #_ Load networks config _#
        with open("./configs/networks.json", "r") as file:
            networks_file = file.read()
        networks_file = json.loads(networks_file)
        self.networks = networks_file

        #_ Load host config _#
        with open("./configs/host.json", "r") as file:
            host_file = file.read()
        host_file = json.loads(host_file)
        self.host = host_file


class Generators:
    def __init__(self):
        print("Generators")


class TemplateFiles:
    def __init__(self):
        print("TemplateFiles")


class GetVmInfo:
    def __init__(self):
        self.host_config = {}
        self.vm_config = {}
    
    def ip_address(self):
        print("Test")