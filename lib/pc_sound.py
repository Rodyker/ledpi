import pyglet
from lib.sound import *

class PCSoundSample(SoundSample):
    def __init__(self, sound: Sound, sample: pyglet.media.Player):
        self._sound = sound
        self._sample = sample

    def play(self):
        if not self._sound.is_muted():
            player = pyglet.media.Player()
            player.queue(self._sample)
            player.volume = self._sound.get_volume() / 100
            player.play()

class PCSound(Sound):
    def get(self, filename: str) -> PCSoundSample:
        sample: pyglet.media.Player
        sample = pyglet.media.load(AUDIO_DIR + "/" + filename + ".wav",
            streaming = False)
        return PCSoundSample(self, sample)
