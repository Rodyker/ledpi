#!/usr/bin/python

from lib.game import *

def start(game: Game):
    while True:
        game.screen.fill(Color.WHITE)
        time.sleep(0.1)

if __name__ == '__main__':
    GameLauncher(
        GameFactory("data/horizontal.csv", "data/font.csv", "color.cfg", [], "data/sprites.csv"), 
        start)
