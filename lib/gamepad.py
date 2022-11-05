from dataclasses import dataclass
import threading
import time
import inputs
from enum import Enum, auto
from typing import List, Callable, Optional

class Button(Enum):
    NONE = auto()

    START = auto()
    SELECT = auto()

    YELLOW = auto()
    GREEN = auto()
    BLUE = auto()
    RED = auto()

    T_L_SHOULDER = auto()
    T_R_SHOULDER = auto()

    L_STICK_THUMB = auto()
    R_STICK_THUMB = auto()

    HAT_UP = auto()
    HAT_DOWN = auto()
    HAT_LEFT = auto()
    HAT_RIGHT = auto()

    L_STICK_UP = auto()
    L_STICK_DOWN = auto()
    L_STICK_LEFT = auto()
    L_STICK_RIGHT = auto()

    R_STICK_UP = auto()
    R_STICK_DOWN = auto()
    R_STICK_LEFT = auto()
    R_STICK_RIGHT = auto()

    B_L_SHOULDER = auto()
    B_R_SHOULDER = auto()

    KEY_UP = auto()
    KEY_DOWN = auto()
    KEY_LEFT = auto()
    KEY_RIGHT = auto()
    KEY_L_SHIFT = auto()
    KEY_SPACE = auto()

@dataclass
class ButtonInfo:
    id: Button
    code: str
    condition: Callable[[int], bool]
    pressed: bool

