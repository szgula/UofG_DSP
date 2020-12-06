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
    """
    Real-time plotting class
    """
    def __init__(self, title):
        x_range = 500
        self.win = pg.GraphicsLayoutWidget()
        self.win.setWindowTitle(title)
        self.plt = self.win.addPlot()
        self.plt.setYRange(-1, 1)
        self.plt.setXRange(0, x_range)
        self.labels = ['x', 'y', 'z', 's']
        self.curve = {name: self.plt.plot() for name in self.labels}
        self.data_ = {name: deque([0] * x_range, maxlen=x_range) for name in self.labels}
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)
        self.layout = QtGui.QGridLayout()
        self.win.setLayout(self.layout)
        self.win.show()
        self.pens = {'x': pg.mkPen('b', width=1),
                     'y': pg.mkPen('g', width=1),
                     'z': pg.mkPen('m', width=1),
                     'e': pg.mkPen('r', width=2),
                     's': pg.mkPen('w', width=2), }
        self.event = False

    def update(self):
        for label_name in self.labels:
            pen_ = self.pens[label_name]
            if self.event and label_name == 's': pen_ = self.pens['e']
            self.curve[label_name].setData(np.hstack(self.data_[label_name]), pen=pen_)

    def addData(self, x, y, z, s, e=False):
        for label_name, input_ in [('x', x), ('y', y), ('z', z), ('s', s)]:
            self.data_[label_name].append(input_)
        self.event = e


class ArduinoScope:
    """
    Visualization class for proof-of-concept fall detector (Arduino based)
    """
    def __init__(self, filters, debug=False):
        self.PORT = Arduino.AUTODETECT
        self.app = QtGui.QApplication(sys.argv)
        self.qtPanningPlot1 = QtPanningPlot("Arduino raw data")
        self.qtPanningPlot2 = QtPanningPlot("Filtered data")
        self.samplingRate = 100
        self.board = Arduino(self.PORT)
        self.board.samplingOn(1000 / self.samplingRate)
        self.filters = filters
        self.debug_ = debug
        if self.debug_: self.file = open('Arduino Python/xyz_output.txt', 'w')
        self.timestamp = 0
        self.event = False
        self.event_time = 0

    def __enter__(self):
        self.board.analog[0].register_callback(self.callback)
        for i in range(3):
            self.board.analog[i].enable_reporting()
        self.time_s = time.time()
        self.app.exec_()

    @staticmethod
    def _convert_to_normalized_acc(x):
        # 3.3V is a sensor output upper voltage, 5V is a upper A/D converter voltage, 2 stands for two regions (+ and -)
        translate_val = 3.3 / (5 * 2)
        scalar_val = 1 / translate_val
        norm_acc = (x - translate_val) * scalar_val if x is not None else 0
        return norm_acc

    def _get_filtered_values(self, x, y, z):
        x_f = self.filters[0].filter(x)
        y_f = self.filters[1].filter(y)
        z_f = self.filters[2].filter(z)
        return x_f, y_f, z_f

    @staticmethod
    def _get_3d_vector(x, y, z):
        return (x**2 + y**2 + z**2)**0.5

    def callback(self, data, *args, **kwargs):
        ch0 = self._convert_to_normalized_acc(data)
        ch1 = self._convert_to_normalized_acc(self.board.analog[1].read())
        ch2 = self._convert_to_normalized_acc(self.board.analog[2].read())
        ch0_f, ch1_f, ch2_f = self._get_filtered_values(ch0, ch1, ch2)

        if ch0 and ch1 and ch2:
            vector = self._get_3d_vector(ch0, ch1, ch2)
            vector_f = self._get_3d_vector(ch0_f, ch1_f, ch2_f)
            self.qtPanningPlot1.addData(ch0, ch1, ch2, vector)

            # Handle fall event
            if vector_f > 0.45:
                self.event = True
                self.event_time = 0
            if self.event: self.event_time += 1
            if self.event_time > 200: self.event = False
            self.qtPanningPlot2.addData(ch0_f, ch1_f, ch2_f, vector_f, self.event)

        self.timestamp += (1 / self.samplingRate)
        if self.debug_:
            self.file.write(f'{round(self.timestamp, 4), ch0, ch1, ch2, ch0_f, ch1_f, ch2_f} \n')

    def __exit__(self, exc_type, exc_val, exc_tb):
        time_f = time.time()
        self.board.samplingOff()
        self.board.exit()
        if self.debug_:
            self.file.close()
        print(f'execution_time: {time_f - self.time_s} actual sampling rate {(time_f - self.time_s) / (self.timestamp / self.samplingRate)}')


if __name__ == "__main__":
    my_iirs = [return_filter() for _ in range(3)]
    with ArduinoScope(my_iirs) as scope:
        time_sleep = 100
        time.sleep(time_sleep)
    print('Finished')