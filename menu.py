#!/usr/bin/python

import os
from lib.gamepad import *
from lib.text import *
from lib.game import *
from lib.screen import *
from lib.sound import *
from lib.config import *

game = GameFactory("data/diagonal.csv", "data/font.csv", "global.cfg", 
    [Button.BLUE, Button.RED, Button.YELLOW, Button.GREEN])

games_list = [
    ["./pong.py", "PONG", ""],
    ["./snake.py", "SNAKE", ""],
    ["./shooter.py", "SPACE", "INVADE"],
    ["./frogger.py", "FROG", ""]
    ]

list_index = 0
last_game = games_list.__len__() - 1
print(last_game)
try:
    while True:
        game.text.write([[games_list[list_index][1] , Color.WHITE], [games_list[list_index][2] , Color.WHITE]])
        game.screen.update()

        game.gamepad.wait_any_button()
        current_button = game.gamepad.get_one()

        if current_button in [Button.HAT_LEFT, Button.L_STICK_LEFT, Button.BLUE]:
            list_index -= 1
            if list_index < 0:
                list_index = last_game
        
        elif current_button in [Button.HAT_RIGHT, Button.L_STICK_RIGHT, Button.RED]:
            list_index += 1
            if list_index > last_game:
                list_index = 0

        elif current_button == Button.GREEN:
            os.system(games_list[list_index][0] + " menu >> menu.out 2>&1")
            game.screen.clear()
            game.gamepad.wait_any_button()
except KeyboardInterrupt:
    pass

game.stop()