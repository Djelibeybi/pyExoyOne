"""ExoyOne integration."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Mapping
from typing import ClassVar

import backoff
from asyncio_dgram.aio import DatagramClient, connect

from . import __version__
from .models import (
    ExoyDevices,
    ExoyOneTimeoutError,
    ExoyOneValueError,
    ModePacks,
    TruthyFalsyWords,
)
from .state import ExoyOneState

_LOGGER = logging.getLogger(__package__)
_GET_DATA = b'{"getData": 1}'

pyexoyone_version = __version__


class ExoyOne:
    """Representation of an ExoyOne Light."""

    TIMEOUT: ClassVar[float] = 3.0

    def __init__(self, host: str, port: int = 8888) -> None:
        """Initialize the ExoyOne library."""
        self._host = host
        self._port = port
        self._state: ExoyOneState
        self._mp = ModePacks()

    @property
    def host(self) -> str:
        """Return the hostname or IP address used to connect."""
        return self._host

    @property
    def name(self) -> str:
        """Return either the user-defined name or mDNS name."""
        name = self._state.mdnsName
        if len(self._state.userDefinedName) > 0:
            name = self._state.userDefinedName
        return name

    @property
    def state(self) -> ExoyOneState:
        """Returns the in-memory state of the ExoyOne."""
        return self._state

    @property
    def device_type(self) -> str:
        """Return the device type."""
        device_type = ExoyDevices(self._state.type).name
        return device_type.replace("_", " ").title()

    @staticmethod
    def _bool_val(value: bool | int | str) -> int:
        """Return 1 for truthy state or 0 for falsy state."""
        if isinstance(value, int):
            return value

        if isinstance(value, str) and value.upper() in TruthyFalsyWords.__members__:
            return TruthyFalsyWords[value.upper()].value

        raise ExoyOneValueError(f"Invalid value: {value}")

    @backoff.on_exception(
        backoff.expo,
        ExoyOneTimeoutError,
        max_tries=3,
        logger=_LOGGER,
        backoff_log_level=logging.DEBUG,
    )
    async def async_set_data(
        self, request: Mapping[str, Mapping[str, int | str] | bool | int | str]
    ) -> None:
        """Update a setting on the ExoyOne, then get the latest state data."""
        encoded_update = json.dumps(request).encode("utf-8")
        try:
            stream: DatagramClient = await connect((self._host, self._port))
            await asyncio.wait_for(stream.send(encoded_update), timeout=self.TIMEOUT)
        except TimeoutError as exc:
            raise ExoyOneTimeoutError() from exc
        finally:
            stream.close()
            del stream
            await self.async_get_data()

    @backoff.on_exception(
        backoff.expo,
        ExoyOneTimeoutError,
        max_tries=3,
        logger=_LOGGER,
        backoff_log_level=logging.DEBUG,
    )
    async def async_get_data(self) -> None:
        """Update the in-memory state using data from the ExoyOne."""
        try:
            stream: DatagramClient = await connect((self._host, self._port))
            await asyncio.wait_for(stream.send(b'{"getData": 1}'), timeout=self.TIMEOUT)
            reply, _ = await asyncio.wait_for(stream.recv(), timeout=self.TIMEOUT)
            data = json.loads(reply.decode("utf-8"))
            self._state = ExoyOneState(**data)
        except TimeoutError as exc:
            raise ExoyOneTimeoutError() from exc
        finally:
            stream.close()
            del stream

    def get_active_pack_name(self) -> str:
        """Return the name of the currently active modpack."""
        return self._mp.get_pack_name_from_index(self._state.currentModpack)

    def get_active_effect(self) -> str:
        """Return the name of the currently active effect."""
        return self._mp.get_effect_name_from_index(
            pack_index=self._state.currentModpack,
            effect_index=self._state.modeIndex,
        )

    async def async_get_state(self) -> ExoyOneState:
        """Return the current state as an ExoyOne object."""
        await self.async_get_data()
        return self._state

    async def restart_in_ap_mode(self) -> None:
        """Restart the device in AP mode."""
        await self.async_set_data({"restartInApMode": True})

    async def toggle_power(self, state: bool | int | str) -> None:
        """Toggle power."""
        request = {"togglePower": self._bool_val(state)}
        await self.async_set_data(request)

    async def toggle_direction(self, state: bool | int | str) -> None:
        """Toggle direction."""
        request = {"toggleDirection": self._bool_val(state)}
        await self.async_set_data(request)

    async def _async_set_hsbs(self, key: str, value: int) -> None:
        """Helper method to set hue, saturation, brightness and speed."""
        value = max(0, min(value, 255))
        await self.async_set_data({key: value})

    async def set_color(self, hsb: tuple[int, int, int]) -> None:
        """Set the hue, saturation and brightness in a single call."""
        hue = max(0, min(hsb[0], 255))
        saturation = max(0, min(hsb[1], 255))
        brightness = max(0, min(hsb[2], 255))
        await self.async_set_data(
            {
                "setHue": hue,
                "setSaturation": saturation,
                "setBrightness": brightness,
            }
        )

    async def set_hue(self, hue: int) -> None:
        """Set the hue."""
        await self._async_set_hsbs(key="setHue", value=hue)

    async def set_saturation(self, saturation: int) -> None:
        """Set the saturation."""
        await self._async_set_hsbs(key="setSaturation", value=saturation)

    async def set_brightness(self, brightness: int) -> None:
        """Set the brightness."""
        await self._async_set_hsbs(key="setBrightness", value=brightness)

    async def set_speed(self, speed: int) -> None:
        """Set the speed."""
        await self._async_set_hsbs(key="setSpeed", value=speed)

    async def toggle_mode_cycle(self, state: bool | int | str) -> None:
        """Toggle automatic mode change after set interval."""
        request = {"toggleModeCycle": self._bool_val(state)}
        await self.async_set_data(request)

    async def toggle_music_sync(self, state: bool | int | str) -> None:
        """Toggle music sync."""
        request = {"toggleMusicSync": self._bool_val(state)}
        await self.async_set_data(request)

    async def set_cycle_speed(self, cycle_speed: int) -> None:
        """Set cycle speed in seconds."""
        await self.async_set_data({"setCycleSpeed": cycle_speed})

    async def set_effect(self, effect: str | tuple[int, int]) -> None:
        """Set mode mode_pack and effect."""
        if isinstance(effect, str):
            pack_index, effect_index = self._mp.get_indices_from_effect_name(effect)
        else:
            pack_index, effect_index = effect

        if pack_index > -1 and effect_index > -1:
            await self.async_set_data(
                {
                    "setModPack": pack_index,
                    "setEffect": effect_index,
                }
            )

    async def toggle_scene_generation(self, state: bool | int | str) -> None:
        """Toggle scene generation."""
        request = {"toggleSceneGeneration": self._bool_val(state)}
        await self.async_set_data(request)

    async def set_name(self, name: str) -> None:
        """Set a new user-friendly name."""
        if len(name) > 39:
            name = name[:39]
            _LOGGER.warning("Name truncated to maximum allowed length: %s", name[:39])
        await self.async_set_data({"setName": name})

    async def set_shutdown_timer(self, minutes: int) -> None:
        """Set a shutdown timer of at least 5 and at most 480 minutes."""
        minutes = int(minutes)

        if minutes == 0:
            _LOGGER.debug("Disabling shutdown timer.")

        elif 1 < minutes < 5:
            _LOGGER.debug("Shutdown timer set to minimum duration of 5 minutes.")
            minutes = 5

        if minutes > 480:
            _LOGGER.debug("Shutdown timer set to maximum duration of 8 hours.")
            minutes = 480

        hours: int = 0
        if minutes > 60:
            hours = minutes // 60
            minutes = minutes % 60

        await self.async_set_data(
            {"setShutdownTimer": {"hours": hours, "minutes": minutes}}
        )

    async def connect_to_wifi(self, ssid: str, password: str) -> None:
        """Set new Wi-Fi connection credentials."""
        if len(ssid) == 0 or len(password) == 0:
            raise ExoyOneValueError(
                "Both SSID and password must be set to change WiFi credentials"
            )
        if len(ssid) > 31:
            raise ExoyOneValueError(
                "SSID is longer than maximum allowed length of 31 characters"
            )
        if len(password) > 31:
            raise ExoyOneValueError(
                "Password is longer than the maximum allowed length of 31 characters"
            )

        await self.async_set_data(
            {"connectToWifi": {"ssid": ssid, "password": password}}
        )

    async def powered_by_powerbank(self, state: bool | int | str) -> None:
        """Toggle power consumption reduction when running on batteries."""
        request = {"poweredByPowerbank": self._bool_val(state)}
        await self.async_set_data(request)

    async def set_pattern(self, value: int) -> None:
        """Use async_set_data to change the selectedPattern value."""
        await self.async_set_data({"setPattern": value})

    async def set_palette(self, value: int) -> None:
        """Use async_set_data to change the selectedPalette value."""
        await self.async_set_data({"setPalette": value})

    async def set_render_mode(self, value: int) -> None:
        """Use async_set_data to change the selectedRenderMode value."""
        await self.async_set_data({"setRenderMode": value})

    async def set_color_mode(self, value: int) -> None:
        """Use async_set_data to change the selectedColorMode value."""
        await self.async_set_data({"setColorMode": value})
