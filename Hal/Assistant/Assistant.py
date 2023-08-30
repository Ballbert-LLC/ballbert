import inspect
import os
import platform
import subprocess
import time
from Event_Handler import event_handler
from .SkillMangager import SkillMangager
from ..Voice import Voice
from ..Websocket_Client import Websocket_Client
from Config import Config

config = Config()


class NoVoiceException(Exception):
    pass


class Assistant:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.action_dict = dict()
        self.installed_skills = dict()
        uid = config["UID"]
        self.websocket_client = Websocket_Client(uid)

        self.porcupine_api_key = ""
        self.openai_api_key = ""

        time.sleep(1)
        self.setup_config()

        time.sleep(1)
        self.skill_manager = SkillMangager(self.openai_api_key)
        voice = self.setup_voice()
        self.voice = voice

    def setup_config(self):
        def get_porcupine_api_key(key):
            self.porcupine_api_key = key

        self.websocket_client.add_route(get_porcupine_api_key, "get_porcupine_api_key")
        self.websocket_client.send_message("get_porcupine_api_key")

        def get_openai_api_key(key):
            self.openai_api_key = key

        self.websocket_client.add_route(get_openai_api_key, "get_openai_api_key")
        self.websocket_client.send_message("get_openai_api_key")

        def error():
            print("Ws had an error")

        self.websocket_client.add_route(error)

    def setup_voice(self):
        try:
            voice = Voice(self.porcupine_api_key)
            return voice
        except Exception as e:
            event_handler.trigger("Error", e)
            return None

    def voice_to_voice_chat(self):
        try:
            if self.voice == None:
                raise NoVoiceException("No Voice")
            self.voice.start()
        except NoVoiceException as e:
            event_handler.trigger("Error", e)
            self.voice = self.setup_voice()
            self.voice_to_voice_chat()
        except Exception as e:
            event_handler.trigger("Error", e)


# Module-level variable to store the shared instance
assistant = None


# Initialization function to create the instance
def initialize_assistant():
    allowed_file_paths = ["./main.py", "./Flask/main.py"]
    allowed_skills = ["Ballbert"]

    for skill in allowed_skills:
        new_path = os.path.join("Skills", skill, f"{skill}.py")
        allowed_file_paths.append(new_path)

    def setup_assistant(assistant: Assistant):
        directory_names = [
            name
            for name in os.listdir("./Skills")
            if os.path.isdir(os.path.join("./Skills", name)) and name != "__pycache__"
        ]

        for name in directory_names:
            print(name)
            assistant.skill_manager.add_skill_from_local(name, assistant)

    # Get the caller's frame
    caller_frame = inspect.stack()[1]

    # Extract the filename and path from the frame
    calling_file_path = caller_frame.filename

    allowed_file_paths = [os.path.abspath(path) for path in allowed_file_paths]

    for path in allowed_file_paths:
        if not (os.path.exists(path) and os.path.exists(calling_file_path)):
            continue
        if os.path.samefile(path, calling_file_path):
            break
    else:
        raise Exception("Hey dont do that")

    global assistant
    if assistant is None:
        assistant = Assistant()

        try:
            setup_assistant(assistant)
        except Exception as e:
            event_handler.trigger("Error", e)

        return assistant

    else:
        return assistant
