"""Get commands for exoyOneCLI."""

import logging
from types import SimpleNamespace
from typing import Annotated

import rich
import typer
from click import Choice
from rich import box
from rich.color import Color
from rich.columns import Columns
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from ..models import mode_packs as mp
from . import helpers as hp

_LOGGER = logging.getLogger(__package__)
app = typer.Typer(no_args_is_help=True)


@app.command()
def effects(
    mode_pack: Annotated[
        str,
        typer.Option(
            click_type=Choice(choices=mp.mode_packs, case_sensitive=False),
            help="Name of a mode pack",
            show_choices=False,
            show_default=False,
        ),
    ]
    | None = None,
) -> None:
    """Get a list of effects for the specified mode pack or all mode packs."""
    trees: list[Tree] = []

    if mode_pack is not None:
        pack_index = mp.get_pack_index_from_name(mode_pack)
        if pack_index > -1:
            trees.append(Tree(f"[red]{mode_pack.title()}[/red]", guide_style="red"))
            mp_effects = mp.get_effects_by_index(pack_index)
            for effect in mp_effects:
                trees[0].add(effect)
        else:
            rich.print(f"Invalid mode pack: {mode_pack}")
            raise typer.Exit(2)
    else:
        for pack_index, pack_name in enumerate(mp.mode_packs):
            trees.append(
                Tree(
                    pack_name,
                    style=f"color({pack_index + 1})",
                )
            )

            for _, effect_name in enumerate(mp.get_effects_by_index(pack_index)):
                trees[pack_index].add(effect_name, style="white")

    columns = Columns(trees, equal=False, expand=False)
    rich.print(columns)


@app.command("power-state")
def power_state(ctx: typer.Context) -> None:
    """Get the power state (on/off)."""
    exoyone = hp.get_exoyone(ctx.obj.host)
    state = "[green]ON[/]" if exoyone.state.fadingOff else "[red]OFF[/]"
    rich.print(f"Power state: {state}")


@app.command("music-sync")
def music_sync(ctx: typer.Context) -> None:
    """Get music sync state (on/off)."""
    exoyone = hp.get_exoyone(ctx.obj.host)
    state = "[green]ON[/]" if exoyone.state.musicSync else "[red]OFF[/]"
    rich.print(f"Music sync: {state}")


@app.command("scene-generation")
def scene_generation(ctx: typer.Context) -> None:
    """Get scene generation state (on/off)."""
    exoyone = hp.get_exoyone(ctx.obj.host)
    state = "[green]ON[/]" if exoyone.state.sceneGeneration else "[red]OFF[/]"
    rich.print(f"Scene generation: {state}")


@app.command("powerbank-mode")
def powerbank_mode(ctx: typer.Context) -> None:
    """Get powered by powerbank state (on/off)."""
    exoyone = hp.get_exoyone(ctx.obj.host)
    state = "[green]ON[/]" if exoyone.state.poweredByPowerbank else "[red]OFF[/]"
    rich.print(f"Powered by powerbank mode: {state}")


@app.command("mode-cycle")
def mode_cycle(ctx: typer.Context) -> None:
    """Get mode cycle state (on/off)."""
    exoyone = hp.get_exoyone(ctx.obj.host)
    state = "[green]ON[/]" if exoyone.state.autoChange else "[red]OFF[/]"
    rich.print(f"Mode cycle: {state}")


@app.command("cycle-speed")
def cycle_speed(ctx: typer.Context) -> None:
    """Get the current effect speed."""
    exoyone = hp.get_exoyone(ctx.obj.host)
    state = str(exoyone.state.cycleSpeed)
    rich.print(f"Current mode cycle speed: [yellow]{state}[/]")


@app.command("direction")
def direction(ctx: typer.Context) -> None:
    """Get the effect direction (left/right)."""
    exoyone = hp.get_exoyone(ctx.obj.host)
    state = "[green]LEFT[/]" if exoyone.state.direction else "[red]RIGHT[/]"
    rich.print(f"Effect direction: {state}")


@app.command("effect-speed")
def effect_speed(ctx: typer.Context) -> None:
    """Get the current effect speed."""
    exoyone = hp.get_exoyone(ctx.obj.host)
    state = str(exoyone.state.speed)
    rich.print(f"Current effect speed: [yellow]{state}[/]")


@app.command("shutdown-timer")
def shutdown_timer(ctx: typer.Context) -> None:
    """Get the current shutdown timer."""
    exoyone = hp.get_exoyone(ctx.obj.host)
    shutdown_timer_output = "Shutdown timer: "
    if exoyone.state.shutdownTimer > 0:
        minutes = int(exoyone.state.shutdownTimer / 60)
        shutdown_timer_output = f"{shutdown_timer_output}[yellow]{minutes} minutes[/]"
    else:
        shutdown_timer_output = f"{shutdown_timer_output}[red]Disabled[/]"
    rich.print(shutdown_timer_output)


