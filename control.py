import datetime
import sys
import threading
import time
import random
import serial
import numpy as np
from math import pi
#The COM PORT of Arduino

comPort = "COM11"

pulse_per_round = 12
delayLoop = 0.1

newAngle = 90

presentData = ""
prevData = ""

stopThread = False;
startFrame = "A5"
endFrame = "E5"

def receiveData():
    global mySerial
    data = str(mySerial.read_command(),'utf-8').split()
    if(len(data) == 22 and data[0] == startFrame and data[-1] == endFrame): # check if data len = 22, first byte = 0xA5, last byte = 0xE5
        return data[1:-1] # không lấy bye thứ len(data) - 1
    else:
        return None

def convertStringtoInt32(strData):
    return (np.int32(strData[0]) << 24) + (np.int32(strData[1]) << 16) + (np.int32(strData[2]) << 8) + (np.int32(strData[3]))

def ComputeDistance(raw):

    if(raw == None):
        return

    print(raw)
    print(raw[1:5])
    print(raw[6:10])
    print(raw[11:15])
    print(raw[16:])
    
    distance = np.array([0,0,0,0], dtype=np.int32)

    distance[0] = convertStringtoInt32(raw[1:5])
    distance[1] = convertStringtoInt32(raw[6:10])
    distance[2] = convertStringtoInt32(raw[11:15])
    distance[3] = convertStringtoInt32(raw[16:])

    print(distance)
    print("=====================================================")
    return distance

def mixedCommand(delay):
    global newAngle, mySerial, presentData, prevData, stopThread
    while not stopThread:

        ComputeDistance(receiveData())
        
        # print(ComputeDistance(presentData))
        
        #Send new speed
        newSpeed = random.choice([1,1,1])
        mySerial.write_command("n," + str(newSpeed) + "," + str(newSpeed) + ","+ str(newSpeed) + ","+ str(newSpeed) + ";")

        #Send new angle
        if(newAngle == 90):
            mySerial.write_command("q," + str(newAngle) + "," + str(newAngle) + ","+ str(newAngle) + ","+ str(newAngle) + ";")
            newAngle = -90
        else:
            mySerial.write_command("q," + str(newAngle) + "," + str(newAngle) + ","+ str(newAngle) + ","+ str(newAngle) + ";")
            newAngle = 90

        #Send new read position command
        mySerial.write_command("5,;")
        prevData = presentData
        time.sleep(delay)

class MyChannel:
    def __init__(self, port, baud_rate):
        try:
            print("Opening serial port: %s..." % port + ".")
            self.mychannel = serial.Serial(port, baud_rate, timeout=None)
            time.sleep(0.5)
            self.mychannel.reset_input_buffer()
            self.mychannel.reset_output_buffer()
        except serial.serialutil.SerialException:
            print("Serial not found at port " + port + ".")
            sys.exit(0)

    def write_command(self, cmd):
        self.mychannel.write(bytes(str(cmd), 'utf-8'))

    def read_command(self):
        bytesRead = self.mychannel.inWaiting()
        return self.mychannel.read(bytesRead)
        

# Initialize Serial Channel
mySerial = MyChannel(comPort, 115200)
print("Command List:\r\n")
print("Undone.......... :D");
print("Type your command here:")
data = []
x = threading.Thread(target=mixedCommand, args=(delayLoop,))
while(1):
    # Get user's input
    myInput = input()

    # If change speed
    if(myInput[0] == "n"): 
        mySerial.write_command("n,1,1,1,1;")

    # If change target encoder's value
    elif(myInput[0] == "0"): 
        if(len(myInput) >= 2):
            value = int(myInput[2:len(myInput)-1])*pulse_per_round
            print(value)
            print("Set target encoder value to: " + str(int(value/pulse_per_round)) + " round")
            mySerial.write_command("0,"+str(value)+";")
        else:
            print("Invalid")

    # If set speed mode
    elif(myInput[0] == "V"): 
        mySerial.write_command("V,;")
        print("Change to speed mode !")

    # If set position mode
    elif(myInput[0] == "X"): 
        mySerial.write_command("X,;")
        print("Change to position mode !")

    elif(myInput[0] == "x"): 
        mySerial.write_command("x,;")
        print("STOP !")

    # Xoay 4 bánh xe về góc 0 độ
    elif(myInput[0] == "q"): 
        mySerial.write_command("q,0,0,0,0;")

    # Xoay 4 bánh xe về góc 90 độ
    elif(myInput[0] == "w"): 
        mySerial.write_command("q,90,90,90,90;")

    # Tăng tốc 4 bánh xe lên 1km/h
    elif(myInput[0] == "m"): 
        
        try:
            stopThread = False;
            x.start() # 0.1
        except:
            print (sys.exc_info())

    elif(myInput[0] == "p"):  #Stop 
        if(stopThread == False):
            stopThread = True;
    elif(myInput[0] == "o"): #Start
        if(stopThread == True):
            stopThread = False;
            x = threading.Thread(target=mixedCommand, args=(delayLoop,)).start()




