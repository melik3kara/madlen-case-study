"""Test configuration for pytest."""

import pytest
import sys
import os

# Backend app'i import edebilmek için path'e ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def pytest_configure(config):
    """Configure pytest-asyncio mode."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
