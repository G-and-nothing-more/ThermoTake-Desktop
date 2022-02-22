"""Top-level package for the ThermoApp."""
import io
import re
import kivy
import time
import serial
import smtplib
import matplotlib.pyplot as plt
from sys import platform
from email.message import EmailMessage
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.properties import StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

###
# Important: Make sure the bluetooth HC-05 device is connected and paired (pswd: 1234) and the port variable matches the
#       correct COM port on your machine.
###

port = 'COM6'
serialPort, data = 0,0
if platform not in "linux, linux2":
    serialPort = serial.Serial(port=port, baudrate=9600, timeout=1, stopbits=1)
    data = io.TextIOWrapper(io.BufferedRWPair(serialPort, serialPort, 1), newline="\r\n", line_buffering=True)

kivy.require('2.0.0')

def null():
    return

listLength = 300
x = [w for w in range(listLength, 0, -1)]
y = [null()]*listLength
status = "Nominal"
debugDict = {"hrw": "Horseradish Wireless",
             "atmnt": "ATMNT",
             'pbc': "Picklebox Cellular"}

fig = plt.figure()
ax = fig.add_subplot(111)
plt.ylim(-5,70)
plt.ylabel("Temperature")
plt.xlabel("Seconds")
plt.title("Thermometer Reading")
line, = ax.plot(x, y, 'r-')

##############################################
# Name: newReadLine
# Description: This function is a more robust version of serial.readline() function. This function
#   then splits it into its data and checksum parts respectively. Then it compares the checksum and prints if it passes.
# Inputs: None
# Outputs: Print
##############################################


def newReadLine():
    """Read in the data string.
    Then split it into its data and checksum parts respectively.
    Then compare the checksum and prints if it passes."""

    if data:  # If there is data to be read.
        # Read the data and store it in a variable
        rcv = data.readline()

        # Split the data from message and checksum (original rcv should be "double:int")
        transmission = rcv.split(':')

        # try to parse the data into numerals from string

        try:
            msg = float(transmission[0])
            checkSum = int(transmission[1])

            # If the mod 64 checkSum matches, print the msg
            if (msg * 100) % 64 == checkSum:
                data.flush()
                print(msg)
                return msg
            elif (msg <= -125):
                #print('error')
                data.flush()
                return -127
            else:
                data.flush()
                print('WRONG')
        # If not dont yell at me
        except:
            data.flush()
        # Clear the data buffer... we dont want to be using old sensor data
        data.flush()


class ThermoApp(App):
    """Top-level application class."""

    def updateYData(self):
        """Update the graphed data."""
        newData = newReadLine()

        if (newData):
            if (newData == -127):
                print('error')
            else:
                self.addNewValue(newData)

    def addNewValue(self, _y):
        """Add a new value to the front of the graph."""
        global y
        y = [_y] + y[:-1]

    def animationTick(self, i):
        """Process all changes needed to update the graph."""
        global y
        print("tick")
        self.updateYData()
        self.repaintGraph()
        self.statusTicker.text = "Status: " + status

        if y[-1]:
            if y[-1] >= 300:
                self.msgAlert(
                    "Alert", "Tempterature is above 300F", "--------@txt.att.net")
        return line,

    def repaintGraph(self):
        """Update graph to match new data."""
        line.set_ydata(y)
        fig.canvas.draw()
        fig.canvas.flush_events()

# Here's how to do error messages with Logger
# Logger.exception('Pictures: Unable to load <%s>' % filename)

    def build(self):
        """Bind controls and major elements to instance variables."""
        root = self.root
        self.statusTicker = root.ids.statusTicker
        box = root.ids.graphBox
        box.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        Clock.schedule_interval(self.animationTick, 0.5)
        self.animationTick(0.5)
        carrierDropButton = root.ids.carrierDropButton
        dropdown = root.ids.carrierDrop
        carrierDropButton.bind(on_press=dropdown.open)
        dropdown.bind(on_select=lambda instance, x:
                      setattr(carrierDropButton, 'text', debugDict[x]))
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


class CarrierDropDown(DropDown):
    """Used to select which phone carrier to use."""

    def __init__(self, **kwargs):
        """Create a dropdown button for each carrier."""
        super(CarrierDropDown, self).__init__()
        for key in debugDict.keys():
            button = Button()
            button.text = debugDict[key]
            button.height = 44
            button.size_hint_y = None
            button.cid = key
            button.bind(on_release=lambda btn: self.select(btn.cid))
            self.add_widget(button)

    pass


if __name__ == '__main__':
    ThermoApp().run()
