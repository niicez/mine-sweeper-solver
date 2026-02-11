"""
Minesweeper Board Editor GUI

A user-friendly interface for creating and editing Minesweeper boards,
with real-time solver integration.

Usage:
    python -m ui.board_editor
"""

from __future__ import annotations

import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Tuple

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


class CellStyles:
    """Visual styles for different cell states."""

    # Colors
    COLOR_UNKNOWN = "#BFBFBF"  # Gray for unrevealed
    COLOR_REVEALED = "#FFFFFF"  # White for revealed
    COLOR_MINE = "#FF6B6B"  # Red for mines
    COLOR_SAFE = "#51CF66"  # Green for safe cells
    COLOR_FLAGGED = "#FFD93D"  # Yellow for flagged
    COLOR_HOVER = "#D4D4D4"  # Light gray for hover

    # Text colors for numbers
    NUMBER_COLORS = {
        0: "#FFFFFF",
        1: "#0066CC",
        2: "#009900",
        3: "#CC0000",
        4: "#660099",
        5: "#990000",
        6: "#009999",
        7: "#000000",
        8: "#808080",
    }

    # Icons (Unicode symbols)
    ICON_UNKNOWN = ""
    ICON_FLAG = ""
    ICON_MINE = ""
    ICON_SAFE = ""
    ICON_PROBABILITY = ""


class BoardCell:
    """Represents a single cell in the GUI board."""

    def __init__(self, canvas: tk.Canvas, row: int, col: int, size: int = 40):
        self.canvas = canvas
        self.row = row
        self.col = col
        self.size = size
        self.x1 = col * size
        self.y1 = row * size
        self.x2 = self.x1 + size
        self.y2 = self.y1 + size
        self.center_x = self.x1 + size // 2
        self.center_y = self.y1 + size // 2

        self.state = CellState.UNKNOWN
        self.is_hovered = False
        self.is_probability_cell = False
        self.probability = 0.0
        self.highlight_color: Optional[str] = None  # Track solver highlight color

        # Create canvas items
        self.rect_id: Optional[int] = None
        self.text_id: Optional[int] = None
        self.icon_id: Optional[int] = None

        self._create_cell()

    def _create_cell(self):
        """Create the cell rectangle on canvas."""
        self.rect_id = self.canvas.create_rectangle(
            self.x1,
            self.y1,
            self.x2,
            self.y2,
            fill=CellStyles.COLOR_UNKNOWN,
            outline="#808080",
            width=1,
        )

    def update_state(self, state: CellState):
        """Update the visual state of the cell."""
        self.state = state
        self._update_visuals()

    def set_probability(self, prob: float):
        """Set probability display for this cell."""
        self.probability = prob
        self.is_probability_cell = True
        self._update_visuals()

    def clear_probability(self):
        """Clear probability display."""
        self.probability = 0.0
        self.is_probability_cell = False
        self._update_visuals()

    def _update_visuals(self):
        """Update the visual appearance based on state."""
        # Clear existing text/icon
        if self.text_id:
            self.canvas.delete(self.text_id)
            self.text_id = None
        if self.icon_id:
            self.canvas.delete(self.icon_id)
            self.icon_id = None

        # Set background color
        if self.state == CellState.UNKNOWN:
            bg_color = CellStyles.COLOR_UNKNOWN
        elif self.state == CellState.MINE:
            bg_color = CellStyles.COLOR_FLAGGED
        elif self.state.value >= 0:
            bg_color = CellStyles.COLOR_REVEALED
        else:
            bg_color = CellStyles.COLOR_UNKNOWN

        # Apply probability highlight
        if self.is_probability_cell and self.state == CellState.UNKNOWN:
            # Blend with probability color
            if self.probability > 0.5:
                bg_color = CellStyles.COLOR_MINE
            elif self.probability < 0.3:
                bg_color = CellStyles.COLOR_SAFE

        if self.rect_id is not None:
            self.canvas.itemconfig(self.rect_id, fill=bg_color)

        # Add text/icon based on state
        if self.state == CellState.UNKNOWN:
            if self.is_probability_cell:
                # Show probability
                prob_text = f"{self.probability * 100:.0f}%"
                color = "#000000" if self.probability < 0.5 else "#FFFFFF"
                self.text_id = self.canvas.create_text(
                    self.center_x,
                    self.center_y,
                    text=prob_text,
                    fill=color,
                    font=("Arial", 8, "bold"),
                )
            else:
                # Empty unknown cell
                pass

        elif self.state == CellState.MINE:
            # Mine flag
            self.icon_id = self.canvas.create_text(
                self.center_x,
                self.center_y,
                text=CellStyles.ICON_FLAG,
                fill="#000000",
                font=("Segoe UI Emoji", 20),
            )

        elif self.state.value == 0:
            # Empty revealed cell (no number)
            pass

        else:
            # Number cell
            num = self.state.value
            color = CellStyles.NUMBER_COLORS.get(num, "#000000")
            self.text_id = self.canvas.create_text(
                self.center_x,
                self.center_y,
                text=str(num),
                fill=color,
                font=("Arial", 16, "bold"),
            )

    def set_hover(self, hovered: bool):
        """Set hover state."""
        self.is_hovered = hovered
        if self.state == CellState.UNKNOWN and self.rect_id is not None:
            # Don't change color if cell has a solver highlight
            if self.highlight_color is not None:
                return
            color = CellStyles.COLOR_HOVER if hovered else CellStyles.COLOR_UNKNOWN
            self.canvas.itemconfig(self.rect_id, fill=color)

    def highlight(self, color: str):
        """Temporarily highlight the cell."""
        if self.rect_id is not None:
            self.highlight_color = color
            self.canvas.itemconfig(self.rect_id, fill=color)

    def clear_highlight(self):
        """Remove highlight and restore normal state."""
        self.highlight_color = None
        self._update_visuals()

    def contains(self, x: int, y: int) -> bool:
        """Check if point is inside this cell."""
        return self.x1 <= x < self.x2 and self.y1 <= y < self.y2


