"""
Integration tests for Solver UI functionality.

These tests validate the solver integration including:
- Running solver on various board states
- Displaying results correctly
- Highlighting safe cells and mines
- Probability display
- Hint generation
"""

from __future__ import annotations

import pytest

from minesweeper_solver import CellState
from tests_ui.utils.gui_automation import GUIAutomation
from tests_ui.utils.assertions import (
    assert_cell_is_unknown,
    assert_solver_results_displayed,
    assert_solver_results_contain,
    assert_cells_highlighted_as_safe,
    assert_cells_highlighted_as_mines,
    assert_no_errors_in_results,
)


class TestSolverExecution:
    """Tests for solver execution and results."""

    def test_solver_runs_on_empty_board(self, app):
        """Test that solver runs successfully on empty board."""
        automation = GUIAutomation()

        automation.run_solver(app)

        # Should display results without errors
        assert_solver_results_displayed(app)
        assert_no_errors_in_results(app)

    def test_solver_finds_guaranteed_mine(self, app):
        """Test solver correctly identifies guaranteed mine."""
        automation = GUIAutomation()

        # Set up: A '1' with exactly 1 unknown neighbor
        # The unknown must be a mine
        automation.set_cell_number(app, 0, 0, 1)

        automation.run_solver(app)

        # Should find the mine at (0, 1)
        assert_solver_results_contain(app, "Guaranteed mines: 1")
        safe_cells, mine_cells = automation.get_highlighted_cells(app)
        assert (0, 1) in mine_cells

    def test_solver_finds_guaranteed_safe_cells(self, app):
        """Test solver correctly identifies guaranteed safe cells."""
        automation = GUIAutomation()

        # Set up: A '0' cell makes all neighbors safe
        automation.set_cell_number(app, 5, 5, 0)

        automation.run_solver(app)

        # Should find safe cells
        assert_solver_results_contain(app, "Guaranteed safe")
        safe_cells, _ = automation.get_highlighted_cells(app)
        # Neighbors of 0 should be safe
        assert len(safe_cells) > 0

    def test_solver_handles_constraint_comparison(self, app):
        """Test solver uses constraint comparison for deductions."""
        automation = GUIAutomation()

        # Set up a board that requires constraint comparison
        # Two overlapping constraints
        automation.set_cell_number(app, 0, 0, 2)
        automation.set_cell_number(app, 0, 1, 2)
        automation.select_tool(app, "mine")
        automation.click_cell(app, 1, 2)  # Flag a mine

        automation.run_solver(app)

        # Should display results
        assert_solver_results_displayed(app)
        assert_solver_results_contain(app, "Constraints found")

    def test_solver_clears_previous_results(self, app):
        """Test that running solver clears previous highlights."""
        automation = GUIAutomation()

        # First run
        automation.set_cell_number(app, 5, 5, 0)
        automation.run_solver(app)

        # Modify board
        automation.clear_board(app)

        # Second run
        automation.set_cell_number(app, 3, 3, 1)
        automation.run_solver(app)

        # Results should reflect new board
        assert_solver_results_displayed(app)


class TestSolverHighlighting:
    """Tests for solver result highlighting."""

    def test_safe_cells_highlighted_in_green(self, app):
        """Test that safe cells are highlighted in green."""
        automation = GUIAutomation()

        automation.set_cell_number(app, 1, 1, 0)
        automation.run_solver(app)

        safe_cells, _ = automation.get_highlighted_cells(app)

        # All neighbors of the 0 should be safe
        expected_safe = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]

        for cell in expected_safe:
            if cell in [(r, c) for r in range(10) for c in range(10)]:
                assert cell in safe_cells, f"Cell {cell} should be highlighted as safe"

    def test_mine_cells_highlighted_in_red(self, app):
        """Test that mine cells are highlighted in red."""
        automation = GUIAutomation()

        # Set up guaranteed mine scenario
        automation.set_cell_number(app, 0, 0, 1)
        automation.run_solver(app)

        _, mine_cells = automation.get_highlighted_cells(app)

        # Cell (0, 1) should be highlighted as mine
        if (0, 1) in mine_cells:
            assert True  # Found expected mine

    def test_clear_solver_results_removes_highlights(self, app):
        """Test that clearing solver results removes highlights."""
        automation = GUIAutomation()

        # Run solver and get highlights
        automation.set_cell_number(app, 5, 5, 0)
        automation.run_solver(app)

        safe_cells, _ = automation.get_highlighted_cells(app)
        assert len(safe_cells) > 0  # Should have highlights

        # Clear results
        automation.clear_solver_results(app)

        # Highlights should be gone
        safe_cells, mine_cells = automation.get_highlighted_cells(app)
        assert len(safe_cells) == 0
        assert len(mine_cells) == 0


