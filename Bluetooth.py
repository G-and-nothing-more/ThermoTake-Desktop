import io
import serial
import time

###
#Important: Make sure the bluetooth HC-05 device is connected and paired (pswd: 1234) and the port variable matches the
#       correct COM port on your machine.
###
port = 'COM6'

serialPort = serial.Serial(port=port, baudrate=9600, timeout=1, stopbits=1)
data = io.TextIOWrapper(io.BufferedRWPair(serialPort, serialPort, 1), newline="\r\n", line_buffering=True)

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


while 1:

    #Run the function
    newReadLine()

    #Wait .5 sec
    time.sleep(.5)
