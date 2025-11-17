from Game.GameSetup import GameSetup
from Game.GameHandler import GameHandler

setup = GameSetup()
config = setup.run() # config will store the player's choices in a map

p1 = config[0]
p2 = config[1]

game=GameHandler(player1=p1, player2=p2)
game.play()
