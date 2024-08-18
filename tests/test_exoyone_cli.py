"""Test ExoyOne CLI."""

import random

import pytest
from typer.testing import CliRunner

from exoyone.cli import app
from exoyone.models import mode_packs

runner = CliRunner()
mp = mode_packs

pack_effects_params: list[tuple[str, list[str]]] = []
for pack_name in mp.mode_packs:
    pack_effects_params.append(
        (pack_name, mp.get_effects_by_index(mp.get_pack_index_from_name(pack_name)))
    )

set_effects_params: list[tuple[str, str]] = []
for effect_name in mp.effects:
    pack_index, effect_index = mp.get_indices_from_effect_name(effect_name)
    pack_name = mp.get_pack_name_from_index(pack_index)
    set_effects_params.append((effect_name, pack_name))

toggle_states: list[tuple[str, str]] = [
    ("power-state", "Power state"),
    ("music-sync", "Music sync"),
    ("scene-generation", "Scene generation"),
    ("powerbank-mode", "Powered by powerbank mode"),
    ("mode-cycle", "Mode cycle"),
]

direction_states: list[tuple[str, bool]] = [
    ("left", True),
    ("in", True),
    ("up", True),
    ("forwards", True),
    ("clockwise", True),
    ("right", False),
    ("out", False),
    ("down", False),
    ("backwards", False),
    ("counterclockwise", False),
]
random.shuffle(direction_states)


