# CLI Reference

This page provides documentation for the `exoyone` command line tool.

## Usage

```console
exoyone [OPTIONS] COMMAND [ARGS]...
```

## Commands

| Command | Description                        |
| ------- | ---------------------------------- |
| `get`   | Get information from your ExoyOne. |
| `set`   | Change things on your ExoyOne.     |

## Global Options

| Option   | Description                     |
| -------- | ------------------------------- |
| `--help` | Show the help message and exit. |

## `exoyone get`

Get information from your ExoyOne. This includes the current state of the device,
including power, color, effects, and more.

```console
exoyone get --host HOST COMMAND [ARGS]...
```

| Option         | Description                                                                  |
| -------------- | ---------------------------------------------------------------------------- |
| `--host`, `-H` | Hostname or IP address of your ExoyOne. Can also be set with `EXOYONE_HOST`. |
| `--help`       | Show the help message and exit.                                              |

| Command            | Description                                                          |
| ------------------ | -------------------------------------------------------------------- |
| `color`            | Get the current hue, saturation and brightness values.               |
| `cycle-speed`      | Get the current mode cycle speed.                                    |
| `device-name`      | Get the device name.                                                 |
| `direction`        | Get the effect direction (left/right).                               |
| `effect-speed`     | Get the current effect speed.                                        |
| `effects`          | Get a list of effects for the specified mode pack or all mode packs. |
| `everything`       | Get the state and value of all the things.                           |
| `mode-cycle`       | Get mode cycle state (on/off).                                       |
| `music-sync`       | Get music sync state (on/off).                                       |
| `power-state`      | Get the power state (on/off).                                        |
| `powerbank-mode`   | Get powered by powerbank state (on/off).                             |
| `scene-generation` | Get scene generation state (on/off).                                 |
| `shutdown-timer`   | Get the current shutdown timer.                                      |

## `exoyone set`

Change things on your ExoyOne. This includes turning it on or off, changing the
color, effect, and more.

```console
exoyone set --host HOST COMMAND [ARGS]...
```

| Option         | Description                                                                  |
| -------------- | ---------------------------------------------------------------------------- |
| `--host`, `-H` | Hostname or IP address of your ExoyOne. Can also be set with `EXOYONE_HOST`. |
| `--help`       | Show the help message and exit.                                              |

| Command                    | Description                                                   |
| -------------------------- | ------------------------------------------------------------- |
| `color HUE SAT BRI`        | Set the color by changing the hue, saturation and brightness. |
| `cycle-speed SECONDS`      | Set the mode cycle duration in seconds.                       |
| `device-name NAME`         | Set the device name of the ExoyOne.                           |
| `direction DIRECTION`      | Set a direction for the active effect.                        |
| `effect EFFECT`            | Change the active effect.                                     |
| `effect-speed SPEED`       | Set the speed of the effect.                                  |
| `mode-cycle off\|on`       | Turn mode cycle off or on.                                    |
| `music-sync off\|on`       | Turn music sync on or off.                                    |
| `power-state off\|on`      | Turn power state on or off.                                   |
| `powerbank-mode off\|on`   | Turn powered by powerbank mode on or off.                     |
| `restart-in-ap-mode`       | Restart the ExoyOne to enable Wi-Fi access point.             |
| `scene-generation off\|on` | Turn scene generation off or on.                              |
| `shutdown-timer MINUTES`   | Set the shutdown timer duration.                              |
