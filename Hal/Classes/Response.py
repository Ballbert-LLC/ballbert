import datetime


class Response:
    def __init__(
        self,
        succeeded=False,
        original_message: str = "",
        action: str = "",
        data="",
    ):
        self.time_created = datetime.datetime.now()
        self.original_message = original_message
        self.data = data
        self.suceeded = succeeded
        self.action = action
