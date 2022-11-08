# Requirements:
# - enable spi using raspi-config
# - add spidev.bufsiz=32768 to end of /boot/cmdline.txt
# - add to /etc/rc.local:
#   CPUFREQ="/sys/devices/system/cpu/cpu0/cpufreq/"
#   cat $CPUFREQ/cpuinfo_max_freq > $CPUFREQ/scaling_min_freq
# - reboot

import csv
import board
from typing import Optional
from neopixel import NeoPixel
from lib.colors import *
from lib.pixels import *

class LEDPixels(Pixels):
    _BASE_BRIGHTNESS = 92
    _MAX_BRIGHTNESS = 255

    def __init__(self, definition_filename: str, relative_brightness: Optional[float] = None):
        super().__init__(self._BASE_BRIGHTNESS, self._MAX_BRIGHTNESS, relative_brightness)

        definition_file = open(definition_filename)
        definition_reader = csv.reader(definition_file)

        self._pixels = []
        for row in definition_reader:
            self._pixels.append(row)

        self._num_columns = len(self._pixels[0])
        self._num_rows = len(self._pixels)

        num_pixels = self._num_columns * self._num_rows
        self._strip = NeoPixel(board.D10, num_pixels, auto_write = False)

    def get_num_columns(self) -> int:
        return self._num_columns

    def get_num_rows(self) -> int:
        return self._num_rows

    def update(self):
        self._strip.show()

    def fill(self, color: Color, relative_brightness: Optional[float] = None):
        self._strip.fill(self._get_leds_brightness(color, relative_brightness))

    def set_pixel(self, column_num: int, row_num: int, color: Color,
        relative_brightness: Optional[float] = None):

        pixel_num = int(self._pixels[row_num][column_num])
        self._strip[pixel_num] = self._get_leds_brightness(color, relative_brightness)
        return
