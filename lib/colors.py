from enum import Enum, auto

class Color(Enum):
    OFF = auto()
    WHITE = auto()
    YELLOW = auto()
    ORANGE = auto()
    RED = auto()
    FUCHSIA = auto()
    MAGENTA = auto()
    PURPLE = auto()
    BLUE = auto()
    AQUA = auto()
    CYAN = auto()
    TURQOISE = auto()
    GREEN = auto()
    LIME = auto()

class Colors:
    colors = [
        ["W", Color.WHITE],
        ["Y", Color.YELLOW],
        ["O", Color.ORANGE],
        ["R", Color.RED],
        ["F", Color.FUCHSIA],
        ["M", Color.MAGENTA],
        ["P", Color.PURPLE],
        ["B", Color.BLUE],
        ["A", Color.AQUA],
        ["C", Color.CYAN],
        ["T", Color.TURQOISE],
        ["G", Color.GREEN],
        ["L", Color.LIME],
    ]

    def get(self, letter: str) -> Color:
        for color in self.colors:
            if color[0] == letter:
                return color[1]

        return Color.OFF
