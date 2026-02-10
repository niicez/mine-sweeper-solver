"""
Minesweeper Solver - Constraint Satisfaction Problem (CSP) based solver.

This module provides a comprehensive Minesweeper solver using:
1. Constraint propagation for deterministic deductions
2. Constraint comparison for advanced deductions
3. Probability calculation for optimal guessing
4. Mistake analysis for learning

Author: Production-Grade Solver
"""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Tuple, Optional, FrozenSet


class CellState(Enum):
    """Represents the state of a cell on the board."""

    UNKNOWN = -1  # Unrevealed cell
    MINE = -2  # Flagged mine
    EMPTY_0 = 0  # Revealed with 0 adjacent mines
    EMPTY_1 = 1  # Revealed with 1 adjacent mine
    EMPTY_2 = 2
    EMPTY_3 = 3
    EMPTY_4 = 4
    EMPTY_5 = 5
    EMPTY_6 = 6
    EMPTY_7 = 7
    EMPTY_8 = 8


@dataclass(frozen=True)
class Position:
    """Represents a position on the Minesweeper board."""

    row: int
    col: int

    def __add__(self, other: Position) -> Position:
        return Position(self.row + other.row, self.col + other.col)

    def neighbors(self, max_row: int, max_col: int) -> List[Position]:
        """Get all valid neighboring positions (8-directional)."""
        deltas = [
            Position(-1, -1),
            Position(-1, 0),
            Position(-1, 1),
            Position(0, -1),
            Position(0, 1),
            Position(1, -1),
            Position(1, 0),
            Position(1, 1),
        ]
        neighbors = []
        for delta in deltas:
            new_pos = self + delta
            if 0 <= new_pos.row < max_row and 0 <= new_pos.col < max_col:
                neighbors.append(new_pos)
        return neighbors


@dataclass
class Constraint:
    """Represents a constraint: sum of cells equals a value."""

    cells: FrozenSet[Position]
    mine_count: int

    def __post_init__(self):
        if not isinstance(self.cells, frozenset):
            object.__setattr__(self, "cells", frozenset(self.cells))

    def is_satisfied(self, assignments: Dict[Position, bool]) -> bool:
        """Check if constraint is satisfied given cell assignments."""
        known_cells = {c for c in self.cells if c in assignments}
        unknown_cells = self.cells - known_cells

        if not unknown_cells:
            # All cells assigned, check if sum matches
            actual_count = sum(1 for c in self.cells if assignments.get(c, False))
            return actual_count == self.mine_count

        # Check if remaining mines can fit in unknown cells
        assigned_mines = sum(1 for c in known_cells if assignments[c])
        remaining_mines = self.mine_count - assigned_mines

        if remaining_mines < 0 or remaining_mines > len(unknown_cells):
            return False

        return True

    def is_subset(self, other: Constraint) -> bool:
        """Check if this constraint's cells are a subset of other's cells."""
        return self.cells < other.cells

    def __hash__(self) -> int:
        return hash((self.cells, self.mine_count))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Constraint):
            return False
        return self.cells == other.cells and self.mine_count == other.mine_count


