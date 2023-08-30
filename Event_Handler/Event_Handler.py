class Event_Handler:
    def __init__(self) -> None:
        self.callbacks = {}

    def on(self, event_name: str, callback):
        """Calls the callback when an event happens.

        Arguments:
        event_name -- the name of the event you want to listen for
        callback -- the function you want to be called when the event happens.
        """
        if not event_name in self.callbacks:
            self.callbacks[event_name] = []

        self.callbacks[event_name].append(callback)

    def trigger(self, event_name, *args, **kwargs):
        if not event_name in self.callbacks:
            return

        for callback in self.callbacks[event_name]:
            callback(*args, **kwargs)


event_handler = Event_Handler()
