"""
Minesweeper Solver - Example Usage and Demo

This script demonstrates how to use the Minesweeper solver and mistake analyzer.

Usage:
    python example.py
"""

import sys

sys.path.insert(0, "D:\\Labs\\mine-sweeper-solver\\src")

from minesweeper_solver import (
    MinesweeperSolver,
    MinesweeperBoard,
    SolverConfig,
    SolverResult,
    MistakeAnalyzer,
    Position,
    CellState,
)


def demo_basic_solver():
    """Demonstrate basic solver functionality."""
    print("=" * 60)
    print("DEMO: Basic Solver Functionality")
    print("=" * 60)

    # Create a sample board state
    board_str = """
    12?
    ??X
    ???
    """

    board = MinesweeperBoard.from_string(board_str, total_mines=3)

    print("\nBoard State:")
    print(board.to_string())
    print(f"\nTotal mines: {board.total_mines}")

    # Solve the board
    solver = MinesweeperSolver()
    result = solver.solve(board)

    print(f"\nSolver Results:")
    print(f"  Guaranteed safe cells: {len(result.safe_cells)}")
    for pos in sorted(result.safe_cells, key=lambda p: (p.row, p.col)):
        print(f"    - ({pos.row}, {pos.col})")

    print(f"\n  Guaranteed mines: {len(result.mines)}")
    for pos in sorted(result.mines, key=lambda p: (p.row, p.col)):
        print(f"    - ({pos.row}, {pos.col}) [FLAG THIS!]")

    print(f"\n  Constraints found: {len(result.constraints)}")

    print(f"\n  Mine probabilities for uncertain cells:")
    sorted_probs = sorted(result.probabilities.items(), key=lambda x: x[1])
    for pos, prob in sorted_probs[:5]:
        print(f"    - ({pos.row}, {pos.col}): {prob * 100:.1f}%")


def demo_mistake_analyzer():
    """Demonstrate mistake analysis functionality."""
    print("\n" + "=" * 60)
    print("DEMO: Mistake Analysis")
    print("=" * 60)

    analyzer = MistakeAnalyzer()
    solver = MinesweeperSolver()

    # Example 1: Good move
    print("\nExample 1: Analyzing a good move")
    board_str = """
    0??
    ???
    ???
    """
    board = MinesweeperBoard.from_string(board_str, total_mines=5)

    # (0,1) is safe because it's adjacent to a 0
    analysis = analyzer.analyze_move(
        board, Position(0, 1), was_mine=False, solver=solver
    )
    print(f"Board:\n{board.to_string()}")
    print(f"\nMove: Clicked (0, 1)")
    print(f"Analysis: {analysis}")

    # Example 2: Bad move (clicked a mine)
    print("\n" + "-" * 60)
    print("\nExample 2: Analyzing a mistake (clicked a guaranteed mine)")
    board_str = """
    1?
    """
    board = MinesweeperBoard.from_string(board_str, total_mines=1)

    # (0,1) is definitely a mine
    analysis = analyzer.analyze_move(
        board, Position(0, 1), was_mine=True, solver=solver
    )
    print(f"Board:\n{board.to_string()}")
    print(f"\nMove: Clicked (0, 1)")
    print(f"Analysis: {analysis}")

    # Example 3: Get a hint
    print("\n" + "-" * 60)
    print("\nExample 3: Getting a hint")
    board_str = """
    12?
    ??X
    ???
    """
    board = MinesweeperBoard.from_string(board_str, total_mines=3)
    hint = analyzer.get_hint(board, solver)
    print(f"Board:\n{board.to_string()}")
    print(f"\nHint: {hint}")


def demo_custom_config():
    """Demonstrate custom configuration."""
    print("\n" + "=" * 60)
    print("DEMO: Custom Configuration")
    print("=" * 60)

    # Create custom config
    config = SolverConfig(
        mine_marker="M",
        safe_marker="S",
        unknown_marker=".",
        use_constraint_comparison=True,
        use_probability_calculation=True,
    )

    solver = MinesweeperSolver(config)

    board_str = """
    12?
    ??X
    ???
    """
    board = MinesweeperBoard.from_string(board_str, total_mines=3)

    print(f"\nCustom markers:")
    print(f"  Mine marker: {config.mine_marker}")
    print(f"  Safe marker: {config.safe_marker}")
    print(f"  Unknown marker: {config.unknown_marker}")

    result = solver.solve(board)
    print(
        f"\nSolver found {len(result.safe_cells)} safe cells and {len(result.mines)} mines"
    )


def demo_learning_mode():
    """Demonstrate learning mode with lesson generation."""
    print("\n" + "=" * 60)
    print("DEMO: Learning Mode")
    print("=" * 60)

    analyzer = MistakeAnalyzer()
    solver = MinesweeperSolver()

    # Complex board for lesson
    board_str = """
    12?
    ??X
    ???
    """
    board = MinesweeperBoard.from_string(board_str, total_mines=3)

    print("\nGenerating lesson for current board state...\n")
    lesson = analyzer.generate_lesson(board, solver)
    print(lesson)


