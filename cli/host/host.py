#!bin/python

# Native Python functions
import os
import subprocess
from os.path import exists
import json

# Installed packages/modules
import typer
import uptime
import psutil
from tabulate import tabulate

# Own libs
from cli import time_date_converter


class HostInfo:
    def __init__(self):
        # Hostname
        self.hostName = os.uname()[1]

        # RAM
        self.totalRam = round(psutil.virtual_memory().total / 1024 / 1024 / 1024)
        self.usedRam = round((psutil.virtual_memory().total-psutil.virtual_memory().available)/ 1024 / 1024 / 1024)
        self.freeRam = round(psutil.virtual_memory().available / 1024 / 1024 / 1024)
        self.finalRam = str(self.usedRam) + "G/" + str(self.totalRam) + "G"

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

        # Average Load %
        self.averageLoad = round(psutil.getloadavg()[-1] / psutil.cpu_count() * 100)

    
    def table_output(self):
        hostTable = [   ["HostName", "RAM", "Uptime", "RunningVMs", "ZfsArcSize", "ZfsStatus", "ZfsFree", "Average Load"],
                        [self.hostName, self.finalRam, self.uptime, self.numberOfRunningVMs, self.arcSize, self.zfsStatus, self.zfsFree, self.averageLoad]
                    ]
        return tabulate(hostTable, headers="firstrow", tablefmt="fancy_grid", )


    def json_output(self):
        jsonOutputDict = {}
        jsonOutputDict["hostname"] = self.hostName
        jsonOutputDict["total_ram"] = str(self.totalRam) + "G"
        jsonOutputDict["used_ram"] = str(self.usedRam) + "G"
        jsonOutputDict["free_ram"] = str(self.freeRam) + "G"
        jsonOutputDict["uptime"] = self.uptime
        jsonOutputDict["number_of_running_vms"] = self.numberOfRunningVMs
        jsonOutputDict["zfs_acr_size"] = self.arcSize
        jsonOutputDict["zfs_status"] = self.zfsStatus
        jsonOutputDict["zfs_free"] = self.zfsFree
        jsonOutputDict["average_load"] = self.averageLoad

        return json.dumps(jsonOutputDict, indent=2)


""" Section below is responsible for the CLI input/output """
app = typer.Typer(context_settings=dict(max_content_width=800))


@app.command()
def info(json: bool = typer.Option(False, help="Output json instead of a table")):
    """
    Example: hoster host info
    """
    if json:
        print(HostInfo().json_output())
    else:
        print(HostInfo().table_output())


""" If this file is executed from the command line, activate Typer """
if __name__ == "__main__":
    app()