class MinesweeperBoardEditor:
    """Main GUI application for the Minesweeper board editor."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Minesweeper Board Editor & Solver")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)

        # Initialize solver
        self.solver = MinesweeperSolver()
        self.analyzer = MistakeAnalyzer()

        # Board state
        self.rows = 10
        self.cols = 10
        self.total_mines = 10
        self.cell_size = 40
        self.board: Optional[MinesweeperBoard] = None
        self.cells: Dict[Tuple[int, int], BoardCell] = {}

        # Editor mode
        self.current_tool = "unknown"  # unknown, mine, number
        self.current_number = 0

        # Solver results
        self.last_result: Optional[SolverResult] = None

        self._create_ui()
        self._create_new_board()

    def _create_ui(self):
        """Create the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - Board canvas
        self._create_board_panel(main_frame)

        # Right panel - Controls
        self._create_control_panel(main_frame)

        # Bottom panel - Results
        self._create_results_panel()

    def _create_board_panel(self, parent: ttk.Frame):
        """Create the board canvas panel."""
        board_frame = ttk.LabelFrame(parent, text="Board Editor", padding=10)
        board_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas with scrollbars
        canvas_frame = ttk.Frame(board_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg="#E0E0E0",
            highlightthickness=1,
            highlightbackground="#808080",
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbars
        h_scroll = ttk.Scrollbar(
            canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview
        )
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        v_scroll = ttk.Scrollbar(
            canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview
        )
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        # Bind mouse events
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<Motion>", self._on_canvas_hover)

    def _create_control_panel(self, parent: ttk.Frame):
        """Create the control panel."""
        control_frame = ttk.LabelFrame(parent, text="Controls", padding=10, width=300)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        control_frame.pack_propagate(False)

        # Board settings
        settings_frame = ttk.LabelFrame(
            control_frame, text="Board Settings", padding=10
        )
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        # Rows
        ttk.Label(settings_frame, text="Rows:").grid(row=0, column=0, sticky=tk.W)
        self.rows_var = tk.StringVar(value="10")
        rows_spin = ttk.Spinbox(
            settings_frame, from_=5, to=30, textvariable=self.rows_var, width=10
        )
        rows_spin.grid(row=0, column=1, padx=5)

        # Columns
        ttk.Label(settings_frame, text="Columns:").grid(row=1, column=0, sticky=tk.W)
        self.cols_var = tk.StringVar(value="10")
        cols_spin = ttk.Spinbox(
            settings_frame, from_=5, to=30, textvariable=self.cols_var, width=10
        )
        cols_spin.grid(row=1, column=1, padx=5)

        # Total mines
        ttk.Label(settings_frame, text="Total Mines:").grid(
            row=2, column=0, sticky=tk.W
        )
        self.mines_var = tk.StringVar(value="10")
        mines_spin = ttk.Spinbox(
            settings_frame, from_=1, to=50, textvariable=self.mines_var, width=10
        )
        mines_spin.grid(row=2, column=1, padx=5)

        # New board button
        ttk.Button(
            settings_frame, text="Create New Board", command=self._create_new_board
        ).grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky=tk.EW)

        # Tools frame
        tools_frame = ttk.LabelFrame(control_frame, text="Editing Tools", padding=10)
        tools_frame.pack(fill=tk.X, pady=(0, 10))

        # Tool buttons
        self.tool_var = tk.StringVar(value="unknown")

        ttk.Radiobutton(
            tools_frame,
            text="Unclear Cell (?)",
            variable=self.tool_var,
            value="unknown",
            command=self._on_tool_change,
        ).pack(anchor=tk.W, pady=2)

        ttk.Radiobutton(
            tools_frame,
            text="Marked Mine (X)",
            variable=self.tool_var,
            value="mine",
            command=self._on_tool_change,
        ).pack(anchor=tk.W, pady=2)

        ttk.Radiobutton(
            tools_frame,
            text="Revealed Number",
            variable=self.tool_var,
            value="number",
            command=self._on_tool_change,
        ).pack(anchor=tk.W, pady=2)

        # Number selector
        number_frame = ttk.Frame(tools_frame)
        number_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(number_frame, text="Number:").pack(side=tk.LEFT)
        self.number_var = tk.StringVar(value="0")
        number_combo = ttk.Combobox(
            number_frame,
            textvariable=self.number_var,
            values=["0", "1", "2", "3", "4", "5", "6", "7", "8"],
            width=5,
            state="readonly",
        )
        number_combo.pack(side=tk.LEFT, padx=5)
        number_combo.bind("<<ComboboxSelected>>", lambda e: self._on_tool_change())

        # Solver frame
        solver_frame = ttk.LabelFrame(control_frame, text="Solver", padding=10)
        solver_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            solver_frame,
            text="Solve Board",
            command=self._solve_board,
            style="Accent.TButton",
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            solver_frame, text="Show Probabilities", command=self._show_probabilities
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            solver_frame,
            text="Clear Solver Results",
            command=self._clear_solver_results,
        ).pack(fill=tk.X, pady=2)

        ttk.Button(solver_frame, text="Get Hint", command=self._get_hint).pack(
            fill=tk.X, pady=2
        )

        # Import/Export frame
        io_frame = ttk.LabelFrame(control_frame, text="Import/Export", padding=10)
        io_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            io_frame, text="Load from String", command=self._load_from_string
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            io_frame, text="Export to String", command=self._export_to_string
        ).pack(fill=tk.X, pady=2)

        ttk.Button(io_frame, text="Clear Board", command=self._clear_board).pack(
            fill=tk.X, pady=2
        )

        # Legend
        legend_frame = ttk.LabelFrame(control_frame, text="Legend", padding=10)
        legend_frame.pack(fill=tk.X, pady=(0, 10))

        legends = [
            (CellStyles.COLOR_UNKNOWN, "Unclear Cell"),
            (CellStyles.COLOR_REVEALED, "Revealed/Cleared"),
            (CellStyles.COLOR_FLAGGED, "Marked Mine"),
            (CellStyles.COLOR_SAFE, "Safe (Solver)"),
            (CellStyles.COLOR_MINE, "Dangerous (Solver)"),
        ]

        for color, text in legends:
            frame = ttk.Frame(legend_frame)
            frame.pack(fill=tk.X, pady=1)

            canvas = tk.Canvas(
                frame, width=20, height=20, bg=color, highlightthickness=1
            )
            canvas.pack(side=tk.LEFT)

            ttk.Label(frame, text=text).pack(side=tk.LEFT, padx=5)

    def _create_results_panel(self):
        """Create the results display panel."""
        results_frame = ttk.LabelFrame(self.root, text="Solver Results", padding=10)
        results_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Results text with scrollbar
        text_frame = ttk.Frame(results_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.results_text = tk.Text(
            text_frame, height=8, wrap=tk.WORD, font=("Consolas", 10)
        )
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_frame, command=self.results_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.configure(yscrollcommand=scrollbar.set)

        self.results_text.insert(
            tk.END, "Ready. Create a board and click 'Solve Board' to analyze."
        )
        self.results_text.configure(state=tk.DISABLED)

    def _create_new_board(self):
        """Create a new board with current settings."""
        try:
            self.rows = int(self.rows_var.get())
            self.cols = int(self.cols_var.get())
            self.total_mines = int(self.mines_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid board settings")
            return

        # Clear canvas
        self.canvas.delete("all")
        self.cells.clear()

        # Create new board
        self.board = MinesweeperBoard(self.rows, self.cols, self.total_mines)

        # Calculate canvas size
        canvas_width = self.cols * self.cell_size
        canvas_height = self.rows * self.cell_size
        self.canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))

        # Create cells
        for row in range(self.rows):
            for col in range(self.cols):
                cell = BoardCell(self.canvas, row, col, self.cell_size)
                self.cells[(row, col)] = cell

        self._update_results(
            "New board created. Use editing tools to set up the board state."
        )

    def _on_canvas_click(self, event):
        """Handle canvas click."""
        self._handle_canvas_action(event.x, event.y)

    def _on_canvas_drag(self, event):
        """Handle canvas drag."""
        self._handle_canvas_action(event.x, event.y)

    def _handle_canvas_action(self, x: int, y: int):
        """Handle click or drag on canvas."""
        # Get canvas coordinates
        canvas_x = self.canvas.canvasx(x)
        canvas_y = self.canvas.canvasy(y)

        # Find clicked cell
        for (row, col), cell in self.cells.items():
            if cell.contains(canvas_x, canvas_y):
                self._apply_tool(row, col)
                break

    def _apply_tool(self, row: int, col: int):
        """Apply current tool to a cell."""
        if not self.board:
            return

        pos = Position(row, col)
        tool = self.tool_var.get()

        if tool == "unknown":
            self.board.set(pos, CellState.UNKNOWN)
        elif tool == "mine":
            self.board.set(pos, CellState.MINE)
        elif tool == "number":
            try:
                num = int(self.number_var.get())
                self.board.set(pos, CellState(num))
            except ValueError:
                pass

        # Update cell display
        self.cells[(row, col)].update_state(self.board.get(pos))

        # Clear solver results when board changes
        self._clear_solver_results()
        self._update_results(
            "Ready. Board modified. Solver results cleared. Click 'Solve Board' to re-analyze."
        )

    def _on_canvas_hover(self, event):
        """Handle mouse hover over canvas."""
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        for cell in self.cells.values():
            was_hovered = cell.is_hovered
            is_hovered = cell.contains(canvas_x, canvas_y)

            if was_hovered != is_hovered:
                cell.set_hover(is_hovered)

    def _on_tool_change(self):
        """Handle tool selection change."""
        tool = self.tool_var.get()
        if tool == "number":
            try:
                self.current_number = int(self.number_var.get())
            except ValueError:
                pass

    def _solve_board(self):
        """Run solver on current board."""
        if not self.board:
            messagebox.showwarning("Warning", "No board to solve")
            return

        # Clear previous visual highlights before running solver
        self._clear_solver_highlights()

        self.last_result = self.solver.solve(self.board)

        # Highlight safe cells
        for pos in self.last_result.safe_cells:
            if (pos.row, pos.col) in self.cells:
                self.cells[(pos.row, pos.col)].highlight(CellStyles.COLOR_SAFE)

        # Highlight mines
        for pos in self.last_result.mines:
            if (pos.row, pos.col) in self.cells:
                self.cells[(pos.row, pos.col)].highlight(CellStyles.COLOR_MINE)

        # Build results message
        msg = []
        msg.append(f"Solver Analysis Results:")
        msg.append(f"  Constraints found: {len(self.last_result.constraints)}")
        msg.append(f"  Guaranteed safe cells: {len(self.last_result.safe_cells)}")
        msg.append(f"  Guaranteed mines: {len(self.last_result.mines)}")
        msg.append(
            f"  Cells with probability analysis: {len(self.last_result.probabilities)}"
        )

        if self.last_result.safe_cells:
            msg.append(f"\nSafe cells to click:")
            for pos in sorted(
                self.last_result.safe_cells, key=lambda p: (p.row, p.col)
            ):
                msg.append(f"  ({pos.row}, {pos.col})")

        if self.last_result.mines:
            msg.append(f"\nMines to flag:")
            for pos in sorted(self.last_result.mines, key=lambda p: (p.row, p.col)):
                msg.append(f"  ({pos.row}, {pos.col})")

        self._update_results("\n".join(msg))

    def _show_probabilities(self):
        """Display probability analysis on the board."""
        if not self.last_result:
            self._solve_board()

        if not self.last_result:
            return

        # Clear previous probabilities
        for cell in self.cells.values():
            cell.clear_probability()

        # Show probabilities
        for pos, prob in self.last_result.probabilities.items():
            if (pos.row, pos.col) in self.cells:
                self.cells[(pos.row, pos.col)].set_probability(prob)

        # Update results
        msg = []
        msg.append("Probability Analysis:")
        msg.append("(Showing probability of each cell being a mine)\n")

        sorted_probs = sorted(
            self.last_result.probabilities.items(), key=lambda x: x[1]
        )
        for pos, prob in sorted_probs:
            status = ""
            if pos in self.last_result.safe_cells:
                status = " [SAFE]"
            elif pos in self.last_result.mines:
                status = " [MINE]"
            msg.append(f"  ({pos.row}, {pos.col}): {prob * 100:.1f}%{status}")

        self._update_results("\n".join(msg))

    def _clear_solver_highlights(self):
        """Clear solver visual highlights without clearing results."""
        for cell in self.cells.values():
            cell.clear_highlight()
            cell.clear_probability()

    def _clear_solver_results(self):
        """Clear solver highlighting and results."""
        self._clear_solver_highlights()
        self.last_result = None

    def _get_hint(self):
        """Get a hint for the current board state."""
        if not self.board:
            messagebox.showwarning("Warning", "No board to analyze")
            return

        # Run solver first to get results for highlighting
        self._clear_solver_highlights()
        self.last_result = self.solver.solve(self.board)

        # Get hint text
        hint = self.analyzer.get_hint(self.board, self.solver)
        self._update_results(f"HINT:\n{hint}")

        # Highlight safe cells and mines from solver results
        for pos in self.last_result.safe_cells:
            if (pos.row, pos.col) in self.cells:
                self.cells[(pos.row, pos.col)].highlight(CellStyles.COLOR_SAFE)

        for pos in self.last_result.mines:
            if (pos.row, pos.col) in self.cells:
                self.cells[(pos.row, pos.col)].highlight(CellStyles.COLOR_MINE)

    def _load_from_string(self):
        """Load board from string representation."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Load Board from String")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(
            dialog,
            text="Enter board string (use digits 0-8, X for mines, ? for unknown):",
        ).pack(padx=10, pady=5)

        text = tk.Text(dialog, height=10, wrap=tk.NONE)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        ttk.Label(dialog, text="Total mines:").pack(padx=10)
        mines_entry = ttk.Entry(dialog)
        mines_entry.insert(0, "10")
        mines_entry.pack(padx=10, pady=5)

        def load():
            try:
                board_str = text.get("1.0", tk.END).strip()
                total_mines = int(mines_entry.get())

                self.board = MinesweeperBoard.from_string(board_str, total_mines)
                self.rows = self.board.rows
                self.cols = self.board.cols
                self.total_mines = total_mines

                # Update UI
                self.rows_var.set(str(self.rows))
                self.cols_var.set(str(self.cols))
                self.mines_var.set(str(self.total_mines))

                # Redraw board
                self._create_new_board()

                # Apply loaded state
                for (row, col), cell in self.cells.items():
                    pos = Position(row, col)
                    cell.update_state(self.board.get(pos))

                dialog.destroy()
                self._update_results("Board loaded from string.")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load board: {e}")

        ttk.Button(dialog, text="Load", command=load).pack(pady=10)

    def _export_to_string(self):
        """Export board to string representation."""
        if not self.board:
            messagebox.showwarning("Warning", "No board to export")
            return

        board_str = self.board.to_string()

        dialog = tk.Toplevel(self.root)
        dialog.title("Export Board to String")
        dialog.geometry("400x300")
        dialog.transient(self.root)

        text = tk.Text(dialog, height=10, wrap=tk.NONE)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert("1.0", board_str)
        text.configure(state=tk.DISABLED)

        ttk.Button(
            dialog,
            text="Copy to Clipboard",
            command=lambda: self._copy_to_clipboard(board_str),
        ).pack(pady=10)
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=5)

    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Success", "Copied to clipboard!")

    def _clear_board(self):
        """Clear the board to all unknown cells."""
        if not self.board:
            return

        for (row, col), cell in self.cells.items():
            pos = Position(row, col)
            self.board.set(pos, CellState.UNKNOWN)
            cell.update_state(CellState.UNKNOWN)

        self._clear_solver_results()
        self._update_results("Board cleared. All cells set to unknown.")

    def _update_results(self, text: str):
        """Update the results text area."""
        self.results_text.configure(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.configure(state=tk.DISABLED)


def main():
    """Run the board editor GUI."""
    root = tk.Tk()

    # Set theme
    style = ttk.Style()
    style.theme_use("clam")

    app = MinesweeperBoardEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
