import typer
from cli.vm import vmdeploy
from cli.vm import vmlist

""" Section below is responsible for the CLI input/output """
app = typer.Typer(context_settings=dict(max_content_width=800))
app.add_typer(vmlist.app, name="list")
app.add_typer(vmdeploy.app, name="deploy")

""" If this file is executed from the command line, activate Typer """
if __name__ == "__main__":
    app()