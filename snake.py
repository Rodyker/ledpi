#!/usr/bin/python

import secrets
from lib.game import *

CONTROL_UP    = [Button.L_STICK_UP, Button.HAT_UP, Button.YELLOW, Button.KEY_UP]
CONTROL_DOWN  = [Button.L_STICK_DOWN, Button.HAT_DOWN, Button.GREEN, Button.KEY_DOWN]
CONTROL_LEFT  = [Button.L_STICK_LEFT, Button.HAT_LEFT, Button.BLUE, Button.KEY_LEFT]
CONTROL_RIGHT = [Button.L_STICK_RIGHT, Button.HAT_RIGHT, Button.RED, Button.KEY_RIGHT]

class Snake:
    _delay = 0.5
    _snake_colors = [Color.GREEN, Color.BLUE, Color.RED]

    def __init__(self, game: Game):
        self._game = game
        self._score = 0
        self.eat_sound = game.sound.get(SoundSample.EAT)

        screen = self._game.screen
        screen.fill(Color.OFF)

        snake_column = int(screen.pixels.get_num_columns() / 2)
        snake_row = int(screen.pixels.get_num_rows() / 2)
        screen.set_pixel(snake_column, snake_row, Color.GREEN)
        self._snake = [[snake_column, snake_row]]
        self._grow = False

        self._apple = [0, 0]
        self.create_apple()
        screen.update()
        game.gamepad.set_sticky_button(CONTROL_RIGHT[0])

    def create_apple(self):
        screen = self._game.screen

        while True:
            apple_column = secrets.randbelow(screen.pixels.get_num_columns())
            apple_row = secrets.randbelow(screen.pixels.get_num_rows())

            colision = False
            for snake_segment in self._snake:
                if (apple_column == snake_segment[0] and apple_row == snake_segment[1]):
                    colision = True
                    break
            if not colision:
                break

        screen.set_pixel(apple_column, apple_row, Color.RED)
        self._apple = [apple_column, apple_row]

    def step_delay(self):
        time.sleep(self._delay)

    def detect(self):
        apple = self._apple
        snake_head = self._snake[0]

        if (snake_head[0] == apple[0] and
            snake_head[1] == apple[1]):

            self.eat_sound.play()
            self._grow = True
            self._score += 1
            self._delay -= self._delay * 0.1
            self.create_apple()

    def move(self) -> bool:
        snake = self._snake
        head = snake[0]
        new_column = head[0]
        new_row = head[1]

        gamepad = self._game.gamepad
        gamepad.pause_tracking()
        button = gamepad.get_sticky_button()
        if button in CONTROL_UP:
            new_row -= 1
            gamepad.ignore_sticky_buttons(CONTROL_DOWN)
        elif button in CONTROL_DOWN:
            new_row += 1
            gamepad.ignore_sticky_buttons(CONTROL_UP)
        elif button in CONTROL_LEFT:
            new_column -= 1
            gamepad.ignore_sticky_buttons(CONTROL_RIGHT)
        elif button in CONTROL_RIGHT:
            new_column += 1
            gamepad.ignore_sticky_buttons(CONTROL_LEFT)
        gamepad.restart_tracking()

        screen = self._game.screen
        if (new_column < 0 or new_row < 0 or
            new_column > screen.last_column or
            new_row > screen.last_row):

            gamepad.clear_ignored_sticky_button()
            self._game.show_game_over(self._score)
            return True

        snake.insert(0, [new_column, new_row])

        if not self._grow:
            last_segment = snake.pop()
            screen.set_pixel(last_segment[0], last_segment[1], Color.OFF)
        self._grow = False

        colors = self._snake_colors
        for n, segment in enumerate(snake):
            screen.set_pixel(segment[0], segment[1], colors[n % len(colors)])    

        screen.update()

        for segment in snake[1:]:
            if new_column == segment[0] and new_row == segment[1]:
                self._game.show_game_over(self._score)
                return True

        return False

def start(game: Game):
    snake = Snake(game)

    while True:
        if snake.move():
            break
        snake.detect()
        snake.step_delay()

if __name__ == '__main__':
    controls = []
    controls.extend(CONTROL_UP)
    controls.extend(CONTROL_DOWN)
    controls.extend(CONTROL_LEFT)
    controls.extend(CONTROL_RIGHT)

    GameLauncher(
        GameFactory("data/diagonal.csv", "data/font.csv", "snake.cfg", controls), 
        start)
