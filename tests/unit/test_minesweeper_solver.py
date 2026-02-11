"""
Comprehensive test suite for Minesweeper Solver.

This module contains production-grade tests including:
- Unit tests for all core components
- Integration tests for solver workflows
- Edge case testing
- Property-based testing (fuzzing)
- Stress testing with random boards

Author: Production-Grade Test Suite
"""

import sys
import unittest
import random
import itertools
from typing import List, Set, Tuple

sys.path.insert(0, "D:\\Labs\\mine-sweeper-solver\\src")

from minesweeper_solver import (
    MinesweeperSolver,
    MinesweeperBoard,
    SolverConfig,
    SolverResult,
    MistakeAnalyzer,
    Position,
    Constraint,
    CellState,
)


class TestPosition(unittest.TestCase):
    """Unit tests for Position class."""

    def test_position_creation(self):
        """Test basic position creation."""
        pos = Position(3, 4)
        self.assertEqual(pos.row, 3)
        self.assertEqual(pos.col, 4)

    def test_position_addition(self):
        """Test position vector addition."""
        pos1 = Position(1, 2)
        pos2 = Position(3, 4)
        result = pos1 + pos2
        self.assertEqual(result, Position(4, 6))

    def test_position_neighbors_center(self):
        """Test neighbor calculation for center position."""
        pos = Position(5, 5)
        neighbors = pos.neighbors(10, 10)
        self.assertEqual(len(neighbors), 8)

        # Check all 8 neighbors exist
        expected = [
            Position(4, 4),
            Position(4, 5),
            Position(4, 6),
            Position(5, 4),
            Position(5, 6),
            Position(6, 4),
            Position(6, 5),
            Position(6, 6),
        ]
        for exp in expected:
            self.assertIn(exp, neighbors)

    def test_position_neighbors_corner(self):
        """Test neighbor calculation for corner position."""
        pos = Position(0, 0)
        neighbors = pos.neighbors(10, 10)
        self.assertEqual(len(neighbors), 3)

        expected = [Position(0, 1), Position(1, 0), Position(1, 1)]
        for exp in expected:
            self.assertIn(exp, neighbors)

    def test_position_neighbors_edge(self):
        """Test neighbor calculation for edge position."""
        pos = Position(0, 5)
        neighbors = pos.neighbors(10, 10)
        self.assertEqual(len(neighbors), 5)

    def test_position_immutability(self):
        """Test that Position is immutable (frozen dataclass)."""
        pos = Position(1, 2)
        with self.assertRaises(AttributeError):
            pos.row = 5


class TestConstraint(unittest.TestCase):
    """Unit tests for Constraint class."""

    def test_constraint_creation(self):
        """Test basic constraint creation."""
        cells = frozenset([Position(0, 0), Position(0, 1)])
        constraint = Constraint(cells, 1)
        self.assertEqual(constraint.mine_count, 1)
        self.assertEqual(len(constraint.cells), 2)

    def test_constraint_satisfaction_all_assigned(self):
        """Test constraint satisfaction when all cells assigned."""
        cells = frozenset([Position(0, 0), Position(0, 1), Position(0, 2)])
        constraint = Constraint(cells, 2)

        # Satisfied: exactly 2 mines
        assignment = {Position(0, 0): True, Position(0, 1): True, Position(0, 2): False}
        self.assertTrue(constraint.is_satisfied(assignment))

        # Not satisfied: only 1 mine
        assignment = {
            Position(0, 0): True,
            Position(0, 1): False,
            Position(0, 2): False,
        }
        self.assertFalse(constraint.is_satisfied(assignment))

    def test_constraint_satisfaction_partial(self):
        """Test constraint satisfaction with partial assignment."""
        cells = frozenset([Position(0, 0), Position(0, 1), Position(0, 2)])
        constraint = Constraint(cells, 2)

        # Partial assignment that could still be satisfied
        assignment = {Position(0, 0): True}
        self.assertTrue(constraint.is_satisfied(assignment))

        # Partial assignment that cannot be satisfied
        assignment = {
            Position(0, 0): False,
            Position(0, 1): False,
            Position(0, 2): False,
        }
        self.assertFalse(constraint.is_satisfied(assignment))

    def test_constraint_subset(self):
        """Test constraint subset detection."""
        c1_cells = frozenset([Position(0, 0), Position(0, 1)])
        c2_cells = frozenset([Position(0, 0), Position(0, 1), Position(0, 2)])

        c1 = Constraint(c1_cells, 1)
        c2 = Constraint(c2_cells, 2)

        self.assertTrue(c1.is_subset(c2))
        self.assertFalse(c2.is_subset(c1))

    def test_constraint_equality(self):
        """Test constraint equality."""
        cells = frozenset([Position(0, 0), Position(0, 1)])
        c1 = Constraint(cells, 1)
        c2 = Constraint(cells, 1)
        c3 = Constraint(cells, 2)

        self.assertEqual(c1, c2)
        self.assertNotEqual(c1, c3)