@app.command("device-name")
def device_name(ctx: typer.Context) -> None:
    """Get the device name."""
    exoyone = hp.get_exoyone(ctx.obj.host)
    dev_name = (
        f"[yellow]{exoyone.state.userDefinedName}[/]"
        if exoyone.state.userDefinedName
        else "[dim red]Unset[/]"
    )
    mdns_name = f"{exoyone.state.mdnsName}"
    rich.print(f"Device name: {dev_name}")
    rich.print(f"mDNS address: [blue]{mdns_name}[/]")


@app.command("color")
def color(ctx: typer.Context) -> None:
    """Get the current hue, saturation and brightness values."""
    exoyone = hp.get_exoyone(ctx.obj.host)

    console = Console()
    hue = exoyone.state.hue
    brightness = exoyone.state.brightness
    saturation = exoyone.state.saturation
    red, green, blue = hp.hsb_to_rgb(hue, saturation, brightness)
    color_obj: Color = Color.from_rgb(red, green, blue)

    console.print(
        Text()
        .append("RGB: ")
        .append(f"{red:>3}", style=f"{color_obj.name}")
        .append(", ")
        .append(f"{green:>3}", style=f"{color_obj.name}")
        .append(", ")
        .append(f"{blue:>3}", style=f"{color_obj.name}")
        .append(" [red, green, blue]", style="dim"),
    )
    console.print(
        Text()
        .append("HSB: ")
        .append(f"{hue:>3}", style=f"{color_obj.name}")
        .append(", ")
        .append(f"{saturation:>3}", style=f"{color_obj.name}")
        .append(", ")
        .append(f"{brightness:>3}", style=f"{color_obj.name}")
        .append(" [hue, saturation, brightness]", style="dim"),
    )
    console.print(
        Text()
        .append("CSS: ")
        .append(f"{color_obj.name}", style=f"{color_obj.name}")
        .append("       [HTML/CSS color]", style="dim"),
    )


@app.command("everything")
def everything(
    ctx: typer.Context,
) -> None:
    """Get the state and value of all the things."""
    exoyone = hp.get_exoyone(ctx.obj.host)
    state = exoyone.state

    console = Console()

    root = Table(
        box=None,
        highlight=True,
        show_footer=False,
        show_header=False,
    )

    root.add_column("Content", no_wrap=True)

    for section in state.friendly.keys():
        table = Table(
            box=box.SIMPLE_HEAD,
            highlight=True,
            show_footer=False,
            show_header=True,
        )

        table.add_column(f"{section}")
        table.add_column("Value")

        value: bool | int | str | tuple[int, int, int]
        for field, value in state.friendly[section].items():
            vt = Text()

            if field.lower() == "color" and isinstance(value, tuple):
                field = "Color: [[dim]Hue, Sat, Bri[/]]"
                (hue, sat, bri) = value
                red, green, blue = hp.hsb_to_rgb(hue, sat, bri)
                effect_color = Color.from_rgb(red, green, blue)

                hue_str = Text(f"({hue}, ", style=f"{effect_color.name}")
                sat_str = Text(f"{sat}, ", style=f"{effect_color.name}")
                bri_str = Text(f"{bri})", style=f"{effect_color.name}")

                vt = Text.assemble(hue_str, sat_str, bri_str)

            value_text = str(value)

            if field.lower() == "shutdown timer":
                value_text = "Disabled"
                if isinstance(value, int) and value > 0:
                    value_text = f"{int(value / 60)} minutes"

            elif field.lower() == "mode cycle speed":
                value_text = "Disabled"
                if state.autoChange is True:
                    value_text = f"{value} seconds"

            vt.append(Text(f"{value_text}", style="bold blue"))

            vt.highlight_words(["On ", "on "], style="bold green")
            vt.highlight_words(["Off ", "off "], style="bold red")
            vt.highlight_words(["Disabled"], style="dark_red")
            vt.highlight_words(mp.mode_packs, style="bold cyan")
            vt.highlight_words(mp.effects, style="bold magenta")
            cells = [field, vt]

            table.add_row(*cells)

        root.add_row(table, end_section=True)

    console.print(root)


@app.callback()
def get(
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
    Get information from your ExoyOne.

    This includes the current state of the device, including power, color, effects,
    and more.
    """
    if not host:
        rich.print("Missing required argument: '--host'")
        raise typer.Exit(1)

    ctx.obj = SimpleNamespace(host=host)
