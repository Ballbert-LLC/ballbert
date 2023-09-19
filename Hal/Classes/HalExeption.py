class HalExeption(Exception):
    def __init__(self, error_code=500, *args: object) -> None:
        super().__init__(*args)
        self.error_code = error_code


class NoTTSException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

