"""Top-level package for the ThermoApp."""
import io
import re
import kivy
import time
import serial
import smtplib
from sys import platform
from pathlib import Path
import matplotlib.pyplot as plt
from email.message import EmailMessage
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

###
# Important: Make sure the bluetooth HC-05 device is connected and paired (pswd: 1234) and the port variable matches the
#       correct COM port on your machine.
###

debugMode = Path("debugmode.txt").is_file()
print(debugMode)

port = 'COM5'
serialPort, data = 0,0
if not debugMode:
    serialPort = serial.Serial(port=port, baudrate=9600, timeout=1, stopbits=1)
    data = io.TextIOWrapper(io.BufferedRWPair(serialPort, serialPort, 1), newline="\r\n", line_buffering=False)

kivy.require('2.0.0')

def null():
    return

listLength = 300
x = [w for w in range(-1 * listLength, 0, 1)]
y = [w for w in range(listLength)]
status = "Nominal"

lines = open("Carrierlookup.txt").readlines()
carrierDict = dict()
for line in lines:
    tup = line.split(',')
    carrierDict[tup[1].strip()] = tup[0].strip()
debugDict = {"hrw": "Horseradish Wireless",
             "atmnt": "ATMNT",
             'pbc': "Picklebox Cellular"}

print(carrierDict)

fig = plt.figure()
ax = fig.add_subplot(111)
plt.ylim(-12, 65)
plt.xlim(-1 * listLength, 0)
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
        serialPort.flushInput()
        serialPort.flushOutput()

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
        # data.readline(1024)


class ThermoApp(App):
    """Top-level application class."""

    def updateYData(self):
        """Update the graphed data."""
        newData = newReadLine()
        if debugMode:
            newData = 20
        if (newData):
            if (newData == -127):
                self.addNewValue(null())
                print('error')
            elif (newData >= -10 and newData <= 100):
                self.addNewValue(newData)

    def addNewValue(self, _y):
        """Add a new value to the front of the graph."""
        global y
        y = y[1:] + [_y]

    def animationTick(self, i):
        """Process all changes needed to update the graph."""
        global y
        print("tick")
        self.updateYData()
        self.repaintGraph()
        self.statusTicker.text = "Status: " + status

        self.textCooldown = max(self.textCooldown-1, 0)
        if y[-1]:
            if y[-1] >= self.upper and self.textCooldown < 1:
                self.msgAlert(
                    "Alert", "Tempterature is above upper limit.",
                    "--------@txt.att.net")
                self.textCooldown = 60
            if y[-1] <= self.lower and self.textCooldown < 1:
                self.msgAlert(
                    "Alert", "Tempterature is below lower limit.",
                    "--------@txt.att.net")
                self.textCooldown = 60
        return line,

    def repaintGraph(self):
        """Update graph to match new data."""
        line.set_ydata(y)
        fig.canvas.draw()
        fig.canvas.flush_events()

    def setCarrier(self, newKey):
        """Change the internal carrier tracker variable."""
        self.carrierKey = newKey
        setattr(self.carrierDropButton, 'text', carrierDict[newKey])

    def build(self):
        """Bind controls and major elements to instance variables."""
        global y
        root = self.root
        self.statusTicker = root.ids.statusTicker
        box = root.ids.graphBox
        box.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        Clock.schedule_interval(self.animationTick, 0.5)

        self.carrierDropButton = root.ids.carrierDropButton
        dropdown = root.ids.carrierDrop
        self.carrierDropButton.bind(on_press=dropdown.open)
        dropdown.bind(on_select=lambda instance, x:
                      self.setCarrier(x))
        self.carrierKey = list(carrierDict.keys())[0]

        y = [null() for w in range(listLength)]

        self.lower = -5
        self.upper = 50
        self.textCooldown = 60
        root.ids.upperText.bind(text=self.tryUpdateUpper)
        root.ids.lowerText.bind(text=self.tryUpdateLower)
        root.ids.upperText.text = str(self.upper)
        root.ids.lowerText.text = str(self.lower)
        self.animationTick(0.5)

    def on_pause(self):
        """TODO: Figure out when this runs. It was recommended."""
        return True

    def tryUpdateUpper(self, e, s):
        """Attempt to change upper bound to int value of string."""
        try:
            f = float(s)
            self.upper = f
        except:
            pass

    def tryUpdateLower(self, e, s):
        """Attempt to change lower bound to int value of string."""
        try:
            f = float(s)
            self.lower = f
        except:
            pass

    def activateDisplayBTN(self):
        """Buttonpress method for Display."""
        print("burf")
        serialPort.write(1)

    def sendMessageBTN(self):
        """Buttonpress method for Send Message."""
        # TODO: Error popup on invalid number
        area, code1, code2 = self.getTLFN()  # Each of these is a string

        print(area)
        print(code1)
        print(code2)

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
        for key in carrierDict.keys():
            button = Button()
            button.text = carrierDict[key]
            button.height = 44
            button.size_hint_y = None
            button.cid = key
            button.bind(on_release=lambda btn: self.select(btn.cid))
            self.add_widget(button)

    pass


class NumericInput(TextInput):
    """An input that only allows numbers."""

    forbiddenInputs = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        """Override allowed text."""
        pat = self.forbiddenInputs
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super(NumericInput, self).insert_text(s, from_undo=from_undo)


if __name__ == '__main__':
    ThermoApp().run()

# Here's how to do error messages with Logger
# Logger.exception('Pictures: Unable to load <%s>' % filename)