@pytest.mark.usefixtures("set_host_envvar", "run_moxyone")
class TestExoyOneCli:
    """Test the ExoyOne CLI."""

    @pytest.mark.parametrize("set_host_envvar", ["override"])
    def test_exoyone_cli_no_envvar(self, set_host_envvar):
        """Test ExoyOne CLI without the environment variable."""
        result = runner.invoke(app, ["get"])
        assert result.exit_code == 0

        result = runner.invoke(app, ["get", "--help"])
        assert result.exit_code == 0

        result = runner.invoke(app, ["set"])
        assert result.exit_code == 0

        result = runner.invoke(app, ["set", "--help"])
        assert result.exit_code == 0

    def test_exoyone_cli(self):
        """Test invoking the CLI."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "ExoyOne Command-Line Interface" in result.stdout

    def test_get(self):
        """Test invoking the get command without parameters."""
        result = runner.invoke(app, ["get"])
        assert result.exit_code == 0
        assert "Get information from your ExoyOne" in result.stdout

    def test_get_help(self):
        """Test invoking the get command with the --help option."""
        result = runner.invoke(app, ["get", "--help"])
        assert result.exit_code == 0
        assert "Get information from your ExoyOne" in result.stdout

    def test_set(self):
        """Test invoking the set command without parameters."""
        result = runner.invoke(app, ["set"])
        assert result.exit_code == 0
        assert "Change things on your ExoyOne" in result.stdout

    def test_set_help(self):
        """Test invoking the get command with the --help option."""
        result = runner.invoke(app, ["set", "--help"])
        assert result.exit_code == 0
        assert "Change things on your ExoyOne" in result.stdout

    def test_get_device_name_unset(self):
        """Test invoking the get device-name command with no custom name."""
        result = runner.invoke(app, ["get", "device-name"])
        assert result.exit_code == 0
        assert "Device name: Unset" in result.stdout
        assert "mDNS address: exoyone" in result.stdout

    def test_set_device_name(self):
        """Test invoking the set-device name command."""
        result = runner.invoke(app, ["set", "device-name", "TestExoyOne"])
        assert result.exit_code == 0
        assert "Setting device name to TestExoyOne: DONE" in result.stdout

    def test_get_device_name(self):
        """Test invoking the get device-name command after configuring a custom name."""
        result = runner.invoke(app, ["get", "device-name"])
        assert result.exit_code == 0
        assert "Device name: TestExoyOne" in result.stdout
        assert "mDNS address: exoyone" in result.stdout

    def test_set_shutdown_timer(self):
        """Test invoking the set shutdown-timer command."""
        result = runner.invoke(app, ["set", "shutdown-timer", "120"])
        assert result.exit_code == 0
        assert "Setting shutdown timer to 120 minutes: DONE" in result.stdout

    def test_get_shutdown_timer(self):
        """Test invoking the get shutdown-timer command."""
        result = runner.invoke(app, ["get", "shutdown-timer"])
        assert result.exit_code == 0
        assert "Shutdown timer: 120 minutes" in result.stdout

    def test_set_get_shutdown_timer_off(self):
        """Test invoking the set shutdown-timer command with 0."""
        result = runner.invoke(app, ["set", "shutdown-timer", "0"])
        assert result.exit_code == 0
        assert "Disabling the shutdown timer: DONE" in result.stdout
        result = runner.invoke(app, ["get", "shutdown-timer"])
        assert result.exit_code == 0
        assert "Shutdown timer: Disabled" in result.stdout

    def test_restart_in_ap_mode(self):
        """Test invoking the set restart-in-ap-mode command."""
        result = runner.invoke(app, ["set", "restart-in-ap-mode"])
        assert result.exit_code == 0

    def test_set_cycle_speed(self):
        """Test invoking the set cycle-speed command."""
        result = runner.invoke(app, ["set", "cycle-speed", "30"])
        assert result.exit_code == 0
        assert "Setting mode cycle speed to 30 seconds: DONE" in result.stdout

    def test_get_cycle_speed(self):
        """Test invoking the get cycle-speed command."""
        result = runner.invoke(app, ["get", "cycle-speed"])
        assert result.exit_code == 0
        assert "Current mode cycle speed: 30" in result.stdout

    @pytest.mark.parametrize("direction, state", direction_states)
    def test_set_get_direction(self, direction, state):
        """Test invoking the set and get direction commands."""
        result = runner.invoke(app, ["set", "direction", direction])
        assert result.exit_code == 0
        assert f"Setting effect direction to {direction.title()}: DONE" in result.stdout

        result = runner.invoke(app, ["get", "direction"])
        assert result.exit_code == 0
        if state is True:
            state_direction = "LEFT"
        else:
            state_direction = "RIGHT"
        assert f"Effect direction: {state_direction}" in result.stdout

    def test_get_effects(self):
        """Test invoking the get effects command."""
        result = runner.invoke(app, ["get", "effects"])
        assert result.exit_code == 0
        for effect in mp.effects:
            assert effect in result.stdout

    def test_get_effects_invalid_mode_pack(self):
        """Test invoking the get effects command with an invalid mode pack."""
        result = runner.invoke(
            app, ["get", "effects", "--mode-pack", "invalid_mode_pack"]
        )
        assert result.exit_code == 2
        assert "Invalid mode pack" in result.stdout

    @pytest.mark.parametrize("mode_pack, effects", pack_effects_params)
    def test_get_effects_for_mode_pack(self, mode_pack, effects):
        """Test invoking the get effects command with a pack."""
        result = runner.invoke(app, ["get", "effects", "--mode-pack", mode_pack])
        assert result.exit_code == 0
        for effect in effects:
            assert effect in result.stdout

    @pytest.mark.parametrize("effect, mode_pack", set_effects_params)
    def test_set_effect_by_name(self, exoyone, effect, mode_pack):
        """Test invoking the set effect command."""
        result = runner.invoke(app, ["set", "effect", effect])
        assert result.exit_code == 0
        assert (
            f"Changing mode pack to {mode_pack} and effect to {effect}: DONE"
            in result.stdout
        )

    def test_set_effect_invalid_effect(self):
        """Test invoking the set effect command with an invalid effect."""
        result = runner.invoke(app, ["set", "effect", "invalid_effect"])
        assert result.exit_code == 2
        assert "Invalid value for '[EFFECT]'" in result.stdout

    def test_set_effect_no_effect(self):
        """Test invoking the set effect command without an effect."""
        result = runner.invoke(app, ["set", "effect"])
        assert result.exit_code == 2
        assert "Missing argument '[EFFECT]'" in result.stdout

    def test_set_effect_speed(self):
        """Test invoking the set speed command."""
        result = runner.invoke(app, ["set", "effect-speed", "30"])
        assert result.exit_code == 0
        assert "Setting effect speed to 30: DONE" in result.stdout

    def test_get_effect_speed(self):
        """Test invoking the get speed command."""
        result = runner.invoke(app, ["get", "effect-speed"])
        assert result.exit_code == 0
        assert "Current effect speed: 30" in result.stdout

    @pytest.mark.parametrize("state, str_state ", toggle_states)
    def test_set_get_toggle_states(self, state, str_state):
        """Test invoking the set and get toggle commands."""
        for set_state in ["on", "off"]:
            result = runner.invoke(
                app,
                ["set", state, set_state],
            )
            assert result.exit_code == 0
            assert (
                f"turning {str_state.lower()} {set_state.lower()}: done"
                in result.stdout.lower()
            )

            result = runner.invoke(app, ["get", state])
            assert result.exit_code == 0
            assert f"{str_state.lower()}: {set_state.lower()}" in result.stdout.lower()

    def test_set_get_color(self):
        """Test setting and getting color values."""
        hue = random.randint(0, 255)
        sat = random.randint(0, 255)
        bri = random.randint(0, 255)

        result = runner.invoke(app, ["set", "color", f"{hue}", f"{sat}", f"{bri}"])
        assert result.exit_code == 0
        assert f"Setting HSB to {hue}, {sat}, {bri}: DONE" in result.stdout

        result = runner.invoke(app, ["get", "color"])
        assert result.exit_code == 0
        assert f"HSB: {hue:>3}, {sat:>3}, {bri:>3}" in result.stdout

    def test_get_everything(self):
        """Test invoking the get everything command."""
        result = runner.invoke(app, ["get", "everything"])
        assert result.exit_code == 0

        runner.invoke(app, ["set", "shutdown-timer", "30"])
        runner.invoke(app, ["set", "mode-cycle", "on"])

        result = runner.invoke(app, ["get", "everything"])
        assert result.exit_code == 0