@dataclass
class MinesweeperBoard:
    """Represents a Minesweeper game board."""

    rows: int
    cols: int
    total_mines: int
    grid: List[List[CellState]] = field(default_factory=list)

    def __post_init__(self):
        if not self.grid:
            self.grid = [
                [CellState.UNKNOWN for _ in range(self.cols)] for _ in range(self.rows)
            ]

    def get(self, pos: Position) -> CellState:
        """Get cell state at position."""
        return self.grid[pos.row][pos.col]

    def set(self, pos: Position, state: CellState) -> None:
        """Set cell state at position."""
        self.grid[pos.row][pos.col] = state

    def get_number(self, pos: Position) -> int:
        """Get the number value of a revealed cell, -1 if not a number."""
        state = self.get(pos)
        if state.value >= 0:  # EMPTY_0 to EMPTY_8 have values 0-8
            return state.value
        return -1

    def is_revealed(self, pos: Position) -> bool:
        """Check if cell is revealed."""
        return self.get(pos).value >= 0  # EMPTY_0 to EMPTY_8 have values 0-8

    def is_unknown(self, pos: Position) -> bool:
        """Check if cell is unrevealed."""
        return self.get(pos) == CellState.UNKNOWN

    def is_flagged(self, pos: Position) -> bool:
        """Check if cell is flagged as mine."""
        return self.get(pos) == CellState.MINE

    def get_all_positions(self) -> List[Position]:
        """Get all positions on the board."""
        positions = []
        for r in range(self.rows):
            for c in range(self.cols):
                positions.append(Position(r, c))
        return positions

    def get_unknown_cells(self) -> Set[Position]:
        """Get all unrevealed cells."""
        return {pos for pos in self.get_all_positions() if self.is_unknown(pos)}

    def get_revealed_numbers(self) -> Dict[Position, int]:
        """Get all revealed cells with their numbers."""
        result = {}
        for pos in self.get_all_positions():
            num = self.get_number(pos)
            if num >= 0:
                result[pos] = num
        return result

    def copy(self) -> MinesweeperBoard:
        """Create a deep copy of the board."""
        new_board = MinesweeperBoard(self.rows, self.cols, self.total_mines)
        new_board.grid = [[cell for cell in row] for row in self.grid]
        return new_board

    def to_string(
        self,
        mine_char: str = "X",
        clear_char: str = ".",
        unknown_char: str = "?",
        zero_char: str = " ",
    ) -> str:
        """Convert board to string representation."""
        lines = []
        for row in self.grid:
            line = ""
            for cell in row:
                if cell == CellState.MINE:
                    line += mine_char
                elif cell == CellState.UNKNOWN:
                    line += unknown_char
                elif cell == CellState.EMPTY_0:
                    line += zero_char
                else:
                    line += str(cell.value)
            lines.append(line)
        return "\n".join(lines)

    @staticmethod
    def from_string(
        board_str: str,
        total_mines: int,
        mine_char: str = "X",
        clear_chars: str = "0123456789. ",
        unknown_char: str = "?",
    ) -> MinesweeperBoard:
        """Create board from string representation."""
        # Strip and split, then filter out empty lines
        lines = [line.strip() for line in board_str.strip().split("\n") if line.strip()]
        rows = len(lines)
        cols = len(lines[0]) if lines else 0

        board = MinesweeperBoard(rows, cols, total_mines)

        for r, line in enumerate(lines):
            for c, char in enumerate(line):
                pos = Position(r, c)
                if char == mine_char:
                    board.set(pos, CellState.MINE)
                elif char == unknown_char:
                    board.set(pos, CellState.UNKNOWN)
                elif char in clear_chars:
                    if char == " " or char == ".":
                        board.set(pos, CellState.EMPTY_0)
                    else:
                        board.set(pos, CellState(int(char)))

        return board


@dataclass
class SolverConfig:
    """Configuration for the Minesweeper solver."""

    mine_marker: str = "X"
    safe_marker: str = "O"
    unknown_marker: str = "?"
    use_constraint_comparison: bool = True
    use_probability_calculation: bool = True
    max_combinations: int = 100000


@dataclass
class SolverResult:
    """Result from the solver."""

    safe_cells: Set[Position] = field(default_factory=set)
    mines: Set[Position] = field(default_factory=set)
    probabilities: Dict[Position, float] = field(default_factory=dict)
    constraints: List[Constraint] = field(default_factory=list)
    is_solvable: bool = True
    message: str = ""


