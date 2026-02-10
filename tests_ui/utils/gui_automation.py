"""
GUI Automation Utilities for Minesweeper UI Testing.

This module provides high-level abstractions for interacting with the Minesweeper
GUI in tests. It uses direct widget manipulation for reliability and speed.
"""

from __future__ import annotations

import time
from typing import List, Optional, Tuple, Union


class GUIAutomation:
    """
    High-level automation interface for Minesweeper GUI.

    This class provides methods to interact with the GUI in a way that mimics
    user behavior while using direct widget access for reliability.

    Example:
        >>> automation = GUIAutomation()
        >>> automation.click_cell(app, 0, 0)
        >>> automation.select_tool(app, "mine")
        >>> assert automation.get_cell_state(app, 0, 0) == CellState.MINE
    """

    # Tool names mapping
    TOOLS = {
        "unknown": "unknown",
        "mine": "mine",
        "number": "number",
    }

    def __init__(self, delay: float = 0.0):
        """
        Initialize automation interface.

        Args:
            delay: Optional delay between actions (seconds) for visual debugging
        """
        self.delay = delay

    def _sleep(self):
        """Sleep for configured delay if any."""
        if self.delay > 0:
            time.sleep(self.delay)

    # ======================================================================
    # Cell Interactions
    # ======================================================================

    def click_cell(self, app, row: int, col: int) -> None:
        """
        Click on a specific cell to apply the current tool.

        Args:
            app: MinesweeperBoardEditor instance
            row: Row index of cell
            col: Column index of cell
        """
        app._apply_tool(row, col)
        app.root.update_idletasks()
        self._sleep()

    def click_cells(self, app, positions: List[Tuple[int, int]]) -> None:
        """
        Click multiple cells in sequence.

        Args:
            app: MinesweeperBoardEditor instance
            positions: List of (row, col) tuples
        """
        for row, col in positions:
            self.click_cell(app, row, col)

    def get_cell_state(self, app, row: int, col: int):
        """
        Get the current state of a cell.

        Args:
            app: MinesweeperBoardEditor instance
            row: Row index of cell
            col: Column index of cell

        Returns:
            CellState enum value
        """
        from minesweeper_solver import Position

        pos = Position(row, col)
        return app.board.get(pos)

    def is_cell_unknown(self, app, row: int, col: int) -> bool:
        """
        Check if a cell is in unknown state.

        Args:
            app: MinesweeperBoardEditor instance
            row: Row index of cell
            col: Column index of cell

        Returns:
            True if cell is unknown
        """
        from minesweeper_solver import CellState

        return self.get_cell_state(app, row, col) == CellState.UNKNOWN

    def is_cell_mine(self, app, row: int, col: int) -> bool:
        """
        Check if a cell is flagged as mine.

        Args:
            app: MinesweeperBoardEditor instance
            row: Row index of cell
            col: Column index of cell

        Returns:
            True if cell is a mine
        """
        from minesweeper_solver import CellState

        return self.get_cell_state(app, row, col) == CellState.MINE

    def is_cell_number(self, app, row: int, col: int) -> bool:
        """
        Check if a cell is a revealed number.

        Args:
            app: MinesweeperBoardEditor instance
            row: Row index of cell
            col: Column index of cell

        Returns:
            True if cell is a revealed number
        """
        state = self.get_cell_state(app, row, col)
        return state.value >= 0

    def get_cell_number(self, app, row: int, col: int) -> int:
        """
        Get the number value of a revealed cell.

        Args:
            app: MinesweeperBoardEditor instance
            row: Row index of cell
            col: Column index of cell

        Returns:
            Number value (0-8) or -1 if not a number
        """
        from minesweeper_solver import Position

        pos = Position(row, col)
        return app.board.get_number(pos)

    def set_cell_number(self, app, row: int, col: int, number: int) -> None:
        """
        Set a cell to a specific number value.

        Args:
            app: MinesweeperBoardEditor instance
            row: Row index of cell
            col: Column index of cell
            number: Number value (0-8)
        """
        self.select_tool(app, "number")
        app.number_var.set(str(number))
        app._on_tool_change()
        self.click_cell(app, row, col)

    # ======================================================================
    # Tool Selection
    # ======================================================================

    def select_tool(self, app, tool_name: str) -> None:
        """
        Select an editing tool.

        Args:
            app: MinesweeperBoardEditor instance
            tool_name: One of "unknown", "mine", "number"

        Raises:
            ValueError: If tool_name is invalid
        """
        if tool_name not in self.TOOLS:
            raise ValueError(
                f"Invalid tool: {tool_name}. Must be one of {list(self.TOOLS.keys())}"
            )

        app.tool_var.set(tool_name)
        app._on_tool_change()
        app.root.update_idletasks()
        self._sleep()

    def select_number_tool(self, app, number: int) -> None:
        """
        Select the number tool with a specific value.

        Args:
            app: MinesweeperBoardEditor instance
            number: Number value (0-8)

        Raises:
            ValueError: If number is not in range 0-8
        """
        if not 0 <= number <= 8:
            raise ValueError(f"Number must be between 0 and 8, got {number}")

        self.select_tool(app, "number")
        app.number_var.set(str(number))
        app._on_tool_change()
        app.root.update_idletasks()

    def get_current_tool(self, app) -> str:
        """
        Get the currently selected tool.

        Args:
            app: MinesweeperBoardEditor instance

        Returns:
            Current tool name
        """
        return app.tool_var.get()

    # ======================================================================
    # Board Operations
    # ======================================================================

    def create_new_board(self, app, rows: int, cols: int, total_mines: int) -> None:
        """
        Create a new board with specified dimensions.

        Args:
            app: MinesweeperBoardEditor instance
            rows: Number of rows
            cols: Number of columns
            total_mines: Total number of mines
        """
        app.rows_var.set(str(rows))
        app.cols_var.set(str(cols))
        app.mines_var.set(str(total_mines))
        app._create_new_board()
        app.root.update_idletasks()
        self._sleep()

    def clear_board(self, app) -> None:
        """
        Clear all cells to unknown state.

        Args:
            app: MinesweeperBoardEditor instance
        """
        app._clear_board()
        app.root.update_idletasks()
        self._sleep()

    def get_board_dimensions(self, app) -> Tuple[int, int]:
        """
        Get current board dimensions.

        Args:
            app: MinesweeperBoardEditor instance

        Returns:
            Tuple of (rows, cols)
        """
        return (app.rows, app.cols)

    def count_cells_with_state(self, app, state) -> int:
        """
        Count cells with a specific state.

        Args:
            app: MinesweeperBoardEditor instance
            state: CellState to count

        Returns:
            Number of cells with the given state
        """
        count = 0
        for row in range(app.rows):
            for col in range(app.cols):
                if self.get_cell_state(app, row, col) == state:
                    count += 1
        return count

    # ======================================================================
    # Solver Operations
    # ======================================================================

    def run_solver(self, app) -> None:
        """
        Execute the solver on the current board.

        Args:
            app: MinesweeperBoardEditor instance
        """
        app._solve_board()
        app.root.update_idletasks()
        self._sleep()

    def show_probabilities(self, app) -> None:
        """
        Display probability analysis on the board.

        Args:
            app: MinesweeperBoardEditor instance
        """
        app._show_probabilities()
        app.root.update_idletasks()
        self._sleep()

    def clear_solver_results(self, app) -> None:
        """
        Clear solver highlighting and probabilities.

        Args:
            app: MinesweeperBoardEditor instance
        """
        app._clear_solver_results()
        app.root.update_idletasks()
        self._sleep()

    def get_hint(self, app) -> str:
        """
        Get a hint for the current board state.

        Args:
            app: MinesweeperBoardEditor instance

        Returns:
            Hint text
        """
        app._get_hint()
        app.root.update_idletasks()
        return app.results_text.get("1.0", "end-1c")

    def get_solver_results_text(self, app) -> str:
        """
        Get the text from the solver results panel.

        Args:
            app: MinesweeperBoardEditor instance

        Returns:
            Results text
        """
        return app.results_text.get("1.0", "end-1c")

    # ======================================================================
    # Import/Export Operations
    # ======================================================================

    def load_board_from_string(self, app, board_str: str, total_mines: int) -> None:
        """
        Load a board from string representation.

        Args:
            app: MinesweeperBoardEditor instance
            board_str: String representation of board
            total_mines: Total number of mines
        """
        from minesweeper_solver import MinesweeperBoard

        board = MinesweeperBoard.from_string(board_str, total_mines)
        app.board = board
        app.rows = board.rows
        app.cols = board.cols
        app.total_mines = total_mines

        # Update UI variables
        app.rows_var.set(str(board.rows))
        app.cols_var.set(str(board.cols))
        app.mines_var.set(str(total_mines))

        # Recreate board display
        app._create_new_board()

        # Apply loaded state
        for (row, col), cell in app.cells.items():
            from minesweeper_solver import Position

            pos = Position(row, col)
            cell.update_state(app.board.get(pos))

        app.root.update_idletasks()
        self._sleep()

    def export_board_to_string(self, app) -> str:
        """
        Export current board to string representation.

        Args:
            app: MinesweeperBoardEditor instance

        Returns:
            String representation of board
        """
        return app.board.to_string()

    # ======================================================================
    # State Verification Helpers
    # ======================================================================

    def is_solver_result_displayed(self, app) -> bool:
        """
        Check if solver results are currently displayed.

        Args:
            app: MinesweeperBoardEditor instance

        Returns:
            True if results panel has content
        """
        text = self.get_solver_results_text(app)
        return (
            len(text.strip()) > 0
            and text != "Ready. Create a board and click 'Solve Board' to analyze."
        )

    def get_highlighted_cells(
        self, app
    ) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
        Get cells highlighted by solver (safe and mines).

        Args:
            app: MinesweeperBoardEditor instance

        Returns:
            Tuple of (safe_cells, mine_cells) as lists of (row, col)
        """
        from ui import CellStyles

        safe_cells = []
        mine_cells = []

        for (row, col), cell in app.cells.items():
            # Check cell background color
            if cell.rect_id:
                color = app.canvas.itemcget(cell.rect_id, "fill")
                if color == CellStyles.COLOR_SAFE:
                    safe_cells.append((row, col))
                elif color == CellStyles.COLOR_MINE:
                    mine_cells.append((row, col))

        return safe_cells, mine_cells


# Convenience function to create automation instance
automation = GUIAutomation()
