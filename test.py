#!/usr/bin/python

from lib.game import *

def start(game: Game):
    game.screen.test()
    game.text.test()
    game.sprites.test()

if __name__ == '__main__':
    GameLauncher(
        GameFactory("data/diagonal.csv", "data/font.csv", "test.cfg", [], "data/sprites.csv"), 
        start)
