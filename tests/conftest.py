"""Pytest configuration and fixtures."""

import pytest

from uuid_forge.core import IDConfig


@pytest.fixture
def test_config() -> IDConfig:
    """Fixture providing test configuration."""
    return IDConfig(salt="test-salt-fixture")


@pytest.fixture
def prod_config() -> IDConfig:
    """Fixture providing production-like configuration."""
    return IDConfig(salt="production-secret-salt-do-not-use-in-real-prod")
