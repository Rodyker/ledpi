import csv
from enum import IntEnum
from lib.screen import *
from lib.util import *
from lib.colors import *
from typing import List, Tuple, Dict

class SpriteID(IntEnum):
    BULLET = 0
    ENEMY_BULLET = 1
    ROCKET = 2
    SHIP = 3
    ENEMY_FLIPER = 4
    ENEMY_SQUARE = 5
    ENEMY_FLASHER = 6
    ENEMY_SHIP = 7
    ENEMY_LONG = 8
    ENEMY_SHORT = 9
    ENEMY_BIRD = 10
    ENEMY_SPINNER = 11
    FROG = 12
    CAR = 13
    TRUCK = 14
    WALL = 15
    PACMAP = 16
    PACMAN = 17
    BLINKY = 18
    PINKY = 19
    INKY = 20
    CLYDE = 21
    BLOCK_J = 22
    BLOCK_L = 23
    BLOCK_O = 24
    BLOCK_Z = 25
    BLOCK_S = 26
    BLOCK_T = 27
    BLOCK_I = 28

class MoveDirection(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

class Sprite:
    def __init__(self, definition: List[List[List[Color]]], screen: Screen):
        self._definition = definition
        self._screen = screen
        self._form = 0
        self._column = 0
        self._row = 0
        self._brightness = None
        self._visible = False
        self._under_save = []

    def set_position(self, column: int, row: int):
        self._column = column
        self._row = row
        self.draw()

    def get_column(self) -> int:
        return self._column

    def get_row(self) -> int:
        return self._row

    def get_middle_position(self) -> Tuple[int, int]:
        middle_column = self._column + int(self.get_width() / 2)
        return middle_column, self._row

    def on_screen(self) -> bool:
        if (self._column >= 0 and self._row >= 0 and
            self._column < (self._screen.last_column - self.get_width()) and
            self._row < (self._screen.last_row - self.get_height())):
        
            return True
        return False

    def set_brightness(self, brightness: Optional[float] = None):
        self._brightness = brightness

    def move(self, direction: MoveDirection, outside = 0, walls: List["Sprite"] = [],
        pulsate: bool = False, under_save = False, skip_draw = False) -> bool:
        
        if pulsate:
            self.transform()

        new_row = self._row
        new_column = self._column

        if direction == MoveDirection.UP:
            new_row -= 1
            if new_row < -outside:
                return False
        elif direction == MoveDirection.DOWN:
            new_row += 1
            if (new_row + self.get_height()) > (self._screen.pixels.get_num_rows() + outside):
                return False
        elif direction == MoveDirection.LEFT:
            new_column -= 1
            if new_column < -outside:
                return False
        elif direction == MoveDirection.RIGHT:
            new_column += 1
            if (new_column + self.get_width()) > (self._screen.pixels.get_num_columns() + outside):
                return False

        if len(self.get_collisions(walls, if_my_position = [new_column, new_row])) > 0:
            return False

        if under_save:
            for under in self._under_save:
                self._screen.set_pixel(under[0], under[1], under[2], under[3])
        elif not skip_draw:
            self.erase()
        
        self._column = new_column
        self._row = new_row
        if not skip_draw:
            self.draw(under_save = under_save)
        return True

    def draw(self, color: Optional[Color] = None, brightness: Optional[float] = None,
        under_save = False):

        self._visible = color != Color.OFF

        if under_save:
            self._under_save = []

        for num_row, sprite_row in enumerate(self._definition[self._form]):
            for num_column, pixel_color in enumerate(sprite_row):
                if pixel_color == Color.OFF:
                    continue
                
                if color != None:
                    pixel_color = color

                pixel_brightness = self._brightness
                if brightness != None:
                    pixel_brightness = brightness

                column = self._column + num_column
                row = self._row + num_row

                if under_save and self._screen.on_screen(column, row):
                    old_color, old_brightness = self._screen.get_pixel(column, row)
                    self._under_save.append([column, row, old_color, old_brightness])

                self._screen.set_pixel(column, row, pixel_color, pixel_brightness)

    def erase(self):
        self.draw(color = Color.OFF)

    def transform(self, form: Optional[int] = None, walls: List["Sprite"] = [],
        skip_draw: bool = False) -> bool:
        
        if form == None:
            new_form = self._form + 1
        else:
            new_form = form
        
        max_form = len(self._definition) - 1
        if new_form > max_form:
            new_form = 0

        if len(self.get_collisions(walls, if_my_form = new_form)) > 0:
            return False

        if skip_draw:
            self._form = new_form
        else:
            self.erase()
            self._form = new_form
            self.draw()

        return True

    def fragment(self) -> List["Sprite"]:
        self.erase()
        sprites: List[Sprite] = []
        for num_row, sprite_row in enumerate(self._definition[self._form]):
            for num_column, pixel_color in enumerate(sprite_row):
                if pixel_color == Color.OFF:
                    continue
                sprite = Sprite([[[pixel_color]]], self._screen)
                sprite.set_position(self._column + num_column, self._row + num_row)
                sprites.append(sprite)
        return sprites

    def get_height(self) -> int:
        return len(self._definition[self._form])

    def get_width(self) -> int:
        return len(self._definition[self._form][0])

    def is_colliding(self, sprite: "Sprite", if_my_position: Optional[List[int]] = None,
        if_my_form: Optional[int] = None) -> bool:
        
        column = self._column
        row = self._row
        form = self._form

        if if_my_position != None:
            column = if_my_position[0]
            row = if_my_position[1]

        if if_my_form != None:
            form = if_my_form

        cells: Dict[str, bool] = {}
        
        if not (self._visible and sprite._visible):
            return False

        for num_row, sprite_row in enumerate(self._definition[form]):
            for num_column, color in enumerate(sprite_row):
                if color != Color.OFF:
                    key = "{},{}".format(column + num_column, row + num_row)
                    cells[key] = True
        
        for num_row, sprite_row in enumerate(sprite._definition[sprite._form]):
            for num_column, color in enumerate(sprite_row):
                if color != Color.OFF:
                    key = "{},{}".format(sprite._column + num_column, sprite._row + num_row)
                    if cells.get(key):
                        return True
        
        return False

    def get_collisions(self, sprites: List["Sprite"],
        if_my_position: Optional[List[int]] = None, if_my_form: Optional[int] = None
        ) -> List["Sprite"]:
        
        collisions: List["Sprite"] = []

        for sprite in sprites:
            if self.is_colliding(sprite, if_my_position, if_my_form):
                collisions.append(sprite)

        return collisions

class Sprites:
    def __init__(self, definition_filename: str, screen: Screen):
        self._screen = screen
        definition_file = open(definition_filename)
        definition_reader = csv.reader(definition_file)

        self._sprite_definitions = []
        while True:
            animation = []
            animation_width = 0

            for row in definition_reader:
                row_width = 0
                for column, element in enumerate(row):
                    if element != "":
                        row_width = column + 1

                if row_width == 0:
                    break

                if row_width > animation_width:
                    animation_width = row_width

                animation.append(row)

            if animation_width == 0:
                break

            trimmed_animation = []
            for row in animation:
                trimmed_animation.append(row[:animation_width])

            self._sprite_definitions.append(
                self._split_sprite_animation(trimmed_animation, animation_width))

    def _split_sprite_animation(self, animation: List[List[str]], width: int) -> (
            List[List[List[Color]]]):
        
        sprites = []

        while width > 0:
            sprite_width = width
            for color in range(width):
                is_empty_column = True

                for row in range(len(animation)):
                    if animation[row][color] != "":
                        is_empty_column = False
                        break

                if is_empty_column:
                    sprite_width = color
                    break

            sprite = []
            for i, row in enumerate(animation):
                sprite_row = row[:sprite_width]
                animation[i] = row[sprite_width + 1:]
                if any(cell != "" for cell in sprite_row):
                    sprite.append(sprite_row)
            
            for num_row, row in enumerate(sprite):
                for num_column, color in enumerate(row):
                    sprite[num_row][num_column] = Colors().get(color)

            width = len(animation[0])
            sprites.append(sprite)

        return sprites

    def get(self, sprite: SpriteID) -> Sprite:
        return Sprite(self._sprite_definitions[sprite], self._screen)

    def test(self):
        screen = self._screen
        screen.clear()

        sprites: List[Sprite] = []
        for sprite_definition in self._sprite_definitions:
            sprites.append(Sprite(sprite_definition, self._screen))

        max_width = 0
        column = 0
        row = 0

        for sprite in sprites:
            sprite_height = sprite.get_height()
            max_width = max_int(sprite.get_width(), max_width)

            if row + sprite_height > screen.pixels.get_num_rows():
                row = 0
                column += max_width + 1
                max_width = 0

            sprite.set_position(column, row)
            row += sprite_height + 1

        for i in range(10):
            for sprite in sprites:
                sprite.transform()

            screen.update()
            time.sleep(0.5)
