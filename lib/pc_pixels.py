import time
from typing import List, Optional
from lib.colors import *
from lib.pixels import *
import pyglet
from pyglet import shapes

class Shape(Enum):
    CIRCLE = auto()
    SQUARE = auto()

class PCPixels(Pixels):
    COLUMNS = 24
    ROWS = 18
    SHAPE_WIDTH = 16
    BORDER = SHAPE_WIDTH
    DEFAULT_SHAPE = Shape.CIRCLE
    _MAX_BRIGHTNESS = 255
    _BASE_BRIGHTNESS = _MAX_BRIGHTNESS

    def __init__(self, relative_brightness: Optional[float] = None,
        shape: Shape = DEFAULT_SHAPE):
        
        super().__init__(self._BASE_BRIGHTNESS, self._MAX_BRIGHTNESS, relative_brightness)

        self._shape = shape
        self._interval = self.SHAPE_WIDTH * 2
        self._width_pixels = self.COLUMNS * self._interval + self.BORDER * 2
        self._height_pixels = self.ROWS * self._interval + self.BORDER * 2

        self._window = pyglet.window.Window(self._width_pixels, self._height_pixels)
        self._batch = pyglet.graphics.Batch()

        self._shapes: List[List[shapes._ShapeBase]] = []
        for row_num in range(self.ROWS):
            row: List[shapes._ShapeBase] = []

            for column_num in range(self.COLUMNS):
                x = column_num * self._interval + self.SHAPE_WIDTH + self.BORDER
                y = row_num * self._interval + self.SHAPE_WIDTH + self.BORDER
                row.append(self._create_shape(x, self._height_pixels - y))

            self._shapes.append(row)

    def get_num_columns(self) -> int:
        return self.COLUMNS
       
    def get_num_rows(self) -> int:
        return self.ROWS

    def update(self):
        pulse_time = 1.25 / 1000000
        bits_per_pixel = 24
        pixels = self.COLUMNS * self.ROWS
        time.sleep(pixels * bits_per_pixel * pulse_time)

        pyglet.clock.tick(True)
        pyglet.app.platform_event_loop.dispatch_posted_events()
        self._window.switch_to()
        self._window.dispatch_events()
        self._batch.draw()
        self._window.flip()

    def fill(self, color: Color, brightness: Optional[float] = None):
        for column in range(self.COLUMNS):
            for row in range(self.ROWS):
                self.set_pixel(column, row, color, brightness)

    def set_pixel(self, column_num: int, row_num: int, color: Color,
        brightness: Optional[float] = None):
        
        shape = self._shapes[row_num][column_num]
        shape.color = self._get_leds_brightness(color, brightness)

    def _create_shape(self, x: int, y: int) -> shapes._ShapeBase:
        if self._shape == Shape.SQUARE:
            return shapes.Rectangle(x, y, self.SHAPE_WIDTH, self.SHAPE_WIDTH, batch = self._batch)

        return shapes.Circle(x, y, self.SHAPE_WIDTH / 2, batch = self._batch)
