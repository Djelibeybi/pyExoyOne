# type: ignore

"""A mock ExoyOne device."""

import asyncio
import json
import logging
import random
from dataclasses import asdict, dataclass
from typing import Annotated

import asyncio_dgram
import typer
from rich.logging import RichHandler

FIELD_MAP = {
    "setBrightness": "brightness",
    "setModPack": "currentModpack",
    "setEffect": "modeIndex",
    "setSpeed": "speed",
    "setHue": "hue",
    "setSaturation": "saturation",
    "toggleModeCycle": ("autoChange", True),
    "toggleMusicSync": ("musicSync", True),
    "togglePower": ("fadingOff", True),
    "toggleSceneGeneration": ("sceneGeneration", True),
    "toggleDirection": ("direction", True),
    "setName": "userDefinedName",
    "setCycleSpeed": "cycleSpeed",
    "setShutdownTimer": "shutdownTimer",
    "poweredByPowerbank": ("poweredByPowerbank", True),
    "setPattern": "selectedPattern",
    "setRenderMode": "selectedRenderMode",
    "setColorMode": "selectedColorMode",
    "setPalette": "selectedPalette",
}

app = typer.Typer(no_args_is_help=True)


@dataclass
class MoxyOneState:
    """Fake MoxyOne state."""

    mdnsName: str
    type: int = 4
    brightness: int = 0
    currentModpack: int = 0
    modeIndex: int = 0
    speed: int = 10
    hue: int = 0
    saturation: int = 255
    autoChange: bool = False
    musicSync: bool = False
    fadingOff: bool = False
    buttonEnabled: bool = True
    sceneGeneration: bool = False
    lockColorWheel: bool = False
    forceMusicSync: bool = False
    selectedPattern: int = 1
    selectedRenderMode: int = 1
    selectedColorMode: int = 1
    selectedPalette: int = 1
    userDefinedName: str = ""
    cycleSpeed: int = 20
    shutdownTimer: int = 0
    direction: bool = True
    connectedToWiFi: bool = True
    firmwareVersion: str = "2.1"
    poweredByPowerbank: bool = False

    def as_dict(self) -> dict:
        """Return as dict."""
        values = asdict(self)
        values["shutdownTimer"] = values["shutdownTimer"] * 60
        return values


class MoxyOne:
    """A mock ExoyOne device."""

    def __init__(self, logger: logging.Logger, delay: bool = False) -> None:
        """Initialize MoxyOne."""
        self._state = MoxyOneState(
            mdnsName=f"exoyone{random.randint(12345, 67890):05d}"
        )
        self._stream: asyncio_dgram.aio.DatagramServer | None = None
        self._lock = asyncio.Lock()
        self._logger = logger
        self._timeout: float = 0.1
        self._delay = delay

    async def serve(self) -> None:
        """Start responding to requests."""
        self._stream = await asyncio_dgram.bind(("127.0.0.1", 8888))
        self._logger.info("MoxyOne started serving on %s", self._stream.sockname)
        self._logger.debug("Current status: %s", self._state.as_dict())

        while True:
            try:
                data, remote_addr = await self._stream.recv()
                request = json.loads(data.decode())
                self._logger.debug("Received %s from %s", request, remote_addr)

                if request.get("getData", False) is False:
                    for key, value in request.items():
                        self._logger.info("Handling %s = %s", key, value)
                        if key in FIELD_MAP:
                            param = FIELD_MAP[key]
                            if len(param) == 2:
                                value = bool(value)
                                param = param[0]
                            elif key == "setShutdownTimer":
                                value = value.get("minutes") + (value.get("hours") * 60)
                                param = param

                            elif key == "cycleSpeed":
                                value = value.get("minutes") + (value.get("hours") * 60)
                                param = param
                            elif key == "connectToWiFi" or key == "restartInApMode":
                                continue
                            self._logger.info(
                                "Changing %s from %s to %s",
                                param,
                                getattr(self._state, param),
                                value,
                            )
                            setattr(self._state, f"{param}", value)
                        else:
                            self._logger.info("Ignoring %s", key)
                            continue
                elif request.get("getData", False) == 1:
                    if self._delay:
                        await asyncio.sleep(0.6)
                    self._logger.info(
                        "Sending %s to %s", self._state.as_dict(), remote_addr
                    )
                    await self._stream.send(
                        json.dumps(self._state.as_dict()).encode(), remote_addr
                    )

            except asyncio_dgram.aio.TransportClosed:
                self._logger.error("Transport closed.")
            except Exception as e:
                self._logger.error("Error: %s", e, exc_info=e)


@app.command()
def serve(ctx: typer.Context) -> None:
    """Start the server."""
    loop = asyncio.get_event_loop()
    logger = ctx.obj.get("logger")
    moxyone = MoxyOne(logger)

    task = loop.create_task(moxyone.serve())

    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        task.cancel()
    except asyncio.CancelledError:
        pass


@app.callback()
def main(
    ctx: typer.Context,
    debug: Annotated[bool, typer.Option("--debug")] = False,
    delay: Annotated[bool, typer.Option("--delay")] = False,
) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )

    _LOGGER = logging.getLogger(__package__)

    if debug:
        _LOGGER.setLevel(level=logging.DEBUG)

    ctx.ensure_object(dict)
    ctx.obj["logger"] = _LOGGER

    if delay:
        ctx.obj["delay"] = True


if __name__ == "__main__":
    app()
