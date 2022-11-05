#!/usr/bin/python

import secrets
from lib.game import *

CONTROL_LEFT  = [Button.L_STICK_LEFT, Button.HAT_LEFT, Button.KEY_LEFT]
CONTROL_RIGHT = [Button.L_STICK_RIGHT, Button.HAT_RIGHT, Button.KEY_RIGHT]
CONTROL_DOWN  = [Button.L_STICK_DOWN, Button.HAT_DOWN, Button.KEY_DOWN]
CONTROL_TURN  = [Button.L_STICK_UP, Button.HAT_UP, Button.KEY_UP]
CONTROL_DROP  = [Button.GREEN, Button.KEY_SPACE]

class Blocks:
    FIELD_WIDTH = 10

    def __init__(self, game: Game):
        self._game = game
        screen = game.screen
        self._delay = 1
        self._dropped = False
        self._score = 0
        self.line_sound = game.sound.get(SoundSample.EAT)

        screen.clear()

        self._walls: List[Sprite] = []
        self._fallen: List[Sprite] = []

        self._first_column = int((self._game.screen.last_column - self.FIELD_WIDTH) / 3)
        self._second_column = self._first_column + self.FIELD_WIDTH + 1
        self._middle_column = int((self._first_column + self._second_column) / 2)

        for row in range(screen.pixels.get_num_rows()):
            wall = self._game.sprites.get(SpriteID.BULLET)
            wall.set_position(self._first_column, row)
            wall.draw(color = Color.WHITE)
            self._walls.append(wall)

            wall = self._game.sprites.get(SpriteID.BULLET)
            wall.set_position(self._second_column, row)
            wall.draw(color = Color.WHITE)
            self._walls.append(wall)

        self._next_pieces: List[Sprite] = []
        row = 0
        for _ in range(5):
            piece = self._game.sprites.get(SpriteID(SpriteID.BLOCK_J + secrets.randbelow(7)))
            piece.set_position(self._second_column + 2, row)
            self._next_pieces.append(piece)
            row += piece.get_height() + 1

        self.create_block()
        screen.update()

    def step_delay(self):
        self._game.gamepad.wait_any_button(delay = 0.1, timeout = self._delay)

    def move(self) -> bool:
        button = self._game.gamepad.get_sticky_button()
        if button in CONTROL_LEFT:
            self._block.move(MoveDirection.LEFT, walls = self._walls)
        elif button in CONTROL_RIGHT:
            self._block.move(MoveDirection.RIGHT, walls = self._walls)
        elif button in CONTROL_TURN:
            self.turn()
        elif button in CONTROL_DROP:
            while True:
                if not self._block.move(MoveDirection.DOWN, walls = self._walls):
                    break
            if not self.block_dropped():
                return True
        elif not self._block.move(MoveDirection.DOWN, walls = self._walls):
            if not self.block_dropped():
                return True

        self._game.gamepad.clear_sticky_button()
        self._game.screen.update()
        return False

    def turn(self):
        saved_column = self._block.get_column()
        saved_row = self._block.get_row()

        while not self._block.transform(walls = self._walls):
            if not self._block.move(MoveDirection.LEFT, walls = self._walls):
                self._block.erase()
                self._block.set_position(saved_column, saved_row)
                break

    def block_dropped(self) -> bool:
        if self._block.get_row() == 0:
            self._game.show_game_over(self._score)
            return False

        pieces = self._block.fragment()
        self._walls.extend(pieces)
        self._fallen.extend(pieces)
        self._dropped = True
        del self._block
        return True

    def create_block(self):
        self._block = self._next_pieces.pop(0)
        self._block.erase()
        self._block.set_position(self._middle_column, 0)
        self._dropped = False

        block = self._game.sprites.get(SpriteID(SpriteID.BLOCK_J + secrets.randbelow(7)))
        last_piece = self._next_pieces[-1]
        row = last_piece.get_row() + last_piece.get_height() + 1
        block.set_position(self._second_column + 2, row)
        self._next_pieces.append(block)

        moved = 0
        while self._next_pieces[0].move(MoveDirection.UP):
            moved += 1

        for block in self._next_pieces[1:]:
            for _ in range(moved):
                block.move(MoveDirection.UP)

    def detect(self):
        if not self._dropped:
            return

        memory = self._game.screen.save()
        c1 = self._first_column + 1
        c2 = self._first_column + self.FIELD_WIDTH + 1
        sound_played = False

        for row_num in range(self._game.screen.pixels.get_num_rows()):
            row = memory[row_num][c1:c2]

            if all(cell[0] != Color.OFF for cell in row):
                if not sound_played:
                    self.line_sound.play()
                    sound_played = True

                self._score += 1
                self._delay -= self._delay * 0.05
                fallen = self._fallen.copy()
                for block in fallen:
                    if block.get_row() == row_num:
                        block.erase()
                        self._fallen.remove(block)
                        self._walls.remove(block)

                for block in self._fallen:
                    if block.get_row() < row_num:
                        block.erase()
                        block.move(MoveDirection.DOWN, skip_draw = True)

                for block in self._fallen:
                    if block.get_row() <= row_num:
                        block.draw()

        self.create_block()
        self._game.screen.update()
        self._dropped = False
        return

def start(game: Game):
    blocks = Blocks(game)

    while True:
        if blocks.move():
            break

        blocks.detect()
        blocks.step_delay()

if __name__ == '__main__':
    controls = []
    controls.extend(CONTROL_LEFT)
    controls.extend(CONTROL_RIGHT)
    controls.extend(CONTROL_DOWN)
    controls.extend(CONTROL_TURN)
    controls.extend(CONTROL_DROP)

    GameLauncher(
        GameFactory("data/diagonal.csv", "data/font.csv", "blocks.cfg", controls,
            "data/sprites.csv"), 
        start)
