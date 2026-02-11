"""
Integration tests for Import/Export functionality.

These tests validate:
- Loading boards from string
- Exporting boards to string
- Board state preservation during import/export
- Error handling for invalid imports
"""

from __future__ import annotations

import pytest

from minesweeper_solver import CellState, MinesweeperBoard, Position
from tests_ui.utils.gui_automation import GUIAutomation
from tests_ui.utils.assertions import (
    assert_cell_is_unknown,
    assert_cell_is_mine,
    assert_cell_is_number,
    assert_board_dimensions,
    assert_board_matches_string,
)


class TestImportFromString:
    """Tests for importing boards from string representation."""

    def test_import_simple_board(self, app):
        """Test importing a simple 3x3 board."""
        automation = GUIAutomation()

        board_str = """
        12?
        ??X
        ???
        """

        automation.load_board_from_string(app, board_str, 3)

        assert_board_dimensions(app, 3, 3)
        assert_cell_is_number(app, 0, 0, 1)
        assert_cell_is_number(app, 0, 1, 2)
        assert_cell_is_unknown(app, 0, 2)
        assert_cell_is_mine(app, 1, 2)

    def test_import_beginner_board(self, app):
        """Test importing a beginner-level board."""
        automation = GUIAutomation()

        board_str = """
        000000000
        011100000
        01X100000
        011100000
        000000000
        000000000
        000000000
        000000000
        000000000
        """

        automation.load_board_from_string(app, board_str, 10)

        assert_board_dimensions(app, 9, 9)
        assert_cell_is_number(app, 1, 1, 1)
        assert_cell_is_mine(app, 2, 2)

    def test_import_with_spaces_as_zeros(self, app):
        """Test importing board with spaces representing zeros."""
        automation = GUIAutomation()

        board_str = """
        1 2
        ?X?
        """

        automation.load_board_from_string(app, board_str, 2)

        assert_cell_is_number(app, 0, 0, 1)
        assert_cell_is_number(app, 0, 1, 0)
        assert_cell_is_number(app, 0, 2, 2)
        assert_cell_is_mine(app, 1, 1)

    def test_import_preserves_total_mines(self, app):
        """Test that import preserves total mines setting."""
        automation = GUIAutomation()

        board_str = """
        ???
        ???
        ???
        """

        automation.load_board_from_string(app, board_str, 5)

        assert app.total_mines == 5

    def test_import_updates_ui_variables(self, app):
        """Test that import updates UI dimension variables."""
        automation = GUIAutomation()

        board_str = """
        0000
        0000
        0000
        0000
        """

        automation.load_board_from_string(app, board_str, 0)

        assert app.rows_var.get() == "4"
        assert app.cols_var.get() == "4"
        assert app.mines_var.get() == "0"

    def test_import_single_row(self, app):
        """Test importing a single-row board."""
        automation = GUIAutomation()

        board_str = "1?X?2"

        automation.load_board_from_string(app, board_str, 2)

        assert_board_dimensions(app, 1, 5)
        assert_cell_is_number(app, 0, 0, 1)
        assert_cell_is_unknown(app, 0, 1)
        assert_cell_is_mine(app, 0, 2)
        assert_cell_is_number(app, 0, 4, 2)

    def test_import_single_column(self, app):
        """Test importing a single-column board."""
        automation = GUIAutomation()

        board_str = """
        1
        ?
        X
        2
        """

        automation.load_board_from_string(app, board_str, 2)

        assert_board_dimensions(app, 4, 1)
        assert_cell_is_number(app, 0, 0, 1)
        assert_cell_is_unknown(app, 1, 0)
        assert_cell_is_mine(app, 2, 0)
        assert_cell_is_number(app, 3, 0, 2)


class TestExportToString:
    """Tests for exporting boards to string representation."""

    def test_export_empty_board(self, app):
        """Test exporting an empty board."""
        automation = GUIAutomation()

        board_str = automation.export_board_to_string(app)

        # Should be 10 lines of 10 '?' each (default board size)
        lines = board_str.strip().split("\n")
        assert len(lines) == 10
        assert all(line == "?" * 10 for line in lines)

    def test_export_board_with_mines(self, app):
        """Test exporting board with mine flags."""
        automation = GUIAutomation()

        automation.select_tool(app, "mine")
        automation.click_cell(app, 0, 0)
        automation.click_cell(app, 1, 1)

        board_str = automation.export_board_to_string(app)

        lines = board_str.strip().split("\n")
        assert lines[0][0] == "X"
        assert lines[1][1] == "X"

    def test_export_board_with_numbers(self, app):
        """Test exporting board with number cells."""
        automation = GUIAutomation()

        automation.set_cell_number(app, 0, 0, 1)
        automation.set_cell_number(app, 0, 1, 2)
        automation.set_cell_number(app, 0, 2, 3)

        board_str = automation.export_board_to_string(app)

        lines = board_str.strip().split("\n")
        assert lines[0][:3] == "123"

    def test_export_preserves_board_state(self, app):
        """Test that export preserves all board state."""
        automation = GUIAutomation()

        # Set up specific pattern
        automation.set_cell_number(app, 0, 0, 0)
        automation.select_tool(app, "mine")
        automation.click_cell(app, 0, 1)
        automation.set_cell_number(app, 0, 2, 2)

        board_str = automation.export_board_to_string(app)

        # Verify pattern is preserved
        # Note: Don't use strip() as it removes leading spaces (which represent 0s)
        lines = board_str.split("\n")
        first_row = lines[0]

        # 0 is represented as space in to_string()
        assert (
            first_row[0] == " "
        ), f"Expected space at position 0, got {repr(first_row[0])}"
        assert first_row[1] == "X"
        assert first_row[2] == "2"

    def test_round_trip_import_export(self, app):
        """Test that import followed by export preserves board."""
        automation = GUIAutomation()

        # Note: 0 is exported as space by default, so use 1-8 for round-trip
        original_str = """
        12X
        ?4?
        X?1
        """

        automation.load_board_from_string(app, original_str, 3)
        exported_str = automation.export_board_to_string(app)

        # Normalize for comparison (strip whitespace)
        original_normalized = "\n".join(
            line.strip() for line in original_str.strip().split("\n")
        )

        assert exported_str == original_normalized


