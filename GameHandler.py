import time
import tkinter as tk
from tkinter import messagebox

import Board
import Player
import fileReading
import random as rd
import RandomStrategy
import GreedyStrategy


class GameHandler:
    def __init__(self, player1, player2, root=None):
        self.root = root if root is not None else tk.Tk()
        self.players = [player1, player2]   # 0 = P1, 1 = P2
        self.current_player = 0             # 0 = P1, 1 = P2
        self.score = [0, 0]
        self.matrix = fileReading.load_board_until_ok()
        self.dimMat = len(self.matrix)
        self.last_move = None

        # Create Board and link this handler
        self.board = Board.Board(self)

    def play(self):
        # If P1 is a computer, let it start
        if not self.players[0].is_human:
            self.computer_turn()

        self.board.set_visible()
        print("the game has started")

    # ---- Helpers for ending the game ----
    def has_any_legal_moves(self) -> bool:
        """
        Returns True if at least one button is currently clickable (state='normal').
        Assumes Board.update_active_buttons(...) has set button states correctly.
        """
        for row_btns in self.board.grid_buttons:
            for btn in row_btns:
                if str(btn['state']) == 'normal':
                    return True
        return False

    def end_game_and_announce(self):
        """Disable the board and pop up a winner dialog."""
        self.board.disable_all_buttons()

        p1, p2 = self.score
        if p1 > p2:
            winner = "Player 1"
        elif p2 > p1:
            winner = "Player 2"
        else:
            winner = None  # tie

        if winner:
            message = f"🎉 {winner} wins!\n\nScores:\nPlayer 1: {p1}\nPlayer 2: {p2}"
        else:
            message = f"🤝 It's a tie!\n\nScores:\nPlayer 1: {p1}\nPlayer 2: {p2}"

        messagebox.showinfo("Game Over", message)

    # ---- Computer turn (AI) ----
    def computer_turn(self):
        self.board.disable_all_buttons()
        player = self.players[self.current_player]
        move_result = player.move(self.matrix, self.last_move, self.score)
        if move_result is None:
            # No legal moves for this player → game over
            self.end_game_and_announce()
            return
        row, col = move_result
        self.handle_cell_click(row, col)

    # ---- Handle a click from the board (human or AI) ----
    def handle_cell_click(self, row, col):
        print(f"[DEBUG] Player {self.current_player+1} clicked ({row}, {col})")

        # Update score for the current player
        self.score[self.current_player] += self.matrix[row][col]
        self.board.update_scores()

        # Update matrix (mark cell as taken)
        self.matrix[row][col] = "-"

        # Update the button on the board
        button = self.board.grid_buttons[row][col]
        button.config(text="-", state="disabled", bg="#555")

        self.last_move = (row, col)

        # Switch player
        self.current_player = 1 if self.current_player == 0 else 0
        self.board.highlight_current_player(self.current_player)

        # Enable legal buttons for the NEXT player based on the last move
        self.board.update_active_buttons(row, col)

        # If the next player has no legal moves, end now
        if not self.has_any_legal_moves():
            # Small delay so UI shows the last click before the dialog
            self.root.after(100, self.end_game_and_announce)
            return

        # If the next player is a computer, schedule its move
        if not self.players[self.current_player].is_human:
            self.root.after(1000, self.computer_turn)