class MinesweeperSolver:
    """
    Constraint Satisfaction Problem based Minesweeper solver.

    Uses multiple strategies:
    1. Basic constraint propagation (simple deduction)
    2. Constraint subset comparison (advanced deduction)
    3. Probability calculation for optimal guessing
    """

    def __init__(self, config: Optional[SolverConfig] = None):
        self.config = config or SolverConfig()

    def solve(self, board: MinesweeperBoard) -> SolverResult:
        """
        Solve the current state of the Minesweeper board.

        Returns safe cells (guaranteed not mines), mines (guaranteed mines),
        and probabilities for uncertain cells.
        """
        result = SolverResult()

        # Step 1: Extract constraints from revealed numbers
        constraints = self._extract_constraints(board)
        result.constraints = constraints

        # Step 2: Basic constraint propagation
        self._propagate_constraints(board, constraints, result)

        # Step 3: Advanced constraint comparison (if enabled)
        if self.config.use_constraint_comparison:
            self._compare_constraints(constraints, result)

        # Step 4: Calculate probabilities for remaining unknown cells
        if self.config.use_probability_calculation:
            self._calculate_probabilities(board, constraints, result)

        return result

    def _extract_constraints(self, board: MinesweeperBoard) -> List[Constraint]:
        """Extract constraints from revealed number cells."""
        constraints = []

        for pos in board.get_all_positions():
            number = board.get_number(pos)
            if number < 0:
                continue

            # Get all adjacent cells
            neighbors = pos.neighbors(board.rows, board.cols)
            unknown_neighbors = [n for n in neighbors if board.is_unknown(n)]
            flagged_neighbors = [n for n in neighbors if board.is_flagged(n)]

            if not unknown_neighbors:
                continue

            # Remaining mines = number - flagged neighbors
            remaining_mines = number - len(flagged_neighbors)

            if remaining_mines < 0 or remaining_mines > len(unknown_neighbors):
                # Inconsistent state
                continue

            constraint = Constraint(
                cells=frozenset(unknown_neighbors), mine_count=remaining_mines
            )
            constraints.append(constraint)

        return constraints

    def _propagate_constraints(
        self,
        board: MinesweeperBoard,
        constraints: List[Constraint],
        result: SolverResult,
    ) -> None:
        """Apply basic constraint propagation."""
        changed = True
        while changed:
            changed = False

            for constraint in constraints:
                if constraint.mine_count == 0:
                    # All cells are safe
                    for cell in constraint.cells:
                        if cell not in result.safe_cells and cell not in result.mines:
                            result.safe_cells.add(cell)
                            changed = True

                elif constraint.mine_count == len(constraint.cells):
                    # All cells are mines
                    for cell in constraint.cells:
                        if cell not in result.mines and cell not in result.safe_cells:
                            result.mines.add(cell)
                            changed = True

    def _compare_constraints(
        self, constraints: List[Constraint], result: SolverResult
    ) -> None:
        """
        Compare constraints to find subset relationships.
        If A is a subset of B, we can derive new constraints from B - A.
        """
        changed = True
        max_iterations = 100
        iteration = 0

        while changed and iteration < max_iterations:
            changed = False
            iteration += 1

            # Convert to list for indexing
            constraint_list = list(constraints)

            for i, c1 in enumerate(constraint_list):
                for j, c2 in enumerate(constraint_list):
                    if i >= j:
                        continue

                    # Check if c1 is a subset of c2
                    if c1.cells < c2.cells:
                        diff_cells = c2.cells - c1.cells
                        diff_mines = c2.mine_count - c1.mine_count

                        if diff_mines == 0:
                            # All cells in diff are safe
                            for cell in diff_cells:
                                if (
                                    cell not in result.safe_cells
                                    and cell not in result.mines
                                ):
                                    result.safe_cells.add(cell)
                                    changed = True
                        elif diff_mines == len(diff_cells):
                            # All cells in diff are mines
                            for cell in diff_cells:
                                if (
                                    cell not in result.mines
                                    and cell not in result.safe_cells
                                ):
                                    result.mines.add(cell)
                                    changed = True

    def _calculate_probabilities(
        self,
        board: MinesweeperBoard,
        constraints: List[Constraint],
        result: SolverResult,
    ) -> None:
        """
        Calculate exact mine probabilities for boundary cells.
        Uses combinatorial enumeration with pruning.
        """
        # Get boundary cells (unknown cells adjacent to revealed numbers)
        boundary_cells: Set[Position] = set()
        for constraint in constraints:
            boundary_cells.update(constraint.cells)

        # Get non-boundary unknown cells
        all_unknown = board.get_unknown_cells()
        non_boundary = all_unknown - boundary_cells

        # Get known mine count
        flagged_count = sum(
            1 for pos in board.get_all_positions() if board.is_flagged(pos)
        )
        remaining_mines = board.total_mines - flagged_count

        if not boundary_cells:
            # No boundary, use simple probability
            total_unknown = len(all_unknown)
            if total_unknown > 0:
                prob = remaining_mines / total_unknown
                for cell in all_unknown:
                    result.probabilities[cell] = prob
            return

        # Enumerate all valid configurations
        cell_list = sorted(boundary_cells, key=lambda p: (p.row, p.col))

        if len(cell_list) > 20:  # Too many cells for enumeration
            # Use simple heuristic
            for cell in boundary_cells:
                # Count how many constraints include this cell
                count = sum(1 for c in constraints if cell in c.cells)
                # Approximate probability
                result.probabilities[cell] = min(0.99, count * 0.15)
            return

        # Count valid configurations
        mine_counts: Dict[Position, int] = {cell: 0 for cell in cell_list}
        valid_configs = 0

        for r in range(len(cell_list) + 1):
            if r > remaining_mines:
                break

            for combo in itertools.combinations(range(len(cell_list)), r):
                # Create assignment
                assignment: Dict[Position, bool] = {}
                for i, cell in enumerate(cell_list):
                    assignment[cell] = i in combo

                # Check all constraints
                valid = all(c.is_satisfied(assignment) for c in constraints)

                if valid:
                    # Check if total mines doesn't exceed remaining
                    total_in_config = r
                    if total_in_config <= remaining_mines:
                        valid_configs += 1
                        for cell, is_mine in assignment.items():
                            if is_mine:
                                mine_counts[cell] += 1

        # Calculate probabilities
        if valid_configs > 0:
            for cell in cell_list:
                result.probabilities[cell] = mine_counts[cell] / valid_configs

        # Calculate probability for non-boundary cells
        if non_boundary:
            # Average probability that remaining mines are in non-boundary
            avg_boundary_mines = (
                sum(mine_counts.values()) / valid_configs if valid_configs > 0 else 0
            )
            expected_remaining = remaining_mines - avg_boundary_mines
            if len(non_boundary) > 0:
                non_boundary_prob = max(
                    0, min(1, expected_remaining / len(non_boundary))
                )
                for cell in non_boundary:
                    result.probabilities[cell] = non_boundary_prob


