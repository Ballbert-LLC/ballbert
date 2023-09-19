import multiprocessing
import os
import platform
import time
from kivymd.tools.hotreload.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Line
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivymd.theming import ThemeManager
from threading import Thread
import socket
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Color
from kivy.uix.label import Label


class App(MDApp):
    def __init__(self, **kwargs):
        self.colors = {
            "green": "./Skills/GUI/CO/green.jpeg",
            "blue": "./Skills/GUI/CO/blue.jpeg",
            "red": "./Skills/GUI/CO/red.jpeg",
            "yellow": "./Skills/GUI/CO/yellow.jpeg",
            "grey": "./Skills/GUI/CO/grey.jpeg",
        }

        self.images = {
            "admiration": "./Skills/GUI/BA/Admiration.png",
            "amusement": "./Skills/GUI/BA/Happy.png",
            "anger": "./Skills/GUI/BA/Anger.png",
            "annoyance": "./Skills/GUI/BA/annoyance.png",
            "approval": "./Skills/GUI/BA/Approval.png",
            "caring": "./Skills/GUI/BA/caring.png",
            "confusion": "./Skills/GUI/BA/Confusion.png",
            "curiosity": "./Skills/GUI/BA/Confusion.png",
            "desire": "./Skills/GUI/BA/Admiration.png",
            "disappointment": "./Skills/GUI/BA/Dissapointment.png",
            "disapproval": "./Skills/GUI/BA/Dissapointment.png",
            "disgust": "./Skills/GUI/BA/Scared.png",
            "embarrassment": "./Skills/GUI/BA/Embaresed.png",
            "excitement": "./Skills/GUI/BA/Exitment.png",
            "fear": "./Skills/GUI/BA/Scared.png",
            "gratitude": "./Skills/GUI/BA/7o.png",
            "grief": "./Skills/GUI/BA/Sad.png",
            "joy": "./Skills/GUI/BA/Happy.png",
            "love": "./Skills/GUI/BA/caring.png",
            "nervousness": "./Skills/GUI/BA/Scared.png",
            "optimism": "./Skills/GUI/BA/Happy.png",
            "pride": "./Skills/GUI/BA/7o.png",
            "realization": "./Skills/GUI/BA/Exitment.png",
            "relief": "./Skills/GUI/BA/Normal.png",
            "remorse": "./Skills/GUI/BA/Dissapointment.png",
            "sadness": "./Skills/GUI/BA/Sad.png",
            "surprise": "./Skills/GUI/BA/Exitment.png/",
            "neutral": "./Skills/GUI/BA/Normal.png",
        }

        if platform.system() == "Linux":
            Window.borderless = True
        # else:
        #     Window.left = 3000
        #     Window.top = -100

        Clock.schedule_interval(self.run_clock, 0.1)

        super().__init__(**kwargs)

    def run_clock(self, *args):
        if os.path.exists("./UPDATE"):
            try:
                self.stop()
            except:
                open("./NOUPDATE", "w").close()
        if self.queue.empty():
            return
        else:
            emotion = self.queue.get()
            if emotion[0] == "E":
                emotion = emotion[1:]
                page = self.images[emotion]
                self.eyes.source = page
            elif emotion[0] == "C":
                color = emotion[1:]
                page = self.colors[color]
                self.line.source = page

    def run(self, queue: multiprocessing.Queue):
        self.queue = queue
        super().run()

    def build_app(self, first=False):
        self.theme_cls = ThemeManager()
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.index = 0

        layout = ScreenManager()
        screen = Screen()
        self.line = Image(
            source=self.colors["yellow"],
            size_hint=(0.9, 1),
            pos_hint={"center-x": 0, "center_y": 0.98},
            size_hint_y=0.7,
            size_hint_x=1.1,
        )

        self.eyes = Image(
            source=self.images["neutral"],
            size_hint=(0.9, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )

        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)

        self.label = Label(
            text=IPAddr, pos_hint={"x": 0.85, "bottom": 1}, size_hint=[0.1, 0.1]
        )

        screen.add_widget(self.eyes)
        screen.add_widget(self.line)
        screen.add_widget(self.label)

        layout.add_widget(screen)

        return layout
