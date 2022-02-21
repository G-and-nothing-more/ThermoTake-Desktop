"""Top-level package for the ThermoApp."""

import smtplib
from email.message import EmailMessage
import kivy
import re
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.properties import StringProperty
import matplotlib.pyplot as plt
from kivy.app import App
from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

kivy.require('2.0.0')

listLength = 20
x = [w for w in range(-4, -4+listLength)]
y = [40]*listLength
debugDict = {"Horseradish Wireless": "hrw",
             "ATMNT": "atmnt",
             "Picklebox Cellular": 'pbc'}

fig = plt.figure()
ax = fig.add_subplot(111)
plt.ylabel("Temperature")
plt.xlabel("Seconds")
plt.title("Thermometer Reading")
line, = ax.plot(x, y, 'r-')


def updateYData():
    """Update the graphed data."""
    global y
    y = y[1:] + [y[0]]
    y[-1] = y[-1]  # Change this line


def addNewValue(_y):
    """Add a new value to the front of the graph."""
    global y
    y = y[1:] + [_y]


def animationTick(i):
    """Process all changes needed to update the graph."""
    global y
    updateYData()
    repaintGraph()
    return line,


def repaintGraph():
    """Update graph to match new data."""
    line.set_ydata(y)
    fig.canvas.draw()
    fig.canvas.flush_events()

# Here's how to do error messages with Logger
# Logger.exception('Pictures: Unable to load <%s>' % filename)


class CarrierDropDown(DropDown):
    """Used to select which phone carrier to use."""

    def __init__(self, **kwargs):
        super(CarrierDropDown, self).__init__()
        for key in debugDict.keys():
            button = Button()
            button.text = key
            button.bind(on_release=self.select(debugDict[key]))
            self.add_widget(button)

    pass


class ThermoApp(App):
    """Top-level application class."""

    def build(self):
        """Bind controls and major elements to instance variables."""
        root = self.root
        box = root.ids.graphBox
        box.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        Clock.schedule_interval(animationTick, 0.5)
        animationTick(0.5)
        carrierDropButton = root.ids.carrierDropButton
        dropdown = root.ids.carrierDrop
        carrierDropButton.bind(on_press=dropdown.open)
        dropdown.bind(on_select=lambda instance, x:
                      setattr(carrierDropButton, 'text', x))
        # root.ids.sidebar.ids.phoneNumBox.text = self.teleNum
        # ...stuff with root

    def on_pause(self):
        """TODO: Figure out when this runs. It was recommended."""
        return True

    def activateDisplayBTN(self):
        """Buttonpress method for Display."""
        print("burf")

        # TODO: Error popup on invalid number
    def sendMessageBTN(self):
        """Buttonpress method for Send Message."""
        area, code1, code2 = self.getTLFN()  # Each of these is a string

        print(area)
        print(code1)
        print(code2)

        # if temp>300F then
        if y[-1] >= 300:
            self.msgAlert("Alert", "Tempterature is above 300F", "--------@txt.att.net")

    def getTLFN(self):
        """Return a tuple of the 3 parts of a phone number."""
        m = re.search(r'\(?(\d{3})[) \- ]?(\d{3})[- ]?(\d{4})',
                      self.root.phoneNum)
        return (m.group(1), m.group(2), m.group(3))

    def msgAlert(subject, body, to):
        """Message alert function."""
        msg = EmailMessage()
        msg.set_content(body)
        msg['subject'] = subject
        msg['to'] = to
        user = "-----------@gmail.com"
        msg['from'] = user
        password = "--------"

        # setting server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
        server.quit()


if __name__ == '__main__':
    ThermoApp().run()
