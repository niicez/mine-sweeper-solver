# Minesweeper UI Test Suite

Production-ready, enterprise-level UI testing strategy for the Minesweeper application's interactive GUI.

## Overview

This test suite provides comprehensive integration and end-to-end testing for the tkinter-based Minesweeper GUI, achieving 80-90% code coverage with automated UI interaction capabilities.

## Features

- **Comprehensive Coverage**: 80-90% code coverage targeting core functionality
- **Headless Execution**: CI/CD friendly with Xvfb support for Linux
- **Automated UI Interaction**: Direct widget manipulation for reliability
- **Clear Architecture**: Separation of test utilities, fixtures, and assertions
- **Cross-Platform**: Works on Linux, Windows, and macOS
- **Fast Execution**: Direct widget access instead of OS-level automation

## Quick Start

### Installation

```bash
# Install test dependencies
pip install -r requirements-ui-test.txt
```

### Running Tests

```bash
# Run all UI tests
pytest tests_ui/ -v

# Run with coverage report
pytest tests_ui/ -v --cov=ui --cov-report=term-missing --cov-fail-under=80

# Run specific test file
pytest tests_ui/integration/test_board_editor.py -v

# Run specific test class
pytest tests_ui/integration/test_board_editor.py::TestBoardCreation -v

# Run headless (for CI)
HEADLESS=true pytest tests_ui/ -v

# Run with timeout protection
pytest tests_ui/ --timeout=60
```

### Running Tests by Markers

```bash
# Run only integration tests
pytest tests_ui/ -m integration -v

# Run only E2E tests
pytest tests_ui/ -m e2e -v

# Skip slow tests
pytest tests_ui/ -m "not slow" -v

# Run GUI tests only
pytest tests_ui/ -m gui -v
```

## Test Structure

```
tests_ui/
├── conftest.py                 # Shared fixtures and configuration
├── utils/
│   ├── gui_automation.py      # GUI automation utilities
│   └── assertions.py          # Custom assertions
├── integration/
│   ├── test_board_editor.py   # Board creation and editing tests
│   ├── test_solver_ui.py      # Solver functionality tests
│   ├── test_tools.py          # Tool selection tests
│   └── test_import_export.py  # Import/export tests
└── e2e/
    └── test_user_workflows.py # Complete user workflows
```

## Test Categories

### Integration Tests

Test individual components and their interactions:

- **Board Editor**: Board creation, cell editing, clearing, dimensions
- **Solver UI**: Solver execution, results display, highlighting
- **Tools**: Tool selection, number values, tool switching
- **Import/Export**: String import/export, state preservation

### End-to-End Tests

Test complete user workflows:

- **User Workflows**: Complete scenarios from board creation to analysis
- **Error Recovery**: Recovery from errors and edge cases

## Key Components

### GUIAutomation

High-level interface for GUI interactions:

```python
from tests_ui.utils.gui_automation import GUIAutomation

automation = GUIAutomation()
automation.click_cell(app, 0, 0)
automation.select_tool(app, "mine")
automation.run_solver(app)
```

### Custom Assertions

Specialized assertions for GUI state validation:

```python
from tests_ui.utils.assertions import (
    assert_cell_is_mine,
    assert_solver_results_displayed,
    assert_board_dimensions,
)

assert_cell_is_mine(app, 0, 0)
assert_board_dimensions(app, 9, 9)
```

### Fixtures

Pre-configured test setups:

```python
def test_example(app):
    """Use the default app fixture."""
    assert app.rows == 10

def test_with_board(app_with_board):
    """Use pre-configured board."""
    # Board is ready for testing
    pass
```

## Configuration

### pytest.ini

Located in `tests_ui/pytest.ini`:

```ini
[pytest]
testpaths = tests_ui
markers =
    gui: GUI tests requiring display
    slow: Slow tests
    integration: Integration tests
    e2e: End-to-end tests
```

### Coverage

Configuration in `.coveragerc-ui`:

- Minimum coverage: 80%
- HTML reports: `htmlcov_ui/`
- XML reports: `coverage_ui.xml`

## CI/CD Integration

### GitHub Actions

Automatically runs on push/PR to main branches. See `.github/workflows/ui-tests.yml`.

Features:

- Multi-platform testing (Ubuntu, Windows, macOS)
- Python 3.9-3.12 support
- Coverage reporting to Codecov
- Quick smoke tests for faster feedback
- Lint and format checks

### Environment Variables

- `HEADLESS=true`: Run in headless mode
- `CI=true`: Indicates CI environment
- `PYTHONPATH`: Set to include src/ and ui/ directories

## Writing Tests

### Basic Test Structure

```python
def test_feature(self, app):
    """Test description."""
    automation = GUIAutomation()

    # Arrange
    automation.create_new_board(app, 9, 9, 10)

    # Act
    automation.set_cell_number(app, 0, 0, 1)

    # Assert
    assert_cell_is_number(app, 0, 0, 1)
```

### Using Fixtures

```python
def test_with_custom_board(app):
    """Test with fresh app instance."""
    automation = GUIAutomation()
    automation.create_new_board(app, 5, 5, 3)
    # Test with 5x5 board
```

### Adding Custom Assertions

```python
from tests_ui.utils.assertions import GUIAssertionError

def assert_custom_condition(app, msg=None):
    """Custom assertion example."""
    if not condition:
        raise GUIAssertionError(msg or "Custom condition failed")
```

## Best Practices

1. **One Concept Per Test**: Each test validates one specific behavior
2. **Use Automation Layer**: Don't interact with widgets directly
3. **Descriptive Names**: Test names explain what is validated
4. **Proper Cleanup**: Fixtures handle cleanup automatically
5. **Independent Tests**: No dependencies between tests
6. **Coverage Awareness**: Run coverage reports regularly

## Troubleshooting

### Display Issues

**Problem**: `No display available for GUI testing`

**Solution**:

- Linux: Install Xvfb (`sudo apt-get install xvfb`)
- Windows/macOS: Run in normal mode (not headless)

### Import Errors

**Problem**: `ImportError: cannot import name 'MinesweeperBoardEditor'`

**Solution**: Ensure PYTHONPATH includes src/ and ui/:

```bash
export PYTHONPATH="${PWD}/src:${PWD}/ui:$PYTHONPATH"
```

### Timeout Issues

**Problem**: Tests timeout unexpectedly

**Solution**: Increase timeout or check for infinite loops:

```bash
pytest tests_ui/ --timeout=120
```

## Coverage Report

Generate HTML coverage report:

```bash
pytest tests_ui/ --cov=ui --cov-report=html
open htmlcov_ui/index.html
```

## Contributing

When adding new tests:

1. Place in appropriate directory (integration/ or e2e/)
2. Use existing fixtures and automation utilities
3. Follow naming convention: `test_<feature>_<scenario>`
4. Add markers if needed (`@pytest.mark.slow`, etc.)
5. Verify coverage improvement
6. Update documentation

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

## License

Same as main project.
