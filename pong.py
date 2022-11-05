#!/usr/bin/python

import secrets
import time
import signal
import sys
import math

from threading import Thread

from lib.screen import *
from lib.led_pixels import *
from lib.gamepad import *
from lib.sound import *
from lib.text import *
from lib.config import *
from lib.game import *

is_debug = True

def debug(message):
    if is_debug:
        print(message) 

class Paddle:
    def __init__(self, x_coordinate, y_coordinate):
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
    
    def up(self):
        if self.y_coordinate > 0:
            self.y_coordinate -=1
            screen.set_pixel(self.x_coordinate, self.y_coordinate+4, Color.OFF)
            self.show()

    def down(self):
        if self.y_coordinate < (screen.pixels.get_num_rows() - 4):
            self.y_coordinate += 1
            screen.set_pixel(self.x_coordinate, self.y_coordinate-1, Color.OFF)
            self.show()

    def show(self):
        screen.draw_line(self.x_coordinate, self.y_coordinate, DrawDirection.VERTICAL, 4, Color.WHITE)

class Ball:
    def __init__(self, x_coordinate, y_coordinate, angle, color, speed = .1):
        global game
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.old_x = self.x_coordinate
        self.old_y = self.y_coordinate
        self.angle = angle
        self.color = color
        self.speed = speed

    def move(self):
        global score
        global end_game_flag
        global win_flag

        self.old_x = self.x_coordinate
        self.old_y = self.y_coordinate

        self.predicted_x = self.x_coordinate + round(math.cos(math.radians(self.angle)))
        self.predicted_y = self.y_coordinate + round(math.sin(math.radians(self.angle)))
        
        if self.predicted_x < 0:
            self.predicted_x = 0
        elif self.predicted_x > screen.pixels.get_num_columns() - 1:
            self.predicted_x = screen.pixels.get_num_columns() - 1
        
        if self.predicted_y <= 0 or self.predicted_y >= screen.pixels.get_num_rows() - 1:
            self.angle = self.angle * -1
            self.predicted_y = self.y_coordinate + round(math.sin(math.radians(self.angle)))

        if self.predicted_y <= 0:
            self.predicted_y = 0
        if self.predicted_y >= screen.pixels.get_num_rows() - 1:
            self.predicted_y = screen.pixels.get_num_rows() - 1

        if self.predicted_x <= .5:
            if left_paddle.y_coordinate <= round(self.predicted_y) and round(self.predicted_y) <= left_paddle.y_coordinate + 3:
                score += 1
                self.speed -= self.speed / 10
                debug(((self.predicted_y - left_paddle.y_coordinate) - 1.5) * 10)
                self.angle = (90 - ( self.angle - 90)) + (((self.predicted_y - left_paddle.y_coordinate) - 1.5) * 10)
            else:
                debug([self.x_coordinate, self.y_coordinate, self.predicted_x, self.predicted_y])
                self.thread_flag = False

                end_game_flag = True

        if self.predicted_x >= screen.pixels.get_num_columns() - 1.5:
            if right_paddle.y_coordinate <= self.predicted_y and self.predicted_y <= right_paddle.y_coordinate + 3:
                self.speed -= self.speed / 10
                self.angle = (90 - ( self.angle - 90)) + (((self.predicted_y - right_paddle.y_coordinate) - 1.5) * 10)
            else:
                debug([self.x_coordinate, self.y_coordinate, self.predicted_x, self.predicted_y])
                self.thread_flag = False

                win_flag = True
                end_game_flag = True

        self.x_coordinate += math.cos(math.radians(self.angle))
        self.y_coordinate += math.sin(math.radians(self.angle))

    def show(self):
        screen.set_pixel(round(self.old_x), round(self.old_y), Color.OFF)
        screen.set_pixel(round(self.x_coordinate), round(self.y_coordinate), self.color)

    def ball_thread(self):
        self.thread_flag = True
        while self.thread_flag:
            ball.move()
            ball.show()

            if end_game_flag:
                break

            self.update_flag = True
            screen.update()
            self.update_flag = False

            time.sleep(self.speed)

##########################################################################################################

score = 0
end_game_flag = False
win_flag = False

screen = Screen(LEDPixels("data/diagonal.csv"))
gamepad = Gamepad(0)
config = Config("pong.cfg")
text = Text("data/font.csv", screen)
sound = SoundFactory(config.get_int("volume", 100), config.get_bool("muted", False))
game = Game(screen, text, gamepad, sound, config)

left_paddle = Paddle(0, round(screen.pixels.get_num_rows() / 2))
right_paddle = Paddle(screen.pixels.get_num_columns()-1, round(screen.pixels.get_num_rows() / 2))
ball = Ball(screen.pixels.get_num_columns() / 1.5 , screen.pixels.get_num_rows() / 2, secrets.randbelow(40) - 20, Color.RED)
ball_thread = Thread(target=ball.ball_thread)

try:
    left_paddle.show()
    right_paddle.show()
    ball.show()

    paddle_speed = .1

    ball_thread.start()

    while True:
        current_direction = gamepad.get_one()

        if current_direction == Button.YELLOW:
            left_paddle.up()
        elif current_direction == Button.GREEN:
            left_paddle.down()

        if ball.y_coordinate > right_paddle.y_coordinate + 1:
            right_paddle.down()
        if ball.y_coordinate < right_paddle.y_coordinate + 1:
            right_paddle.up()

        while(ball.update_flag == True):
            time.sleep(.001)
        screen.update()

        if end_game_flag:
            time.sleep(1)

            ball_thread.join()

            screen.clear()

            game.show_win_lose(win_flag, score)

            exit()

        time.sleep(paddle_speed)

except KeyboardInterrupt:
    ball.thread_flag = False
    ball_thread.join()

    screen.clear()
    pass