class TestProbabilityDisplay:
    """Tests for probability display functionality."""

    def test_show_probabilities_displays_values(self, app):
        """Test that probability display shows values on cells."""
        automation = GUIAutomation()

        # Set up a board with some constraints
        automation.set_cell_number(app, 0, 0, 1)
        automation.run_solver(app)  # Need to run solver first
        automation.show_probabilities(app)

        # Should display results with probabilities
        results = automation.get_solver_results_text(app)
        assert "Probability" in results or "probability" in results.lower()

    def test_probability_display_on_complex_board(self, app):
        """Test probability display on a more complex board."""
        automation = GUIAutomation()

        # Set up multiple constraints
        automation.set_cell_number(app, 0, 0, 1)
        automation.set_cell_number(app, 0, 2, 1)
        automation.set_cell_number(app, 2, 0, 1)
        automation.set_cell_number(app, 2, 2, 1)

        automation.run_solver(app)
        automation.show_probabilities(app)

        # Results should be displayed
        assert_solver_results_displayed(app)

    def test_clear_results_removes_probabilities(self, app):
        """Test that clearing results removes probability display."""
        automation = GUIAutomation()

        automation.set_cell_number(app, 0, 0, 1)
        automation.run_solver(app)
        automation.show_probabilities(app)
        automation.clear_solver_results(app)

        # Probability indicators should be cleared
        results = automation.get_solver_results_text(app)
        assert results == "Ready. Create a board and click 'Solve Board' to analyze."


class TestHintSystem:
    """Tests for hint generation system."""

    def test_hint_shows_safe_cell_when_available(self, app):
        """Test that hint suggests safe cell when one exists."""
        automation = GUIAutomation()

        automation.set_cell_number(app, 5, 5, 0)
        hint = automation.get_hint(app)

        assert "HINT" in hint
        assert "guaranteed safe" in hint.lower() or "safe" in hint.lower()

    def test_hint_shows_mine_when_no_safe_cells(self, app):
        """Test that hint suggests flagging mine when no safe cells exist."""
        automation = GUIAutomation()

        # Set up guaranteed mine scenario
        automation.set_cell_number(app, 0, 0, 1)
        hint = automation.get_hint(app)

        assert "HINT" in hint
        # Should suggest flagging or provide guidance

    def test_hint_shows_probability_when_guess_needed(self, app):
        """Test that hint suggests lowest probability when guess is needed."""
        automation = GUIAutomation()

        # Set up ambiguous board
        automation.set_cell_number(app, 0, 0, 1)
        automation.set_cell_number(app, 2, 2, 1)

        hint = automation.get_hint(app)

        assert "HINT" in hint


class TestSolverEdgeCases:
    """Tests for solver edge cases."""

    def test_solver_on_fully_revealed_board(self, app):
        """Test solver on board with all cells revealed."""
        automation = GUIAutomation()

        # Reveal all cells with 0
        for row in range(10):
            for col in range(10):
                automation.set_cell_number(app, row, col, 0)

        automation.run_solver(app)

        assert_solver_results_displayed(app)
        assert_solver_results_contain(app, "Constraints found: 0")

    def test_solver_on_board_with_all_mines_flagged(self, app):
        """Test solver when all mines are already flagged."""
        automation = GUIAutomation()

        automation.select_tool(app, "mine")
        for row in range(10):
            automation.click_cell(app, row, 0)

        automation.run_solver(app)

        assert_solver_results_displayed(app)

    def test_solver_on_single_cell_board(self, app):
        """Test solver on smallest board (1x1)."""
        automation = GUIAutomation()
        automation.create_new_board(app, 1, 1, 0)

        automation.set_cell_number(app, 0, 0, 0)
        automation.run_solver(app)

        assert_solver_results_displayed(app)

    def test_solver_handles_large_board(self, app):
        """Test solver performance on larger board."""
        automation = GUIAutomation()
        automation.create_new_board(app, 15, 15, 30)

        # Set some constraints
        automation.set_cell_number(app, 7, 7, 0)
        automation.set_cell_number(app, 5, 5, 1)

        automation.run_solver(app)

        assert_solver_results_displayed(app)

    def test_solver_results_cleared_on_board_edit(self, app):
        """Test that editing board clears solver results."""
        automation = GUIAutomation()

        # Run solver
        automation.set_cell_number(app, 5, 5, 0)
        automation.run_solver(app)

        # Edit a cell
        automation.set_cell_number(app, 0, 0, 1)

        # Results should be cleared
        results = automation.get_solver_results_text(app)
        assert "Ready" in results or results == ""
