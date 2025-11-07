import tkinter as tk
import Player
import Strategy
from GameHandler import GameHandler

class GameSetup: 
    def __init__(self):
        self.root = tk.Tk() # own set-up window
        self.root.title("Game Start")
        self.root.geometry("320x260")
        self.root.config(bg="#222")
        self.player_choice = {"p1": None, "p2": None}
        self.show_start_page()


    def run(self): 
        self.root.mainloop()
        return self.player_choice

    # start page
    def show_start_page(self): 
        self.clear_window()
        
        # title
        tk.Label(self.root, text="Welcome to the Row-Column Game!", 
                 font=("Helvetica", 20, "bold"), fg="white",bg="#222").pack(pady=40)
        
        # START button
        tk.Button(self.root, text="START", width=15, height=2, command=self.show_setup_page).pack(pady=10)
        
        # Instructions button
        tk.Button(self.root, text="Instructions", width=15, height=2, command=self.show_instructions).pack(pady=10)


    # switches to instruction page
    def show_instructions(self): 
        self.clear_window()

        tk.Label(self.root, text="Row-Column Game Instructions", font=("Helvetica", 20, "bold")).pack(pady=20)

        # Go back button
        tk.Button(self.root, text="Go back to start page", command=self.show_start_page).pack(pady=10)


    # switches to setup page
    def show_setup_page(self): 
        self.clear_window()

        # Title
        title = tk.Label(self.root, text="Row-Column Game Setup", font=("Helvetica", 20, "bold"))
        title.pack(pady=20)

        # Container (Player 1 vs. Player 2)
        container = tk.Frame(self.root, bg="#222")
        container.pack(expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=0)
        container.grid_columnconfigure(2, weight=1)

        # Player 1 label
        tk.Label(container, text="Player 1", font=("Arial", 16, "bold"),
                fg="white", bg="#222").grid(row=0, column=0, pady=10)
        
        # Player 2 label
        tk.Label(container, text="Player 2", font=("Arial", 16, "bold"),
                fg="white", bg="#222").grid(row=0, column=2, pady=10)
        
        # vs. label
        tk.Label(container, text="VS.", font=("Arial", 16, "bold"),
                fg="white", bg="#222").grid(row=0, column=1, pady=30)
        
        # Player 1 Buttons
        self.p1_human = tk.Button(container, text="Human", width=12,
                                  command=lambda: self.select_player("p1", "human"))
        self.p1_human.grid(row=1, column=0, pady=5)

        self.p1_computer = tk.Button(container, text="Computer", width=12, 
                                     command=lambda: self.select_player("p1", "computer"))
        self.p1_computer.grid(row=2, column=0, pady=5)
        
        # Player 2 Buttons
        self.p2_human = tk.Button(container, text="Human", width=12,
                                  command=lambda: self.select_player("p2", "human"))
        self.p2_human.grid(row=1, column=2, pady=5)

        self.p2_computer = tk.Button(container, text="Computer", width=12, 
                                     command=lambda: self.select_player("p2", "computer"))
        self.p2_computer.grid(row=2, column=2, pady=5)

        # Go back button
        tk.Button(self.root, text="Go back to start page", command=self.show_start_page).pack(pady=10)

        # Start the game button
        self.start_button = tk.Button(self.root, text="Start Game", 
                                      command=self.finish_setup, state="disabled")
        self.start_button.pack(pady=10)


    def select_player(self, player, choice): 
        if player == "p1": 
            if choice == "human": 
                self.p1_computer.config(state="disabled")
            else: 
                self.p1_human.config(state="disabled")
        else: 
            if choice == "human": 
                self.p2_computer.config(state="disabled")
            else: 
                self.p2_human.config(state="disabled")

        self.player_choice[player] = choice
        # if both players have chosen, activate the 'Start' button
        if self.player_choice["p1"] and self.player_choice["p2"]: 
            self.start_button.config(state="normal")

    def finish_setup(self): 
        self.root.destroy()

    def clear_window(self): 
          for widget in self.root.winfo_children():
            widget.destroy()
