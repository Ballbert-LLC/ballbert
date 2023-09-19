import threading
import queue
from Hal.Classes import Response
from Hal.Decorators import reg
from Hal.Skill import Skill
from Event_Handler import event_handler
import simpleaudio as sa

class Text_To_Speech(Skill):
    def __init__(self):
        super().__init__()
        self.audio_queue = queue.Queue()  # Create a queue for audio playback
        self.playing = False  # Flag to indicate if audio is currently playing

        event_handler.on("Audio", self.enqueue_audio)

    def enqueue_audio(self, audio_data):
        # Add audio data to the queue
        self.audio_queue.put(audio_data)

        # If audio is not currently playing, start playback
        if not self.playing:
            self.play_audio()
        

    def play_audio(self):
        while not self.audio_queue.empty():
            audio_data = self.audio_queue.get()

            # Mark that audio is currently playing
            self.playing = True

            def play_text(audio):
                start_after = 46
                wave_obj = sa.WaveObject(
                    audio[start_after:], num_channels=1, bytes_per_sample=2, sample_rate=24000
                )
                play_obj = wave_obj.play()
                play_obj.wait_done()

            play_text(audio_data)

            # Mark that audio playback is complete
            self.playing = False
            
            # Remove the audio data from the queue
            self.audio_queue.task_done()
        