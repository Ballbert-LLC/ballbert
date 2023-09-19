import inspect
import json
import os
import platform
import subprocess
import time
from Event_Handler import event_handler
from .SkillMangager import SkillMangager, deepcopy
from ..Websocket_Client import Websocket_Client
from Config import Config
from ..Classes import Response


config = Config()
repos_path = "./Skills"

def serialize_action_dict(action_dict: dict):
    return {key: {"id": value["id"], "name": value["name"], "description": value["description"], "skill": value["skill"], "parameters": value["parameters"]} for key, value in action_dict.items()}


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
        self.setup_routes()

        self.porcupine_api_key = ""
        self.openai_api_key = ""

        time.sleep(1)
        self.setup_config()

        while not self.openai_api_key :
            time.sleep(1)
        self.skill_manager = SkillMangager(self.openai_api_key, self.websocket_client)

    
    def setup_routes(self):
        
        def error():
            print("Ws had an error")
            
        def echo(message):
            print(message)
            
        def add_skill(version, url: str, name: str):
            if os.path.exists(os.path.join(repos_path, name)):
                prev_action_dict: dict = deepcopy(assistant.action_dict)
                self.skill_manager.add_skill(self, name)
                new_actions_dict = self.skill_manager.get_new_actions(self, prev_action_dict)
                new_actions_dict = serialize_action_dict(new_actions_dict)
                self.websocket_client.send_message(f"skill_added/{name}", succeeded=True, new_action_dict = new_actions_dict)
                return 
            
            try:
                new_actions_dict = self.skill_manager.add_skill_from_url(self, url, name)
                new_actions_dict = serialize_action_dict(new_actions_dict)
                self.websocket_client.send_message(f"skill_added/{name}", succeeded=True, new_action_dict = new_actions_dict)

            except Exception as e:
                raise e
                self.websocket_client.send_message(f"skill_added/{name}", succeeded=False)
                
        def call_function(function_name, arguments, user_message):
            res : Response = self.call_function(function_name, **arguments)
            if not isinstance(res.data, str):
                res.data = str(res.data)
            self.websocket_client.send_message("function_result", result=res.data, function_name=function_name, original_message=user_message, succeded=res.suceeded)
            
            
        
        self.websocket_client.add_route(add_skill)
        self.websocket_client.add_route(call_function)
        self.websocket_client.add_route(error)
        self.websocket_client.add_route(echo)
        
        
    def setup_config(self):

        def get_openai_api_key(key):
            self.openai_api_key = key
            
        self.websocket_client.add_route(get_openai_api_key)
        self.openai_api_key = self.websocket_client.send_message("get_openai_api_key")

    
    def call_function(self, name:str, *args, **kwargs):
        name = name.lower()
        try:
            return self.action_dict[name]["function"](*args, **kwargs)
        except Exception as e:
            return Response(succeeded=False, data=e)

# Module-level variable to store the shared instance
assistant = None
allowed_file_paths = ["./main.py", "./Flask/main.py"]

def setup_assistant(assistant: Assistant):
    directory_names = [
        name
        for name in os.listdir("./Skills")
        if os.path.isdir(os.path.join("./Skills", name)) and name != "__pycache__"
    ]

    for name in directory_names:
        assistant.skill_manager.add_skill_from_local(name, assistant)

allowed_skills = None

def is_allowed(assistant: Assistant):
    global allowed_skills
    global allowed_file_paths
    
    def approved_skills(skills: list):
        global allowed_skills

        allowed_skills = skills
    
    assistant.websocket_client.add_route(approved_skills)
    
    assistant.websocket_client.send_message("approved_skills")
    
    while not allowed_skills:
        time.sleep(0.1)
    
    
    for skill in allowed_skills:
        new_path = os.path.join("Skills", skill, f"{skill}.py")
        allowed_file_paths.append(new_path)

    # Get the caller's frame
    caller_frame = inspect.stack()[2]

    # Extract the filename and path from the frame
    calling_file_path = caller_frame.filename

    allowed_file_paths = [os.path.abspath(path) for path in allowed_file_paths]

    for path in allowed_file_paths:
        if not (os.path.exists(path) and os.path.exists(calling_file_path)):
            continue
        if os.path.samefile(path, calling_file_path):
            break
    else:
        return False
    
    return True

# Initialization function to create the instance
def initialize_assistant():
    global assistant
    caller_frame = inspect.stack()
        
    if assistant is None:
        assistant = Assistant()
        try:
            print("setting")
            setup_assistant(assistant)
            print("setting past")
        except Exception as e:
            event_handler.trigger("Error", e)

    if is_allowed(assistant):
        return assistant
    else:
        print("unauthorised")
    

