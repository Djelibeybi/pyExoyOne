"""ExoyOne CLI interface."""

import logging

import typer
from typer import Typer

from . import get, set

_LOGGER = logging.getLogger(__package__)

APP_NAME = "exoyone"

app: Typer = typer.Typer(no_args_is_help=True)
app.add_typer(get.app, name="get")
app.add_typer(set.app, name="set")


@app.callback()
def cli() -> None:
    """ExoyOne Command-Line Interface (CLI)."""


if __name__ == "__main__":
    """Run the ExoyOne CLI."""
    app()
