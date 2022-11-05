import signal
import sys
from typing import List, Callable, Optional

from lib.screen import *
from lib.gamepad import *
from lib.sound import *
from lib.text import *
from lib.config import *
from lib.sprites import *

CONTROL_VOLUME = Button.SELECT
CONTROL_VOLUME_UP = Button.HAT_UP
CONTROL_VOLUME_DOWN = Button.HAT_DOWN

class Game:
    def __init__(self, screen: Screen, text: Text, gamepad: Gamepad, sound: Sound, 
        config: Config, sprites: Optional[Sprites] = None):

        self.screen = screen
        self.text = text
        self.gamepad = gamepad
        self.sound = sound
        self.config = config
        self.victory_sound = sound.get(SoundSample.VICTORY)
        self.game_over_sound = sound.get(SoundSample.GAME_OVER)
        self.click_sound = sound.get(SoundSample.CLICK)

        if sprites != None:
            self.sprites = sprites

    def stop(self):
        self.screen.clear()
        self.gamepad.stop()

    def show_game_over(self, score: Optional[int] = None):
        if score != None and score > self.config.get_int("high_score", 0):
            self.victory_sound.play()
            self.config.set("high_score", score)
            lines = [["HIGH", Color.WHITE], ["SCORE", Color.YELLOW]]
        else:
            self.game_over_sound.play()
            lines = [["GAME", Color.RED], ["OVER", Color.GREEN]]

        self._add_points(lines, score)
        self.show_text_screen(lines)

    def show_win_lose(self, win: bool, score: Optional[int] = None):
        if win:
            self.victory_sound.play()
            lines = [["YOU", Color.WHITE], ["WIN", Color.YELLOW]]
        else:
            self.game_over_sound.play()
            lines = [["YOU", Color.RED], ["LOSE", Color.GREEN]]

        self._add_points(lines, score)
        self.show_text_screen(lines)

    def _add_points(self, lines, score: Optional[int] = None):
        if score != None:
            lines.append([str(score), Color.MAGENTA, " PTS", Color.BLUE])

    def show_text_screen(self, lines) -> Button:
        self.screen.clear()
        self.text.write(lines)
        self.screen.update()
        button = self.wait_any_button()
        self.screen.clear()
        return button

    def wait_any_button(self, delay = 0.5, timeout: float = 0) -> Button:
        gamepad = self.gamepad
        while True:
            button = gamepad.wait_any_button(delay, timeout)
            if button == CONTROL_VOLUME:
                self._change_volume()
                continue

            gamepad.clear_sticky_button()
            return button

    def _change_volume(self):
        screen = self.screen
        sound = self.sound

        memory = screen.save()
        screen.clear()

        while True:
            self.text.write([
                ["VOL", Color.RED], 
                [str(sound.get_volume()), Color.GREEN]])
            screen.update()

            button = self.gamepad.wait_any_button(timeout = 2)
            if button == CONTROL_VOLUME_DOWN:
                sound.decrease_volume()
            elif button == CONTROL_VOLUME_UP:
                sound.increase_volume()
            else:
                screen.restore(memory)
                return
                
            self.click_sound.play()
            self.config.set("volume", sound.get_volume())

_game: Game

def sigterm_handler(_signo, _stack_frame):
    print("Killed")
    _game.screen.clear()
    sys.exit(0)

def GameFactory(screen_def: str, font_def: str, config_file: str, 
    sticky_buttons: List[Button] = [], sprite_def: Optional[str] = None,
    brightness: Optional[float] = None) -> Game:
    
    screen = Screen(PixelsFactory(screen_def, brightness))
    text = Text(font_def, screen)
    gamepad = Gamepad(0, sticky_buttons)
    config = Config(config_file)
    sound = SoundFactory(config.get_int("volume", 100), config.get_bool("muted", False))

    sprite = None
    if sprite_def != None:
        sprite = Sprites(sprite_def, screen)

    global _game
    _game = Game(screen, text, gamepad, sound, config, sprite)

    signal.signal(signal.SIGTERM, sigterm_handler)

    return _game

def GameLauncher(game: Game, start: Callable[[Game],None]):
    ran_from_menu = "menu" in sys.argv

    try:
        while True:
            start(game)

            if ran_from_menu:
                break

    except KeyboardInterrupt:
        print("Interrupted")
        pass

    game.stop()