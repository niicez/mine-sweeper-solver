# AGENTS.md - Minesweeper Solver

Guidelines for AI agents working on this codebase.

## Commands

### Testing
```bash
# Run all tests
python -m pytest test_minesweeper_solver.py -v

# Run a single test class
python -m pytest test_minesweeper_solver.py::TestMinesweeperSolver -v

# Run a single test method
python -m pytest test_minesweeper_solver.py::TestMinesweeperSolver::test_solver_basic_mine -v

# Run tests matching a pattern
python -m pytest test_minesweeper_solver.py -k "stress" -v

# Run with coverage (if pytest-cov installed)
python -m pytest test_minesweeper_solver.py --cov=minesweeper_solver --cov-report=html
```

### Linting & Formatting
```bash
# Format with ruff (preferred)
ruff format minesweeper_solver.py test_minesweeper_solver.py example.py

# Check with ruff
ruff check minesweeper_solver.py test_minesweeper_solver.py example.py

# Fix auto-fixable issues
ruff check --fix minesweeper_solver.py test_minesweeper_solver.py example.py

# Alternative: Format with black
black minesweeper_solver.py test_minesweeper_solver.py example.py
```

### Running the Example
```bash
python example.py
```

## Code Style Guidelines

### General
- **Python Version**: 3.8+ (uses standard library only, no external dependencies)
- **Line Length**: 100 characters max
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings, single quotes acceptable for single characters

### Imports
```python
# Standard library imports grouped and sorted
from __future__ import annotations  # Always first

import itertools
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Tuple, Optional, FrozenSet

# No external dependencies allowed - use only standard library
```

### Type Hints
- Use type hints for all function signatures
- Use `Optional[X]` for nullable types (not `X | None` for Python 3.8 compatibility)
- Use built-in generics: `list[X]`, `dict[X, Y]` requires Python 3.9+, else use `List[X]`, `Dict[X, Y]`
- Return type `-> None` for procedures

```python
def solve(self, board: MinesweeperBoard) -> SolverResult:
    """Solve the board and return results."""
    ...

def get_number(self, pos: Position) -> int:
    """Get number value, -1 if not a number."""
    ...
```

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `MinesweeperSolver`, `CellState`)
- **Functions/Methods**: `snake_case` (e.g., `solve`, `get_number`)
- **Variables**: `snake_case` (e.g., `mine_count`, `safe_cells`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_COMBINATIONS`)
- **Private**: Prefix with underscore `_private_method`

### Documentation
```python
def function_name(param: str) -> int:
    """One-line description.
    
    More detailed explanation if needed.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When input is invalid
    """
    pass
```

### Error Handling
- Use specific exceptions, never bare `except:`
- Provide informative error messages
- Handle edge cases explicitly

```python
# Good
def set(self, pos: Position, state: CellState) -> None:
    if not (0 <= pos.row < self.rows and 0 <= pos.col < self.cols):
        raise ValueError(f"Position {pos} out of bounds")
    self.grid[pos.row][pos.col] = state
```

### Dataclasses
- Use `@dataclass(frozen=True)` for immutable value types
- Use `@dataclass` for mutable entities
- Use `field(default_factory=list)` for mutable defaults

```python
@dataclass(frozen=True)
class Position:
    row: int
    col: int

@dataclass
class SolverResult:
    safe_cells: Set[Position] = field(default_factory=set)
```

### Testing
- Use `unittest` framework with `pytest` runner
- Test class names: `TestPascalCase`
- Test method names: `test_snake_case_descriptive`
- One assertion per test, or group related assertions
- Use descriptive docstrings explaining what is tested

```python
class TestMinesweeperSolver(unittest.TestCase):
    def test_solver_finds_guaranteed_mines(self):
        """Test that solver correctly identifies cells that must be mines."""
        board = create_test_board()
        result = self.solver.solve(board)
        self.assertIn(Position(0, 1), result.mines)
```

### Code Organization
- One class per logical unit
- Keep methods focused and under 50 lines
- Group related methods together
- Extract complex logic into helper methods

### Performance
- Profile before optimizing
- Use generators for large data processing
- Prefer built-in functions over loops
- Document complexity in docstrings for algorithms

### Pre-commit Checklist
Before finishing:
1. Run tests: `python -m pytest test_minesweeper_solver.py -v`
2. Format code: `ruff format .` or `black .`
3. Check for errors: `ruff check .`
4. Verify type safety (if using mypy): `mypy minesweeper_solver.py`
5. Run example to verify it works: `python example.py`

## Project Structure

```
mine-sweeper-solver/
├── minesweeper_solver.py    # Main solver implementation
├── test_minesweeper_solver.py  # Comprehensive test suite
├── example.py               # Usage examples and demo
├── README.md               # User documentation
└── AGENTS.md              # This file - developer guidelines
```

## Key Design Principles

1. **Immutability**: Use frozen dataclasses for positions, constraints
2. **Type Safety**: All public APIs must be typed
3. **No External Dependencies**: Standard library only
4. **Test Coverage**: All code paths must be testable
5. **Clear Documentation**: Every public class/function needs docstrings
