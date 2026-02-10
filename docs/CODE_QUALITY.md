# Code Quality Tools - Black & Ruff

Enterprise-grade linting and formatting configuration for the Minesweeper Solver project.

## Overview

This project uses two complementary tools for code quality:

- **Black** - The uncompromising code formatter
- **Ruff** - An extremely fast Python linter and code checker

Both are configured for Python 3.11+ with enterprise-grade settings for scalability and maintainability.

## Features

- **Consistent formatting** with Black (88 character line length)
- **Comprehensive linting** with Ruff (700+ rules enabled)
- **Automatic import sorting** with Ruff isort
- **Pre-commit hooks** to catch issues before commits
- **Cross-platform** helper scripts (Windows & Unix)
- **CI/CD ready** with strict quality gates

## Installation

### Install Dependencies

```bash
# Using pip
pip install black ruff pre-commit

# Or install all dev dependencies
pip install -e ".[dev]"

# Or using the requirements file
pip install -r requirements-dev.txt
```

### Install Pre-commit Hooks

```bash
# Using the helper script (Unix/Linux/macOS)
./scripts/lint.sh install

# Or on Windows
scripts\lint.bat install

# Or manually
pre-commit install
```

## Quick Start

### Using Helper Scripts

#### Unix/Linux/macOS

```bash
# Run all checks and fixes (recommended)
./scripts/lint.sh all

# Check code without changes
./scripts/lint.sh check

# Format code
./scripts/lint.sh format

# Fix with Ruff + format with Black
./scripts/lint.sh fix
```

#### Windows

```batch
# Run all checks and fixes (recommended)
scripts\lint.bat all

# Check code without changes
scripts\lint.bat check

# Format code
scripts\lint.bat format

# Fix with Ruff + format with Black
scripts\lint.bat fix
```

### Using Tools Directly

#### Black

```bash
# Format all code
black src/ ui/ tests/ tests_ui/ example.py main.py

# Check formatting without changes
black --check src/ ui/ tests/ tests_ui/ example.py main.py

# Show diff
black --diff src/ ui/ tests/ tests_ui/ example.py main.py
```

#### Ruff

```bash
# Check code
ruff check src/ ui/ tests/ tests_ui/ example.py main.py

# Check with auto-fix
ruff check --fix src/ ui/ tests/ tests_ui/ example.py main.py

# Check specific rules
ruff check --select E,W,F src/ ui/ tests/
```

## Configuration

### Black Configuration (`pyproject.toml`)

```toml
[tool.black]
target-version = ["py311", "py312"]
line-length = 88
include = '\.pyi?$'
exclude = '''
/(
    \.eggs
    | \.git
    | \.venv
    | build
    | dist
)/
'''
```

### Ruff Configuration (`pyproject.toml`)

```toml
[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = [
    "F",    # Pyflakes
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "SIM",  # flake8-simplify
    "PTH",  # flake8-use-pathlib
    "RUF",  # Ruff-specific rules
]

[tool.ruff.lint.isort]
profile = "black"
known-first-party = ["minesweeper_solver", "ui", "tests", "tests_ui"]
```

## Pre-commit Hooks

### Available Hooks

1. **General Checks**
   - `check-ast` - Validate Python syntax
   - `check-json` - Validate JSON syntax
   - `check-yaml` - Validate YAML syntax
   - `check-toml` - Validate TOML syntax
   - `check-merge-conflict` - Detect merge conflicts
   - `debug-statements` - Detect debugger calls
   - `detect-private-key` - Detect private keys

2. **Code Quality**
   - `black` - Format Python code
   - `black-jupyter` - Format Jupyter notebooks
   - `ruff` - Lint Python code with auto-fix
   - `ruff-format` - Additional formatting checks

3. **Additional Checks**
   - `bandit` - Security checks
   - `pyupgrade` - Python upgrade checks
   - `codespell` - Spell checking

### Running Hooks

```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Run without installing
pre-commit run --all-files --hook-stage pre-commit
```

## Code Quality Rules

### Ruff Rules Enabled

The configuration enables 700+ rules across these categories:

- **F** - Pyflakes (syntax errors, undefined names)
- **E/W** - pycodestyle (PEP 8 style)
- **I** - isort (import sorting)
- **N** - pep8-naming (naming conventions)
- **UP** - pyupgrade (Python upgrade)
- **B** - flake8-bugbear (likely bugs)
- **C4** - flake8-comprehensions (unnecessary comprehensions)
- **SIM** - flake8-simplify (code simplification)
- **PTH** - flake8-use-pathlib (pathlib usage)
- **S** - bandit (security)
- **PL** - Pylint (various checks)
- **RUF** - Ruff-specific rules

### Relaxed Rules for Tests

Test files have relaxed rules:
- Allow `assert` statements (needed for pytest)
- Allow missing type annotations
- Allow missing docstrings
- Allow magic values

## Workflow Integration

### Git Workflow

```bash
# Before committing
git add <files>

# Pre-commit hooks run automatically
# If they fail, fix issues and re-add

# Manual check
./scripts/lint.sh check

# Or fix automatically
./scripts/lint.sh all
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install black ruff
      - run: black --check .
      - run: ruff check .
```

## Common Issues

### Black and Ruff Conflict

Both are configured with:
- Line length: 88 characters
- Target Python: 3.11+
- Black-compatible isort profile

### Import Sorting

Imports are automatically sorted by Ruff isort:
1. Future imports
2. Standard library
3. Third-party
4. First-party (project modules)
5. Local imports

### Ignoring Rules

```python
# Ignore a specific line
x = 1  # noqa: E501

# Ignore multiple rules
x = 1  # noqa: E501, W503

# Ignore for entire file
# ruff: noqa: E501
```

## Best Practices

1. **Run before committing**: Use `./scripts/lint.sh all` or pre-commit hooks
2. **Fix automatically**: Most issues can be auto-fixed with `--fix`
3. **Check in CI**: Ensure quality gates in CI/CD pipeline
4. **Team consistency**: Everyone uses the same configuration
5. **Incremental adoption**: Run on new code first, then existing code

## IDE Integration

### VS Code

Install extensions:
- Python (Microsoft)
- Ruff (Astral Software)

Settings (`settings.json`):
```json
{
    "python.formatting.provider": "black",
    "python.linting.ruffEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll.ruff": true,
        "source.organizeImports.ruff": true
    }
}
```

### PyCharm

1. Install Black plugin
2. Configure external tools for Ruff
3. Enable "Reformat code" on save

## Troubleshooting

### "Black produced different code..."

Ruff and Black may conflict. Ensure both use same line length (88).

### Pre-commit hooks fail

Run manually to see errors:
```bash
pre-commit run --all-files --verbose
```

### Import sorting issues

Ruff handles imports. Ensure `profile = "black"` in config.

## Migration Guide

### From flake8/pylint

Replace with Ruff:
```bash
# Remove old tools
pip uninstall flake8 pylint

# Install Ruff
pip install ruff

# Most rules are equivalent
# See Ruff docs for rule mapping
```

### From autopep8/yapf

Replace with Black:
```bash
# Remove old formatters
pip uninstall autopep8 yapf

# Install Black
pip install black

# Black is opinionated, less configuration needed
```

## Resources

- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Ruff Rules Reference](https://docs.astral.sh/ruff/rules/)

## License

Same as main project.
