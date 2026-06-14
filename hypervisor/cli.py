import typer
from hypervisor.uri.client import Uri3Client
app = typer.Typer(help="Hypervisor thin CLI using uri3")
@app.command()
def scan(uri: str):
    for item in Uri3Client().scan(uri): typer.echo(item)
@app.command()
def resolve(uri: str): typer.echo(Uri3Client().resolve(uri))
def main(): app()
if __name__ == "__main__": main()
