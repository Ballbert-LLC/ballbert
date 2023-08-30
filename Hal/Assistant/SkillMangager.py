import json
import re
import socket
import openai
import inspect
import shutil

import yaml
from git import Repo
import importlib

from Hal.Assistant import Assistant
from Hal.Decorators import reg

import os
from Config import Config

config = Config()

repos_path = f"{os.path.abspath(os.getcwd())}/Skills"

NoneType = type(None)
import requests


def save_image_from_url(url, filename):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Image saved as {filename}")
        else:
            print("Failed to retrieve the image")
    except Exception as e:
        print(f"An error occurred: {e}")


def rmtree_hard(path, _prev=None):
    try:
        shutil.rmtree(path)
    except PermissionError as e:
        if e == _prev:
            return
        match = re.search(r"Access is denied: '(.*)'", str(e))
        if match:
            file_path = match.group(1)
            os.chmod(file_path, 0o777)

            # Delete the file
            os.remove(file_path)
            rmtree_hard(path, _prev=e)
        else:
            raise e


def deepcopy(original_dict):
    """
    Performs a deep copy of a dictionary.

    Args:
        original_dict (dict): The original dictionary to be copied.

    Returns:
        dict: A deep copy of the original dictionary.
    """
    copied_dict = {}
    for key, value in original_dict.items():
        if isinstance(value, dict):
            copied_dict[key] = deepcopy(value)
        elif isinstance(value, list):
            copied_dict[key] = value.copy()
        else:
            copied_dict[key] = value
    return copied_dict


