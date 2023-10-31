import asyncio
import platform
import threading
import os
import multiprocessing
import threading
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.background import BackgroundTask
from Config import Config
from Event_Handler import event_handler
import speech_recognition

config = Config()


def run_assistant():
    if os.path.exists("./UPDATE"):
        return
    time.sleep(1)

    from Hal import initialize_assistant

    assistant = initialize_assistant()
    
    print("hio")
    print(assistant.action_dict)
        
    event_handler.trigger("Ready")
    
    
    while True:
        time.sleep(1)
        print(assistant.websocket_client.thread.is_alive())
        event_handler.trigger("Ready")
    
    time.sleep(2)

def start_setup():
    import setup

    try:
        setup.setup()
    except Exception as e:
        event_handler.trigger("Error", e)


def ready_stage():
    if not config["CURRENT_STAGE"]:
        if platform.system() == "Linux":
            config["CURRENT_STAGE"] = 0
        else:
            config["CURRENT_STAGE"] = 1


def start_event_handlers():
    def error_event(error: Exception):
        raise error

    event_handler.on("Error", error_event)


def main():
    try:
        ready_stage()
        start_event_handlers()

        while config["CURRENT_STAGE"] == 0:
            if platform.system() == "Linux":
                from OTAWifi import run_api

                run_api()

        while config["CURRENT_STAGE"] == 1:
            start_setup()

            break

        while config["CURRENT_STAGE"] == 2:
            run_assistant()
            break
    except Exception as e:

        event_handler.trigger("Error", e)


def setup_and_teardown():
    try:
        main()
    except KeyboardInterrupt as e:
        print("KEYBOARD")


if __name__ == "__main__":    
    setup_and_teardown()
