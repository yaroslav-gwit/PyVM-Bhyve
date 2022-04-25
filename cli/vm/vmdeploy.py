import typer

app = typer.Typer()

@app.command()
def deploy(item: str):
    print("Deploy Test")


if __name__ == "__main__":
    app()