class MistakeAnalyzer:
    """Analyzes Minesweeper mistakes to help players learn."""

    def analyze_move(
        self,
        board: MinesweeperBoard,
        move: Position,
        was_mine: bool,
        solver: MinesweeperSolver,
    ) -> str:
        """
        Analyze a move to explain why it was right or wrong.

        Args:
            board: Board state before the move
            move: Position that was clicked
            was_mine: Whether the move hit a mine
            solver: Solver instance to check what could have been deduced

        Returns:
            Detailed analysis message
        """
        if was_mine:
            return self._analyze_mistake(board, move, solver)
        else:
            return self._analyze_safe_move(board, move, solver)

    def _analyze_mistake(
        self, board: MinesweeperBoard, move: Position, solver: MinesweeperSolver
    ) -> str:
        """Analyze why clicking a mine was a mistake."""
        result = solver.solve(board)

        if move in result.mines:
            return (
                f"CRITICAL ERROR: Position ({move.row}, {move.col}) was a guaranteed mine! "
                f"You should have flagged it instead of clicking. "
                f"The solver determined this was definitely a mine based on the constraints."
            )

        if move in result.probabilities:
            prob = result.probabilities[move]
            if prob > 0.5:
                return (
                    f"RISKY MOVE: Position ({move.row}, {move.col}) had a {prob * 100:.1f}% "
                    f"chance of being a mine. High probability squares should be avoided. "
                    f"Look for cells with lower probabilities (ideally safe cells marked with 'O')."
                )
            else:
                return (
                    f"UNLUCKY: Position ({move.row}, {move.col}) only had a {prob * 100:.1f}% "
                    f"chance of being a mine, but you hit it. "
                    f"Sometimes you need to guess - consider flagging certain mines first "
                    f"to get more information before guessing."
                )

        return f"Position ({move.row}, {move.col}) was a mine. Always check the solver's recommendations before clicking."

    def _analyze_safe_move(
        self, board: MinesweeperBoard, move: Position, solver: MinesweeperSolver
    ) -> str:
        """Analyze a safe move to provide feedback."""
        result = solver.solve(board)

        if move in result.safe_cells:
            return (
                f"EXCELLENT: Position ({move.row}, {move.col}) was a guaranteed safe cell! "
                f"You correctly identified this was safe based on the constraints. "
                f"This is the type of logical deduction that wins games."
            )

        if move in result.probabilities:
            prob = result.probabilities[move]
            if prob < 0.1:
                return (
                    f"GOOD MOVE: Position ({move.row}, {move.col}) had only {prob * 100:.1f}% "
                    f"chance of being a mine. Low probability guesses are smart when "
                    f"no guaranteed safe cells are available."
                )

        # Check if there was a better move available
        if result.safe_cells:
            safe_list = list(result.safe_cells)[:3]
            safe_str = ", ".join(f"({p.row}, {p.col})" for p in safe_list)
            return (
                f"ACCEPTABLE: Position ({move.row}, {move.col}) was safe. "
                f"However, there were guaranteed safe cells available: {safe_str}. "
                f"Always check for guaranteed safe moves before guessing."
            )

        return f"GOOD: Position ({move.row}, {move.col}) was safe."

    def get_hint(self, board: MinesweeperBoard, solver: MinesweeperSolver) -> str:
        """Get a hint for the current board state."""
        result = solver.solve(board)

        if result.safe_cells:
            safe = list(result.safe_cells)[0]
            return (
                f"HINT: Cell ({safe.row}, {safe.col}) is guaranteed safe. "
                f"Click it to reveal more information."
            )

        if result.mines:
            mine = list(result.mines)[0]
            return (
                f"HINT: Cell ({mine.row}, {mine.col}) is definitely a mine. "
                f"Flag it to reduce the constraints."
            )

        if result.probabilities:
            # Find lowest probability cell
            min_prob = min(result.probabilities.values())
            best_cells = [
                p
                for p, prob in result.probabilities.items()
                if abs(prob - min_prob) < 0.001
            ]
            if best_cells:
                best = best_cells[0]
                return (
                    f"HINT: No guaranteed safe cells. Cell ({best.row}, {best.col}) "
                    f"has the lowest mine probability ({min_prob * 100:.1f}%). "
                    f"Consider clicking it if you must guess."
                )

        return "No hints available - the board state is ambiguous."

    def generate_lesson(
        self, board: MinesweeperBoard, solver: MinesweeperSolver
    ) -> str:
        """Generate a lesson explaining the current board state."""
        result = solver.solve(board)

        lesson = []
        lesson.append("=" * 50)
        lesson.append("MINESWEEPER ANALYSIS LESSON")
        lesson.append("=" * 50)

        # Explain constraints
        lesson.append(f"\nActive Constraints: {len(result.constraints)}")
        for i, constraint in enumerate(result.constraints[:5], 1):
            cells_str = ", ".join(
                f"({p.row},{p.col})" for p in list(constraint.cells)[:3]
            )
            if len(constraint.cells) > 3:
                cells_str += f" ... (+{len(constraint.cells) - 3} more)"
            lesson.append(
                f"  {i}. Cells [{cells_str}] must contain exactly {constraint.mine_count} mines"
            )

        if len(result.constraints) > 5:
            lesson.append(f"  ... and {len(result.constraints) - 5} more constraints")

        # Explain deductions
        if result.safe_cells:
            lesson.append(f"\nGuaranteed Safe Cells: {len(result.safe_cells)}")
            for pos in list(result.safe_cells)[:3]:
                lesson.append(f"  - ({pos.row}, {pos.col})")
            if len(result.safe_cells) > 3:
                lesson.append(f"  ... and {len(result.safe_cells) - 3} more")

        if result.mines:
            lesson.append(f"\nGuaranteed Mines: {len(result.mines)}")
            for pos in list(result.mines)[:3]:
                lesson.append(f"  - ({pos.row}, {pos.col}) - FLAG THIS!")
            if len(result.mines) > 3:
                lesson.append(f"  ... and {len(result.mines) - 3} more")

        # Strategy advice
        lesson.append("\n" + "-" * 50)
        lesson.append("STRATEGY ADVICE:")
        lesson.append("-" * 50)

        if result.safe_cells:
            lesson.append("Priority 1: Click all guaranteed safe cells first.")
        elif result.mines:
            lesson.append("Priority 1: Flag all guaranteed mines first.")
            lesson.append(
                "Priority 2: After flagging, check if new deductions become available."
            )
        else:
            lesson.append("No guaranteed moves available. You must guess.")
            lesson.append("Pick the cell with the LOWEST probability of being a mine.")

        lesson.append("\n" + "=" * 50)

        return "\n".join(lesson)


# Export main classes
__all__ = [
    "MinesweeperSolver",
    "MinesweeperBoard",
    "SolverConfig",
    "SolverResult",
    "MistakeAnalyzer",
    "Position",
    "Constraint",
    "CellState",
]
