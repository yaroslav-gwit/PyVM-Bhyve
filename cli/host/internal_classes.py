#!/usr/bin/env python3
import json
import os
import subprocess
import sys

class LoadKernelModules:
    def __init__(self):
        """
        kldstat -m $MODULE
        kldstat -mq $MODULE

        kldload vmm
        kldload nmdm
        kldload if_bridge
        kldload if_tuntap
        kldload if_tap

        sysctl net.link.tap.up_on_open=1

        13.0-RELEASE-p11
        """
    
    def init(self):
        command = "kldload vmm"
        subprocess.run(command, shell=True)
        print("DEBUG: " + command)

        command = "kldload nmdm"
        subprocess.run(command, shell=True)
        print("DEBUG: " + command)

        command = "kldload if_bridge"
        subprocess.run(command, shell=True)
        print("DEBUG: " + command)

        command = "kldload if_tap"
        subprocess.run(command, shell=True)
        print("DEBUG: " + command)

        command = "sysctl net.link.tap.up_on_open=1"
        subprocess.run(command, shell=True)
        print("DEBUG: " + command)