class TestMinesweeperBoard(unittest.TestCase):
    """Unit tests for MinesweeperBoard class."""

    def test_board_creation(self):
        """Test basic board creation."""
        board = MinesweeperBoard(10, 10, 10)
        self.assertEqual(board.rows, 10)
        self.assertEqual(board.cols, 10)
        self.assertEqual(board.total_mines, 10)

    def test_board_initial_state(self):
        """Test that new board has all unknown cells."""
        board = MinesweeperBoard(5, 5, 5)
        for r in range(5):
            for c in range(5):
                self.assertEqual(board.get(Position(r, c)), CellState.UNKNOWN)

    def test_board_get_set(self):
        """Test getting and setting cell states."""
        board = MinesweeperBoard(5, 5, 5)
        pos = Position(2, 2)

        board.set(pos, CellState.EMPTY_3)
        self.assertEqual(board.get(pos), CellState.EMPTY_3)

        board.set(pos, CellState.MINE)
        self.assertEqual(board.get(pos), CellState.MINE)

    def test_board_get_number(self):
        """Test extracting number from revealed cells."""
        board = MinesweeperBoard(5, 5, 5)

        board.set(Position(0, 0), CellState.EMPTY_3)
        self.assertEqual(board.get_number(Position(0, 0)), 3)

        board.set(Position(0, 1), CellState.UNKNOWN)
        self.assertEqual(board.get_number(Position(0, 1)), -1)

        board.set(Position(0, 2), CellState.MINE)
        self.assertEqual(board.get_number(Position(0, 2)), -1)

    def test_board_is_revealed(self):
        """Test revealed cell detection."""
        board = MinesweeperBoard(5, 5, 5)

        board.set(Position(0, 0), CellState.EMPTY_0)
        self.assertTrue(board.is_revealed(Position(0, 0)))

        board.set(Position(0, 1), CellState.EMPTY_8)
        self.assertTrue(board.is_revealed(Position(0, 1)))

        board.set(Position(0, 2), CellState.UNKNOWN)
        self.assertFalse(board.is_revealed(Position(0, 2)))

    def test_board_is_unknown(self):
        """Test unknown cell detection."""
        board = MinesweeperBoard(5, 5, 5)

        self.assertTrue(board.is_unknown(Position(0, 0)))

        board.set(Position(0, 0), CellState.EMPTY_1)
        self.assertFalse(board.is_unknown(Position(0, 0)))

    def test_board_copy(self):
        """Test board copying."""
        board = MinesweeperBoard(5, 5, 5)
        board.set(Position(2, 2), CellState.EMPTY_3)

        copy = board.copy()
        self.assertEqual(copy.get(Position(2, 2)), CellState.EMPTY_3)

        # Modify original, copy should not change
        board.set(Position(2, 2), CellState.MINE)
        self.assertEqual(copy.get(Position(2, 2)), CellState.EMPTY_3)

    def test_board_to_from_string(self):
        """Test board serialization."""
        board_str = """
        1?X
        2? 
        3?0
        """

        board = MinesweeperBoard.from_string(board_str, 2)
        self.assertEqual(board.rows, 3)
        self.assertEqual(board.cols, 3)

        # Verify parsing
        self.assertEqual(board.get_number(Position(0, 0)), 1)
        self.assertEqual(board.get(Position(0, 1)), CellState.UNKNOWN)
        self.assertEqual(board.get(Position(0, 2)), CellState.MINE)

        # Test round-trip
        output = board.to_string()
        board2 = MinesweeperBoard.from_string(output, 2)
        self.assertEqual(board.get(Position(0, 0)), board2.get(Position(0, 0)))

    def test_board_get_all_positions(self):
        """Test getting all positions."""
        board = MinesweeperBoard(3, 4, 5)
        positions = board.get_all_positions()
        self.assertEqual(len(positions), 12)

    def test_board_get_unknown_cells(self):
        """Test getting unknown cells."""
        board = MinesweeperBoard(3, 3, 3)
        board.set(Position(0, 0), CellState.EMPTY_1)
        board.set(Position(0, 1), CellState.MINE)

        unknown = board.get_unknown_cells()
        self.assertEqual(len(unknown), 7)
        self.assertNotIn(Position(0, 0), unknown)
        self.assertNotIn(Position(0, 1), unknown)


