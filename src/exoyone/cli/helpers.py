"""Helper functions for the ExoyOne CLI."""

from __future__ import annotations

import asyncio
import colorsys
from enum import StrEnum

import rich
from rich.progress import Progress, SpinnerColumn, TextColumn

from .. import ExoyOne


def hsb_to_rgb(hue: int, saturation: int, brightness: int) -> tuple[int, int, int]:
    """Convert from HSB to RGB."""
    r, g, b = colorsys.hsv_to_rgb(hue / 255.0, saturation / 255.0, brightness / 255.0)
    return int(r * 255), int(g * 255), int(b * 255)


class DirectionOptions(StrEnum):
    """Direction options."""

    LEFT = "left"
    RIGHT = "right"
    IN = "in"
    OUT = "out"
    UP = "up"
    DOWN = "down"
    FORWARDS = "forwards"
    BACKWARDS = "backwards"
    CLOCKWISE = "clockwise"
    COUNTERCLOCKWISE = "counterclockwise"


class ToggleOptions(StrEnum):
    """Toggle options."""

    OFF = "off"
    ON = "on"


def send_request_with_progress(
    exoyone: ExoyOne,
    method_to_call: str,
    value_to_set: bool | int | str | tuple[int, int] | tuple[int, int, int],
    key_to_check: str,
    description: str = "Working...",
    value_to_check: bool | int | str | None = None,
    value_to_bool: bool = True,
) -> None:
    """Wrapper that calls an async toggle method with progress bar."""

    async def _with_progress() -> None:  # pragma: no cover
        """Async method with progress."""
        value = value_to_set

        if value_to_bool and (
            isinstance(value_to_set, bool)
            or isinstance(value_to_set, str)
            or isinstance(value_to_set, int)
        ):
            value = exoyone._bool_val(value_to_set)

        to_check = value_to_check if value_to_check is not None else value

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task(description, total=1)

            try:
                func = getattr(exoyone, method_to_call)
                await func(value)
                while not progress.finished:
                    if getattr(exoyone.state, key_to_check) == to_check:
                        progress.update(task, completed=1)
                    await asyncio.sleep(0.2)

            except AttributeError:
                return

    asyncio.run(_with_progress())
    rich.print(f"{description.removesuffix("...")}: [green]DONE[/green]")


def get_exoyone(host: str) -> ExoyOne:
    """Use asyncer to get the state of an ExoyOne instance."""
    exoyone = ExoyOne(host=host)

    async def _async_get() -> None:  # pragma: no cover
        """Connect to an ExoyOne device."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task(f"Connecting to {exoyone.host}...", total=1)
            await exoyone.async_get_data()

            while not progress.finished:
                if exoyone.state.currentModpack > -1:
                    progress.update(task, completed=1)
                await asyncio.sleep(0.1)

    asyncio.run(_async_get())
    return exoyone
