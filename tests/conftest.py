"""Shared pytest configuration.

Tests must never read or write the real ``~/.gulfofmexico_runtime`` store, so
``GOM_HOME`` is redirected to a temporary directory for the whole session.
"""

from __future__ import annotations

import os
import tempfile

import pytest

_SESSION_HOME = tempfile.mkdtemp(prefix="gom-tests-")


@pytest.fixture(scope="session", autouse=True)
def _isolate_persistent_store() -> None:
    os.environ["GOM_HOME"] = _SESSION_HOME
    # Never import an old pickle store during tests.
    os.environ.pop("GOM_ALLOW_LEGACY_PICKLE", None)


@pytest.fixture()
def fresh_store(tmp_path, monkeypatch):
    """Point ``GOM_HOME`` at an empty directory for a single test."""
    monkeypatch.setenv("GOM_HOME", str(tmp_path))
    return tmp_path
