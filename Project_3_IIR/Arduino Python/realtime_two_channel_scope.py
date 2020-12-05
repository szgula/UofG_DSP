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
import time


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
        self.data_s = deque([0]*x_range, maxlen=x_range)
        # any additional initialisation code goes here (filters etc)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)
        self.layout = QtGui.QGridLayout()
        self.win.setLayout(self.layout)
        self.win.show()
        self.pens = {'b': pg.mkPen('b', width=1),
                     'g': pg.mkPen('g', width=1),
                     'm': pg.mkPen('m', width=1),
                     'r': pg.mkPen('r', width=2),
                     'w': pg.mkPen('w', width=2),}
        self.event = False

    def update(self):
        self.curve_x.setData(np.hstack(self.data_x), pen=self.pens['b'])
        self.curve_y.setData(np.hstack(self.data_y), pen=self.pens['g'])
        self.curve_z.setData(np.hstack(self.data_z), pen=self.pens['m'])
        pen_ = pen=self.pens['r'] if self.event else self.pens['w']
        self.curve_s.setData(np.hstack(self.data_s), pen=pen_)

    def addData(self, x, y, z, s, e=False):
        self.data_x.append(x)
        self.data_y.append(y)
        self.data_z.append(z)
        self.data_s.append(s)
        self.event = e


class ArduinoScope:
    def __init__(self, filters):
        self.PORT = Arduino.AUTODETECT
        self.app = QtGui.QApplication(sys.argv)
        self.qtPanningPlot1 = QtPanningPlot("Arduino raw data")
        self.qtPanningPlot2 = QtPanningPlot("Filtered data")
        self.samplingRate = 100
        self.board = Arduino(self.PORT)
        self.board.samplingOn(1000 / self.samplingRate)
        self.filters = filters
        #test
        self.file = open('xyz_output.txt', 'w')
        self.timestamp = 0
        self.event = False
        self.event_time = 0
        #test

    def __enter__(self):
        self.board.analog[0].register_callback(self.callback)
        self.board.analog[0].enable_reporting()
        self.board.analog[1].enable_reporting()
        self.board.analog[2].enable_reporting()
        self.app.exec_()

        self.board.analog[0].register_callback(self.myPrintCallback)
        #self.board.analog[1].register_callback(self.myPrintCallback_y)
        self.board.samplingOn(10)

        #for _ in range(3):
        #   self.board.analog[_].enable_reporting()

    def callback(self, data, *args, **kwargs):
        translate_val = 3.3/(5*2)
        scalar_val = 1/translate_val
        mod_fun = lambda x: (x - translate_val) * scalar_val if x is not None else 0

        ch0 = mod_fun(data)
        ch0_f = self.filters[0].filter(ch0)

        ch1 = self.board.analog[1].read()
        ch1 = mod_fun(ch1)
        ch1_f = self.filters[1].filter(ch1)

        ch2 = self.board.analog[2].read()
        ch2 = mod_fun(ch2)
        ch2_f = self.filters[2].filter(ch2)

        if ch0 and ch1 and ch2:
            vector = (ch0 ** 2 + ch1 ** 2 + ch2 ** 2) ** 0.5
            vector_f = (ch0_f**2 + ch1_f**2 + ch2_f**2)**0.5
            self.qtPanningPlot1.addData(ch0, ch1, ch2, vector)
            if vector_f > 0.45:
                self.event = True
                self.event_time = 0
            if self.event: self.event_time += 1
            if self.event_time > 20:
                self.event = False
            self.qtPanningPlot2.addData(ch0_f, ch1_f, ch2_f, vector_f, self.event)


        print('raw and filtered data: ', round(self.timestamp, 4), ch0, ch1, ch2, ch0_f, ch1_f, ch2_f)
        self.timestamp += (1 / self.samplingRate)

        self.file.write(f'{round(self.timestamp, 4), ch0, ch1, ch2, ch0_f, ch1_f, ch2_f} \n')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.board.samplingOff()
        self.board.exit()
        self.file.close()


if __name__ == "__main__":
    my_iirs = [return_filter() for _ in range(3)]
    with ArduinoScope(my_iirs) as scope:
        time_sleep = 100
        time.sleep(time_sleep)

        # for i in range(100000):
        # time.sleep(0.0001)

    print("Finished")
