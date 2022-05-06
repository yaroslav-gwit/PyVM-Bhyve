#!bin/python
import typer

""" Section below is responsible for the CLI input/output """
app = typer.Typer(context_settings=dict(max_content_width=800))


@app.command()
def init(json:bool = typer.Option(False, help="Output json instead of a table")):
    """
    List the VMs using table or JSON output
    """
    print("Debil")