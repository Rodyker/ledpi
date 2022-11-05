import subprocess
from simpleaudio import WaveObject
from lib.sound import *

class PiSoundSample(SoundSample):
    def __init__(self, sound: Sound, sample: WaveObject):
        self._sound = sound
        self._sample = sample

    def play(self):
        if not self._sound.is_muted():
            self._sample.play()

class PiSound(Sound):
    def set_volume(self, volume: int):
        super().set_volume(volume)
        command = ["amixer", "sset", "Master", "{}%".format(self._volume)]
        subprocess.run(command, stdout = subprocess.DEVNULL)

    def get(self, filename: str) -> PiSoundSample:
        sample = WaveObject.from_wave_file(AUDIO_DIR + "/" + filename + ".wav")
        return PiSoundSample(self, sample)
