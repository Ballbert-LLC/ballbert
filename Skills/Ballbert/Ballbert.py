import base64
import zlib
from Hal.Classes import Response
from Hal.Decorators import reg
from Hal.Skill import Skill
from Hal import initialize_assistant

from Event_Handler import event_handler

import speech_recognition as sr

assistant = initialize_assistant()


class Ballbert(Skill):
    def __init__(self):
        super().__init__()
        self.recogniser = sr.Recognizer()

        def handle_keyword(source):
            print("Keyword")
            self.handle_keyword(source)

        event_handler.on("Keyword", handle_keyword)

        def handle_audio(audio):
            decoded_compressed_data = base64.b64decode(audio)
            decompressed_frame_data = zlib.decompress(decoded_compressed_data)

            event_handler.trigger("Audio", audio_data=decompressed_frame_data)

        self.websocket_client.add_route(handle_audio, "audio")

    def handle_keyword(self, source):
        print("Keyword Detected")

        audio_data = self.recogniser.listen(source)
        # Compress binary audio data using zlib
        compressed_audio_data = zlib.compress(audio_data.frame_data)

        # Convert compressed data to base64-encoded string
        base64_compressed_audio_data = base64.b64encode(compressed_audio_data).decode(
            "utf-8"
        )

        assistant.websocket_client.send_message(
            "handle_audio",
            audio_data=base64_compressed_audio_data,
            sample_rate=audio_data.sample_rate,
            sample_width=audio_data.sample_width,
        )

    @reg(name="get_available")
    def get_available(self, double_check=False):
        """
        Checks if the backend is available

        :param boolean double_check: (Optional) If true the code double checks to make sure it is online
        """

        return True
