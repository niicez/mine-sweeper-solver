"""
Custom Assertions for GUI Testing.

This module provides specialized assertion functions for validating GUI state
in tests. These assertions provide clear, informative error messages.
"""

from typing import List, Tuple


class GUIAssertionError(AssertionError):
    """Custom assertion error with GUI context."""

    pass


def assert_cell_state(app, row: int, col: int, expected_state, msg: str = None):
    """
    Assert that a cell has the expected state.

    Args:
        app: MinesweeperBoardEditor instance
        row: Row index
        col: Column index
        expected_state: Expected CellState value
        msg: Optional custom message

    Raises:
        GUIAssertionError: If cell state doesn't match
    """
    from minesweeper_solver import Position

    pos = Position(row, col)
    actual_state = app.board.get(pos)

    if actual_state != expected_state:
        error_msg = (
            msg or f"Cell ({row}, {col}): expected {expected_state}, got {actual_state}"
        )
        raise GUIAssertionError(error_msg)


def assert_cell_is_unknown(app, row: int, col: int, msg: str = None):
    """
    Assert that a cell is in unknown state.

    Args:
        app: MinesweeperBoardEditor instance
        row: Row index
        col: Column index
        msg: Optional custom message

    Raises:
        GUIAssertionError: If cell is not unknown
    """
    from minesweeper_solver import CellState

    assert_cell_state(
        app,
        row,
        col,
        CellState.UNKNOWN,
        msg or f"Cell ({row}, {col}) should be unknown",
    )


def assert_cell_is_mine(app, row: int, col: int, msg: str = None):
    """
    Assert that a cell is flagged as a mine.

    Args:
        app: MinesweeperBoardEditor instance
        row: Row index
        col: Column index
        msg: Optional custom message

    Raises:
        GUIAssertionError: If cell is not a mine
    """
    from minesweeper_solver import CellState

    assert_cell_state(
        app, row, col, CellState.MINE, msg or f"Cell ({row}, {col}) should be a mine"
    )


def assert_cell_is_number(
    app, row: int, col: int, expected_number: int = None, msg: str = None
):
    """
    Assert that a cell is a revealed number.

    Args:
        app: MinesweeperBoardEditor instance
        row: Row index
        col: Column index
        expected_number: Optional specific number value to check
        msg: Optional custom message

    Raises:
        GUIAssertionError: If cell is not a number or has wrong value
    """
    from minesweeper_solver import Position

    pos = Position(row, col)
    actual_number = app.board.get_number(pos)

    if actual_number < 0:
        error_msg = (
            msg
            or f"Cell ({row}, {col}): expected a number, got state {app.board.get(pos)}"
        )
        raise GUIAssertionError(error_msg)

    if expected_number is not None and actual_number != expected_number:
        error_msg = (
            msg
            or f"Cell ({row}, {col}): expected number {expected_number}, got {actual_number}"
        )
        raise GUIAssertionError(error_msg)


def assert_tool_selected(app, expected_tool: str, msg: str = None):
    """
    Assert that a specific tool is selected.

    Args:
        app: MinesweeperBoardEditor instance
        expected_tool: Expected tool name
        msg: Optional custom message

    Raises:
        GUIAssertionError: If wrong tool is selected
    """
    actual_tool = app.tool_var.get()
    if actual_tool != expected_tool:
        error_msg = msg or f"Expected tool '{expected_tool}', got '{actual_tool}'"
        raise GUIAssertionError(error_msg)


def assert_board_dimensions(
    app, expected_rows: int, expected_cols: int, msg: str = None
):
    """
    Assert that board has expected dimensions.

    Args:
        app: MinesweeperBoardEditor instance
        expected_rows: Expected number of rows
        expected_cols: Expected number of columns
        msg: Optional custom message

    Raises:
        GUIAssertionError: If dimensions don't match
    """
    actual_rows = app.rows
    actual_cols = app.cols

    if actual_rows != expected_rows or actual_cols != expected_cols:
        error_msg = (
            msg
            or f"Expected board size {expected_rows}x{expected_cols}, got {actual_rows}x{actual_cols}"
        )
        raise GUIAssertionError(error_msg)


