# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pyExoyOne is a Python library and CLI for configuring and controlling Exoy™ ONE lighting devices via UDP. It provides async device communication with auto-retry and exponential backoff.

## Commands

### Development Setup

```bash
uv sync --all-groups        # Install all dependencies
uv run pre-commit install   # Set up git hooks
```

### Testing

```bash
uv run pytest                              # Run all tests with coverage
uv run pytest tests/test_exoyone.py        # Run specific test file
uv run pytest -k test_state                # Run tests matching pattern
uv run moxyone serve                       # Run mock device server standalone
```

### Code Quality

```bash
uv run ruff check --fix    # Lint and auto-fix
uv run ruff format         # Format code
uv run ty check src tests  # Type checking
uv run pre-commit run -a   # Run all checks (ruff, ty, prettier, codespell)
```

### Documentation

```bash
uv sync --all-groups       # Install docs dependencies (included in all-groups)
uv run mkdocs serve        # Serve docs locally
```

## Architecture

```
src/exoyone/
├── exoyone.py      # Core ExoyOne class - async UDP communication with device
├── state.py        # ExoyOneState dataclass (26 fields for device state)
├── models.py       # Enums (ExoyDevices, TruthyFalsyWords), ModePacks, exceptions
└── cli/
    ├── cli.py      # Typer CLI app entry point (get/set subcommands)
    ├── get.py      # Get subcommands (state, effects, settings)
    ├── set.py      # Set subcommands (color, effect, brightness, power)
    └── helpers.py  # CLI utilities (progress bars, HSB-to-RGB conversion)

tests/
├── moxyone/        # Mock ExoyOne device (UDP server) - also installable as `moxyone` CLI
├── conftest.py     # Fixtures: exoyone (device), run_moxyone (xprocess test server)
└── test_*.py       # Test files
```

## Key Patterns

- **UDP protocol**: Default port 8888. JSON requests (e.g., `{"getData": 1}`) and JSON responses. State updates require `async_get_data()` call after `async_set_data()`.
- **Async operations**: All device methods are async using `asyncio_dgram` for UDP. Methods prefixed `async_*` for clarity.
- **Auto-retry**: `@backoff.on_exception` decorator with 3 tries and exponential backoff on `ExoyOneTimeoutError`.
- **Boolean values**: Methods accepting on/off state use `_bool_val()` which accepts `bool`, `int` (0/1), or string keywords (ON/OFF, YES/NO, TRUE/FALSE, etc. via `TruthyFalsyWords` enum).
- **HSB color model**: Hue, saturation, brightness values are 0-255 range.
- **Device limits**: Names max 39 chars, SSID/password max 31 chars, shutdown timer 5-480 minutes.

## Testing

Tests use pytest-xprocess to manage a `moxyone` mock UDP server. The `run_moxyone` fixture starts/stops the server at class scope. The `exoyone` fixture provides an `ExoyOne` instance connected to localhost.

## Commit Conventions

Uses Conventional Commits enforced by commitizen. Releases are automated via python-semantic-release on the main branch.

Format: `type(scope): description` (e.g., `feat(cli): add color command`)
