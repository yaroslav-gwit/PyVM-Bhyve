#!/usr/bin/env python3
import typer
import sys
import os
import subprocess

# Own libraries
from extra import vm_list
from extra import vm_operations
from extra import vm_mass_operations
from extra import vm_deploy
from extra import vm_backups

""" Section below is responsible for the CLI input/output """
app = typer.Typer(context_settings=dict(max_content_width=800))

@app.command()
def vmlist(json: bool = typer.Option(False, help="Output json instead of a table")):
    """
    Example: hoster vmlist
    """

    print("Hello from few pyvm!")