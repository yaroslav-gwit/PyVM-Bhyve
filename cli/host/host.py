import typer

# Core functions
from core.host import hostinfo

""" Section below is responsible for the CLI input/output """
app = typer.Typer(context_settings=dict(max_content_width=800))

@app.command()
def info(json: bool = typer.Option(False, help="Output json instead of a table")):
    """
    Example: hoster host info
    """
    if json:
        hostinfo.HostInfoJson()
    else:
        hostinfo.HostInfoTable().hostinfo()

""" If this file is executed from the command line, activate Typer """
if __name__ == "__main__":
    app()