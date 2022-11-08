from abc import ABC, abstractmethod
from sqlite3 import PARSE_COLNAMES
from lib.util import *
import os

AUDIO_DIR = "audio"
VOLUME_STEP = 5

class SoundSample(ABC):
    CLICK         = "263133__pan14__tone-beep"
    EAT           = "404769__owlstorm__retro-video-game-sfx-bounce"
    GAME_OVER     = "190843__deathbygeko__boss-fight"
    VICTORY       = "270404__littlerobotsoundfactory__jingle-achievement-00"
    SHOOT         = "421704__bolkmar__sfx-laser-shoot-02"
    ROCKET        = "273332__robinhood76__05780-space-missile"
    EXPLOSION     = "170144__timgormly__8-bit-explosion2"
    BIG_EXPLOSION = "155790__deleted-user-1941307__shipboard-railgun"
    POWERUP       = "523654__matrixxx__powerup-10"

    @abstractmethod
    def play(self):
        raise NotImplementedError

class Sound(ABC):
    def __init__(self, volume: int, muted: bool):
        self.set_volume(volume)
        self._muted = muted

    def get_volume(self) -> int:
        return self._volume

    def set_volume(self, volume: int):
        self._volume = between_int(volume, 0, 100)

    def mute(self):
        self._muted = True

    def unmute(self):
        self._muted = False
        
    def is_muted(self):
        return self._muted

    def increase_volume(self, step = VOLUME_STEP):
        if self.is_muted():
            self.unmute()
            return

        volume = self.get_volume() + step
        volume = between_int(volume, 0, 100)
        self.set_volume(volume)

    def decrease_volume(self, step = VOLUME_STEP):
        volume = self.get_volume() - step
        volume = between_int(volume, 0, 100)
        self.set_volume(volume)

    @abstractmethod
    def get(self, filename: str) -> SoundSample:
        raise NotImplementedError

def SoundFactory(volume: int, muted: bool) -> Sound:
    if os.name == "nt":
        from lib.pc_sound import PCSound
        return PCSound(volume, muted)
    else:
        from lib.pi_sound import PiSound
        return PiSound(volume, muted)
