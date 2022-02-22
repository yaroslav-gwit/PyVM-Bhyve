#!bin/python

# Native Python functions
import sys
import os
import subprocess
import copy
import socket
import platform
import re
from os.path import exists
from os import listdir
import ast

# Installed packages/modules
import typer
import uptime
import psutil
from tabulate import tabulate
from natsort import natsorted

# Own libs
from cli import time_date_converter

with open("/root/bin/host.info", 'r') as file_object:
    host_info_raw = file_object.read()
host_info_dict = ast.literal_eval(host_info_raw)


class HostInfo:
    def __init__(self):
        # Hostname
        self.hostName = os.uname()[1]

        # RAM
        self.totalRam = round(psutil.virtual_memory().total / 1024 / 1024 / 1024)
        self.freeRam = round(psutil.virtual_memory().used / 1024 / 1024 / 1024)
        self.finalRam = str(FreeRam) + "G/" + str(TotalRam) + "G"

        # Uptime
        self.uptime = time_date_converter.function(uptime._uptime_posix())

        # Number of running VMs
        if exists("/dev/vmm/"):
            command = "ls /dev/vmm/"
            shell_command = subprocess.check_output(command, shell=True)
            self.numberOfRunningVMs = len(shell_command.decode("utf-8").split())
        else:
            self.numberOfRunningVMs = "0"

        # ARC size
        command = "top | grep -i arc | awk '{ print $2 }'"
        shell_command = subprocess.check_output(command, shell=True)
        self.arcSize = shell_command.decode("utf-8").split()[0]

        # Zpool status
        command = "zpool status | grep zroot | grep -v pool | awk '{ print $2 }'"
        shell_command = subprocess.check_output(command, shell=True)
        self.zfsStatus = shell_command.decode("utf-8").split()[0]

        # Datasets free space
        command = "zfs list | grep -G 'zroot/ROOT' | head -1 | awk '{ print $3 }'"
        shell_command = subprocess.check_output(command, shell=True)
        self.zfsFree = shell_command.decode("utf-8").split()[0]


    def tableOutput(self):
        hostTable = [   ["HostName", "RAM", "Uptime", "RunningVMs", "ZfsArcSize", "ZfsStatus", "ZfsFree", ],
                        [self.hostName, self.finalRam, self.uptime, self.numberOfRunningVMs, self.arcSize, self.zfsStatus, self.zfsFree, ]
                    ]
        # return tabulate(hostTable, headers="firstrow", tablefmt="fancy_grid", )
        print(tabulate(hostTable, headers="firstrow", tablefmt="fancy_grid", ))

    def jsonOutput(self):
        print("This would be a JSON output")



""" Section below is responsible for the CLI input/output """
app = typer.Typer(context_settings=dict(max_content_width=800))

@app.command()
def info(json: bool = typer.Option(False, help="Output json instead of a table")):
    """
    Example: hoster host info
    """
    if json:
        HostInfo().jsonOutput()
    else:
        HostInfo().tableOutput()

""" If this file is executed from the command line, activate Typer """
if __name__ == "__main__":
    app()