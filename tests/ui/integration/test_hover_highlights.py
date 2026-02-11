"""
Tests for hover behavior with solver highlights.

These tests ensure that solver highlights (green/red) persist when hovering over cells.
"""

from __future__ import annotations

import pytest

from minesweeper_solver import CellState
from tests.ui.utils.gui_automation import GUIAutomation
from ui import CellStyles


class TestHoverWithSolverHighlights:
    """Tests for hover interaction with solver highlights."""

    def test_hover_preserves_safe_cell_highlight(self, app):
        """Test that hover doesn't clear green safe cell highlight."""
        automation = GUIAutomation()

        # Set up a board where solver will find safe cells
        automation.set_cell_number(app, 5, 5, 0)
        automation.run_solver(app)

        # Get a safe cell position
        safe_positions = [
            (row, col)
            for (row, col), cell in app.cells.items()
            if cell.rect_id
            and app.canvas.itemcget(cell.rect_id, "fill") == CellStyles.COLOR_SAFE
        ]

        if not safe_positions:
            pytest.skip("No safe cells found by solver")

        safe_row, safe_col = safe_positions[0]
        cell = app.cells[(safe_row, safe_col)]

        # Verify cell is highlighted green
        original_color = app.canvas.itemcget(cell.rect_id, "fill")
        assert (
            original_color == CellStyles.COLOR_SAFE
        ), f"Expected safe cell to be green, got {original_color}"

        # Simulate hover by calling set_hover
        cell.set_hover(True)

        # Check color after hover - should still be green
        hover_color = app.canvas.itemcget(cell.rect_id, "fill")
        assert (
            hover_color == CellStyles.COLOR_SAFE
        ), f"Hover cleared safe highlight! Expected {CellStyles.COLOR_SAFE}, got {hover_color}"

        # Remove hover
        cell.set_hover(False)

        # Check color after hover removed - should still be green
        final_color = app.canvas.itemcget(cell.rect_id, "fill")
        assert (
            final_color == CellStyles.COLOR_SAFE
        ), f"Color changed after hover removed! Expected {CellStyles.COLOR_SAFE}, got {final_color}"

    def test_hover_preserves_mine_cell_highlight(self, app):
        """Test that hover doesn't clear red mine highlight."""
        automation = GUIAutomation()

        # Get an unknown cell and manually highlight it as mine
        unknown_cell = None
        for (row, col), cell in app.cells.items():
            if cell.state == CellState.UNKNOWN and cell.rect_id:
                unknown_cell = cell
                break

        if unknown_cell is None:
            pytest.skip("No unknown cells found")

        # Manually highlight as mine (simulating solver result)
        unknown_cell.highlight(CellStyles.COLOR_MINE)

        # Verify cell is highlighted red
        original_color = app.canvas.itemcget(unknown_cell.rect_id, "fill")
        assert (
            original_color == CellStyles.COLOR_MINE
        ), f"Expected mine cell to be red, got {original_color}"

        # Simulate hover
        unknown_cell.set_hover(True)

        # Check color after hover - should still be red
        hover_color = app.canvas.itemcget(unknown_cell.rect_id, "fill")
        assert (
            hover_color == CellStyles.COLOR_MINE
        ), f"Hover cleared mine highlight! Expected {CellStyles.COLOR_MINE}, got {hover_color}"

        # Remove hover
        unknown_cell.set_hover(False)

        # Check color after hover removed - should still be red
        final_color = app.canvas.itemcget(unknown_cell.rect_id, "fill")
        assert (
            final_color == CellStyles.COLOR_MINE
        ), f"Color changed after hover removed! Expected {CellStyles.COLOR_MINE}, got {final_color}"

    def test_hover_works_on_non_highlighted_unknown_cells(self, app):
        """Test that hover still works on regular unknown cells."""
        automation = GUIAutomation()

        # Just set up a simple board without running solver
        automation.set_cell_number(app, 0, 0, 1)

        # Get an unknown cell
        unknown_cell = None
        for (row, col), cell in app.cells.items():
            if cell.state == CellState.UNKNOWN and cell.rect_id:
                unknown_cell = cell
                break

        if unknown_cell is None:
            pytest.skip("No unknown cells found")

        # Verify initial color is unknown
        initial_color = app.canvas.itemcget(unknown_cell.rect_id, "fill")

        # Simulate hover
        unknown_cell.set_hover(True)

        # Should change to hover color
        hover_color = app.canvas.itemcget(unknown_cell.rect_id, "fill")
        assert (
            hover_color == CellStyles.COLOR_HOVER
        ), f"Expected hover color {CellStyles.COLOR_HOVER}, got {hover_color}"

        # Remove hover
        unknown_cell.set_hover(False)

        # Should return to initial color
        final_color = app.canvas.itemcget(unknown_cell.rect_id, "fill")
        assert (
            final_color == initial_color
        ), f"Expected return to {initial_color}, got {final_color}"

    def test_hover_on_revealed_number_cell_no_change(self, app):
        """Test that hover doesn't affect revealed number cells."""
        automation = GUIAutomation()

        # Set a cell to a number
        automation.set_cell_number(app, 0, 0, 3)

        cell = app.cells[(0, 0)]

        # Get initial color
        initial_color = app.canvas.itemcget(cell.rect_id, "fill")

        # Simulate hover
        cell.set_hover(True)

        # Color should not change for revealed cells
        hover_color = app.canvas.itemcget(cell.rect_id, "fill")
        assert (
            hover_color == initial_color
        ), f"Hover should not change revealed cell color. Expected {initial_color}, got {hover_color}"
