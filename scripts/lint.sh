#!/bin/bash
#
# Linting and Formatting Scripts for Unix/Linux/macOS
# Provides convenient commands for running Black and Ruff
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE} Minesweeper Solver - Code Quality Tools${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Show help
show_help() {
    cat << EOF
Usage: ./lint.sh [command]

Commands:
  format   Format code with Black
  check    Check code format without making changes
  lint     Run Ruff linter with auto-fix
  fix      Fix code with both Ruff and Black
  all      Run all checks and fixes (recommended)
  install  Install pre-commit hooks
  update   Update pre-commit hooks
  clean    Clean cache files
  help     Show this help message

Examples:
  ./lint.sh format    Format all code
  ./lint.sh all       Run complete linting/formatting
  ./lint.sh check     Check code before committing
EOF
}

# Format code with Black
format_code() {
    print_info "Formatting code with Black..."
    black src/ ui/ tests/ tests_ui/ example.py main.py
    print_success "Code formatted successfully!"
}

# Check code format
check_code() {
    print_info "Checking code format with Black..."
    if black --check src/ ui/ tests/ tests_ui/ example.py main.py; then
        print_success "Black check passed!"
    else
        print_error "Black check failed! Run './lint.sh format' to fix."
        exit 1
    fi
    
    echo ""
    print_info "Running Ruff checks..."
    if ruff check src/ ui/ tests/ tests_ui/ example.py main.py; then
        print_success "Ruff check passed!"
    else
        print_error "Ruff check failed! Run './lint.sh fix' to fix."
        exit 1
    fi
}

# Run Ruff linter with auto-fix
lint_code() {
    print_info "Running Ruff linter with auto-fix..."
    ruff check --fix src/ ui/ tests/ tests_ui/ example.py main.py
    print_success "Linting complete!"
}

# Fix code with both tools
fix_code() {
    print_info "Fixing code with Ruff..."
    ruff check --fix src/ ui/ tests/ tests_ui/ example.py main.py
    
    echo ""
    print_info "Formatting with Black..."
    black src/ ui/ tests/ tests_ui/ example.py main.py
    
    print_success "Code fixed successfully!"
}

# Run all checks and fixes
run_all() {
    print_header
    
    print_info "Step 1/3: Running Ruff with auto-fix..."
    ruff check --fix src/ ui/ tests/ tests_ui/ example.py main.py || true
    
    echo ""
    print_info "Step 2/3: Formatting with Black..."
    black src/ ui/ tests/ tests_ui/ example.py main.py
    
    echo ""
    print_info "Step 3/3: Running final checks..."
    ruff check src/ ui/ tests/ tests_ui/ example.py main.py
    black --check src/ ui/ tests/ tests_ui/ example.py main.py
    
    echo ""
    print_success "All checks complete!"
}

# Install pre-commit hooks
install_hooks() {
    print_info "Installing pre-commit hooks..."
    if ! command -v pre-commit &> /dev/null; then
        print_error "pre-commit is not installed. Install with: pip install pre-commit"
        exit 1
    fi
    
    pre-commit install
    print_success "Pre-commit hooks installed successfully!"
    print_info "Run 'pre-commit run --all-files' to test hooks."
}

# Update pre-commit hooks
update_hooks() {
    print_info "Updating pre-commit hooks..."
    if ! command -v pre-commit &> /dev/null; then
        print_error "pre-commit is not installed. Install with: pip install pre-commit"
        exit 1
    fi
    
    pre-commit autoupdate
    print_success "Pre-commit hooks updated successfully!"
}

# Clean cache files
clean_cache() {
    print_info "Cleaning cache files..."
    rm -rf .ruff_cache
    rm -rf .pytest_cache
    rm -rf htmlcov
    rm -rf .coverage
    rm -rf coverage.xml
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    print_success "Cache files cleaned!"
}

# Main script logic
main() {
    case "${1:-help}" in
        format)
            format_code
            ;;
        check)
            check_code
            ;;
        lint)
            lint_code
            ;;
        fix)
            fix_code
            ;;
        all)
            run_all
            ;;
        install)
            install_hooks
            ;;
        update)
            update_hooks
            ;;
        clean)
            clean_cache
            ;;
        help|--help|-h)
            print_header
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
