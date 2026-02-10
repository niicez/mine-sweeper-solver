"""
Minesweeper Solver - Scalable Project Structure

This is a refactored version of the Minesweeper Solver with improved
organization for scalability and maintainability.

Project Structure:
    src/minesweeper_solver/  - Core solver library
    ui/                       - Tkinter GUI interface
    tests/                    - Comprehensive test suite
    docs/                     - Documentation
    assets/icons/            - Icon resources

Usage:
    # Run the GUI
    python -m ui

    # Run tests
    python -m pytest tests/ -v

    # Use as library
    from src.minesweeper_solver import MinesweeperSolver, MinesweeperBoard
"""

__version__ = "2.0.0"
__author__ = "Minesweeper Solver Team"
