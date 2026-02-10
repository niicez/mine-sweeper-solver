"""
End-to-End tests for complete user workflows.

These tests simulate realistic user scenarios:
- Creating and editing a board
- Running solver and analyzing results
- Importing and exporting boards
- Complete game analysis workflow
"""

from __future__ import annotations

import pytest

from minesweeper_solver import CellState
from tests_ui.utils.gui_automation import GUIAutomation
from tests_ui.utils.assertions import (
    assert_cell_is_unknown,
    assert_cell_is_mine,
    assert_cell_is_number,
    assert_solver_results_contain,
    assert_board_dimensions,
)


class TestBasicEditingWorkflow:
    """Tests for basic board editing workflow."""

    def test_create_and_edit_board_workflow(self, app):
        """
        Test complete workflow: create board, set cells, verify state.

        Scenario:
        1. Create a 9x9 board
        2. Set some cells to numbers
        3. Flag some mines
        4. Verify final state
        """
        automation = GUIAutomation()

        # Step 1: Create beginner board
        automation.create_new_board(app, 9, 9, 10)
        assert_board_dimensions(app, 9, 9)

        # Step 2: Set up a revealed area
        automation.set_cell_number(app, 0, 0, 0)
        automation.set_cell_number(app, 0, 1, 1)
        automation.set_cell_number(app, 0, 2, 0)
        automation.set_cell_number(app, 1, 0, 1)
        automation.set_cell_number(app, 1, 1, 1)
        automation.set_cell_number(app, 1, 2, 1)

        # Step 3: Flag suspected mines
        automation.select_tool(app, "mine")
        automation.click_cell(app, 2, 2)

        # Step 4: Verify state
        assert_cell_is_number(app, 0, 0, 0)
        assert_cell_is_number(app, 0, 1, 1)
        assert_cell_is_mine(app, 2, 2)

    def test_edit_clear_edit_cycle(self, app):
        """
        Test editing, clearing, and re-editing workflow.

        Scenario:
        1. Set some cells
        2. Clear board
        3. Set different cells
        4. Verify only new cells are set
        """
        automation = GUIAutomation()

        # First edit session
        automation.set_cell_number(app, 0, 0, 1)
        automation.set_cell_number(app, 0, 1, 2)
        automation.set_cell_number(app, 0, 2, 3)

        # Clear
        automation.clear_board(app)

        # Verify cleared
        assert_cell_is_unknown(app, 0, 0)
        assert_cell_is_unknown(app, 0, 1)
        assert_cell_is_unknown(app, 0, 2)

        # Second edit session
        automation.set_cell_number(app, 5, 5, 5)
        automation.select_tool(app, "mine")
        automation.click_cell(app, 5, 6)

        # Verify new state
        assert_cell_is_number(app, 5, 5, 5)
        assert_cell_is_mine(app, 5, 6)


class TestSolverWorkflow:
    """Tests for solver analysis workflow."""

    def test_basic_solver_workflow(self, app):
        """
        Test basic solver workflow.

        Scenario:
        1. Create a board with constraints
        2. Run solver
        3. View results
        4. Clear results
        """
        automation = GUIAutomation()

        # Set up a simple constraint
        automation.set_cell_number(app, 1, 1, 0)

        # Run solver
        automation.run_solver(app)

        # Verify results
        assert_solver_results_contain(app, "Solver Analysis Results")
        assert_solver_results_contain(app, "Guaranteed safe")

        # Clear results
        automation.clear_solver_results(app)

        # Verify cleared
        results = automation.get_solver_results_text(app)
        assert "Ready" in results

    def test_solver_with_mine_flagging_workflow(self, app):
        """
        Test solver workflow with mine flagging.

        Scenario:
        1. Set up board with numbers
        2. Flag some mines
        3. Run solver
        4. Verify solver uses flag information
        """
        automation = GUIAutomation()

        # Set up board
        automation.set_cell_number(app, 0, 0, 2)
        automation.select_tool(app, "mine")
        automation.click_cell(app, 0, 1)
        automation.click_cell(app, 1, 0)

        # Run solver
        automation.run_solver(app)

        # Should show results
        assert_solver_results_contain(app, "Constraints found")

    def test_analyze_and_get_hint_workflow(self, app):
        """
        Test analysis and hint workflow.

        Scenario:
        1. Set up board
        2. Run solver
        3. Get hint
        4. Verify hint is relevant
        """
        automation = GUIAutomation()

        # Set up board with clear safe cells
        automation.set_cell_number(app, 5, 5, 0)

        # Get hint
        hint = automation.get_hint(app)

        # Should suggest safe cells
        assert "HINT" in hint

    def test_probability_analysis_workflow(self, app):
        """
        Test probability analysis workflow.

        Scenario:
        1. Set up ambiguous board
        2. Run solver
        3. Show probabilities
        4. Verify probability display
        """
        automation = GUIAutomation()

        # Set up board with some constraints
        automation.set_cell_number(app, 0, 0, 1)
        automation.set_cell_number(app, 2, 2, 1)

        # Run solver and show probabilities
        automation.run_solver(app)
        automation.show_probabilities(app)

        # Should show probability analysis
        results = automation.get_solver_results_text(app)
        assert "Probability" in results or "probability" in results.lower()


