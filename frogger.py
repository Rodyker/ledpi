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

class Frog:
    def __init__(self, game: Game):
        self._game = game
        self.sprite = game.sprites.get(SpriteID.FROG)
        self.sprite.set_position(
            int(game.screen.pixels.get_num_columns() / 2), 
            game.screen.pixels.get_num_rows() - self.sprite.get_height())
        self.eat_sound = game.sound.get(SoundSample.EAT)

    def move(self) -> bool:
        gamepad = self._game.gamepad

        button = gamepad.get_sticky_button()
        gamepad.clear_sticky_button()
        if button == Button.BLUE:
            self.sprite.move(MoveDirection.LEFT, walls= walls) 
            self.sprite.move(MoveDirection.LEFT, walls= walls)  
            self.sprite.draw()
            self.eat_sound.play()
            self.sprite.transform(3)
        elif button == Button.RED:
            self.sprite.move(MoveDirection.RIGHT, walls= walls)
            self.sprite.move(MoveDirection.RIGHT)
            self.sprite.draw()
            self.eat_sound.play()
            self.sprite.transform(1)
        elif button == Button.YELLOW:
            self.sprite.move(MoveDirection.UP, walls= walls)
            self.sprite.move(MoveDirection.UP, walls= walls)
            self.sprite.draw()
            self.eat_sound.play()
            self.sprite.transform(0)
        elif button == Button.GREEN:
            self.sprite.move(MoveDirection.DOWN, walls= walls)
            self.sprite.move(MoveDirection.DOWN, walls= walls)
            self.sprite.draw()
            self.eat_sound.play()
            self.sprite.transform(2)

        return False

class Car:
    def __init__(self, game: Game, x_coordinate, y_coordinate, direction, sprite = SpriteID.CAR):
        self._game = game
        self.sprite = game.sprites.get(sprite)
        self.sprite.set_position(x_coordinate, y_coordinate)
        self.direction = direction
        self.y_coordinate = y_coordinate

    def move(self):
        return self.sprite.move(self.direction, outside= 3)

def make_cars(cars: List):
    for i in range(2, game.screen.pixels.get_num_rows() - 2, 2):
        if i % 4 == 0:
            direction = MoveDirection.LEFT
        else:
            direction = MoveDirection.RIGHT
        cars.append(Car(game, game.screen.pixels.get_num_columns(), 
            i, direction))
        cars.append(Car(game, game.screen.pixels.get_num_columns() // 2, 
                i, direction))

def make_walls(game: Game, walls):
    for i in range(-2, game.screen.pixels.get_num_rows() + 5, 6):
        walls.append(game.sprites.get(SpriteID.WALL))
        walls[-1].set_position(i, 0)
        walls[-1].draw()

if __name__ == '__main__':
    game = GameFactory("data/diagonal.csv", "data/font.csv", "frogger.cfg", [Button.RED, Button.BLUE, Button.GREEN, Button.YELLOW], "data/sprites.csv")
    frog = Frog(game)
    cars: List[Car] = []
    walls = []
    make_cars(cars)
    make_walls(game, walls)

    car_sprites = []
    for car in cars:
        car_sprites.append(car.sprite)

    clock = 0
    carclock = 6
    required_num_frogs = len(walls)
    num_frogs = 1
    while True:
        frog.move()
        game.screen.update()

        if not frog.sprite.get_collisions(car_sprites) == []:
            game.show_win_lose(False)
            sys.exit()

        clock += 1
        if clock == carclock:
            clock = 0
            for i in range(len(cars)):
                if not cars[i].move():
                    car_y = cars[i].y_coordinate
                    car_direction = cars[i].direction
                    cars[i].sprite.erase()
                    cars.pop(i)

                    random_color = random.randint(0,6)
                    if car_direction == MoveDirection.LEFT:
                        cars.append(Car(game, game.screen.pixels.get_num_columns(), 
                            car_y, car_direction, SpriteID.TRUCK))

                    elif car_direction == MoveDirection.RIGHT:
                        cars.append(Car(game, -3, 
                            car_y, car_direction))

                    cars[-1].sprite.transform(random_color)

                car_sprites = []
                for car in cars:
                    car_sprites.append(car.sprite)

        if frog.sprite.get_row() == 0:
            walls.append(frog.sprite)
            frog = Frog(game)
            num_frogs += 1
            carclock -= 1
        if num_frogs == required_num_frogs:
            game.show_win_lose(True)