class Gamepad:
    _TRACKING_CHECK_DELAY = 1 / 100     # times per second
    PRE_CHECK_DELAY = 0.5               # wait for previous button to be depressed

    def __init__(self, num: int, _sticky_buttons: List[Button] = []):
        self.init_button_table()

        self._sticky_button = Button.NONE
        self._sticky_buttons = _sticky_buttons
        self._ignored_sticky_buttons = []
        self._tracking_lock = threading.Lock()

        gamepads: List[inputs.GamePad] = inputs.DeviceManager().gamepads
        self._gamepad: Optional[inputs.GamePad] = None
        if len(gamepads) > num:
            self._gamepad = gamepads[num]
            thread = threading.Thread(target = self.gamepad_tracker, daemon = True)
            thread.start()

        keyboards: List[inputs.Keyboard] = inputs.DeviceManager().keyboards
        self._keyboard: Optional[inputs.Keyboard] = None
        if len(keyboards) > 0:
            self._keyboard = keyboards[0]
            thread = threading.Thread(target = self.keyboard_tracker, daemon = True)
            thread.start()

    def stop(self):
        if self._keyboard != None:
            self._keyboard.__del__()

    def init_button_table(self):
        push_button = lambda s: s == 1

        hat1 = lambda s: s == -1
        hat2 = lambda s: s == 1

        stick1 = lambda s: s < -10000
        stick2 = lambda s: s > 10000

        accelerator = lambda s: s > 100

        self._buttons = [
            ButtonInfo(Button.START,         "BTN_START",     push_button, False),
            ButtonInfo(Button.SELECT,        "BTN_SELECT",    push_button, False),

            ButtonInfo(Button.YELLOW,        "BTN_WEST",      push_button, False),
            ButtonInfo(Button.GREEN,         "BTN_SOUTH",     push_button, False),
            ButtonInfo(Button.BLUE,          "BTN_NORTH",     push_button, False),
            ButtonInfo(Button.RED,           "BTN_EAST",      push_button, False),

            ButtonInfo(Button.T_L_SHOULDER,  "BTN_TL",        push_button, False),
            ButtonInfo(Button.T_R_SHOULDER,  "BTN_TR",        push_button, False),

            ButtonInfo(Button.L_STICK_THUMB, "BTN_THUMBL",    push_button, False),
            ButtonInfo(Button.R_STICK_THUMB, "BTN_THUMBR",    push_button, False),

            ButtonInfo(Button.HAT_UP,        "ABS_HAT0Y",     hat1,        False),
            ButtonInfo(Button.HAT_DOWN,      "ABS_HAT0Y",     hat2,        False),
            ButtonInfo(Button.HAT_LEFT,      "ABS_HAT0X",     hat1,        False),
            ButtonInfo(Button.HAT_RIGHT,     "ABS_HAT0X",     hat2,        False),

            ButtonInfo(Button.L_STICK_UP,    "ABS_Y",         stick1,      False),
            ButtonInfo(Button.L_STICK_DOWN,  "ABS_Y",         stick2,      False),
            ButtonInfo(Button.L_STICK_LEFT,  "ABS_X",         stick1,      False),
            ButtonInfo(Button.L_STICK_RIGHT, "ABS_X",         stick2,      False),

            ButtonInfo(Button.R_STICK_UP,    "ABS_RY",        stick1,      False),
            ButtonInfo(Button.R_STICK_DOWN,  "ABS_RY",        stick2,      False),
            ButtonInfo(Button.R_STICK_LEFT,  "ABS_RX",        stick1,      False),
            ButtonInfo(Button.R_STICK_RIGHT, "ABS_RX",        stick2,      False),

            ButtonInfo(Button.B_L_SHOULDER,  "ABS_Z",         accelerator, False),
            ButtonInfo(Button.B_R_SHOULDER,  "ABS_RZ",        accelerator, False),

            ButtonInfo(Button.KEY_UP,        "KEY_UP",        push_button, False),
            ButtonInfo(Button.KEY_DOWN,      "KEY_DOWN",      push_button, False),
            ButtonInfo(Button.KEY_LEFT,      "KEY_LEFT",      push_button, False),
            ButtonInfo(Button.KEY_RIGHT,     "KEY_RIGHT",     push_button, False),
            ButtonInfo(Button.KEY_L_SHIFT,   "KEY_LEFTSHIFT", push_button, False),
            ButtonInfo(Button.KEY_SPACE,     "KEY_SPACE",     push_button, False)
       ]

    def set_sticky_button(self, button: Button):
        self._sticky_button = button

    def get_sticky_button(self) -> Button:
        return self._sticky_button

    def clear_sticky_button(self):
        self.set_sticky_button(Button.NONE)

    def ignore_sticky_buttons(self, buttons: List[Button]):
        self._ignored_sticky_buttons = buttons

    def clear_ignored_sticky_button(self):
        self._ignored_sticky_buttons = []

    def pause_tracking(self):
        self._tracking_lock.acquire()

    def restart_tracking(self):
        self._tracking_lock.release()

    def gamepad_tracker(self):
        if self._gamepad == None:
            return

        while True:
            for event in self._gamepad.read():
                if event.ev_type != "Sync":
                   self.process_event(event)

    def keyboard_tracker(self):
        if self._keyboard == None:
            return

        try:
            while True:
                for event in self._keyboard.read():
                    if event.ev_type == "Key":
                        self.process_event(event)
        except Exception:
            pass

    def process_event(self, event: inputs.InputEvent):
        self._tracking_lock.acquire()

        for button in self._buttons:
            if event.code == button.code:
                button.pressed = button.condition(event.state)
                
                if (button.pressed and (button.id in self._sticky_buttons) and
                    (button.id not in self._ignored_sticky_buttons)):

                    self._sticky_button = button.id

        self._tracking_lock.release()

    def get_one(self) -> Button:
        for button in self._buttons:
            if button.pressed:
                return button.id
        return Button.NONE

    def get_all(self) -> List[Button]:
        buttons = []
        for button in self._buttons:
            if button.pressed:
                buttons.append(button.id)
        return buttons

    def wait_any_button(self, delay = PRE_CHECK_DELAY, timeout: float = 0) -> Button:
        start_time = time.time()

        if delay > 0:
            time.sleep(delay)

        while True:
            button = self.get_one()
            if button != Button.NONE:
                return button

            time.sleep(self._TRACKING_CHECK_DELAY)

            passed_time = time.time() - start_time
            if (timeout > 0 and passed_time > timeout):
                return Button.NONE
