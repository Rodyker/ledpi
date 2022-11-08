from abc import abstractmethod, ABC
import math
import sys
from typing import Optional, Tuple
from lib.colors import *
from lib.util import *

class Pixels(ABC):
    def __init__(self, base_brightness: int, max_brightness: int,
        relative_brightness: Optional[float] = None):
        
        self._base_brightness = base_brightness
        self._max_brightness = max_brightness

        self._relative_brightness = 1
        if relative_brightness != None:
            self._relative_brightness = relative_brightness

    @abstractmethod
    def get_num_columns(self) -> int:
        raise NotImplementedError
       
    @abstractmethod
    def get_num_rows(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def update(self):
        raise NotImplementedError

    @abstractmethod
    def fill(self, color: Color, brightness: Optional[float] = None):
        raise NotImplementedError

    @abstractmethod
    def set_pixel(self, column_num: int, row_num: int, color: Color, brightness: Optional[float] = None):
        raise NotImplementedError
    
    def _get_leds_brightness(self, color: Color, relative_brightness: Optional[float] = None
        ) -> Tuple[int, int, int]:
        
        if relative_brightness == None:
            relative_brightness = self._relative_brightness

        if relative_brightness == -1:
            brightness = self._max_brightness
        else:
            brightness = relative_brightness * self._base_brightness
        
        red = green = blue = 0

        if color == Color.OFF:
            pass
        elif color == Color.RED:
            red = int(self.red(brightness))
        elif color == Color.GREEN:
            green = int(self.green(brightness))
        elif color == Color.BLUE:
            blue = int(self.blue(brightness))
        elif color == Color.YELLOW:
            red = math.ceil(self.red(brightness) / 2) 
            green = math.ceil(self.green(brightness) / 2)
        elif color == Color.MAGENTA:
            red = math.ceil(self.red(brightness) / 2) 
            blue = math.ceil(self.blue(brightness) / 2)
        elif color == Color.CYAN:
            green = math.ceil(self.green(brightness) / 2) 
            blue = math.ceil(self.blue(brightness) / 2)
        elif color == Color.WHITE:
            red = math.ceil(self.red(brightness) / 3)
            green = math.ceil(self.green(brightness) / 3) 
            blue = math.ceil(self.blue(brightness) / 3)
        elif color == Color.ORANGE:
            red = int(self.red(brightness))
            green = math.floor(self.green(brightness) / 2)
        elif color == Color.LIME:
            green = int(self.green(brightness))
            red = math.floor(self.red(brightness) / 2)
        elif color == Color.FUCHSIA:
            red = int(self.red(brightness))
            blue = math.floor(self.blue(brightness) / 2)
        elif color == Color.PURPLE:
            blue = int(self.blue(brightness))
            red = math.floor(self.red(brightness) / 2)
        elif color == Color.AQUA:
            blue = int(self.blue(brightness))
            green = math.floor(self.green(brightness) / 2)
        elif color == Color.TURQOISE:
            green = int(self.green(brightness))
            blue = math.floor(self.blue(brightness) / 2)

        red = min_int(red, self._max_brightness)
        green = min_int(green, self._max_brightness)
        blue = min_int(blue, self._max_brightness)

        return red, green, blue

    def red(self, brightness: float):
        return brightness * 1         # 0.6

    def green(self, brightness: float):
        return brightness * 1        # 0.75

    def blue(self, brightness: float):
        return brightness * 1         # 1.5

def PixelsFactory(screen_def: str, brightness: Optional[float] = None) -> Pixels:
    if sys.platform == "win32":
        from lib.pc_pixels import PCPixels
        return(PCPixels(brightness))
    else:
        from lib.led_pixels import LEDPixels
        return(LEDPixels(screen_def, brightness))
