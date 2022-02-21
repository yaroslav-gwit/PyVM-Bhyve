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


class HostInfoTable:
    def __init__(self):
        print("This will be a VmListTable class")

    def tableOutput():
        ### HOST_TABLE ###
        HostName = os.uname()[1]
        # RAM
        TotalRam = round(psutil.virtual_memory().total / 1024 / 1024 / 1024)
        FreeRam = round(psutil.virtual_memory().used / 1024 / 1024 / 1024)
        FinalRam = str(FreeRam) + "G/" + str(TotalRam) + "G"
        # Uptime
        Uptime = time_date_converter.function(uptime._uptime_posix())
        # Number of running VMs
        if exists("/dev/vmm/"):
            command = "ls /dev/vmm/"
            shell_command = subprocess.check_output(command, shell=True)
            numberOfRunningVMs = len(shell_command.decode("utf-8").split())
        else:
            numberOfRunningVMs = "0"
        # ARC size
        command = "top | grep -i arc | awk '{ print $2 }'"
        shell_command = subprocess.check_output(command, shell=True)
        arcSize = shell_command.decode("utf-8").split()[0]
        # Zpool status
        command = "zpool status | grep zroot | grep -v pool | awk '{ print $2 }'"
        shell_command = subprocess.check_output(command, shell=True)
        zfsStatus = shell_command.decode("utf-8").split()[0]
        # Datasets free space
        command = "zfs list | grep -G 'zroot/ROOT' | head -1 | awk '{ print $3 }'"
        shell_command = subprocess.check_output(command, shell=True)
        zfsFree = shell_command.decode("utf-8").split()[0]

        hostTable = [   ["HostName", "RAM", "Uptime", "RunningVMs", "ZfsArcSize", "ZfsStatus", "ZfsFree", ],
                        [HostName, FinalRam, Uptime, numberOfRunningVMs, arcSize, zfsStatus, zfsFree, ]
                    ]
        return tabulate(hostTable, headers="firstrow", tablefmt="fancy_grid", )
        ### EOF_HOST_TABLE ###



class HostInfoJson:
    def __init__(self):
        print("This will be VmListJson class")
    
    def jsonOutput():
        print("This would be a JSON output")


""" Section below is responsible for the CLI input/output """
app = typer.Typer(context_settings=dict(max_content_width=800))

@app.command()
def info(json: bool = typer.Option(False, help="Output json instead of a table")):
    """
    Example: hoster host info
    """
    if json:
        HostInfoJson.jsonOutput()
    else:
        HostInfoTable.tableOutput()

""" If this file is executed from the command line, activate Typer """
if __name__ == "__main__":
    app()