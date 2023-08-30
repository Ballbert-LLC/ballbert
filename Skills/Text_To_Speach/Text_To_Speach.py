from Hal.Classes import Response
from Hal.Decorators import reg
from Hal.Skill import Skill
from Event_Handler import event_handler
import simpleaudio as sa


class Text_To_Speach(Skill):
    def __init__(self):
        super().__init__()
        def tts(audio_data):
            self.tts(audio_data)

        event_handler.on("Audio", tts)

    def tts(self, audio_data: bytes):
        self.play_text(audio_data)

    def play_text(self, audio):
        # have to cut off begining to prevent weird popping
        start_after = 46
        # Create a simpleaudio WaveObject from the audio content
        wave_obj = sa.WaveObject(
            audio[start_after:], num_channels=1, bytes_per_sample=2, sample_rate=24000
        )

        # Play the audio
        play_obj = wave_obj.play()
        play_obj.wait_done()