class SkillMangager:
    def __init__(self, openai) -> None:
        self.openai = openai

    def get_actions_dict(self):
        """
        returns a formated actions dict from the reg.all
        """ 
        action_dict: dict = reg.all
        for skill_id, item in action_dict.items():
            _parameters = action_dict[skill_id]["docstring"].params

            action_dict[skill_id]["parameters"] = (
                action_dict[skill_id]["parameters"]
                if "parameters" in action_dict[skill_id]
                else {}
            )

            for param in _parameters:
                _name = param.arg_name
                _type = param.type_name

                _description = param.description
                _required = not param.is_optional

                action_dict[skill_id]["parameters"][_name] = {
                    "type": _type,
                    "description": _description,
                    "required": _required,
                }

            if "self" in action_dict[skill_id]["parameters"]:
                del action_dict[skill_id]["parameters"]["self"]
        return action_dict

    def get_class_function(self, class_instance):
        "returns the methods of a class_instance that match reg.all"
        class_functions = dict()

        for name, value in inspect.getmembers(class_instance):
            is_method = inspect.ismethod(value) and hasattr(value, "__func__")
            # Check if the function has the reg Decorator First goes through every element of the class, and it checks
            # if it is a function. It then checks if that function is also in the dict of every function with the
            # decorator
            if is_method and name in [
                value["func_name_in_class"] for key, value in reg.all.items()
            ]:
                class_functions[name] = value.__func__

        return class_functions

    def update_actions_function(self, class_functions, action_dict, class_instance):
        "returns a new version of action_dict where the functions are the class version fo the functions"
        new_action_dict = deepcopy(action_dict)

        for func_name, func in class_functions.items():
            for action_name, values in new_action_dict.items():
                new_values = deepcopy(values)
                if func_name == new_values["func_name_in_class"]:
                    # factory is in order to lose referance to the sub function

                    def wrapper_func_factory(func):
                        def wrapper_func(*args, **kwargs):
                            signature = inspect.signature(func)
                            if len(signature.parameters) > 0:
                                return func(class_instance, *args, **kwargs)
                            else:
                                return func(*args, **kwargs)

                        return wrapper_func

                    new_values["function"] = wrapper_func_factory(func)
                    new_values["class_instance"] = class_instance
                    new_action_dict[action_name] = new_values

        return new_action_dict

    def add_skill(self, assistant, skill):
        """Adds a skill to the memeory

        Keyword arguments:
        assistant -- Assistant instance
        assistant -- Name of skill
        Return: return_description
        """

        print("skill", skill)
        prev_actions_dict = deepcopy(assistant.action_dict)

        module = importlib.import_module(f"Skills.{skill}")

        desired_class = getattr(module, skill)

        action_dict = self.get_actions_dict()

        action_dict = self.get_new_actions_from_current_actions(
            action_dict, prev_actions_dict
        )

        image = self.get_image_url(skill=skill, action_dict=action_dict)

        class_instance = desired_class()

        class_functions = self.get_class_function(class_instance)

        assistant.installed_skills[skill] = {
            "image": image,
            "name": skill,
            "version": 0.0,
            "actions": class_functions,
            "class": class_instance,
        }

        action_dict = self.update_actions_function(
            class_functions, action_dict, class_instance
        )

        for key, value in action_dict.items():
            assistant.action_dict[key] = value

    def get_new_actions_from_current_actions(self, new_actions_dict, old_actions_dict):
        "gets actions in the new dict that were not in the old dict"
        updated_actions = {}
        for key, _ in new_actions_dict.items():
            if key not in old_actions_dict:
                updated_actions[key] = new_actions_dict[key]

        return updated_actions

    def get_image_url(self, skill, action_dict):
        "returns the url of the action's iamge"
        if os.path.exists(os.path.join(repos_path, skill, "icon.png")):
            shutil.copyfile(
                os.path.join(repos_path, skill, "icon.png"),
                os.path.join(
                    os.path.abspath("./"),
                    "Flask",
                    "static",
                    "images",
                    f"{skill}_icon.png",
                ),
            )

            IPAddr = socket.gethostbyname(socket.gethostname())

            image = f"https://{IPAddr}:5000/images/{skill}_icon.png"
        else:
            res = ""

            description = res or None

            with open(f"{repos_path}/{skill}/config.yaml", "r") as stream:
                data_loaded = yaml.safe_load(stream)
                name = data_loaded["name"]
                description = (
                    data_loaded["description"]
                    if "description" in data_loaded
                    else "No description provided"
                )

            des = ""
            for id, value in action_dict.items():
                if name == value["skill"]:
                    des += f"      Name: {value['name']}, Paramiters: {value['parameters']}\n"

            result = f"""

                Name of skill:
                    {name}

                Description of skill:
                    {description}

                Actions:
            {des}

            """
            openai.api_key = self.openai

            prompt = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a prompt generator for an image generator that. Your prompts are made to be an turn into an icon for a skill addon with the details in the paramiters the user provides. Constraints: Speak in language that an image generator could understand. Keep max charictors at 500",
                    },
                    {"role": "user", "content": result},
                ],
            )

            prompt = prompt["choices"][0]["message"]["content"]

            response = openai.Image.create(prompt=prompt[0:500], n=1, size="1024x1024")

            image_url = response["data"][0]["url"]
            image = image_url

            save_image_from_url(image_url, os.path.join(repos_path, skill, "icon.png"))

        return image

    def get_new_actions(self, assistant, prev_action_dict):
        "gets actions in the assistant's actions dict that were not in the old dict"

        return self.get_new_actions_from_current_actions(assistant.action_dict, prev_action_dict)

    def add_skill_from_url(self, assistant: Assistant, url: str, name: str):
        """downloads the skill from github

        Args:
            assistant (Assistant): The assistant instance
            url (str): the url of the skill
            name (str): the name of the skill

        Returns:
            dict: the new actions_dict of the skill
        """
        
        Repo.clone_from(url, f"{repos_path}/{name}", depth=1)
        
        prev_action_dict: dict = deepcopy(assistant.action_dict)

        if not self.is_folder_valid(f"{repos_path}/{name}"):
            rmtree_hard(os.path.join(repos_path, name))
            raise Exception("Invallid Package")
        
        try:
            self.add_skill(assistant, name)
            new_action_dict: dict = self.get_new_actions(assistant, prev_action_dict)
        except Exception as e:
            if os.path.exists(f"{repos_path}/{name}"):
                rmtree_hard(f"{repos_path}/{name}")
            raise e

        return new_action_dict

    def is_folder_valid(self, folder_path):
        """checks if a folder is valid

        Args:
            folder_path (str): the path of the folder

        Returns:
            bool: weather the folder is valid
        """
        # Read the config file
        config_file_path = os.path.join(folder_path, "config.yaml")
        with open(config_file_path, "r") as config_file:
            config = yaml.safe_load(config_file)

        # Get the name from the config
        name = config.get("name")

        # Check if the name matches a file in the folder
        file_names = os.listdir(folder_path)
        if f"{name}.py" not in file_names:
            print("name not in file names")
            return False

        # Check if the folder contains a class with the same name
        module_file_path = os.path.join(folder_path, f"{name}.py")
        if not os.path.isfile(module_file_path):
            print("module file path not a file")
            return False

        # Read the file contents
        with open(module_file_path, "r") as module_file:
            file_contents = module_file.read()

        # Check if the class with the same name exists in the file
        if f"class {name}" not in file_contents:
            print("class name not in file contents")
            return False

        return True

    def remove_skill(self, skill_name: str, assistant: Assistant):
        self.remove_from_memory(skill_name, assistant)
        self.delete_files(skill_name)

    def delete_files(self, skill_name):
        rmtree_hard(os.path.join(repos_path, skill_name))

    def remove_from_memory(self, skill_name: str, assistant: Assistant):
        # reg.all
        reg_copy = reg.all.copy()
        for key, value in reg.all.items():
            if value["skill"].lower() == skill_name.lower():
                del reg_copy[key]

        reg.all = reg_copy

        # action_dict
        action_dict_copy = assistant.action_dict.copy()

        for key, value in assistant.action_dict.items():
            key: str
            skill = key.split("-")[0]

            if skill.lower() == skill_name.lower():
                del action_dict_copy[key]

        assistant.action_dict = action_dict_copy

        # installed_skills
        installed_skills_copy = assistant.installed_skills.copy()

        for key, value in assistant.installed_skills.items():
            key: str
            skill = key

            if skill.lower() == skill_name.lower():
                del installed_skills_copy[key]

        assistant.installed_skills = installed_skills_copy