import asyncio
import multiprocessing
import platform
import threading
import time
from Hal.Classes import Response
from Hal.Decorators import reg
from Hal.Skill import Skill
from Event_Handler import event_handler


def run_app(queue: multiprocessing.Queue,):
    from .KivyApp import App

    application = App()
    
    application.run(queue)
       


def run_main():
    q = multiprocessing.Queue()

    app = multiprocessing.Process(target=run_app, args=(q,))
    app.start()
    return q, app


class GUI(Skill):
    def __init__(self):

        self.q, self.app = run_main()
        self.setup_routes()
        
        event_handler.on("Audio_End", self.audio_end)

        t = threading.Thread(target=self.check_if_gui_is_running)
        if platform.system() == "Linux": 
            t.start()
        
    
    
    def check_if_gui_is_running(self):
        while True:
            if not self.app.is_alive():
                if self.q.close :
                    self.q = None
                    self.app = None
                    self.q, self.app = run_main()
            time.sleep(0.5)

    def audio_end(self):
        self.change_indecator_bar_color("grey")
        time.sleep(3)
        self.change_emotion("neutral")
    
    def setup_routes(self):
        
        def sentament(sentament : str):
            self.q.put(f"E{sentament}")
        
        event_handler.on("sentament", sentament)
        
        def indecator_bar_color(color : str):
            self.q.put(f"C{color}")
        
        event_handler.on("indecator_bar_color", indecator_bar_color)
        
        def change_color_blue(_):
            self.change_indecator_bar_color("blue")
        
        event_handler.on("Keyword", change_color_blue)
        
        def ready():
            self.q.put("Cgrey")
        
        event_handler.on("Ready", ready)
        

    @reg(name="change_indecator_bar_color")
    def change_indecator_bar_color(self, color="grey"):
        """
        Changes the color of the indecator bar

        :param string color: (Optional) The color you want to change the indector bar to. Options: blue, green, red, yellow, grey. Default: grey
        """
        
        self.q.put(f"C{color}")
        
        return Response(True)


    @reg(name="change_emotion")
    def change_emotion(self, emotion="neutral"):
        """
        Changes the emotion of the assistant

        :param string emotion: (Optional) The emotion you want to change the assistant to. One of 
            admiration
            amusement
            anger
            annoyance
            approval
            caring
            confusion
            curiosity
            desire
            disappointment
            disapproval
            disgust
            embarrassment
            excitement
            fear
            gratitude
            grief
            joy
            love
            nervousness
            optimism
            pride
            realization
            relief
            remorse
            sadness
            surprise
            neutral 
        """
        
        self.q.put(f"E{emotion}")
        
        return Response(True)
