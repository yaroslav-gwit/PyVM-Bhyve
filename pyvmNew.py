#!/usr/bin/env python3
import typer
import sys
import os
import subprocess

# Own libraries
# from extra import vm_list
# from extra import vm_operations
# from extra import vm_mass_operations
# from extra import vm_deploy
# from extra import vm_backups

""" Section below is responsible for the CLI input/output """
app = typer.Typer(context_settings=dict(max_content_width=800))


@app.command()
def vmlist(json: bool = typer.Option(False, help="Output json instead of a table")):
    """
    Example: hoster vmlist
    """

    print("Hello from few pyvm!")


@app.command()
def vmdeploy(quick: bool = typer.Option(True, help="Clone existing template ZFS dataset instead of copying over VM image")):
    """
    Example: hoster vmdeploy
    """

    print("Hello from few pyvm!")



""" If this file is executed from the command line, activate Typer """
if __name__ == "__main__":
    app()