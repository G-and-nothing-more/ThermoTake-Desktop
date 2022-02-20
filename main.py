"""Top-level package for the ThermoApp."""

import smtplib
from email.message import EmailMessage
import kivy
import re
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.properties import StringProperty
import matplotlib.pyplot as plt
from glob import glob
from random import randint
from os.path import join, dirname
from kivy.app import App
from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.widget import Widget

kivy.require('2.0.0')
# https://stackoverflow.com/questions/44905416/how-to-get-started-use-matplotlib-in-kivy
plt.plot([1, 23, 2, 4])
plt.ylabel('some numbers')

# Here's how to do error messages with Logger
# Logger.exception('Pictures: Unable to load <%s>' % filename)


class ThermoApp(App):
    """Top-level application class."""

    def build(self):
        """Bind controls and major elements to instance variables."""
        root = self.root
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


   ##message alert function
    def msgAlert(subject, body,to):
        msg=EmailMessage()
        msg.set_content(body)
        msg['subject']=subject
        msg['to']=to
        user="-----------@gmail.com"
        msg['from']=user
        password="--------"

        ##setting server
        server=smtplib.SMTP("smtp.gmail.com",587)
        server.starttls()
        server.login(user,password)
        server.send_message(msg)
        server.quit()
        





if __name__ == '__main__':
    ThermoApp().run()
