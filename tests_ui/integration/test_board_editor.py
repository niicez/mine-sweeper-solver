"""
Integration tests for Board Editor functionality.

These tests validate the core board editing capabilities including:
- Board creation and sizing
- Cell state modifications
- Board clearing and reset
- Board dimensions validation
"""

from __future__ import annotations

import pytest

from minesweeper_solver import CellState, Position
from tests_ui.utils.gui_automation import GUIAutomation
from tests_ui.utils.assertions import (
    assert_cell_is_unknown,
    assert_cell_is_mine,
    assert_cell_is_number,
    assert_board_dimensions,
    assert_cell_count_with_state,
    assert_board_matches_string,
)


class TestBoardCreation:
    """Tests for board creation and sizing."""

    def test_default_board_creation(self, app):
        """Test that app creates default 10x10 board on startup."""
        assert_board_dimensions(app, 10, 10)

        # All cells should be unknown initially
        assert_cell_count_with_state(app, CellState.UNKNOWN, 100)

    def test_create_beginner_board(self, app):
        """Test creating a beginner-level board (9x9)."""
        automation = GUIAutomation()
        automation.create_new_board(app, 9, 9, 10)

        assert_board_dimensions(app, 9, 9)
        assert_cell_count_with_state(app, CellState.UNKNOWN, 81)

    def test_create_intermediate_board(self, app):
        """Test creating an intermediate-level board (16x16)."""
        automation = GUIAutomation()
        automation.create_new_board(app, 16, 16, 40)

        assert_board_dimensions(app, 16, 16)
        assert_cell_count_with_state(app, CellState.UNKNOWN, 256)

    def test_create_expert_board(self, app):
        """Test creating an expert-level board (30x16)."""
        automation = GUIAutomation()
        automation.create_new_board(app, 30, 16, 99)

        assert_board_dimensions(app, 30, 16)
        assert_cell_count_with_state(app, CellState.UNKNOWN, 480)

    def test_create_narrow_board(self, app):
        """Test creating a narrow board (5x20)."""
        automation = GUIAutomation()
        automation.create_new_board(app, 5, 20, 15)

        assert_board_dimensions(app, 5, 20)
        assert_cell_count_with_state(app, CellState.UNKNOWN, 100)

    def test_create_tall_board(self, app):
        """Test creating a tall board (20x5)."""
        automation = GUIAutomation()
        automation.create_new_board(app, 20, 5, 15)

        assert_board_dimensions(app, 20, 5)
        assert_cell_count_with_state(app, CellState.UNKNOWN, 100)


class TestCellEditing:
    """Tests for cell editing functionality."""

    def test_set_cell_to_mine(self, app):
        """Test marking a cell as mine."""
        automation = GUIAutomation()

        automation.select_tool(app, "mine")
        automation.click_cell(app, 2, 3)

        assert_cell_is_mine(app, 2, 3)

    def test_set_cell_to_number(self, app):
        """Test setting a cell to a number value."""
        automation = GUIAutomation()

        automation.set_cell_number(app, 1, 1, 3)

        assert_cell_is_number(app, 1, 1, 3)

    def test_set_multiple_cells_to_numbers(self, app):
        """Test setting multiple cells to different numbers."""
        automation = GUIAutomation()

        automation.set_cell_number(app, 0, 0, 0)
        automation.set_cell_number(app, 0, 1, 1)
        automation.set_cell_number(app, 0, 2, 2)

        assert_cell_is_number(app, 0, 0, 0)
        assert_cell_is_number(app, 0, 1, 1)
        assert_cell_is_number(app, 0, 2, 2)

    def test_clear_cell_to_unknown(self, app):
        """Test clearing a cell back to unknown."""
        automation = GUIAutomation()

        # First set to mine
        automation.select_tool(app, "mine")
        automation.click_cell(app, 5, 5)
        assert_cell_is_mine(app, 5, 5)

        # Then clear to unknown
        automation.select_tool(app, "unknown")
        automation.click_cell(app, 5, 5)

        assert_cell_is_unknown(app, 5, 5)

    def test_set_number_range_boundaries(self, app):
        """Test setting numbers at range boundaries (0 and 8)."""
        automation = GUIAutomation()

        automation.set_cell_number(app, 0, 0, 0)
        automation.set_cell_number(app, 0, 1, 8)

        assert_cell_is_number(app, 0, 0, 0)
        assert_cell_is_number(app, 0, 1, 8)

    def test_edit_corner_cells(self, app):
        """Test editing cells at board corners."""
        automation = GUIAutomation()

        # Set all four corners
        automation.set_cell_number(app, 0, 0, 1)
        automation.set_cell_number(app, 0, 9, 2)
        automation.set_cell_number(app, 9, 0, 3)
        automation.set_cell_number(app, 9, 9, 4)

        assert_cell_is_number(app, 0, 0, 1)
        assert_cell_is_number(app, 0, 9, 2)
        assert_cell_is_number(app, 9, 0, 3)
        assert_cell_is_number(app, 9, 9, 4)

    def test_edit_edge_cells(self, app):
        """Test editing cells at board edges."""
        automation = GUIAutomation()

        automation.select_tool(app, "mine")
        automation.click_cell(app, 0, 5)  # Top edge
        automation.click_cell(app, 5, 0)  # Left edge
        automation.click_cell(app, 5, 9)  # Right edge
        automation.click_cell(app, 9, 5)  # Bottom edge

        assert_cell_is_mine(app, 0, 5)
        assert_cell_is_mine(app, 5, 0)
        assert_cell_is_mine(app, 5, 9)
        assert_cell_is_mine(app, 9, 5)

    def test_clear_board_resets_all_cells(self, app):
        """Test that clearing board resets all cells to unknown."""
        automation = GUIAutomation()

        # Set some cells
        automation.select_tool(app, "mine")
        automation.click_cells(app, [(0, 0), (1, 1), (2, 2)])
        automation.set_cell_number(app, 3, 3, 5)

        # Clear board
        automation.clear_board(app)

        # All should be unknown
        assert_cell_count_with_state(app, CellState.UNKNOWN, 100)


