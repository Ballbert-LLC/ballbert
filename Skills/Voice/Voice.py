import platform
import threading
import time
import pvporcupine
import speech_recognition as sr
from pvrecorder import PvRecorder

import numpy as np
import soxr

from Config import Config

from Event_Handler import event_handler
from Hal import initialize_assistant


assistant = initialize_assistant()
config = Config()


class Voice:
    def __init__(self) -> None:
        self.porcupine_api_key = None
        
        def get_porcupine_api_key(key):
            self.porcupine_api_key = key
            
        assistant.websocket_client.add_route(get_porcupine_api_key)
        assistant.websocket_client.send_message("get_porcupine_api_key")

        
        while self.porcupine_api_key == None:
            time.sleep(1)
            
        self.porcupine = self.create_pvporcupine(self.porcupine_api_key)
        
        t = threading.Thread(target=self.start)
        t.start()

    def create_pvporcupine(self, porcupine_api_key):
        try:
            system = platform.system()

            if system == "Windows":
                path = "./Skills/Voice/Ball-Bert_en_windows_v2_2_0.ppn"
            elif system == "Darwin":
                path = "./Skills/Voice/Ball-Bert_en_mac_v2_2_0.ppn"
            elif system == "Linux":
                path = "./Skills/Voice/Ball-Bert_en_raspberry-pi_v2_2_0.ppn"
            else:
                raise Exception("Invalid System")

            return pvporcupine.create(
                access_key=porcupine_api_key,
                keyword_paths=[path],
            )
        except Exception as e:
            event_handler.trigger("Error", e)

    def start(self):
        mic = sr.Microphone(device_index=2)
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 5000

        with mic as source:
            print("Ready!")
            while True:
                audio_frames = source.stream.read(1410)

                np_audio_data = np.frombuffer(audio_frames, dtype=np.int16)

                np_audio_data = soxr.resample(np_audio_data, 44100, 16000)

                keyword_index = self.porcupine.process(np_audio_data)
                if keyword_index >= 0:
                    try:
                        print("keyword")
                        event_handler.trigger("Keyword", source)
                    except Exception as e:
                        event_handler.trigger("Error", e)
