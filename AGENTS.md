# AGENTS.md - Minesweeper Solver

Guidelines for AI agents working on this codebase.

## Quick Start with Poetry

This project uses [Poetry](https://python-poetry.org/) for dependency management and task automation.

### Setup

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3-

# Install dependencies
poetry install

# Activate shell
poetry shell
```

### Running Tasks

Use `poetry poe <task>` to run development tasks (defined in `pyproject.toml`):

```bash
# Show all available tasks
poetry poe help

# Run tests
poetry poe test
poetry poe test-unit
poetry poe test-ui
poetry poe test-cov

# Code quality
poetry poe format
poetry poe lint
poetry poe fix

# Security and spelling
poetry poe security
poetry poe spelling

# CI pipeline
poetry poe ci

# Run application
poetry poe run
poetry poe example
```

## Commands (Manual)

### Testing (Single Test)
```bash
# Run all tests
poetry run pytest tests/ -v
poetry run pytest tests_ui/ -v

# Run single test file
poetry run pytest tests/test_minesweeper_solver.py -v
poetry run pytest tests_ui/integration/test_board_editor.py -v

# Run single test class
poetry run pytest tests/test_minesweeper_solver.py::TestMinesweeperSolver -v

# Run single test method
poetry run pytest tests/test_minesweeper_solver.py::TestMinesweeperSolver::test_solver_basic_mine -v

# Run tests matching pattern
poetry run pytest tests/ -k "stress" -v

# Run with coverage
poetry run pytest tests/ --cov=src --cov-report=html

# Run UI tests headless
HEADLESS=true poetry run pytest tests_ui/ -v
```

### Linting & Formatting
```bash
# Format with Black
poetry run black src/ ui/ tests/ tests_ui/ example.py main.py

# Check with Black
poetry run black --check src/ ui/ tests/ tests_ui/ example.py main.py

# Run Ruff with auto-fix
poetry run ruff check --fix src/ ui/ tests/ tests_ui/ example.py main.py

# Check Ruff
poetry run ruff check src/ ui/ tests/ tests_ui/ example.py main.py

# Run all checks
poetry poe lint
```

### Pre-commit & Application
```bash
# Install hooks
poetry run pre-commit install

# Run on all files
poetry run pre-commit run --all-files

# Run CLI examples
poetry run python example.py

# Run GUI
poetry run python main.py
```

## Code Style Guidelines

### General
- **Python Version**: 3.11+ (uses modern typing features)
- **Line Length**: 88 characters (Black default)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings

### Imports
```python
from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

# Use modern built-in generics
def process(items: list[str]) -> dict[str, int]: ...
```

### Type Hints
- Use type hints for all function signatures
- Use `X | None` for nullable types (Python 3.11+)
- Use built-in generics: `list[X]`, `dict[X, Y]`
- Return type `-> None` for procedures

```python
def solve(self, board: MinesweeperBoard) -> SolverResult:
    """Solve the board and return results."""
    ...

def find_safe(self, cells: list[Position]) -> set[Position]:
    """Find safe cells."""
    ...
```

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `MinesweeperSolver`)
- **Functions/Methods**: `snake_case` (e.g., `solve_board`)
- **Variables**: `snake_case` (e.g., `mine_count`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_DEPTH`)
- **Private**: Prefix with underscore `_private_method`

### Documentation
```python
def analyze_move(self, board: Board, pos: Position) -> str:
    """Analyze a move and return feedback.
    
    Args:
        board: Current board state
        pos: Position that was clicked
        
    Returns:
        Analysis message explaining the move quality
        
    Raises:
        ValueError: If position is out of bounds
    """
    ...
```

### Error Handling
- Use specific exceptions, never bare `except:`
- Provide informative error messages
- Handle edge cases explicitly

```python
def set_cell(self, pos: Position, state: CellState) -> None:
    if not (0 <= pos.row < self.rows and 0 <= pos.col < self.cols):
        raise ValueError(f"Position {pos} out of bounds")
    self.grid[pos.row][pos.col] = state
```

### Dataclasses
```python
@dataclass(frozen=True)
class Position:
    row: int
    col: int

@dataclass
class SolverResult:
    safe_cells: set[Position] = field(default_factory=set)
```

### Testing
- Use `unittest` framework with `pytest` runner
- Test class names: `TestPascalCase`
- Test method names: `test_snake_case_descriptive`
- One assertion per test or group related assertions

```python
class TestMinesweeperSolver(unittest.TestCase):
    def test_solver_finds_guaranteed_mines(self):
        """Test solver correctly identifies cells that must be mines."""
        board = create_test_board()
        result = self.solver.solve(board)
        self.assertIn(Position(0, 1), result.mines)
```

### Code Organization
- One class per logical unit
- Keep methods focused and under 50 lines
- Group related methods together
- Extract complex logic into helper methods

## Project Structure

```
mine-sweeper-solver/
├── src/minesweeper_solver/  # Main solver implementation
├── ui/                       # GUI (tkinter)
├── tests/                    # Unit tests
├── tests_ui/                 # UI integration tests
├── example.py               # Usage examples
├── main.py                  # Entry point
└── pyproject.toml          # Project config (Poetry)
```

## Pre-commit Checklist

Before finishing:
1. Run tests: `poetry poe test`
2. Format code: `poetry poe format`
3. Check linting: `poetry poe lint`
4. Run example: `poetry poe example`
5. Test GUI if changed: `poetry poe run`

## Key Design Principles

1. **Immutability**: Use frozen dataclasses for positions, constraints
2. **Type Safety**: All public APIs must be typed
3. **Standard Library**: Prefer stdlib over external dependencies
4. **Test Coverage**: All code paths must be testable
5. **Clear Documentation**: Every public class/function needs docstrings
6. **Code Quality**: All code must pass Black and Ruff checks
