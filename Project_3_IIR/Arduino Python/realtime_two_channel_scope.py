#!/usr/bin/python3
"""
Plots channels zero and one in two different windows. Requires pyqtgraph.
"""

import sys
from collections import deque
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from pyfirmata2 import Arduino
from IIR_filter import IIRFilter, IIR2Filter, return_filter

class QtPanningPlot:

    def __init__(self, title):
        x_range = 500
        self.win = pg.GraphicsLayoutWidget()
        self.win.setWindowTitle(title)
        self.plt = self.win.addPlot()
        self.plt.setYRange(-1, 1)
        self.plt.setXRange(0, x_range)
        self.curve_x = self.plt.plot()
        self.curve_y = self.plt.plot()
        self.curve_z = self.plt.plot()
        self.curve_s = self.plt.plot()
        self.data_x = deque([0]*x_range, maxlen=x_range)
        self.data_y = deque([0]*x_range, maxlen=x_range)
        self.data_z = deque([0]*x_range, maxlen=x_range)
        self.data_s = deque([0] * x_range, maxlen=x_range)
        # any additional initalisation code goes here (filters etc)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)
        self.layout = QtGui.QGridLayout()
        self.win.setLayout(self.layout)
        self.win.show()

    def update(self):
        self.curve_x.setData(np.hstack(self.data_x))
        self.curve_y.setData(np.hstack(self.data_y))
        self.curve_z.setData(np.hstack(self.data_z))
        self.curve_s.setData(np.hstack(self.data_s))

    def addData(self, x,y,z):
        self.data_x.append(x)
        self.data_y.append(y)
        self.data_z.append(z)
        self.data_s.append((z**2 + y**2 + x**2)**0.5)


class ArduinoScope:
    def __init__(self, filters):
        self.PORT = Arduino.AUTODETECT
        self.app = QtGui.QApplication(sys.argv)
        self.qtPanningPlot1 = QtPanningPlot("Arduino raw data")
        self.qtPanningPlot2 = QtPanningPlot("Filered data")
        self.samplingRate = 100
        self.board = Arduino(self.PORT)
        self.board.samplingOn(1000 / self.samplingRate)
        self.filters = filters

    def __enter__(self):
        self.board.analog[0].register_callback(self)
        for _ in range(3):
            self.board.analog[_].enable_reporting()

    def __call__(self, data, *args, **kwargs):
        ch0 = data
        ch0_f = self.filters[0].filter(ch0)

        ch1 = self.board.analog[1].read()
        ch1_f = self.filters[1].filter(ch1)

        ch2 = self.board.analog[2].read()
        ch2_f = self.filters[2].filter(ch2)

        if ch0 and ch1 and ch2:
            self.qtPanningPlot1.addData(ch0, ch1, ch2)
            self.qtPanningPlot2.addData(ch0_f, ch1_f, ch2_f)

   def __exit__(self, exc_type, exc_val, exc_tb):
       self.board.samplingOff()
       self.board.exit()
       self.app.exec_()


if __name__ == "__main__":
    my_iirs = [return_filter() for _ in range(3)]
    with ArduinoScope(my_iirs) as scope:
        time_sleep = 10

    print("Finished")
