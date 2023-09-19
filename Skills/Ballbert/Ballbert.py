import base64
import threading
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

        self.setup_routes()

    def setup_routes(self):
        #Websocket Rotues
        
        def sentament(sentament : str):
            event_handler.trigger("sentament", sentament)
        
        assistant.websocket_client.add_route(sentament)
        
        def indecator_bar_color(color : str):
            event_handler.trigger("indecator_bar_color", color)
        
        assistant.websocket_client.add_route(indecator_bar_color)

        def handle_audio(audio):
            if audio == "stop!":
                event_handler.trigger("Audio_End")
                return 
            decoded_compressed_data = base64.b64decode(audio)
            decompressed_frame_data = zlib.decompress(decoded_compressed_data)

            event_handler.trigger("Audio", audio_data=decompressed_frame_data)

        assistant.websocket_client.add_route(handle_audio, "audio")
        
        #Event Routes
        def handle_keyword(source):
            print("Keyword")

            t= threading.Thread(target=self.handle_keyword, args=(source,))
            t.start()

        event_handler.on("Keyword", handle_keyword)
        
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
