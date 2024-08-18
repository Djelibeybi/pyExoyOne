"""Test configuration for pyExoyOne."""

import sys
from collections.abc import AsyncGenerator
from typing import ClassVar

import pytest
import pytest_asyncio
from pytest_asyncio import is_async_test
from xprocess import ProcessStarter

from exoyone import ExoyOne


def pytest_collection_modifyitems(items):
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


@pytest_asyncio.fixture()
async def exoyone() -> AsyncGenerator[ExoyOne, None]:
    """Return an instance of ExoyOne."""
    exoyone = ExoyOne(host="127.0.0.1")
    await exoyone.async_get_data()
    yield exoyone


@pytest.fixture
def set_host_envvar(monkeypatch):
    """Mock the host environment variable."""
    monkeypatch.setenv("EXOYONE_HOST", "127.0.0.1")


@pytest.fixture(scope="class")
def run_moxyone(xprocess):
    """Start a MoxyOne instance."""
    exec_path = sys.executable

    class Starter(ProcessStarter):
        pattern = "MoxyOne started serving"
        args: ClassVar[list[str]] = [
            exec_path,
            "-u",
            "-m",
            "moxyone",
            "--debug",
            "serve",
        ]

    _ = xprocess.ensure("moxyone", Starter)
    yield

    xprocess.getinfo("moxyone").terminate()
