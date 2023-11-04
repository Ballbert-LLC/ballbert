import asyncio
import inspect
import json
import threading
import time
import websocket
from Event_Handler import event_handler
from Config import Config

config = Config()

class WebsocketException(Exception):
    pass


WS_URL = config["WS_URL"]

class Websocket_Client:
    def __init__(self, uid) -> None:
        self.url = WS_URL
        self.ws = None
        self.thread = None
        self.uid = uid
        self.routes = dict()
        self.send_queue = []

        self.connect()

    def add_route(self, func, name=None):
        name = name or func.__name__
        self.routes[name] = func

    def on_message(self, ws, message):
        with open("./log.txt", "w") as file:
            file.write(str(message))
        try:
            decoded_json_message = json.loads(message)
        except Exception as e:
            print(e)
            event_handler.trigger("Error", WebsocketException("Invalid Json"))
            return

        

        action = decoded_json_message.get("type")

        if not (action in self.routes and callable(self.routes.get(action))):
            # event_handler.trigger("Error", WebsocketException("Invalid Json"))
            return

        route = self.routes.get(action)

        message_keys = decoded_json_message.keys()

        route_arguments = list(inspect.signature(route).parameters.keys())

        arguments_to_provide = dict()

        for argument in route_arguments:
            if not argument in message_keys:
                event_handler.trigger(
                    "Error", WebsocketException(f"Missing argument {argument}")
                )
                return
            else:
                arguments_to_provide[argument] = decoded_json_message[argument]
        try:
            if inspect.iscoroutinefunction(route):
                asyncio.run(route(**arguments_to_provide))
            elif callable(route):
                route(**arguments_to_provide)
        except Exception as e:
            raise e
            event_handler.trigger("Error", WebsocketException(e))

    def on_error(self, ws, error):
        print(error)
        print("websocket had error reconnecting in 3 seconds")
        try:
            self.ws.close()
        finally:
            self.ws = None
        time.sleep(3)
        self.connect()
        return 

    def on_close(self, ws, close_status_code, close_msg):
        event_handler.trigger("WS Closed", close_status_code, close_msg)

    def on_open(self, ws):
        print("websocket init")
        queue = list(self.send_queue)
        for message in queue:
            self.send_request(message)
            self.send_queue.remove(message)
        event_handler.trigger("WS Opened")

    def connect(self):
        print("connecting")
        self.ws = websocket.WebSocketApp(
            self.url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open,
            header={"UID": self.uid, "User-Agent": "Device"},
        )
        self.thread = threading.Thread(target=self.ws.run_forever)
        self.thread.daemon = True

        self.thread.start()

    def send_request(self, request):
        try:
            if self.ws:
                self.ws.send(request)
            else:
                print("WebSocket is not connected")
        except websocket._exceptions.WebSocketConnectionClosedException as e:
            print("websocket cloased ")
            self.send_queue.append(request)
            self.connect()

    def send_message(self, type, data=None, **kwargs):
        json_data = {"type": type}
        if data:
            json_data = {**json_data, **data}
        if kwargs:
            json_data = {**json_data, **kwargs}

        string_formated_message = json.dumps(json_data)
        self.send_request(string_formated_message)






