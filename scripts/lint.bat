@echo off
REM Linting and Formatting Scripts for Windows
REM Provides convenient commands for running Black and Ruff

echo ============================================================
echo Minesweeper Solver - Code Quality Tools
echo ============================================================
echo.

REM Check if command provided
if "%~1"=="" goto :help

REM Parse command
if /I "%~1"=="format" goto :format
if /I "%~1"=="check" goto :check
if /I "%~1"=="lint" goto :lint
if /I "%~1"=="fix" goto :fix
if /I "%~1"=="all" goto :all
if /I "%~1"=="install" goto :install
if /I "%~1"=="help" goto :help

echo Unknown command: %~1
goto :help

:format
    echo Formatting code with Black...
    black src/ ui/ tests/ tests_ui/ example.py main.py
    echo.
    echo Code formatted successfully!
    goto :eof

:check
    echo Checking code format with Black...
    black --check src/ ui/ tests/ tests_ui/ example.py main.py
    echo.
    echo Running Ruff checks...
    ruff check src/ ui/ tests/ tests_ui/ example.py main.py
    goto :eof

:lint
    echo Running Ruff linter with auto-fix...
    ruff check --fix src/ ui/ tests/ tests_ui/ example.py main.py
    echo.
    echo Linting complete!
    goto :eof

:fix
    echo Fixing code with Ruff and Black...
    ruff check --fix src/ ui/ tests/ tests_ui/ example.py main.py
    black src/ ui/ tests/ tests_ui/ example.py main.py
    echo.
    echo Code fixed successfully!
    goto :eof

:all
    echo Running all checks and fixes...
    echo.
    echo Step 1: Running Ruff with auto-fix...
    ruff check --fix src/ ui/ tests/ tests_ui/ example.py main.py
    echo.
    echo Step 2: Formatting with Black...
    black src/ ui/ tests/ tests_ui/ example.py main.py
    echo.
    echo Step 3: Running final checks...
    ruff check src/ ui/ tests/ tests_ui/ example.py main.py
    black --check src/ ui/ tests/ tests_ui/ example.py main.py
    echo.
    echo All checks complete!
    goto :eof

:install
    echo Installing pre-commit hooks...
    pre-commit install
    echo.
    echo Pre-commit hooks installed successfully!
    echo Run 'pre-commit run --all-files' to test hooks.
    goto :eof

:help
    echo Usage: lint.bat [command]
    echo.
    echo Commands:
    echo   format   Format code with Black
    echo   check    Check code format without making changes
    echo   lint     Run Ruff linter with auto-fix
    echo   fix      Fix code with both Ruff and Black
    echo   all      Run all checks and fixes (recommended)
    echo   install  Install pre-commit hooks
    echo   help     Show this help message
    echo.
    echo Examples:
    echo   lint.bat format    Format all code
    echo   lint.bat all       Run complete linting/formatting
    echo   lint.bat check     Check code before committing
    goto :eof
