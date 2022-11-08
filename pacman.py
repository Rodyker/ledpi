#!/usr/bin/python

import random
import time

from lib.screen import *
from lib.gamepad import *
from lib.sound import *
from lib.text import *
from lib.config import *
from lib.game import *
from lib.util import *

class Pacman:
    def __init__(self, game: Game):
        self._game = game
        self.sprite = game.sprites.get(SpriteID.PACMAN)
        self.sprite.set_position(10, 9)

    def move(self) -> bool:
        gamepad = self._game.gamepad

        button = gamepad.get_sticky_button()
        if button in [Button.BLUE, Button.HAT_LEFT, Button.L_STICK_LEFT, Button.R_STICK_LEFT]:
            self.sprite.move(MoveDirection.LEFT, walls= walls)  
        elif button in [Button.RED, Button.HAT_RIGHT, Button.L_STICK_RIGHT, Button.R_STICK_RIGHT]:
            self.sprite.move(MoveDirection.RIGHT, walls= walls)
        elif button in [Button.YELLOW, Button.HAT_UP, Button.L_STICK_UP, Button.R_STICK_UP]:
            self.sprite.move(MoveDirection.UP, walls= walls)
        elif button in [Button.GREEN, Button.HAT_DOWN, Button.L_STICK_DOWN, Button.R_STICK_DOWN]:
            self.sprite.move(MoveDirection.DOWN, walls= walls)

        return False

class Ghost:
    def __init__(self, game: Game, position_x, position_y, name):
        self._game = game
        self.sprite = game.sprites.get(name)
        self.sprite.set_position(position_x,position_y)
        self.opp_direction = MoveDirection.DOWN
        self.ideal_directions = [MoveDirection.UP, MoveDirection.RIGHT, MoveDirection.LEFT, MoveDirection.DOWN]
        self.possible_directions = []

    def get_possible_directions(self):
        directions = []
        if not self.opp_direction == MoveDirection.UP:
            if self.sprite.move(MoveDirection.UP, walls= walls, under_save= True):
                self.sprite.move(MoveDirection.DOWN, under_save= True)
                directions.append(MoveDirection.UP)

        if not self.opp_direction == MoveDirection.DOWN:
            if self.sprite.move(MoveDirection.DOWN, walls= walls, under_save= True):
                self.sprite.move(MoveDirection.UP, under_save= True)
                directions.append(MoveDirection.DOWN)

        if not self.opp_direction == MoveDirection.LEFT:
            if self.sprite.move(MoveDirection.LEFT, walls= walls, under_save= True):
                self.sprite.move(MoveDirection.RIGHT, under_save= True)
                directions.append(MoveDirection.LEFT)

        if not self.opp_direction == MoveDirection.RIGHT:
            if self.sprite.move(MoveDirection.RIGHT, walls= walls, under_save= True):
                self.sprite.move(MoveDirection.LEFT, under_save= True)
                directions.append(MoveDirection.RIGHT)
        return directions

    def get_ideal_directions(self, reverse):
        rise = pacman.sprite.get_row() - self.sprite.get_row()
        run = pacman.sprite.get_column() - self.sprite.get_column()
        try:
            self.ideal_angle = rise / run
        except ZeroDivisionError:
            self.ideal_angle = 2

        if self.sprite.get_column() < pacman.sprite.get_column():
            if reverse:
                self.ideal_right = False
            else:
                self.ideal_right = True
        else:
            if reverse:
                self.ideal_right = True
            else:
                self.ideal_right = False

        if self.ideal_angle > 1:
            self.ideal_directions = [MoveDirection.DOWN, MoveDirection.RIGHT, MoveDirection.LEFT, MoveDirection.UP]
        elif self.ideal_angle > 0:
            self.ideal_directions = [MoveDirection.RIGHT, MoveDirection.DOWN, MoveDirection.UP, MoveDirection.LEFT]
        elif self.ideal_angle > -1:
            self.ideal_directions = [MoveDirection.RIGHT, MoveDirection.UP, MoveDirection.DOWN, MoveDirection.LEFT]
        else:
            self.ideal_directions = [MoveDirection.UP, MoveDirection.RIGHT, MoveDirection.LEFT, MoveDirection.DOWN]

        if not self.ideal_right:
            self.ideal_directions.reverse()

    def move(self, scatter, reverse):
        self.possible_directions: List[MoveDirection] = self.get_possible_directions()
        self.get_ideal_directions(reverse)

        if self.possible_directions == []:
            self.opp_direction = None
            return

        if scatter:
            while True:
                rand = random.randint(0,3)
                if rand == 0 and MoveDirection.UP in self.possible_directions:
                    self.sprite.move(MoveDirection.UP, walls= walls, under_save= True)
                    self.opp_direction = MoveDirection.DOWN
                elif rand == 1 and MoveDirection.DOWN in self.possible_directions:
                    self.sprite.move(MoveDirection.DOWN, walls= walls, under_save= True)
                    self.opp_direction = MoveDirection.UP
                elif rand == 2 and MoveDirection.LEFT in self.possible_directions:
                    self.sprite.move(MoveDirection.LEFT, walls= walls, under_save= True)
                    self.opp_direction = MoveDirection.RIGHT
                elif rand == 3 and MoveDirection.RIGHT in self.possible_directions:
                    self.sprite.move(MoveDirection.RIGHT, walls= walls, under_save= True)
                    self.opp_direction = MoveDirection.LEFT
                else:
                    continue
                return

        while True:
            for direction in self.ideal_directions:
                if direction in self.possible_directions and random.randint(0,10) < 8:
                    self.sprite.move(direction, walls= walls, under_save= True)
                    if direction == MoveDirection.UP:
                        self.opp_direction = MoveDirection.DOWN
                    elif direction == MoveDirection.DOWN:
                        self.opp_direction = MoveDirection.UP
                    elif direction == MoveDirection.LEFT:
                        self.opp_direction = MoveDirection.RIGHT
                    elif direction == MoveDirection.RIGHT:
                        self.opp_direction = MoveDirection.LEFT
                    else:
                        continue
                    return
            
