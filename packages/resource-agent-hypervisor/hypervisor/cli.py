import sys
from typing import Sequence

import typer
from hypervisor import Hypervisor, get_config, load_config
from hypervisor.uri.client import Uri3Client

app = typer.Typer(help="Hypervisor thin CLI using uri3")


@app.command()
def scan(uri: str):
    for item in Uri3Client().scan(uri):
        typer.echo(item)


@app.command()
def resolve(uri: str):
    typer.echo(Uri3Client().resolve(uri))


@app.command()
def status():
    """Show hypervisor status."""
    hv = Hypervisor()
    st = hv.status()
    typer.echo("hypervisor")
    for k, v in st.items():
        typer.echo(f"{k}: {v}")


@app.command(name="config")
def config_cmd(path: bool = typer.Option(False, "--path", help="Print config path only")):
    """Show or inspect configuration."""
    if path:
        cfg = load_config()
        typer.echo(cfg.get("_config_path", "<embedded-defaults>"))
    else:
        cfg = get_config()
        typer.echo(repr(cfg))


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point that accepts optional argv (for tests and scripts)."""
    args = list(argv) if argv is not None else None
    try:
        app(args=args)
        return 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

