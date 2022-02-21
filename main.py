"""Top-level package for the ThermoApp."""
import io
import serial
import time
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

###
#Important: Make sure the bluetooth HC-05 device is connected and paired (pswd: 1234) and the port variable matches the
#       correct COM port on your machine.
###
port = 'COM6'

serialPort = serial.Serial(port=port, baudrate=9600, timeout=1, stopbits=1)
data = io.TextIOWrapper(io.BufferedRWPair(serialPort, serialPort, 1), newline="\r\n", line_buffering=True)


kivy.require('2.0.0')
# https://stackoverflow.com/questions/44905416/how-to-get-started-use-matplotlib-in-kivy
x = [w for w in range(-4, 1)]
y = [5, 12, 6, 9, 15]

fig = plt.figure()
ax = fig.add_subplot(111)
plt.ylabel("Temperature")
plt.xlabel("Seconds")
plt.title("Thermometer Reading")
line, = ax.plot(x, y, 'r-')

##############################################
#Name: newReadLine
#Description: This function is a more robust version of serial.readline() function. This function reads in the data string,
#   then splits it into its data and checksum parts respectively. Then it compares the checksum and prints if it passes.
#Inputs: None
#Outputs: Print
##############################################
def newReadLine ():

    #If there is data to be read.
    if data:

        #Read the data and store it in a variable
        rcv = data.readline()

        #Split the data from message and checksum (original rcv should be "double:int")
        transmission = rcv.split(':')

        #try to parse the data into numerals from string
        try:
            msg = float(transmission[0])
            checkSum = int(transmission[1])

            #If the mod 64 checkSum matches, print the msg
            if (msg * 100) % 64 == checkSum:
                print(msg)

        #If not dont yell at me
        except:
            data.flush()
        #Clear the data buffer... we dont want to be using old sensor data
        data.flush()


def updateYData():
    """Update the graphed data."""
    global y
    y = y[1:] + [y[0]]
    y[-1] = y[-1]  # Change this line


def animationTick(i):
    """Process all changes needed to update the graph."""
    global y
    updateYData()
    line.set_ydata(y)
    fig.canvas.draw()
    fig.canvas.flush_events()
    return line,

# Here's how to do error messages with Logger
# Logger.exception('Pictures: Unable to load <%s>' % filename)

class ThermoApp(App):
    """Top-level application class."""

    def build(self):
        """Bind controls and major elements to instance variables."""
        root = self.root
        box = root.ids.graphBox
        box.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        Clock.schedule_interval(animationTick, 0.5)
        animationTick(0.5)
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
