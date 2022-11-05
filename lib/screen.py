from enum import Enum, auto
import time
from typing import Optional, Tuple
import copy
from lib.pixels import *
from lib.colors import *

class DrawDirection(Enum):
    HORIZONTAL = auto()
    VERTICAL = auto()

class Screen:
    def __init__(self, pixels: Pixels):
        self.pixels = pixels

        self.last_column = pixels.get_num_columns() - 1
        self.last_row = pixels.get_num_rows() - 1

        self._memory = []    
        for _ in range(pixels.get_num_rows()):
            row = []
            for _ in range(pixels.get_num_columns()):
                row.append([Color.OFF, None])
            self._memory.append(row)

        self.clear()

    def update(self):
        self.pixels.update()

    def clear(self):
        self.fill(Color.OFF)

    def fill(self, color: Color, brightness: Optional[float] = None):
        self.pixels.fill(color, brightness)
        self.pixels.update()
        for column in range(self.pixels.get_num_columns()):
            for row in range(self.pixels.get_num_rows()):
                self._memory[row][column] = [color, brightness]

    def save(self):
        return copy.deepcopy(self._memory)

    def restore(self, memory):
        for column in range(self.pixels.get_num_columns()):
            for row in range(self.pixels.get_num_rows()):
                cell = memory[row][column]
                self.set_pixel(column, row, cell[0], cell[1])
        self.update()

    def set_pixel(self, column_num: int, row_num: int, color: Color,
        brightness: Optional[float] = None):

        if not self.on_screen(column_num, row_num):
            return
        
        self.pixels.set_pixel(column_num, row_num, color, brightness)
        self._memory[row_num][column_num] = [color, brightness]
        return

    def on_screen(self, column_num: int, row_num: int):
        return (column_num >= 0 and column_num <= self.last_column and
            row_num >= 0 and row_num <= self.last_row)

    def get_pixel(self, column_num: int, row_num: int) -> Tuple[Color, int]:
        return self._memory[row_num][column_num]

    def clear_pixel(self, column_num: int, row_num: int):
        self.set_pixel(column_num, row_num, Color.OFF)
        
    def draw_line(self, start_column: int, start_row: int, direction: DrawDirection, 
        length: int, color: Color, brightness: Optional[float] = None):

        if direction == DrawDirection.HORIZONTAL:
            for column in range(start_column, start_column + length):
                self.set_pixel(column, start_row, color, brightness)
        else:
            for row in range(start_row, start_row + length):
                self.set_pixel(start_column, row, color, brightness)

    def draw_rectangle(self, from_column: int, from_row: int, to_column: int, to_row: int,
        color: Color, brightness: Optional[float] = None, fill = False):

        columns = to_column - from_column + 1
        rows = to_row - from_row + 1

        if fill:
            for column in range(columns):
                for row in range(rows):
                    self.set_pixel(from_column + column, from_row + row, color, brightness)
        else:
            self.draw_line(from_column, from_row, DrawDirection.HORIZONTAL, columns, color, brightness)
            self.draw_line(from_column, to_row, DrawDirection.HORIZONTAL, columns, color, brightness)
            self.draw_line(from_column, from_row, DrawDirection.VERTICAL, rows, color, brightness)
            self.draw_line(to_column, from_row, DrawDirection.VERTICAL, rows, color, brightness)

    def test(self, brightness: Optional[float] = None):
        for color in Colors().colors:
            self.fill(color[1], brightness)
            time.sleep(0.5)
        self.clear()

        i = 0
        for color in Colors().colors:
            self.draw_rectangle(i, i, self.last_column - i, self.last_row - i, 
                color[1], brightness, fill = True)
            i += 1

        self.update()
        time.sleep(5)
        self.clear()

        colors_per_row = 4
        sample_width = int(self.pixels.get_num_columns() / colors_per_row)
        rows = math.ceil(len(Colors().colors) / colors_per_row)
        sample_height = int(self.pixels.get_num_rows() / rows)

        row = 0
        column = 0
        num_color = 1
        for color_pair in Colors().colors:
            self.draw_rectangle(column, row, column + sample_width - 1,
                row + sample_height - 1, color_pair[1], fill = True)
            column += sample_width

            if num_color == colors_per_row:
                num_color = 1
                column = 0
                row += sample_height
            else:
                num_color += 1

        self.update()
        time.sleep(5)
        self.clear()
        