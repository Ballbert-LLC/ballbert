import websocket
from Config import Config

config = Config()

uid = config["UID"]

websocket_url = "wss://websocket.ballbert.com:8765"


ws = websocket.create_connection(websocket_url, header={"UID": uid, "User-Agent": "Device-Setup"})