class TestBoardClearing:
    """Tests for board clearing functionality."""

    def test_clear_empty_board(self, app):
        """Test clearing an already empty board."""
        automation = GUIAutomation()

        automation.clear_board(app)

        # Should still have all unknown cells
        assert_cell_count_with_state(app, CellState.UNKNOWN, 100)

    def test_clear_after_setting_mines(self, app):
        """Test clearing after setting multiple mines."""
        automation = GUIAutomation()

        automation.select_tool(app, "mine")
        for row in range(5):
            for col in range(5):
                automation.click_cell(app, row, col)

        assert_cell_count_with_state(app, CellState.MINE, 25)

        automation.clear_board(app)

        assert_cell_count_with_state(app, CellState.UNKNOWN, 100)

    def test_clear_after_setting_numbers(self, app):
        """Test clearing after setting multiple numbers."""
        automation = GUIAutomation()

        # Set numbers in a pattern
        for row in range(3):
            for col in range(3):
                automation.set_cell_number(app, row, col, (row + col) % 9)

        automation.clear_board(app)

        assert_cell_count_with_state(app, CellState.UNKNOWN, 100)

    def test_clear_mixed_board(self, app):
        """Test clearing board with mixed cell states."""
        automation = GUIAutomation()

        automation.set_cell_number(app, 0, 0, 1)
        automation.select_tool(app, "mine")
        automation.click_cell(app, 0, 1)
        automation.set_cell_number(app, 0, 2, 2)
        automation.select_tool(app, "mine")
        automation.click_cell(app, 1, 0)

        automation.clear_board(app)

        # Verify all cleared
        assert_cell_count_with_state(app, CellState.UNKNOWN, 100)


class TestBoardStatePersistence:
    """Tests for board state consistency."""

    def test_board_state_matches_ui(self, app):
        """Test that internal board state matches UI display."""
        automation = GUIAutomation()

        # Set some cells
        automation.set_cell_number(app, 1, 2, 3)
        automation.select_tool(app, "mine")
        automation.click_cell(app, 2, 3)

        # Verify internal state
        pos1 = Position(1, 2)
        pos2 = Position(2, 3)

        assert app.board.get(pos1) == CellState(3)
        assert app.board.get(pos2) == CellState.MINE

    def test_cells_dictionary_matches_board(self, app):
        """Test that cells dictionary stays synchronized with board."""
        automation = GUIAutomation()

        automation.set_cell_number(app, 5, 5, 4)

        # Check that cells dict reflects the change
        cell = app.cells[(5, 5)]
        assert cell.state == CellState(4)

    def test_string_export_matches_state(self, app):
        """Test that board string export reflects current state."""
        automation = GUIAutomation()

        # Create a 3x3 board for predictable output
        automation.create_new_board(app, 3, 3, 1)

        # Set up a simple pattern
        automation.set_cell_number(app, 0, 0, 1)
        automation.set_cell_number(app, 0, 1, 2)
        automation.select_tool(app, "mine")
        automation.click_cell(app, 0, 2)

        actual = automation.export_board_to_string(app)

        # Check first row - should be "12X" followed by unknown cells
        first_row = actual.split("\n")[0]
        assert (
            first_row[:3] == "12X"
        ), f"Expected first 3 chars to be '12X', got '{first_row[:3]}'"


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_minimum_board_size(self, app):
        """Test creating smallest reasonable board (5x5)."""
        automation = GUIAutomation()
        automation.create_new_board(app, 5, 5, 3)

        assert_board_dimensions(app, 5, 5)
        assert_cell_count_with_state(app, CellState.UNKNOWN, 25)

    def test_large_board_creation(self, app):
        """Test creating a large board (20x20)."""
        automation = GUIAutomation()
        automation.create_new_board(app, 20, 20, 50)

        assert_board_dimensions(app, 20, 20)
        assert_cell_count_with_state(app, CellState.UNKNOWN, 400)

    def test_single_row_board(self, app):
        """Test creating a single-row board."""
        automation = GUIAutomation()
        automation.create_new_board(app, 1, 10, 3)

        assert_board_dimensions(app, 1, 10)
        assert_cell_count_with_state(app, CellState.UNKNOWN, 10)

    def test_single_column_board(self, app):
        """Test creating a single-column board."""
        automation = GUIAutomation()
        automation.create_new_board(app, 10, 1, 3)

        assert_board_dimensions(app, 10, 1)
        assert_cell_count_with_state(app, CellState.UNKNOWN, 10)

    def test_rapid_cell_toggles(self, app):
        """Test rapidly toggling a cell between states."""
        automation = GUIAutomation()

        # Toggle same cell multiple times
        for i in range(5):
            automation.select_tool(app, "mine")
            automation.click_cell(app, 5, 5)
            automation.select_tool(app, "unknown")
            automation.click_cell(app, 5, 5)

        # Should end up as unknown
        assert_cell_is_unknown(app, 5, 5)
