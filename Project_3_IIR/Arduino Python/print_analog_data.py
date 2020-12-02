#!/usr/bin/python3

from pyfirmata2 import Arduino
import time

PORT = Arduino.AUTODETECT
# PORT = '/dev/ttyACM0'

# prints data on the screen at the sampling rate of 50Hz
# can easily be changed to saving data to a file

# It uses a callback operation so that timing is precise and
# the main program can just go to sleep.


class AnalogPrinter:

    def __init__(self):
        # sampling rate: 10Hz
        self.samplingRate = 10
        self.timestamp = 0
        self.board = Arduino(PORT)
        self.file = open('output.txt', 'w')

    def __enter__(self):
        self.board.analog[0].register_callback(self.myPrintCallback_x)
        #self.board.analog[1].register_callback(self.myPrintCallback_y)
        self.board.samplingOn(10)
        self.board.analog[0].enable_reporting()
        #self.board.analog[1].enable_reporting()

    def myPrintCallback_x(self, data):
        print("x = %f,%f" % (self.timestamp, data))
        self.timestamp += (1 / self.samplingRate)
        #y_data = self.board.analog[1].read()
        self.file.write(f'{data} \n')

    def myPrintCallback_y(self, data):
        print("y = %f,%f" % (self.timestamp, data))
        self.timestamp += (1 / self.samplingRate)
        self.file.write(f'y: {data} \n')

    def __exit__(self, type, val, tr):
        self.board.samplingOff()
        self.board.exit()
        self.file.close()

print("Let's print data from Arduino's analogue pins for 10secs.")

# Let's create an instance
with AnalogPrinter() as analogPrinter:
    # let's acquire data for n secs. We could do something else but we just sleep!
    time_sleep = 10
    time.sleep(time_sleep)
    #for _ in range(time_sleep):
    #    time.sleep(1)
    #    print(f'done {_} out of {time_sleep}')

print("finished")