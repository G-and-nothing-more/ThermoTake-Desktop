"""Top-level package for the ThermoApp."""

import kivy
kivy.require('2.0.0')
# https://stackoverflow.com/questions/44905416/how-to-get-started-use-matplotlib-in-kivy

from glob import glob
from random import randint
from os.path import join, dirname
from kivy.app import App
from kivy.logger import Logger
from kivy.properties import StringProperty

# Here's how to do error messages with Logger
# Logger.exception('Pictures: Unable to load <%s>' % filename)


class ThermoApp(App):
    """Top-level application class."""

    def build(self):
        """Bind controls and major elements to instance variables."""
        root = self.root
        # ...stuff with root

    def on_pause(self):
        """TODO: Figure out when this runs. It was recommended."""
        return True

    def activateDisplayBTN(self):
        """Buttonpress method for Display."""
        print("burf")

    def sendMessageBTN(self):
        """Buttonpress method for Send Message."""
        print("bort")


if __name__ == '__main__':
    ThermoApp().run()
