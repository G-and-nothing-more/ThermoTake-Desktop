"""Top-level package for the ThermoApp."""

import smtplib
from email.message import EmailMessage
import kivy
import re
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.properties import StringProperty
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from glob import glob
from random import randint
from os.path import join, dirname
from kivy.app import App
from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock

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


def updateYData():
    global y
    y = y[1:] + [y[0]] # Change this line


def animationTick(i):
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

        #TODO: Error popup on invalid number
    def sendMessageBTN(self):
        """Buttonpress method for Send Message."""
        print("bort")
        area, code1, code2 = self.getTLFN()
        
        #self.getTLFN is a tuple of string??? 
        #if so then will convert that to string later #TODO for Rupanti

        print(area)
        print(code1)
        print(code2)

        #### how to check the temperature??????? 
        # if temp>300F then
        self.msgAlert("Alert","Tempterature is above 300F", "--------@txt.att.net")

 

    def getTLFN(self):
        """Return a tuple of the 3 parts of a phone number."""
        m = re.search(r'\(?(\d{3})[) \- ]?(\d{3})[- ]?(\d{4})',
                      self.root.phoneNum)
        return (m.group(1), m.group(2), m.group(3))


   # message alert function
    def msgAlert(subject, body,to):
        msg = EmailMessage()
        msg.set_content(body)
        msg['subject'] = subject
        msg['to'] = to
        user = "-----------@gmail.com"
        msg['from'] = user
        password = "--------"

        ##setting server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
        server.quit()
        





if __name__ == '__main__':
    ThermoApp().run()
