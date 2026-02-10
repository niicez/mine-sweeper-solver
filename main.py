#!/usr/bin/env python3
"""
Minesweeper Solver - Main Entry Point

Easy launcher for the Minesweeper Board Editor GUI.

Usage:
    python main.py
    python main.py --cli       # Run CLI examples only
    python main.py --test      # Run tests
"""

import sys
import argparse


def run_gui():
    """Launch the GUI board editor."""
    sys.path.insert(0, "src")
    sys.path.insert(0, "ui")

    try:
        from ui import main as gui_main

        gui_main()
    except ImportError as e:
        print(f"Error launching GUI: {e}")
        print("Make sure tkinter is installed on your system.")
        sys.exit(1)


def run_cli():
    """Run CLI examples."""
    import example

    example.main()


def run_tests():
    """Run the test suite."""
    import subprocess

    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])
    sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(
        description="Minesweeper Solver - Board Editor and Solver"
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run CLI examples instead of GUI",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run test suite",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch GUI board editor (default)",
    )

    args = parser.parse_args()

    if args.test:
        run_tests()
    elif args.cli:
        run_cli()
    else:
        # Default to GUI
        run_gui()


if __name__ == "__main__":
    main()
