"""ExoyOne state model."""

from __future__ import annotations

import logging
from dataclasses import dataclass, fields

from camel_converter import to_snake

from exoyone.models import mode_packs

_LOGGER = logging.getLogger(__package__)


@dataclass
class ExoyOneState:
    """ExoyOne state data model."""

    mdnsName: str
    type: int
    brightness: int
    currentModpack: int
    modeIndex: int
    speed: int
    hue: int
    saturation: int
    autoChange: bool
    musicSync: bool
    fadingOff: bool
    buttonEnabled: bool
    sceneGeneration: bool
    lockColorWheel: bool
    forceMusicSync: bool
    selectedPattern: int
    selectedRenderMode: int
    selectedColorMode: int
    selectedPalette: int
    userDefinedName: str
    cycleSpeed: int
    shutdownTimer: int
    direction: bool
    connectedToWiFi: bool
    firmwareVersion: str
    poweredByPowerbank: bool

    @property
    def friendly(self) -> dict[str, dict[str, int | str | tuple[int, int, int]]]:
        """Return fields in snake_case as a dictionary."""
        device_name = self.userDefinedName if self.userDefinedName else "Not Set"
        mode_pack = mode_packs.get_pack_name_from_index(self.currentModpack)
        effect = mode_packs.get_effect_name_from_index(
            self.currentModpack, self.modeIndex
        )

        def on_off(value: bool) -> str:
            """Return on if true, off if false."""
            return "On " if value else "Off "

        return {
            "Hardware Details": {
                "mDNS Name": f"{self.mdnsName}",
                "Firmware Version": self.firmwareVersion,
            },
            "Device Details": {
                "Device Name": device_name,
                "Power": on_off(self.fadingOff),
                "Powerbank Mode": on_off(self.poweredByPowerbank),
                "Shutdown Timer": self.shutdownTimer,
            },
            "Effect Details": {
                "Color": (self.hue, self.saturation, self.brightness),
                "Mode Pack": mode_pack,
                "Effect": effect,
                "Effect Speed": self.speed,
                "Effect Direction": self.direction,
            },
            "Effect Options": {
                "Music Sync": on_off(self.musicSync),
                "Scene Generation": on_off(self.sceneGeneration),
                "Mode Cycle": on_off(self.autoChange),
                "Mode Cycle Speed": self.cycleSpeed,
            },
        }

    def as_dict(self) -> dict[str, bool | int | str]:
        """Return fields in snake_case as a dictionary."""
        return {
            to_snake(dc_field.name): getattr(self, dc_field.name)
            for dc_field in fields(self)
        }
