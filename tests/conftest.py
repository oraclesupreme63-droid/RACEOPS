"""Shared pytest configuration."""

import pytest


@pytest.fixture
def anyio_backend() -> str:
    """Use one deterministic async backend for HTTP contract tests."""
    return "asyncio"