def demo_stress_test():
    """Demonstrate stress testing."""
    print("\n" + "=" * 60)
    print("DEMO: Stress Testing")
    print("=" * 60)

    import random

    solver = MinesweeperSolver()

    print("\nRunning stress test with 100 random boards...")

    success_count = 0
    for i in range(100):
        # Generate random board parameters
        rows = random.randint(5, 10)
        cols = random.randint(5, 10)
        total_mines = random.randint(3, min(rows * cols - 1, 15))

        # Create random board with some revealed cells
        board = MinesweeperBoard(rows, cols, total_mines)

        # Randomly reveal some cells (simulating game progress)
        for _ in range(random.randint(5, 15)):
            r, c = random.randint(0, rows - 1), random.randint(0, cols - 1)
            pos = Position(r, c)
            # Randomly set as revealed with number 0-3
            if board.is_unknown(pos):
                board.set(pos, CellState(random.randint(0, 3)))

        try:
            result = solver.solve(board)
            # Verify result consistency
            overlap = result.safe_cells & result.mines
            if len(overlap) == 0:
                success_count += 1
        except Exception as e:
            print(f"  Error on test {i}: {e}")

    print(f"\nStress test complete: {success_count}/100 boards solved without errors")
    print(f"Success rate: {success_count}%")


def demo_interactive():
    """Interactive demo where user can input a board."""
    print("\n" + "=" * 60)
    print("INTERACTIVE DEMO")
    print("=" * 60)
    print("\nEnter a Minesweeper board (use digits 0-8, X for mines, ? for unknown):")
    print("Enter 'done' on a new line when finished.")
    print("Example:")
    print("  12?")
    print("  ??X")
    print("  ???")
    print()

    lines = []
    while True:
        try:
            line = input("> ").strip()
            if line.lower() == "done":
                break
            if line:
                lines.append(line)
        except EOFError:
            break

    if not lines:
        print("No board entered. Using default example.")
        lines = ["12?", "??X", "???"]

    board_str = "\n".join(lines)

    try:
        total_mines = int(
            input("\nEnter total number of mines on board: ").strip() or "3"
        )
    except (ValueError, EOFError):
        total_mines = 3

    board = MinesweeperBoard.from_string(board_str, total_mines)

    print(f"\nParsed board:")
    print(board.to_string())

    solver = MinesweeperSolver()
    result = solver.solve(board)

    print(f"\nSolver Results:")
    print(f"  Safe cells: {len(result.safe_cells)}")
    for pos in sorted(result.safe_cells, key=lambda p: (p.row, p.col)):
        print(f"    ({pos.row}, {pos.col})")

    print(f"\n  Mines to flag: {len(result.mines)}")
    for pos in sorted(result.mines, key=lambda p: (p.row, p.col)):
        print(f"    ({pos.row}, {pos.col})")

    if result.probabilities:
        print(f"\n  Uncertain cells (probabilities):")
        for pos, prob in sorted(result.probabilities.items(), key=lambda x: x[1])[:10]:
            status = (
                "SAFE"
                if pos in result.safe_cells
                else "MINE" if pos in result.mines else "?"
            )
            print(f"    ({pos.row}, {pos.col}): {prob * 100:.1f}% [{status}]")


def demo_gui():
    """Launch the GUI board editor."""
    print("\n" + "=" * 60)
    print("LAUNCHING GUI BOARD EDITOR")
    print("=" * 60)
    print("\nStarting the graphical board editor...")

    try:
        sys.path.insert(0, "D:\\Labs\\mine-sweeper-solver\\ui")
        from ui import main as gui_main

        gui_main()
    except ImportError as e:
        print(f"Error: Could not launch GUI. {e}")
        print("Make sure tkinter is installed.")


def main():
    """Run all demos."""
    import sys

    print("\n" + "=" * 60)
    print("MINESWEEPER SOLVER - COMPREHENSIVE DEMO")
    print("=" * 60)

    # Run all demos
    demo_basic_solver()
    demo_mistake_analyzer()
    demo_custom_config()
    demo_learning_mode()
    demo_stress_test()

    # Ask if user wants interactive demo
    print("\n" + "=" * 60)
    try:
        response = (
            input("\nWould you like to try the interactive demo? (y/n): ")
            .strip()
            .lower()
        )
        if response == "y":
            demo_interactive()
    except (EOFError, KeyboardInterrupt):
        pass

    # Ask if user wants to launch GUI
    print("\n" + "=" * 60)
    try:
        response = (
            input("\nWould you like to launch the GUI board editor? (y/n): ")
            .strip()
            .lower()
        )
        if response == "y":
            demo_gui()
    except (EOFError, KeyboardInterrupt):
        pass

    print("\n" + "=" * 60)
    print("Demo complete! Thanks for using the Minesweeper Solver.")
    print("=" * 60)


if __name__ == "__main__":
    main()
