"""Exponential and predicate based backoff handlers."""

from __future__ import annotations

import logging
from enum import IntEnum
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    pass

_LOGGER = logging.getLogger(__package__)


class ExoyOneException(Exception):
    """ExoyOne exception."""


class ExoyOneTimeoutError(TimeoutError):
    """ExoyOne timeout error."""


class ExoyOneValueError(ValueError):
    """ExoyOne value error."""


class ExoyOneAttributeError(AttributeError):
    """ExoyOne attribute error."""


class ExoyOneAssertionError(AssertionError):
    """ExoyOne assertion error."""


class ExoyDevices(IntEnum):
    """Enumeration of Exoy devices."""

    INFINITY_OBJECT = 0
    HYPERCUBE = 1
    ULTRA_DENSE_HYPERCUBE = 2
    DODECAHEDRON = 3
    ULTRA_DENSE_DODECAHEDRON = 4
    MIRROR = 5
    ULTRA_DENSE_MIRROR = 6
    ICOSAHEDRON = 7
    ULTRA_DENSE_ICOSAHEDRON = 8
    TETRAHEDRON = 9
    ULTRA_DENSE_TETRAHEDRON = 10
    HEXAGON = 11
    ULTRA_DENSE_HEXAGON = 12
    SOUND_VISUALISER = 13
    ULTRA_DENSE_SOUND_VISUALISER = 14


class TruthyFalsyWords(IntEnum):
    """Truthy and falsy words."""

    TRUE = 1
    FALSE = 0
    ON = 1
    OFF = 0
    LEFT = 1
    RIGHT = 0
    CLOCKWISE = 1
    COUNTERCLOCKWISE = 0
    ANTICLOCKWISE = 0
    YES = 1
    NO = 0
    IN = 1
    OUT = 0
    UP = 1
    DOWN = 0
    FORWARD = 1
    BACKWARD = 0
    OPEN = 1
    CLOSE = 0


class ModePacks:
    """Helper class for mode packs and effects."""

    _mode_packs: ClassVar[list[str]] = [
        "Rave",
        "Party",
        "Chill",
        "Mood",
        "Genre",
        "Themes",
        "Nature",
        "Cosmic",
        "Background",
    ]

    _effects: ClassVar[list[list[str]]] = [
        [
            "Beats Burst",
            "Laser Lash",
            "Electric Ave",
            "Hypnosis",
            "Glow Groove",
            "Whirling Spectrum",
            "Rainbow Rumble",
        ],
        [
            "Dance Floor",
            "Rhythm Run",
            "Pop Party",
            "Funky Flash",
            "Jubulo",
            "Gloze",
            "Color Rush",
            "Confetti",
            "Rising Rhythm",
            "Pulse Peaks",
            "Beat Orbit",
        ],
        [
            "Soothing Sound",
            "Euphoria",
            "Dreamscape",
            "Serene Symphony",
            "Svelte",
            "Tranquilo",
        ],
        ["Mood Swing", "Emotional Express", "Feeling Flow", "Zenith", "Nimbus"],
        [
            "Rockin' Rhythms",
            "Jazz Live",
            "Hip Hop Hues",
            "Country Crescendo",
            "EDM Flow",
            "Hardstyle Beats",
        ],
        [
            "Cosmic Carnival",
            "Summer Breeze",
            "Desert Miracle",
            "Winter Wonderland",
            "Underwater Oasis",
            "Rainbow Ripple",
            "Error",
            "Matrix",
            "Beating Heart",
        ],
        [
            "Wildfire",
            "Thunderstorm",
            "Aurora",
            "Rainbow Reflection",
            "Bloom",
            "Celestial",
            "Ebb & Flow",
            "Majestic",
            "Whirlwind",
            "Lightning",
            "Snowstorm",
        ],
        [
            "Galaxy",
            "Cosmic Dust",
            "Solar Flare",
            "Sabre Fight",
            "Black Hole",
            "Meteor",
            "Astro",
            "Super Nova",
        ],
        [
            "Ambient Aura",
            "Twilight",
            "Dawn",
            "Custom Hue",
            "Color Carousel",
            "Shimmer",
            "Whisper",
        ],
    ]

    @property
    def mode_packs(self) -> list[str]:
        """Return a list of mode mode_pack names."""
        return self._mode_packs

    @property
    def pack_names(self) -> str:
        """Return mode_pack names as a comma-seperated string."""
        return f"[{'|'.join(name.lower() for name in self._mode_packs)}]"

    @property
    def effects(self) -> list[str]:
        """Return a list of effect names."""
        effect_names: list[str] = []
        for pack_effects in self._effects:
            effect_names.extend(pack_effects)
        return effect_names

    @property
    def effect_names(self) -> str:
        """Return effect names as a comma-seperated string."""
        return f"[{'|'.join(name.lower() for name in self.effects)}]"

    def get_effects_by_index(self, pack_index: int) -> list[str]:
        """Return a list of effects by mode mode_pack index."""
        return self._effects[pack_index]

    def get_pack_name_from_index(self, pack_index: int) -> str:
        """Return the name of a mode mode_pack given an index value."""
        return self.mode_packs[pack_index]

    def get_pack_index_from_name(self, name: str) -> int:
        """Return the index value of the named mode_pack."""
        try:
            return next(
                index
                for index, pack_name in enumerate(self._mode_packs)
                if pack_name.lower() == name.lower()
            )
        except StopIteration:
            return -1

    def get_effect_name_from_index(self, pack_index: int, effect_index: int) -> str:
        """Get effect name from current mode mode_pack and effect index."""
        active_effects = self.get_effects_by_index(pack_index)
        return active_effects[effect_index]

    def get_effect_index_from_name(self, pack_name: str, effect_name: str) -> int:
        """Return the index values of the mode_pack and effect named."""
        try:
            pack_index = self.get_pack_index_from_name(pack_name)
            if pack_index == -1:
                return -1
            pack_effects = self.get_effects_by_index(pack_index)
            return next(
                index
                for index, name in enumerate(pack_effects)
                if name.lower() == effect_name.lower()
            )
        except StopIteration:
            return -1

    def get_indices_from_effect_name(self, effect_name: str) -> tuple[int, int]:
        """Return the mode_pack index for the given effect name."""
        for index, _ in enumerate(self.mode_packs):
            effects = self.get_effects_by_index(pack_index=index)
            if effect_name in effects:
                return index, effects.index(effect_name)

        return -1, -1


mode_packs = ModePacks()