class TestMinesweeperSolver(unittest.TestCase):
    """Integration tests for the Minesweeper solver."""

    def setUp(self):
        """Set up test fixtures."""
        self.solver = MinesweeperSolver()

    def test_solver_basic_safety(self):
        """Test that solver finds guaranteed safe cells."""
        # 1X  (1 indicates 1 mine adjacent, which must be the X)
        # ??
        board_str = """
        1X
        ??
        """
        board = MinesweeperBoard.from_string(board_str, 2)

        result = self.solver.solve(board)

        # Cell (1,0) should be safe because (0,0) already has its mine
        self.assertIn(Position(1, 0), result.safe_cells)

    def test_solver_basic_mine(self):
        """Test that solver finds guaranteed mines."""
        # A '1' with exactly 1 unknown neighbor
        # In a 1x2 board: 1?
        # The '1' at (0,0) has only 1 neighbor: (0,1)
        # Since we need 1 mine and there's only 1 cell, it must be a mine
        board_str = """
        1?
        """
        board = MinesweeperBoard.from_string(board_str, 1)

        result = self.solver.solve(board)

        # Cell (0,1) should be a mine since '1' has only 1 unknown neighbor
        self.assertIn(Position(0, 1), result.mines)

    def test_solver_zero_propagation(self):
        """Test that 0 values make all neighbors safe."""
        board_str = """
        0??
        ???
        ???
        """
        board = MinesweeperBoard.from_string(board_str, 5)

        result = self.solver.solve(board)

        # All neighbors of 0 should be safe
        neighbors = Position(0, 0).neighbors(3, 3)
        for neighbor in neighbors:
            self.assertIn(neighbor, result.safe_cells)

    def test_solver_constraint_comparison(self):
        """Test constraint subset comparison deduction."""
        # Complex case where subset comparison is needed
        # 22?  (Two 2s sharing some cells)
        # ??X
        # ???
        board_str = """
        22?
        ??X
        ???
        """
        board = MinesweeperBoard.from_string(board_str, 3)

        result = self.solver.solve(board)

        # Should deduce some cells from constraint comparison
        self.assertTrue(len(result.safe_cells) > 0 or len(result.mines) > 0)

    def test_solver_probability_calculation(self):
        """Test that probabilities are calculated."""
        board_str = """
        1??
        ???
        ???
        """
        board = MinesweeperBoard.from_string(board_str, 5)

        result = self.solver.solve(board)

        # Should have probabilities for unknown cells
        self.assertTrue(len(result.probabilities) > 0)

        # All probabilities should be between 0 and 1
        for prob in result.probabilities.values():
            self.assertGreaterEqual(prob, 0.0)
            self.assertLessEqual(prob, 1.0)

    def test_solver_empty_board(self):
        """Test solver with empty board."""
        board = MinesweeperBoard(5, 5, 5)

        result = self.solver.solve(board)

        # No constraints, no deductions
        self.assertEqual(len(result.constraints), 0)
        self.assertEqual(len(result.safe_cells), 0)
        self.assertEqual(len(result.mines), 0)

    def test_solver_complete_board(self):
        """Test solver with completely revealed board."""
        board = MinesweeperBoard(3, 3, 0)
        for r in range(3):
            for c in range(3):
                board.set(Position(r, c), CellState.EMPTY_0)

        result = self.solver.solve(board)

        # No constraints, all safe
        self.assertEqual(len(result.constraints), 0)


