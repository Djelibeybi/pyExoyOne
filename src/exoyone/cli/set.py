"""Set commands for ExoyOne CLI."""

from __future__ import annotations

import asyncio
import logging
from types import SimpleNamespace
from typing import Annotated

import rich
import typer
from click import Choice

from .. import ExoyOne
from .. import mode_packs as mp
from . import helpers as hp

_LOGGER = logging.getLogger(__package__)

app = typer.Typer(no_args_is_help=True)


@app.command("restart-in-ap-mode")
def restart_in_ap_mode(ctx: typer.Context) -> None:
    """Restart the ExoyOne to enable Wi-Fi access point."""
    exoyone = hp.get_exoyone(ctx.obj.host)
    asyncio.run(exoyone.restart_in_ap_mode())


@app.command("color")
def color(
    ctx: typer.Context,
    hue: Annotated[
        int,
        typer.Argument(
            help="Hue value between 0 and 255.",
            metavar="[HUE]",
            show_default=False,
            min=0,
            max=255,
            clamp=True,
        ),
    ],
    saturation: Annotated[
        int,
        typer.Argument(
            help="Saturation value between 0 and 255.",
            metavar="[SAT]",
            show_default=False,
            min=0,
            max=255,
            clamp=True,
        ),
    ],
    brightness: Annotated[
        int,
        typer.Argument(
            help="Brightness value between 0 and 255.",
            metavar="[BRI]",
            show_default=False,
            min=0,
            max=255,
            clamp=True,
        ),
    ],
) -> None:
    """Set the color by changing the hue, saturation and brightness."""
    exoyone = hp.get_exoyone(ctx.obj.host)
    hp.send_request_with_progress(
        exoyone,
        method_to_call="set_color",
        value_to_set=(hue, saturation, brightness),
        key_to_check="hue",
        description=f"Setting HSB to {hue}, {saturation}, {brightness}...",
        value_to_check=hue,
        value_to_bool=False,
    )


@app.command("shutdown-timer")
def shutdown_timer(
    ctx: typer.Context,
    minutes: Annotated[
        int,
        typer.Argument(
            help="Duration of shutdown timer from 5 to 480 minutes, 0 to disable.",
            metavar="[MINUTES]",
            min=0,
            max=480,
            show_choices=False,
            show_default=False,
        ),
    ],
) -> None:
    """Set the shutdown timer duration."""
    exoyone = hp.get_exoyone(ctx.obj.host)
    if minutes == 0:
        description = "Disabling the shutdown timer..."
    else:
        description = f"Setting shutdown timer to {minutes} minutes..."
    hp.send_request_with_progress(
        exoyone,
        method_to_call="set_shutdown_timer",
        value_to_set=minutes,
        key_to_check="shutdownTimer",
        description=description,
        value_to_check=minutes * 60,
        value_to_bool=False,
    )


@app.command("effect")
def change_effect(
    ctx: typer.Context,
    name: Annotated[
        str,
        typer.Argument(
            click_type=Choice(choices=mp.effects, case_sensitive=False),
            help="Name of the effect.",
            metavar="[EFFECT]",
            case_sensitive=False,
            show_default=False,
            show_choices=False,
        ),
    ],
) -> None:
    """Change the active effect."""
    exoyone: ExoyOne = hp.get_exoyone(ctx.obj.host)
    pack_index, effect_index = mp.get_indices_from_effect_name(name)

    pack_name = mp.get_pack_name_from_index(pack_index)
    description = f"Changing mode pack to [red]{pack_name}[/red] and effect to [yellow]{name}[/yellow]..."  # noqa: E501

    hp.send_request_with_progress(
        exoyone,
        method_to_call="set_effect",
        value_to_set=(pack_index, effect_index),
        key_to_check="modexIndex",
        description=description,
        value_to_check=effect_index,
        value_to_bool=False,
    )


@app.command("effect-speed")
def effect_speed(
    ctx: typer.Context,
    speed: Annotated[
        int,
        typer.Argument(
            help="Effect speed", metavar="[SPEED]", show_default=False, min=0, max=250
        ),
    ],
) -> None:
    """Set the speed of the effect."""
    exoyone = hp.get_exoyone(ctx.obj.host)
    hp.send_request_with_progress(
        exoyone,
        method_to_call="set_speed",
        value_to_set=speed,
        key_to_check="speed",
        description=f"Setting effect speed to {speed}...",
    )


@app.command("scene-generation")
def scene_generation(
    ctx: typer.Context,
    state: Annotated[
        hp.ToggleOptions,
        typer.Argument(
            help="Turn scene generation off or on.",
            metavar="[off|on]",
            case_sensitive=False,
            show_choices=False,
            show_default=False,
        ),
    ],
) -> None:
    """Turn scene generation off or on."""
    exoyone: ExoyOne = hp.get_exoyone(ctx.obj.host)
    value = str(state.value)
    hp.send_request_with_progress(
        exoyone,
        "toggle_scene_generation",
        value,
        "sceneGeneration",
        description=f"Turning scene generation {value}...",
    )


@app.command("mode-cycle")
def mode_cycle(
    ctx: typer.Context,
    state: Annotated[
        hp.ToggleOptions,
        typer.Argument(
            help="Turn mode cycle off or on.",
            metavar="[off|on]",
            case_sensitive=False,
            show_choices=False,
            show_default=False,
        ),
    ],
) -> None:
    """Turn mode cycle off or on."""
    exoyone: ExoyOne = hp.get_exoyone(ctx.obj.host)
    value = str(state.value)
    hp.send_request_with_progress(
        exoyone,
        "toggle_mode_cycle",
        value,
        "autoChange",
        description=f"Turning mode cycle {value}...",
    )


