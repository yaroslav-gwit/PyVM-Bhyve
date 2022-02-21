import typer
from cli.vm import vmdeploy

# Core functions
from core.vm import vm_list

""" Section below is responsible for the CLI input/output """
app = typer.Typer(context_settings=dict(max_content_width=800))
# app.add_typer(vmlist.app, name="list")
app.add_typer(vmdeploy.app, name="deploy", help="Manage users in the app.")

@app.command()
def list(json: bool = typer.Option(False, help="Output json instead of a table")):
    """
    Example: hoster vm list
    """
    vm_list

""" If this file is executed from the command line, activate Typer """
if __name__ == "__main__":
    app()