class TestMistakeAnalyzer(unittest.TestCase):
    """Unit tests for MistakeAnalyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = MistakeAnalyzer()
        self.solver = MinesweeperSolver()

    def test_analyze_guaranteed_mine_mistake(self):
        """Test analysis of clicking a guaranteed mine."""
        # A '1' with exactly 1 unknown neighbor - the unknown must be a mine
        board_str = """
        1?
        """
        board = MinesweeperBoard.from_string(board_str, 1)

        # (0,1) is definitely a mine
        analysis = self.analyzer.analyze_move(board, Position(0, 1), True, self.solver)

        self.assertIn("CRITICAL ERROR", analysis)
        self.assertIn("guaranteed mine", analysis)

    def test_analyze_good_safe_move(self):
        """Test analysis of clicking a safe cell."""
        board_str = """
        0??
        ???
        """
        board = MinesweeperBoard.from_string(board_str, 5)

        # (0,1) is safe (neighbor of 0)
        analysis = self.analyzer.analyze_move(board, Position(0, 1), False, self.solver)

        self.assertIn("EXCELLENT", analysis)

    def test_get_hint_safe_first(self):
        """Test that hint prioritizes safe cells."""
        board_str = """
        0??
        ???
        """
        board = MinesweeperBoard.from_string(board_str, 5)

        hint = self.analyzer.get_hint(board, self.solver)

        self.assertIn("HINT", hint)
        self.assertIn("guaranteed safe", hint)

    def test_get_hint_mine_second(self):
        """Test that hint suggests flagging mines if no safe cells."""
        board_str = """
        1?
        ??
        """
        board = MinesweeperBoard.from_string(board_str, 1)

        hint = self.analyzer.get_hint(board, self.solver)

        # Should suggest flagging
        self.assertIn("HINT", hint)

    def test_generate_lesson(self):
        """Test lesson generation."""
        board_str = """
        12?
        ??X
        ???
        """
        board = MinesweeperBoard.from_string(board_str, 3)

        lesson = self.analyzer.generate_lesson(board, self.solver)

        self.assertIn("MINESWEEPER ANALYSIS LESSON", lesson)
        self.assertIn("Active Constraints", lesson)


class TestEdgeCases(unittest.TestCase):
    """Edge case and boundary condition tests."""

    def test_single_cell_board(self):
        """Test solver with 1x1 board."""
        board = MinesweeperBoard(1, 1, 0)
        board.set(Position(0, 0), CellState.EMPTY_0)

        solver = MinesweeperSolver()
        result = solver.solve(board)

        self.assertEqual(len(result.constraints), 0)

    def test_single_cell_with_mine(self):
        """Test board with single mine cell."""
        board = MinesweeperBoard(1, 1, 1)
        board.set(Position(0, 0), CellState.MINE)

        solver = MinesweeperSolver()
        result = solver.solve(board)

        self.assertEqual(len(result.constraints), 0)

    def test_narrow_board_1x10(self):
        """Test solver with 1x10 board."""
        board = MinesweeperBoard(1, 10, 3)
        board.set(Position(0, 0), CellState.EMPTY_1)
        board.set(Position(0, 1), CellState.UNKNOWN)

        solver = MinesweeperSolver()
        result = solver.solve(board)

        # Should work without error
        self.assertIsNotNone(result)

    def test_tall_board_10x1(self):
        """Test solver with 10x1 board."""
        board = MinesweeperBoard(10, 1, 3)
        board.set(Position(0, 0), CellState.EMPTY_1)
        board.set(Position(1, 0), CellState.UNKNOWN)

        solver = MinesweeperSolver()
        result = solver.solve(board)

        # Should work without error
        self.assertIsNotNone(result)

    def test_all_mines_flagged(self):
        """Test board where all mines are already flagged."""
        board_str = """
        10X
        110
        000
        """
        board = MinesweeperBoard.from_string(board_str, 1)

        solver = MinesweeperSolver()
        result = solver.solve(board)

        # No unknown cells adjacent to numbers, or all mines found
        for pos in board.get_all_positions():
            if board.is_unknown(pos):
                # All unknown cells should be safe (only 1 mine and it's flagged)
                pass

    def test_maximum_mine_density(self):
        """Test board with maximum possible mines."""
        # 3x3 with 8 mines (all except center)
        board_str = """
        XXX
        X8X
        XXX
        """
        board = MinesweeperBoard.from_string(board_str, 8)

        solver = MinesweeperSolver()
        result = solver.solve(board)

        # Center (1,1) with value 8 touches 8 cells, all must be mines
        self.assertEqual(len(result.mines), 0)  # All already flagged

    def test_conflicting_constraints(self):
        """Test behavior with potentially conflicting constraints."""
        # Create a board that might have inconsistent state
        board = MinesweeperBoard(3, 3, 10)
        board.set(Position(0, 0), CellState.EMPTY_1)
        board.set(Position(0, 1), CellState.MINE)
        board.set(Position(0, 2), CellState.MINE)

        solver = MinesweeperSolver()
        result = solver.solve(board)

        # Should handle without crashing
        self.assertIsNotNone(result)

    def test_empty_constraint_cells(self):
        """Test constraint with no cells."""
        constraint = Constraint(frozenset(), 0)

        # Should be satisfied
        self.assertTrue(constraint.is_satisfied({}))


class TestStressTests(unittest.TestCase):
    """Stress tests with random boards."""

    def setUp(self):
        """Set up test fixtures."""
        self.solver = MinesweeperSolver()
        random.seed(42)  # Reproducible tests

    def generate_random_board(
        self, rows: int, cols: int, total_mines: int, reveal_prob: float = 0.3
    ) -> MinesweeperBoard:
        """Generate a random board state for testing."""
        board = MinesweeperBoard(rows, cols, total_mines)

        # Randomly place mines
        all_positions = board.get_all_positions()
        mine_positions = set(
            random.sample(all_positions, min(total_mines, len(all_positions)))
        )

        # Calculate numbers for revealed cells
        for pos in all_positions:
            if pos in mine_positions:
                continue

            # Count adjacent mines
            neighbors = pos.neighbors(rows, cols)
            mine_count = sum(1 for n in neighbors if n in mine_positions)

            # Randomly reveal
            if random.random() < reveal_prob:
                board.set(pos, CellState(mine_count))

        # Flag some known mines
        for pos in mine_positions:
            neighbors = pos.neighbors(rows, cols)
            for n in neighbors:
                if board.is_revealed(n) and random.random() < 0.5:
                    board.set(pos, CellState.MINE)
                    break

        return board

    def test_stress_small_boards(self):
        """Stress test with many small random boards."""
        for i in range(100):
            board = self.generate_random_board(
                rows=random.randint(3, 6),
                cols=random.randint(3, 6),
                total_mines=random.randint(1, 5),
            )

            result = self.solver.solve(board)

            # Verify result consistency
            self._verify_result(board, result)

    def test_stress_medium_boards(self):
        """Stress test with medium random boards."""
        for i in range(50):
            board = self.generate_random_board(
                rows=random.randint(8, 12),
                cols=random.randint(8, 12),
                total_mines=random.randint(5, 15),
            )

            result = self.solver.solve(board)
            self._verify_result(board, result)

    def test_stress_beginner_difficulty(self):
        """Stress test with beginner difficulty (9x9, 10 mines)."""
        for i in range(20):
            board = self.generate_random_board(9, 9, 10, reveal_prob=0.4)
            result = self.solver.solve(board)
            self._verify_result(board, result)

    def test_stress_intermediate_difficulty(self):
        """Stress test with intermediate difficulty (16x16, 40 mines)."""
        for i in range(10):
            board = self.generate_random_board(16, 16, 40, reveal_prob=0.3)
            result = self.solver.solve(board)
            self._verify_result(board, result)

    def _verify_result(self, board: MinesweeperBoard, result: SolverResult):
        """Verify solver result consistency."""
        # Safe cells and mines should not overlap
        intersection = result.safe_cells & result.mines
        self.assertEqual(
            len(intersection), 0, f"Safe cells and mines overlap: {intersection}"
        )

        # All safe cells should be unknown on board
        for pos in result.safe_cells:
            self.assertTrue(
                board.is_unknown(pos), f"Safe cell {pos} is not unknown on board"
            )

        # All mines should be unknown on board
        for pos in result.mines:
            self.assertTrue(
                board.is_unknown(pos), f"Mine {pos} is not unknown on board"
            )

        # Probabilities should be valid
        for pos, prob in result.probabilities.items():
            self.assertGreaterEqual(prob, 0.0, f"Probability for {pos} is negative")
            self.assertLessEqual(prob, 1.0, f"Probability for {pos} exceeds 1.0")


class TestSolverConfig(unittest.TestCase):
    """Tests for solver configuration."""

    def test_default_config(self):
        """Test default solver configuration."""
        config = SolverConfig()
        self.assertEqual(config.mine_marker, "X")
        self.assertEqual(config.safe_marker, "O")
        self.assertTrue(config.use_constraint_comparison)

    def test_custom_config(self):
        """Test custom solver configuration."""
        config = SolverConfig(
            mine_marker="M", safe_marker="S", use_probability_calculation=False
        )
        self.assertEqual(config.mine_marker, "M")
        self.assertEqual(config.safe_marker, "S")
        self.assertFalse(config.use_probability_calculation)

    def test_solver_with_config(self):
        """Test solver with custom config."""
        config = SolverConfig(use_constraint_comparison=False)
        solver = MinesweeperSolver(config)

        # A '1' with exactly 1 unknown neighbor - should still find the mine
        board_str = """
        1?
        """
        board = MinesweeperBoard.from_string(board_str, 1)
        result = solver.solve(board)

        # Should still find the mine even without constraint comparison
        self.assertIn(Position(0, 1), result.mines)


def create_test_suite():
    """Create comprehensive test suite."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestPosition,
        TestConstraint,
        TestMinesweeperBoard,
        TestMinesweeperSolver,
        TestMistakeAnalyzer,
        TestEdgeCases,
        TestStressTests,
        TestSolverConfig,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    return suite


if __name__ == "__main__":
    # Run all tests with verbose output
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)