@app.command("cycle-speed")
def cycle_speed(
    ctx: typer.Context,
    seconds: Annotated[
        int,
        typer.Argument(
            help="Delay in seconds between cycles when mode cycle is on.",
            metavar="[SECONDS]",
            min=5,
            max=43200,
            clamp=True,
            show_default=False,
            show_choices=False,
        ),
    ],
) -> None:
    """Set the mode cycle duration in seconds."""
    exoyone: ExoyOne = hp.get_exoyone(ctx.obj.host)
    hp.send_request_with_progress(
        exoyone,
        method_to_call="set_cycle_speed",
        value_to_set=seconds,
        key_to_check="cycleSpeed",
        description=f"Setting mode cycle speed to {seconds} seconds...",
        value_to_check=seconds,
        value_to_bool=False,
    )


@app.command("music-sync")
def music_sync(
    ctx: typer.Context,
    state: Annotated[
        hp.ToggleOptions,
        typer.Argument(
            help="Turn music sync off or on.",
            metavar="[off|on]",
            case_sensitive=False,
            show_choices=False,
            show_default=False,
        ),
    ],
) -> None:
    """Turn music sync on or off."""
    exoyone: ExoyOne = hp.get_exoyone(ctx.obj.host)
    value = str(state.value)
    hp.send_request_with_progress(
        exoyone,
        "toggle_music_sync",
        value,
        "musicSync",
        description=f"Turning music sync {value}...",
    )


@app.command("power-state")
def power_state(
    ctx: typer.Context,
    state: Annotated[
        hp.ToggleOptions,
        typer.Argument(
            help="Switch the power on or off",
            metavar="[off|on]",
            case_sensitive=False,
            show_choices=False,
            show_default=False,
        ),
    ],
) -> None:
    """Turn power state on or off."""
    exoyone: ExoyOne = hp.get_exoyone(ctx.obj.host)
    value = str(state.value)
    hp.send_request_with_progress(
        exoyone,
        "toggle_power",
        value,
        "fadingOff",
        description=f"Turning power state {value}...",
    )


@app.command("powerbank-mode")
def powerbank_mode(
    ctx: typer.Context,
    state: Annotated[
        hp.ToggleOptions,
        typer.Argument(
            help="Switch powered by powerbank mode on or off",
            metavar="[off|on]",
            case_sensitive=False,
            show_choices=False,
            show_default=False,
        ),
    ],
) -> None:
    """Turn powered by powerbank mode on or off."""
    exoyone: ExoyOne = hp.get_exoyone(ctx.obj.host)
    value = str(state.value)
    hp.send_request_with_progress(
        exoyone,
        method_to_call="powered_by_powerbank",
        value_to_set=value,
        key_to_check="poweredByPowerbank",
        description=f"Turning powered by powerbank mode {value}...",
    )


@app.command("device-name")
def device_name(
    ctx: typer.Context,
    name: Annotated[
        str,
        typer.Argument(
            help="Custom name for the ExoyOne.", metavar="[NAME]", show_default=False
        ),
    ],
) -> None:
    """Set the device name of the ExoyOne."""
    exoyone: ExoyOne = hp.get_exoyone(ctx.obj.host)
    hp.send_request_with_progress(
        exoyone,
        method_to_call="set_name",
        value_to_set=name,
        key_to_check="userDefinedName",
        description=f"Setting device name to [yellow]{name}[/yellow]...",
        value_to_check=name,
        value_to_bool=False,
    )


@app.command("direction")
def direction(
    ctx: typer.Context,
    effect_direction: Annotated[
        hp.DirectionOptions,
        typer.Argument(
            help="Set the direction of the effect.",
            metavar="[this-way|that-way]",
            case_sensitive=False,
            show_choices=True,
            show_default=False,
        ),
    ],
) -> None:
    """
    Set a direction for the active effect.

    There are only two directions. The list of options is provided
    for entertainment purposes, as the actual values are 0 and 1.
    Feel free to mix left with down, right with forward and so on.
    """
    exoyone: ExoyOne = hp.get_exoyone(ctx.obj.host)
    value = str(effect_direction.value)

    to_set = -1
    if value.lower() in ["left", "in", "up", "forwards", "clockwise"]:
        to_set = 1
    if value.lower() in ["right", "out", "down", "backwards", "counterclockwise"]:
        to_set = 0

    hp.send_request_with_progress(
        exoyone,
        method_to_call="toggle_direction",
        value_to_set=to_set,
        key_to_check="direction",
        description=f"Setting effect direction to {value.title()}",
        value_to_bool=True,
    )


@app.callback()
def set(
    ctx: typer.Context,
    host: Annotated[
        str,
        typer.Option(
            "--host",
            "-H",
            help="Hostname or IP address of your ExoyOne.",
            case_sensitive=False,
            show_default=False,
            envvar="EXOYONE_HOST",
        ),
    ],
) -> None:  # pragma: no cover
    """
    Change things on your ExoyOne.

    This includes turning it on or off, changing the color, effect, and more.
    """
    if not host:
        rich.print("Missing required argument: '--host'")
        raise typer.Exit(1)

    ctx.obj = SimpleNamespace(host=host)
