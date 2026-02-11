"""
Integration tests for Tool selection and functionality.

These tests validate:
- Tool selection and switching
- Tool-specific behaviors
- Number tool value selection
"""

from __future__ import annotations

import pytest

from tests.ui.utils.gui_automation import GUIAutomation
from tests.ui.utils.assertions import (
    assert_tool_selected,
    assert_cell_is_unknown,
    assert_cell_is_mine,
    assert_cell_is_number,
)


class TestToolSelection:
    """Tests for tool selection functionality."""

    def test_default_tool_is_unknown(self, app):
        """Test that default tool is 'unknown'."""
        assert_tool_selected(app, "unknown")

    def test_select_mine_tool(self, app):
        """Test selecting mine tool."""
        automation = GUIAutomation()

        automation.select_tool(app, "mine")

        assert_tool_selected(app, "mine")

    def test_select_number_tool(self, app):
        """Test selecting number tool."""
        automation = GUIAutomation()

        automation.select_tool(app, "number")

        assert_tool_selected(app, "number")

    def test_select_unknown_tool(self, app):
        """Test selecting unknown tool."""
        automation = GUIAutomation()

        # First select a different tool
        automation.select_tool(app, "mine")
        assert_tool_selected(app, "mine")

        # Then select unknown
        automation.select_tool(app, "unknown")

        assert_tool_selected(app, "unknown")

    def test_switch_between_tools(self, app):
        """Test switching between all tools."""
        automation = GUIAutomation()

        tools = ["unknown", "mine", "number", "unknown", "mine"]
        for tool in tools:
            automation.select_tool(app, tool)
            assert_tool_selected(app, tool)


class TestNumberToolValues:
    """Tests for number tool value selection."""

    def test_select_number_zero(self, app):
        """Test selecting number 0."""
        automation = GUIAutomation()

        automation.select_number_tool(app, 0)

        assert app.number_var.get() == "0"

    def test_select_number_five(self, app):
        """Test selecting number 5."""
        automation = GUIAutomation()

        automation.select_number_tool(app, 5)

        assert app.number_var.get() == "5"

    def test_select_number_eight(self, app):
        """Test selecting number 8 (maximum)."""
        automation = GUIAutomation()

        automation.select_number_tool(app, 8)

        assert app.number_var.get() == "8"

    def test_number_selection_persists_with_tool(self, app):
        """Test that number value persists when tool is selected."""
        automation = GUIAutomation()

        automation.select_number_tool(app, 3)
        automation.click_cell(app, 0, 0)

        # Cell should have number 3
        assert_cell_is_number(app, 0, 0, 3)

    def test_change_number_without_reselecting_tool(self, app):
        """Test changing number value without reselecting tool."""
        automation = GUIAutomation()

        automation.select_number_tool(app, 2)
        automation.click_cell(app, 0, 0)

        # Change number
        app.number_var.set("5")
        app._on_tool_change()
        automation.click_cell(app, 0, 1)

        assert_cell_is_number(app, 0, 0, 2)
        assert_cell_is_number(app, 0, 1, 5)


class TestToolApplication:
    """Tests for tool application to cells."""

    def test_unknown_tool_clears_cell(self, app):
        """Test that unknown tool clears cell state."""
        automation = GUIAutomation()

        # Set to mine first
        automation.select_tool(app, "mine")
        automation.click_cell(app, 5, 5)

        # Clear with unknown tool
        automation.select_tool(app, "unknown")
        automation.click_cell(app, 5, 5)

        assert_cell_is_unknown(app, 5, 5)

    def test_mine_tool_flags_cell(self, app):
        """Test that mine tool flags cell as mine."""
        automation = GUIAutomation()

        automation.select_tool(app, "mine")
        automation.click_cell(app, 3, 4)

        assert_cell_is_mine(app, 3, 4)

    def test_number_tool_sets_value(self, app):
        """Test that number tool sets cell number value."""
        automation = GUIAutomation()

        automation.select_number_tool(app, 4)
        automation.click_cell(app, 2, 2)

        assert_cell_is_number(app, 2, 2, 4)

    def test_tool_applies_to_correct_cell(self, app):
        """Test that tool applies to the clicked cell only."""
        automation = GUIAutomation()

        automation.set_cell_number(app, 1, 1, 1)

        # Verify only that cell changed
        assert_cell_is_number(app, 1, 1, 1)
        assert_cell_is_unknown(app, 0, 0)
        assert_cell_is_unknown(app, 1, 0)
        assert_cell_is_unknown(app, 0, 1)

    def test_multiple_cells_with_same_tool(self, app):
        """Test applying same tool to multiple cells."""
        automation = GUIAutomation()

        automation.select_tool(app, "mine")
        automation.click_cell(app, 0, 0)
        automation.click_cell(app, 0, 1)
        automation.click_cell(app, 0, 2)

        assert_cell_is_mine(app, 0, 0)
        assert_cell_is_mine(app, 0, 1)
        assert_cell_is_mine(app, 0, 2)


class TestToolStateConsistency:
    """Tests for tool state consistency across operations."""

    def test_tool_persists_after_cell_edit(self, app):
        """Test that selected tool persists after editing cells."""
        automation = GUIAutomation()

        automation.select_tool(app, "mine")
        automation.click_cell(app, 0, 0)

        # Tool should still be mine
        assert_tool_selected(app, "mine")

    def test_tool_persists_after_solver_run(self, app):
        """Test that selected tool persists after running solver."""
        automation = GUIAutomation()

        automation.select_tool(app, "number")
        app.number_var.set("3")

        # Set up board and run solver
        automation.set_cell_number(app, 0, 0, 1)
        automation.run_solver(app)

        # Tool should still be number
        assert_tool_selected(app, "number")

    def test_tool_state_after_board_clear(self, app):
        """Test tool state after clearing board."""
        automation = GUIAutomation()

        automation.select_tool(app, "mine")
        automation.clear_board(app)

        # Tool should remain selected
        assert_tool_selected(app, "mine")

    def test_tool_state_after_new_board(self, app):
        """Test tool state after creating new board."""
        automation = GUIAutomation()

        automation.select_tool(app, "number")
        automation.create_new_board(app, 9, 9, 10)

        # Tool should persist
        assert_tool_selected(app, "number")


class TestToolErrorHandling:
    """Tests for tool error handling."""

    def test_invalid_tool_name_raises_error(self, app):
        """Test that invalid tool name raises ValueError."""
        automation = GUIAutomation()

        with pytest.raises(ValueError) as exc_info:
            automation.select_tool(app, "invalid_tool")

        assert "Invalid tool" in str(exc_info.value)

    def test_invalid_number_raises_error(self, app):
        """Test that invalid number value raises ValueError."""
        automation = GUIAutomation()

        with pytest.raises(ValueError) as exc_info:
            automation.select_number_tool(app, 10)

        assert "Number must be between 0 and 8" in str(exc_info.value)

    def test_negative_number_raises_error(self, app):
        """Test that negative number raises ValueError."""
        automation = GUIAutomation()

        with pytest.raises(ValueError) as exc_info:
            automation.select_number_tool(app, -1)

        assert "Number must be between 0 and 8" in str(exc_info.value)
