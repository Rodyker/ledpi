import csv
import time
from lib.screen import *

class Text:
    _symbols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 
        'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    font_height = 5

    def __init__(self, definition_filename: str, screen: Screen):
        self._screen = screen
        definition_file = open(definition_filename)
        definition_reader = csv.reader(definition_file)

        self._fonts = []
        i = 0
        for row in definition_reader:
            if i == self.font_height:
                i = 0
                continue
            self._fonts.append(row)
            i += 1

        self._max_font_width = len(self._fonts[0])

    def write_letter(self, letter: str, column: int, row: int, color: Color,
        brightness: Optional[float] = None) -> int:

        letter_index = self._symbols.index(letter)
        font_index = letter_index * 5

        for font_column in range(self._max_font_width):
            empty_column = True
            for i in range(self.font_height):
                if self._fonts[font_index + i][font_column] != "":
                    empty_column = False
                    break
            if empty_column:
                return font_column

            pixel_column = column + font_column
            pixel_row = row

            for font_row in range(font_index, font_index + self.font_height):        
                pixel_color = color
                if self._fonts[font_row][font_column] == "":
                    pixel_color = Color.OFF

                self._screen.set_pixel(pixel_column, pixel_row, pixel_color, brightness)
                pixel_row += 1

        return self._max_font_width

    def write_at(self, text: str, column: int, row: int, color: Color,
        brightness: Optional[float] = None) -> int:
        
        first = True
        for letter in text:
            if letter == " ":
                column += 1
                continue

            letter_width = self.write_letter(letter, column, row, color, brightness)
            column += letter_width + 1

        return column

    def write(self, lines, brightness: Optional[float] = None):
        for num_line, line in enumerate(lines):
            column = 0
            row = self.font_height * num_line + num_line

            self._screen.draw_rectangle(0, row, self._screen.last_column, 
                row + self.font_height - 1, Color.OFF, fill = True)

            pairs = int(len(line) / 2)
            for pair in range(pairs):
                text = line[pair * 2]
                color = line[pair * 2 + 1]
                column += self.write_at(text, column, row, color,
                    brightness)

    def test(self):
        self.write([
            ["LED", Color.RED], 
            ["SCREEN", Color.GREEN],
            ["TEST", Color.BLUE]])
        self._screen.update()
        time.sleep(1)
        self._screen.clear()
        