def assert_cell_count_with_state(
    app, expected_state, expected_count: int, msg: str = None
):
    """
    Assert that a specific number of cells have a given state.

    Args:
        app: MinesweeperBoardEditor instance
        expected_state: CellState to count
        expected_count: Expected number of cells
        msg: Optional custom message

    Raises:
        GUIAssertionError: If count doesn't match
    """
    actual_count = 0
    from minesweeper_solver import Position

    for row in range(app.rows):
        for col in range(app.cols):
            pos = Position(row, col)
            if app.board.get(pos) == expected_state:
                actual_count += 1

    if actual_count != expected_count:
        error_msg = (
            msg
            or f"Expected {expected_count} cells with state {expected_state}, found {actual_count}"
        )
        raise GUIAssertionError(error_msg)


def assert_solver_results_displayed(app, msg: str = None):
    """
    Assert that solver results are displayed.

    Args:
        app: MinesweeperBoardEditor instance
        msg: Optional custom message

    Raises:
        GUIAssertionError: If no results are displayed
    """
    text = app.results_text.get("1.0", "end-1c").strip()
    default_msg = "Ready. Create a board and click 'Solve Board' to analyze."

    if not text or text == default_msg:
        error_msg = msg or "Expected solver results to be displayed"
        raise GUIAssertionError(error_msg)


def assert_solver_results_contain(app, expected_text: str, msg: str = None):
    """
    Assert that solver results contain specific text.

    Args:
        app: MinesweeperBoardEditor instance
        expected_text: Text that should be in results
        msg: Optional custom message

    Raises:
        GUIAssertionError: If text not found
    """
    text = app.results_text.get("1.0", "end-1c")
    if expected_text not in text:
        error_msg = msg or f"Expected results to contain '{expected_text}'"
        raise GUIAssertionError(error_msg)


def assert_cells_highlighted_as_safe(
    app, expected_cells: List[Tuple[int, int]], msg: str = None
):
    """
    Assert that specific cells are highlighted as safe.

    Args:
        app: MinesweeperBoardEditor instance
        expected_cells: List of (row, col) tuples
        msg: Optional custom message

    Raises:
        GUIAssertionError: If cells not highlighted correctly
    """
    from ui import CellStyles

    missing = []
    for row, col in expected_cells:
        cell = app.cells.get((row, col))
        if not cell:
            missing.append((row, col))
            continue

        color = app.canvas.itemcget(cell.rect_id, "fill")
        if color != CellStyles.COLOR_SAFE:
            missing.append((row, col))

    if missing:
        error_msg = msg or f"Cells not highlighted as safe: {missing}"
        raise GUIAssertionError(error_msg)


def assert_cells_highlighted_as_mines(
    app, expected_cells: List[Tuple[int, int]], msg: str = None
):
    """
    Assert that specific cells are highlighted as mines.

    Args:
        app: MinesweeperBoardEditor instance
        expected_cells: List of (row, col) tuples
        msg: Optional custom message

    Raises:
        GUIAssertionError: If cells not highlighted correctly
    """
    from ui import CellStyles

    missing = []
    for row, col in expected_cells:
        cell = app.cells.get((row, col))
        if not cell:
            missing.append((row, col))
            continue

        color = app.canvas.itemcget(cell.rect_id, "fill")
        if color != CellStyles.COLOR_MINE:
            missing.append((row, col))

    if missing:
        error_msg = msg or f"Cells not highlighted as mines: {missing}"
        raise GUIAssertionError(error_msg)


def assert_board_matches_string(app, expected_str: str, msg: str = None):
    """
    Assert that board matches expected string representation.

    Args:
        app: MinesweeperBoardEditor instance
        expected_str: Expected board string
        msg: Optional custom message

    Raises:
        GUIAssertionError: If board doesn't match
    """
    actual_str = app.board.to_string()
    if actual_str.strip() != expected_str.strip():
        error_msg = (
            msg
            or f"Board doesn't match expected:\nExpected:\n{expected_str}\n\nActual:\n{actual_str}"
        )
        raise GUIAssertionError(error_msg)


def assert_no_errors_in_results(app, msg: str = None):
    """
    Assert that results panel doesn't contain error messages.

    Args:
        app: MinesweeperBoardEditor instance
        msg: Optional custom message

    Raises:
        GUIAssertionError: If error found in results
    """
    text = app.results_text.get("1.0", "end-1c").lower()
    error_indicators = ["error", "exception", "failed", "traceback"]

    found_errors = [indicator for indicator in error_indicators if indicator in text]
    if found_errors:
        error_msg = msg or f"Found error indicators in results: {found_errors}"
        raise GUIAssertionError(error_msg)
