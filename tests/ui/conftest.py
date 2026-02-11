"""
Root conftest.py for UI tests.

This file contains session-wide fixtures and configuration for the UI test suite.
All fixtures here are available to all test files in the tests.ui directory.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Generator

import pytest

# Add source directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ui"))

# =============================================================================
# Session Configuration
# =============================================================================


def pytest_configure(config):
    """Configure pytest for UI testing."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "gui: marks tests as GUI tests (require display)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (longer execution time)"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end tests")
    config.addinivalue_line(
        "markers", "headless: marks tests that can run in headless mode"
    )


# =============================================================================
# Environment Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def is_headless() -> bool:
    """
    Check if tests are running in headless mode.

    Returns:
        True if HEADLESS or CI environment variable is set.
    """
    return bool(os.environ.get("HEADLESS") or os.environ.get("CI"))


@pytest.fixture(scope="session")
def display_available(is_headless: bool) -> bool:
    """
    Check if a display is available for GUI testing.

    In headless mode, this relies on Xvfb being available (handled by
    pytest-xvfb plugin). In non-headless mode, checks for DISPLAY env var.

    Args:
        is_headless: Whether running in headless mode

    Returns:
        True if display is available for GUI testing
    """
    if is_headless:
        # In CI/headless mode, Xvfb should provide a virtual display
        # pytest-xvfb handles this automatically
        return True
    else:
        # Check for actual display
        if sys.platform == "darwin":
            # macOS always has a display when not in CI
            return True
        elif sys.platform == "win32":
            # Windows always has a display when not in CI
            return True
        else:
            # Linux/Unix - check DISPLAY environment variable
            return bool(os.environ.get("DISPLAY"))


# =============================================================================
# GUI Lifecycle Fixtures
# =============================================================================


@pytest.fixture(scope="function")
def tk_root(display_available: bool) -> Generator[Any, None, None]:
    """
    Create a fresh Tk root window for each test.

    This fixture ensures each test starts with a clean GUI environment.
    The window is properly destroyed after each test to prevent resource leaks.

    Args:
        display_available: Ensures display is available before creating GUI

    Yields:
        Fresh Tk root window
    """
    if not display_available:
        pytest.skip("No display available for GUI testing")

    import tkinter as tk

    try:
        root = tk.Tk()
    except Exception as e:
        # Tcl/Tk not properly configured
        pytest.skip(f"Tcl/Tk not available: {e}")

    root.withdraw()  # Hide window during tests

    yield root

    # Cleanup
    try:
        root.destroy()
    except tk.TclError:
        pass  # Window already destroyed


@pytest.fixture(scope="function")
def app(tk_root: Any) -> Generator:
    """
    Create a fresh MinesweeperBoardEditor instance for each test.

    This is the main application fixture used by most UI tests.
    It provides a fully initialized GUI with default settings.

    Args:
        tk_root: Fresh Tk root window

    Yields:
        MinesweeperBoardEditor instance
    """
    from ui import MinesweeperBoardEditor

    application = MinesweeperBoardEditor(tk_root)

    # Process any pending events to ensure GUI is fully initialized
    tk_root.update_idletasks()

    yield application

    # Cleanup is handled by tk_root fixture


@pytest.fixture(scope="function")
def app_with_board(app) -> Generator:
    """
    Create an app with a pre-configured board for testing.

    This fixture creates a 10x10 board with 10 mines (beginner level).
    Useful for tests that need a consistent starting state.

    Args:
        app: Fresh MinesweeperBoardEditor instance

    Yields:
        MinesweeperBoardEditor with initialized board
    """
    # Board is already created by app's _create_new_board in __init__
    # Just ensure it's in a known state
    app._clear_board()
    app.root.update_idletasks()

    yield app


# =============================================================================
# Board State Fixtures
# =============================================================================


@pytest.fixture
def beginner_board_state():
    """
    Provide a beginner-level board state (9x9, 10 mines).

    Returns:
        Dictionary with board configuration
    """
    return {
        "rows": 9,
        "cols": 9,
        "total_mines": 10,
        "cell_size": 40,
    }


@pytest.fixture
def intermediate_board_state():
    """
    Provide an intermediate-level board state (16x16, 40 mines).

    Returns:
        Dictionary with board configuration
    """
    return {
        "rows": 16,
        "cols": 16,
        "total_mines": 40,
        "cell_size": 30,
    }


@pytest.fixture
def expert_board_state():
    """
    Provide an expert-level board state (30x16, 99 mines).

    Returns:
        Dictionary with board configuration
    """
    return {
        "rows": 30,
        "cols": 16,
        "total_mines": 99,
        "cell_size": 25,
    }


@pytest.fixture
def sample_board_string():
    """
    Provide a sample board string for import testing.

    Returns:
        String representation of a test board
    """
    return """
    12?
    ??X
    ???
    """


# =============================================================================
# Test Data Fixtures
# =============================================================================


@pytest.fixture
def cell_positions_3x3():
    """
    Provide all cell positions for a 3x3 board.

    Returns:
        List of (row, col) tuples
    """
    return [(r, c) for r in range(3) for c in range(3)]


@pytest.fixture
def corner_positions():
    """
    Provide corner positions for boundary testing.

    Returns:
        List of corner (row, col) tuples
    """
    return [
        (0, 0),  # Top-left
        (0, 8),  # Top-right (for 9x9)
        (8, 0),  # Bottom-left (for 9x9)
        (8, 8),  # Bottom-right (for 9x9)
    ]


@pytest.fixture
def edge_positions():
    """
    Provide edge positions for boundary testing.

    Returns:
        List of edge (row, col) tuples
    """
    return [
        (0, 4),  # Top edge
        (4, 0),  # Left edge
        (4, 8),  # Right edge
        (8, 4),  # Bottom edge
    ]


# =============================================================================
# Utility Fixtures
# =============================================================================


@pytest.fixture
def wait_for_idle(tk_root: Any):
    """
    Provide a function to wait for GUI to become idle.

    This is useful after async operations or state changes.

    Args:
        tk_root: Tk root window

    Returns:
        Function that waits for idle state
    """

    def _wait():
        tk_root.update_idletasks()
        tk_root.update()

    return _wait


@pytest.fixture
def process_events(tk_root: Any):
    """
    Provide a function to process pending GUI events.

    Args:
        tk_root: Tk root window

    Returns:
        Function that processes events
    """

    def _process(count: int = 1):
        for _ in range(count):
            tk_root.update_idletasks()

    return _process