def count_pellets():
    num_pellets = 0
    for row in range(game.screen.pixels.get_num_rows()):
        for column in range(game.screen.pixels.get_num_columns()):
            if game.screen.get_pixel(column, row)[0] == Color.BLUE:
                num_pellets += 1
    return(num_pellets)

if __name__ == '__main__':
    game = GameFactory("data/horizontal.csv", "data/font.csv", "pacman.cfg", [
        Button.BLUE, Button.HAT_LEFT, Button.L_STICK_LEFT, Button.R_STICK_LEFT,
        Button.RED, Button.HAT_RIGHT, Button.L_STICK_RIGHT, Button.R_STICK_RIGHT,
        Button.YELLOW, Button.HAT_UP, Button.L_STICK_UP, Button.R_STICK_UP,
        Button.GREEN, Button.HAT_DOWN, Button.L_STICK_DOWN, Button.R_STICK_DOWN
        ], "data/sprites.csv", brightness= 1)
    game.gamepad.set_sticky_button(Button.RED)
    pacman = Pacman(game)
    ghosts = [Ghost(game, 9, 5, SpriteID.BLINKY), 
            Ghost(game, 11, 5, SpriteID.PINKY), 
            Ghost(game, 9, 7, SpriteID.INKY), 
            Ghost(game, 11, 7, SpriteID.CLYDE)]
    wall = game.sprites.get(SpriteID.PACMAP)

    game.screen.fill(Color.BLUE, .1)

    walls = [wall]
    for ghost in ghosts:
        walls.append(ghost.sprite)
    #    ghost.sprite.draw(brightness= 1)
    

    wall.draw(color=Color.WHITE, brightness= .5)
    pacman.sprite.draw()
    game.screen.update()

    totalpellets = count_pellets()
    clock = 1
    scatter = True
    reverse = False
    while True:
        clock += 1
        if (clock % 30 == 0 and scatter) or (clock % 50 == 0 and not scatter):
            if scatter:
                scatter = False
            else:
                scatter = True

        pacman.move()
        if clock % 2 == 0:
            pacman.sprite.draw(brightness = 5)
        else:
            pacman.sprite.draw(brightness = 1)

        for ghost in ghosts:
            if ghost.sprite.is_colliding(pacman.sprite):
                game.show_game_over(totalpellets - count_pellets())
                sys.exit()

            ghost.move(scatter, reverse)

            if ghost.sprite.is_colliding(pacman.sprite):
                game.show_game_over(totalpellets - count_pellets())
                sys.exit()

        game.screen.update()
        time.sleep(.3)