class TestImportExportWorkflow:
    """Tests for import/export workflow."""

    def test_import_analyze_export_workflow(self, app):
        """
        Test complete import-analyze-export workflow.

        Scenario:
        1. Import board from string
        2. Run solver
        3. Analyze results
        4. Export board
        5. Verify exported state
        """
        automation = GUIAutomation()

        # Import board
        board_str = """
        12?
        ??X
        ???
        """
        automation.load_board_from_string(app, board_str, 3)

        # Run solver
        automation.run_solver(app)

        # Get results
        results = automation.get_solver_results_text(app)
        assert "Constraints found" in results

        # Export
        exported = automation.export_board_to_string(app)

        # Verify exported matches original
        assert "12?" in exported
        assert "X" in exported

    def test_create_edit_export_import_cycle(self, app):
        """
        Test create-edit-export-import workflow.

        Scenario:
        1. Create board
        2. Edit cells
        3. Export
        4. Clear board
        5. Import exported string
        6. Verify state restored
        """
        automation = GUIAutomation()

        # Create and edit
        automation.create_new_board(app, 5, 5, 5)
        automation.set_cell_number(app, 0, 0, 1)
        automation.select_tool(app, "mine")
        automation.click_cell(app, 2, 2)
        automation.set_cell_number(app, 4, 4, 2)

        # Export
        exported = automation.export_board_to_string(app)

        # Clear
        automation.clear_board(app)
        assert_cell_is_unknown(app, 0, 0)
        assert_cell_is_unknown(app, 2, 2)

        # Import
        automation.load_board_from_string(app, exported, 5)

        # Verify restored
        assert_cell_is_number(app, 0, 0, 1)
        assert_cell_is_mine(app, 2, 2)
        assert_cell_is_number(app, 4, 4, 2)


