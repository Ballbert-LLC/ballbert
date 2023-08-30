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


def run_web():
    import uvicorn
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles

    app = FastAPI()

    def start_web():
        try:
            # Mount the router from the api module
            from Flask.main import router

            app.include_router(router)
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=5000,
            )
        except Exception as e:
            event_handler.trigger("Error", e)

    # Start the web server
    t = threading.Thread(target=start_web)
    t.daemon = True
    t.start()
    return t


def run_assistant():
    if os.path.exists("./UPDATE"):
        return
    time.sleep(1)

    from Hal import initialize_assistant

    assistant_instance = initialize_assistant()

    time.sleep(2)

    assistant_instance.voice_to_voice_chat()


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
            from OTAWifi import run_api

            run_api()

        while config["CURRENT_STAGE"] == 1:
            web_thread = run_web()

            start_setup()

            break

        while config["CURRENT_STAGE"] == 2:
            web_thread = run_web()

            run_assistant()
            break
    except Exception as e:
        from Hal import initialize_assistant

        assistant = initialize_assistant()

        event_handler.trigger("Error", e)


def setup_and_teardown():
    import sys

    if platform.system() == "Linux":
        sys.stdout = open("/etc/ballbert/logs.txt", "w")
    main()
    sys.stdout.close()


if __name__ == "__main__":
    setup_and_teardown()
