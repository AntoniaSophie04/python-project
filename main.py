import GameHandler
import tkinter as tk
import RandomStrategy
import Player
from safe_choice_strategy import SafeChoiceStrategy
from GameSetup import GameSetup

setup = GameSetup()
config = setup.run() # config will store the player's choices in a map

if config["p1"] == "human": 
   p1 = Player.Player("Player 1", True)
else: 
   p1 = Player.Player("Player 1", False, SafeChoiceStrategy)

if config["p2"] == "human": 
   p2 = Player.Player("Player 2", True)
else: 
   p2 = Player.Player("Player 2", False, SafeChoiceStrategy)


game=GameHandler.GameHandler(player1=p1, player2=p2)
game.play()