class TestComplexAnalysisWorkflow:
    """Tests for complex analysis workflows."""

    def test_beginner_puzzle_analysis(self, app):
        """
        Test analysis of a beginner-level puzzle.

        Scenario:
        1. Set up beginner puzzle state
        2. Run solver
        3. Verify solver finds logical deductions
        """
        automation = GUIAutomation()

        # Set up beginner puzzle pattern
        automation.create_new_board(app, 9, 9, 10)

        # Create a corner opening
        automation.set_cell_number(app, 0, 0, 0)
        automation.set_cell_number(app, 0, 1, 0)
        automation.set_cell_number(app, 1, 0, 0)
        automation.set_cell_number(app, 1, 1, 1)
        automation.set_cell_number(app, 0, 2, 1)
        automation.set_cell_number(app, 2, 0, 1)

        # Run solver
        automation.run_solver(app)

        # Should find deductions
        results = automation.get_solver_results_text(app)
        assert "Constraints found" in results

    def test_solver_highlights_persist_across_operations(self, app):
        """
        Test that solver highlights persist appropriately.

        Scenario:
        1. Run solver
        2. Verify highlights shown
        3. Perform other operations
        4. Verify highlights cleared appropriately
        """
        automation = GUIAutomation()

        # Set up and run solver
        automation.set_cell_number(app, 5, 5, 0)
        automation.run_solver(app)

        # Get highlights
        safe_cells, _ = automation.get_highlighted_cells(app)
        assert len(safe_cells) > 0

        # Clear should remove highlights
        automation.clear_solver_results(app)
        safe_cells, _ = automation.get_highlighted_cells(app)
        assert len(safe_cells) == 0

    def test_multiple_solver_runs_sequence(self, app):
        """
        Test running solver multiple times in sequence.

        Scenario:
        1. Run solver on initial state
        2. Edit board based on results
        3. Run solver again
        4. Verify new results reflect changes
        """
        automation = GUIAutomation()

        # Initial state
        automation.set_cell_number(app, 0, 0, 1)
        automation.run_solver(app)
        first_results = automation.get_solver_results_text(app)

        # Edit based on results
        automation.select_tool(app, "mine")
        automation.click_cell(app, 0, 1)

        # Run again
        automation.run_solver(app)
        second_results = automation.get_solver_results_text(app)

        # Results should reflect changes
        assert first_results != second_results or "Constraints found" in second_results


class TestToolSwitchingWorkflow:
    """Tests for tool switching workflows."""

    def test_rapid_tool_switching_workflow(self, app):
        """
        Test rapid switching between tools.

        Scenario:
        1. Switch between tools quickly
        2. Apply each tool
        3. Verify correct application
        """
        automation = GUIAutomation()

        # Rapid switching
        automation.select_tool(app, "mine")
        automation.click_cell(app, 0, 0)

        automation.select_tool(app, "unknown")
        automation.click_cell(app, 0, 1)

        automation.select_number_tool(app, 3)
        automation.click_cell(app, 0, 2)

        automation.select_tool(app, "mine")
        automation.click_cell(app, 0, 3)

        # Verify
        assert_cell_is_mine(app, 0, 0)
        assert_cell_is_unknown(app, 0, 1)
        assert_cell_is_number(app, 0, 2, 3)
        assert_cell_is_mine(app, 0, 3)

    def test_number_tool_value_changes(self, app):
        """
        Test changing number values without switching tools.

        Scenario:
        1. Select number tool
        2. Set multiple cells with different values
        3. Verify each has correct value
        """
        automation = GUIAutomation()

        automation.select_tool(app, "number")

        # Set different numbers
        for i in range(5):
            app.number_var.set(str(i))
            app._on_tool_change()
            automation.click_cell(app, 0, i)

        # Verify
        for i in range(5):
            assert_cell_is_number(app, 0, i, i)


class TestErrorRecoveryWorkflow:
    """Tests for error recovery scenarios."""

    def test_clear_and_recreate_after_error(self, app):
        """
        Test recovery by clearing and recreating board.

        Scenario:
        1. Create complex board
        2. Clear it
        3. Create new board
        4. Verify clean state
        """
        automation = GUIAutomation()

        # Create complex board
        for row in range(5):
            for col in range(5):
                automation.set_cell_number(app, row, col, (row + col) % 9)

        # Clear
        automation.clear_board(app)

        # Create new
        automation.create_new_board(app, 9, 9, 10)

        # Verify clean
        assert_board_dimensions(app, 9, 9)
        assert_cell_is_unknown(app, 0, 0)
        assert_cell_is_unknown(app, 8, 8)

    def test_solver_error_recovery(self, app):
        """
        Test recovery from solver errors.

        Scenario:
        1. Run solver on problematic state
        2. Clear results
        3. Fix state
        4. Run solver again
        """
        automation = GUIAutomation()

        # Create potentially problematic state
        automation.set_cell_number(app, 0, 0, 8)
        automation.run_solver(app)

        # Clear and fix
        automation.clear_board(app)
        automation.set_cell_number(app, 0, 0, 1)

        # Run again
        automation.run_solver(app)

        # Should complete without error
        results = automation.get_solver_results_text(app)
        assert "Constraints found" in results or "Ready" in results
