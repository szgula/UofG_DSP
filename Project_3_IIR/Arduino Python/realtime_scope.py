#!/usr/bin/python3

from pyfirmata2 import Arduino
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Realtime oscilloscope at a sampling rate of 50Hz
# It displays analog channel 0.
# You can plot multiple channels just by instantiating
# more RealtimePlotWindow instances and registering
# callbacks from the other channels.


PORT = Arduino.AUTODETECT
# PORT = '/dev/ttyUSB0'

# Creates a scrolling data display
class RealtimePlotWindow:

    def __init__(self):
        # create a plot window
        self.fig, self.ax = plt.subplots()
        # that's our plotbuffer
        self.plotbuffer = np.zeros(500)
        self.plotbuffer_x = np.zeros(500)
        # create an empty line
        self.line, = self.ax.plot(self.plotbuffer)
        # axis
        self.ax.set_ylim(0, 1)
        # That's our ringbuffer which accumulates the samples
        # It's emptied every time when the plot window below
        # does a repaint
        self.ringbuffer = []
        self.ringbuffer_x = []
        # add any initialisation code here (filters etc)
        # start the animation
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=100)

    # updates the plot
    def update(self, data):
        # add new data to the buffer
        self.plotbuffer = np.append(self.plotbuffer, self.ringbuffer)
        self.plotbuffer_x = np.append(self.plotbuffer_x, self.ringbuffer_x)
        # only keep the 500 newest ones and discard the old ones
        self.plotbuffer = self.plotbuffer[-500:]
        self.plotbuffer_x = self.ringbuffer_x[-500:]
        self.ringbuffer = []
        self.ringbuffer_x = []
        # set the new 500 points of channel 9
        self.line.set_ydata(self.plotbuffer)
        return self.line,

    # appends data to the ringbuffer
    def addData(self, v, y):
        self.ringbuffer.append(v)


# Create an instance of an animated scrolling window
# To plot more channels just create more instances and add callback handlers below
realtimePlotWindow = RealtimePlotWindow()
realtimePlotWindow_2 = RealtimePlotWindow()
# sampling rate: 100Hz
samplingRate = 10

# called for every new sample which has arrived from the Arduino
def callBack(data):
    # send the sample to the plotwindow
    # add any filtering here:
    # data = self.myfilter.dofilter(data)
    realtimePlotWindow.addData(data, 0)
    global board
    print(board.analog[0].read(), board.analog[1].read(), board.analog[2].read())

# Get the Arduino board.
board = Arduino(PORT)

# Set the sampling rate in the Arduino
board.samplingOn(1000 / samplingRate)

# Register the callback which adds the data to the animated plot
board.analog[0].register_callback(callBack)
# Register the second callback which adds the data to the animated plot - (Allan)
#board.analog[1].register_callback(callBack)


# Enable the callback
board.analog[0].enable_reporting()
# Enable the second callback (allan)
board.analog[1].enable_reporting()
board.analog[2].enable_reporting()

# show the plot and start the animation
plt.show()

# needs to be called to close the serial port
board.exit()

print("finished")