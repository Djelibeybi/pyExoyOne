# type: ignore

import random
from unittest.mock import patch

import pytest

from exoyone import ExoyOne, ExoyOneState
from exoyone.models import ExoyOneTimeoutError, ExoyOneValueError, TruthyFalsyWords
from exoyone.models import mode_packs as mp

word_test_params = [
    (word.lower(), bool(TruthyFalsyWords[word].value))
    for word in TruthyFalsyWords.__members__
]
random.shuffle(word_test_params)

effect_test_params: list[tuple[str, str, int, int]] = []
for effect_name in mp.effects:
    pack_index, effect_index = mp.get_indices_from_effect_name(effect_name)
    pack_name = mp.get_pack_name_from_index(pack_index)
    effect_test_params.append((effect_name, pack_name, pack_index, effect_index))
random.shuffle(effect_test_params)


@pytest.mark.usefixtures("run_moxyone")
@pytest.mark.asyncio
class TestExoyOne:
    """Test the ExoyOne class."""

    async def test_state(self, exoyone):
        """Test that MoxyOne is responding."""
        assert isinstance(exoyone.state, ExoyOneState)
        assert isinstance(exoyone.state.as_dict(), dict)
        assert exoyone.state.mdnsName.startswith("exoyone")

        exoyone_state = await exoyone.async_get_state()
        assert isinstance(exoyone_state, ExoyOneState)
        assert exoyone_state == exoyone.state

    async def test_host(self, exoyone):
        """Test the host is set correctly."""
        assert exoyone.host == "127.0.0.1"

    async def test_host_error(self):
        """Test incorrect host config raises an exception."""
        exoyone = ExoyOne(host="192.168.254.254")
        with patch.object(exoyone, "TIMEOUT", 0.0):
            with pytest.raises(ExoyOneTimeoutError):
                await exoyone.async_get_data()
            with pytest.raises(ExoyOneTimeoutError):
                await exoyone.toggle_power(True)

    async def test_device_type(self, exoyone):
        """Test the device type is returned."""
        assert exoyone.device_type == "Ultra Dense Dodecahedron"

    async def test_name(self, exoyone):
        """Test the device name and user defined names are returned."""
        original_name = exoyone.name
        assert original_name is not None

        new_name = f"exoyone-{random.randint(12345, 67890):05d}"
        await exoyone.set_name(new_name)
        assert exoyone.name == new_name
        assert original_name != exoyone.name

        await exoyone.set_name(original_name)

    async def test_name_too_long(self, exoyone):
        """Test the device name and user defined names are returned."""
        original_name = exoyone.name
        new_name = "exoyone1A-exoyone1B-exoyone1C-exoyone1D-exoyone1E"
        await exoyone.set_name(new_name)
        assert exoyone.name == "exoyone1A-exoyone1B-exoyone1C-exoyone1D"
        assert original_name != new_name
        await exoyone.set_name(original_name)

    @pytest.mark.parametrize(
        "set_state, expected_state",
        [("on", True), ("off", False), (1, True), (0, False)],
    )
    async def test_power_state(self, exoyone, set_state, expected_state):
        """Test power state."""
        await exoyone.toggle_power(set_state)
        assert exoyone.state.fadingOff == expected_state

    async def test_direction(self, exoyone):
        """Test direction."""
        this_state = exoyone.state.direction
        next_state = bool(not this_state)
        await exoyone.toggle_direction(next_state)
        assert exoyone.state.direction == next_state

    @pytest.mark.parametrize(
        "set_state, expected_state",
        [("on", True), ("off", False), (1, True), (0, False)],
    )
    async def test_mode_cycle(self, exoyone, set_state, expected_state):
        """Test direction."""
        await exoyone.toggle_mode_cycle(set_state)
        assert exoyone.state.autoChange == expected_state

    @pytest.mark.parametrize(
        "set_state, expected_state",
        [("on", True), ("off", False), (1, True), (0, False)],
    )
    async def test_music_sync(self, exoyone, set_state, expected_state):
        """Test direction."""
        await exoyone.toggle_music_sync(set_state)
        assert exoyone.state.musicSync == expected_state

    @pytest.mark.parametrize(
        "set_state, expected_state",
        [("on", True), ("off", False), (1, True), (0, False)],
    )
    async def test_scene_generation(self, exoyone, set_state, expected_state):
        """Test direction."""
        await exoyone.toggle_scene_generation(set_state)
        assert exoyone.state.sceneGeneration == expected_state

    @pytest.mark.parametrize(
        "set_state, expected_state",
        [("on", True), ("off", False), (1, True), (0, False)],
    )
    async def test_powered_by_powerbank(self, exoyone, set_state, expected_state):
        """Test direction."""
        await exoyone.powered_by_powerbank(set_state)
        assert exoyone.state.poweredByPowerbank == expected_state

    @pytest.mark.parametrize("word,expected", word_test_params)
    async def test_truthy_falsy_words(self, exoyone, word, expected):
        """Test all the truthy and falsy words."""
        await exoyone.toggle_power(word)
        assert exoyone.state.fadingOff is expected

    async def test_invalid_truthy_falsy_word(self, exoyone):
        """Test invalid truthy and falsy word."""
        with pytest.raises(ExoyOneValueError):
            await exoyone.toggle_power("east")

    async def test_set_color(self, exoyone):
        """Test setting hue, saturation and brightness."""
        old_hue = exoyone.state.hue
        old_sat = exoyone.state.saturation
        old_bri = exoyone.state.brightness
        new_hue = random.randint(0, 255)
        new_sat = random.randint(0, 255)
        new_bri = random.randint(0, 255)
        await exoyone.set_color((new_hue, new_sat, new_bri))

        assert exoyone.state.hue == new_hue
        assert exoyone.state.saturation == new_sat
        assert exoyone.state.brightness == new_bri

        await exoyone.set_hue(old_hue)
        assert exoyone.state.hue == old_hue

        await exoyone.set_saturation(old_sat)
        assert exoyone.state.saturation == old_sat

        await exoyone.set_brightness(old_bri)
        assert exoyone.state.brightness == old_bri

    async def test_set_speed(self, exoyone):
        """Test setting effect speed."""
        new_speed = random.randint(0, 255)
        await exoyone.set_speed(new_speed)
        assert exoyone.state.speed == new_speed

    async def test_set_cycle_speed(self, exoyone):
        """Test setting mode cycle speed."""
        new_cycle_speed = random.randint(0, 255)
        await exoyone.set_cycle_speed(new_cycle_speed)
        assert exoyone.state.cycleSpeed == new_cycle_speed

    @pytest.mark.parametrize(
        "effect,expected_pn,expected_pi,expected_ei", effect_test_params
    )
    async def test_set_effect(
        self, exoyone, effect, expected_pn, expected_pi, expected_ei
    ):
        """Test setting effect."""
        pi, ei = mp.get_indices_from_effect_name(effect)
        en = mp.get_effect_name_from_index(pi, ei)

        await exoyone.set_effect(en)
        assert exoyone.state.currentModpack == expected_pi
        assert exoyone.state.modeIndex == expected_ei

        await exoyone.set_effect((pi, ei))

        assert exoyone.state.currentModpack == expected_pi
        assert exoyone.state.modeIndex == expected_ei

        assert exoyone.get_active_pack_name() == expected_pn
        assert exoyone.get_active_effect() == en

    async def test_invalid_effect_name(self, exoyone):
        """Test invalid effect name."""
        mode_pack = exoyone.get_active_pack_name()
        effect = exoyone.get_active_effect()

        invalid_pack_name = "Invalid Pack"
        invalid_effect_name = "Invalid Effect"

        assert mp.pack_names.find(invalid_pack_name) == -1
        assert mp.effect_names.find(invalid_effect_name) == -1
        assert mp.get_pack_index_from_name(invalid_pack_name) == -1
        assert mp.get_effect_index_from_name("Mood", invalid_effect_name) == -1
        assert mp.get_effect_index_from_name(invalid_pack_name, "Whisper") == -1
        assert (
            mp.get_effect_index_from_name(invalid_pack_name, invalid_effect_name) == -1
        )

        await exoyone.set_effect(invalid_effect_name)

        assert exoyone.state.currentModpack == mp.get_pack_index_from_name(mode_pack)
        assert exoyone.state.modeIndex == mp.get_effect_index_from_name(
            mode_pack, effect
        )

    async def test_set_shutdown_timer(self, exoyone):
        """Test setting shutdown timer."""
        minutes = 30
        await exoyone.set_shutdown_timer(minutes)
        assert exoyone.state.shutdownTimer == 1800

        minutes = 3
        await exoyone.set_shutdown_timer(minutes)
        assert exoyone.state.shutdownTimer == 300

        minutes = 500
        await exoyone.set_shutdown_timer(minutes)
        assert exoyone.state.shutdownTimer == 28800

        minutes = 0
        await exoyone.set_shutdown_timer(minutes)
        assert exoyone.state.shutdownTimer == 0

    async def test_connect_to_wifi(self, exoyone):
        """Test connecting to Wi-Fi."""
        with pytest.raises(ExoyOneValueError):
            ssid = ""
            pswd = ""
            await exoyone.connect_to_wifi(ssid, pswd)

        with pytest.raises(ExoyOneValueError):
            ssid = "This SSID is too long for the ExoyOne"
            pswd = "password"
            await exoyone.connect_to_wifi(ssid, pswd)

        with pytest.raises(ExoyOneValueError):
            ssid = "WiFi SSID"
            pswd = "This password is too long for the ExoyOne"
            await exoyone.connect_to_wifi(ssid, pswd)

        ssid = "WiFi SSID"
        pswd = "WiFi Password"
        await exoyone.connect_to_wifi(ssid, pswd)

    async def test_restart_in_ap_mode(self, exoyone):
        """Test restarting in AP mode."""
        await exoyone.restart_in_ap_mode()

    async def test_experimental_settings(self, exoyone):
        """Test experimental settings."""
        new_pattern = random.randint(0, 255)
        await exoyone.set_pattern(new_pattern)
        assert exoyone.state.selectedPattern == new_pattern

        new_palette = random.randint(0, 255)
        await exoyone.set_palette(new_palette)
        assert exoyone.state.selectedPalette == new_palette

        new_render_mode = random.randint(0, 255)
        await exoyone.set_render_mode(new_render_mode)
        assert exoyone.state.selectedRenderMode == new_render_mode

        new_color_mode = random.randint(0, 255)
        await exoyone.set_color_mode(new_color_mode)
        assert exoyone.state.selectedColorMode == new_color_mode
