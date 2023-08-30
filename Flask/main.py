import os
from fastapi import APIRouter, File, UploadFile
import yaml
from Config import Config
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import speech_recognition as sr
from pvrecorder import PvRecorder
from fastapi import status, HTTPException
from Hal.Classes import HalExeption
from OTAWifi import set_wifi_credentials


router = APIRouter()


repos_path = "./Skills"



# @router.post("/add_skill")
# def add_skill(json_data: dict):
#     from Hal import initialize_assistant

#     assistant = initialize_assistant()
#     try:
#         assistant.skill_manager.add_skill_from_url(assistant, json_data["url"])
#     except HalExeption as e:
#         raise HTTPException(
#             status_code=e.error_code,
#             detail=str(e),
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=str(e),
#         )
#     else:
#         response = {"status_code": 200}
#         return response


# @router.post("/remove_skill")
# def remove_skill(json_data: dict):
#     try:
#         from Hal import initialize_assistant

#         assistant = initialize_assistant()
#     except HalExeption as e:
#         raise HTTPException(
#             status_code=e.error_code,
#             detail=e,
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=e,
#         )

#     try:
#         response = assistant.skill_manager.remove_skill(
#             json_data["skill_name"], assistant
#         )
#     except HalExeption as e:
#         raise HTTPException(
#             status_code=e.error_code,
#             detail=e,
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=e,
#         )
#     else:
#         return response


# @router.post("/config")
# def handle_config(json_data: dict):
#     try:
#         if "values" not in json_data:
#             raise HTTPException(
#                 status_code=400,
#                 detail="values not in json data",
#             )

#         values = json_data["values"]

#         for name, value in values.items():
#             try:
#                 skill = name.split("-")[0]
#                 field = name.split("-")[1]
#             except Exception as e:
#                 continue

#             settingsPath = os.path.join(repos_path, skill, "settings.yaml")
#             if not os.path.exists(settingsPath):
#                 continue

#             if value == "True" or value == "true":
#                 value = True

#             with open(settingsPath, "r") as f:
#                 existing_yaml = yaml.safe_load(f)

#             if not existing_yaml or isinstance(existing_yaml, str):
#                 existing_yaml = {}

#             obj = {field: value}

#             # Merge existing YAML with new data
#             merged_yaml = {**existing_yaml, **obj}

#             # Write merged YAML to output file
#             with open(settingsPath, "w") as f:
#                 yaml.dump(merged_yaml, f, default_flow_style=False)

#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#         )
#     else:
#         response = {"status_code": 200}
#         return response


# @router.get("/images/{image_path}")
# async def get_image(image_path: str):
#     # Assuming the images are stored in a directory named 'images'
#     image_location = f"./Flask/static/images"
#     image_path = os.path.join(image_location, image_path)
#     if os.path.exists(image_path):
#         # Return the image file as a response
#         return FileResponse(image_path)
#     else:
#         return {"status_code": 500}


# @router.get("/get_config")
# def get_config(skill_name):
#     try:
#         from Hal import initialize_assistant

#         assistant = initialize_assistant()
#         response = {"status_code": 200, "config": assistant.skill_manager.get_config(skill_name)}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=e)

#     return response


# @router.get("/get_settings_meta_for_skill")
# def get_settings_meta_for_skill(skill_name):
#     try:
#         from Hal import initialize_assistant

#         assistant = initialize_assistant()
#         response = {"status_code": 200, "settings": assistant.skill_manager.get_settings_meta_for_skill(
#             skill_name, assistant
#         )}
#         return response

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=e)


# @router.post("/set_enviroment_variables")
# def set_enviroment_variables(json_data: dict):
#     config = Config()

#     if not ("variables" in json_data and json_data.items()):
#         raise HTTPException(status_code=500, detail="invalid json")

#     for key, value in json_data["variables"].items():
#         config[key] = value

#     return {"status_code": 200}


@router.route("/save_credentials", methods=["GET", "POST"])
def save_credentials(json: dict):
    if "ssid" in json and "wifi_key" in json:
        ssid = json["ssid"]
        wifi_key = json["wifi_key"]
    else:
        raise HTTPException(status_code=400, detail="invalid json")

    try:
        set_wifi_credentials(ssid, wifi_key)
        return {"status": "success", "status_code": 200}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