class TestImportExportEdgeCases:
    """Tests for import/export edge cases."""

    def test_import_empty_lines_ignored(self, app):
        """Test that empty lines in import string are ignored."""
        automation = GUIAutomation()

        board_str = """

        123

        456

        """

        automation.load_board_from_string(app, board_str, 2)

        # Should still create valid board
        assert_board_dimensions(app, 2, 3)

    def test_import_with_leading_trailing_whitespace(self, app):
        """Test importing string with extra whitespace."""
        automation = GUIAutomation()

        board_str = "  123  \n  456  "

        automation.load_board_from_string(app, board_str, 2)

        assert_board_dimensions(app, 2, 3)

    def test_export_after_clearing_board(self, app):
        """Test exporting after clearing board."""
        automation = GUIAutomation()

        # Set some cells
        automation.set_cell_number(app, 0, 0, 1)
        automation.select_tool(app, "mine")
        automation.click_cell(app, 0, 1)

        # Clear board
        automation.clear_board(app)

        # Export
        board_str = automation.export_board_to_string(app)

        # Should be all unknown
        lines = board_str.strip().split("\n")
        assert all("?" in line for line in lines)

    def test_import_preserves_cell_objects(self, app):
        """Test that import updates cell display objects correctly."""
        automation = GUIAutomation()

        # Note: Minesweeper cells only support values 0-8, not 9
        board_str = """
        123
        456
        780
        """

        automation.load_board_from_string(app, board_str, 0)

        # Verify cell objects reflect imported state
        assert app.cells[(0, 0)].state == CellState(1)
        assert app.cells[(1, 1)].state == CellState(5)
        assert app.cells[(2, 2)].state == CellState(0)

    def test_import_various_characters(self, app):
        """Test importing board with various valid characters."""
        automation = GUIAutomation()

        # Using dots for zeros
        board_str = """
        1.2
        X.3
        ?.?
        """

        automation.load_board_from_string(app, board_str, 3)

        assert_cell_is_number(app, 0, 0, 1)
        assert_cell_is_number(app, 0, 1, 0)
        assert_cell_is_number(app, 0, 2, 2)
        assert_cell_is_mine(app, 1, 0)
        assert_cell_is_number(app, 1, 2, 3)


class TestBoardStateValidation:
    """Tests for validating board state after import/export."""

    def test_internal_board_matches_ui_after_import(self, app):
        """Test that internal board state matches UI after import."""
        automation = GUIAutomation()

        board_str = """
        12X
        34?
        """

        automation.load_board_from_string(app, board_str, 2)

        # Check internal board state
        assert app.board.get_number(Position(0, 0)) == 1
        assert app.board.get_number(Position(0, 1)) == 2
        assert app.board.get(Position(0, 2)) == CellState.MINE
        assert app.board.get_number(Position(1, 0)) == 3
        assert app.board.get_number(Position(1, 1)) == 4
        assert app.board.get(Position(1, 2)) == CellState.UNKNOWN

    def test_export_matches_internal_state(self, app):
        """Test that export reflects internal board state accurately."""
        automation = GUIAutomation()

        # Set cells through automation
        automation.set_cell_number(app, 0, 0, 5)
        automation.select_tool(app, "mine")
        automation.click_cell(app, 0, 1)

        # Export
        board_str = automation.export_board_to_string(app)

        # Verify against internal state
        lines = board_str.split("\n")
        assert lines[0][0] == "5"  # Number 5
        assert lines[0][1] == "X"  # Mine
        assert lines[0][2] == "?"  # Unknown (default)

    def test_import_export_maintains_consistency(self, app):
        """Test that import/export maintains internal consistency."""
        automation = GUIAutomation()

        # Import
        board_str = """
        012345678
        X???????X
        """
        automation.load_board_from_string(app, board_str, 5)

        # Verify all cell states are consistent
        for (row, col), cell in app.cells.items():
            board_state = app.board.get(Position(row, col))
            cell_state = cell.state
            assert (
                board_state == cell_state
            ), f"Inconsistency at ({row}, {col}): board={board_state}, cell={cell_state}"
