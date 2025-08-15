#main.py
from game.game import Game

game = Game()
while True:
    game.new()
    game.run()