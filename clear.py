#!/usr/bin/python

from lib.screen import *
from lib.led_pixels import *

screen = Screen(LEDPixels("data/diagonal.csv"))
screen.clear()