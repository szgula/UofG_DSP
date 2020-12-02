from IIR_filter import IIRFilter, IIR2Filter, return_filter

#!/usr/bin/python3

from pyfirmata2 import Arduino
import time

PORT = Arduino.AUTODETECT


class AnalogPrinter:

    def __init__(self, filter):
        # sampling rate: 10Hz
        self.samplingRate = 10
        self.timestamp = 0
        self.board = Arduino(PORT)
        self._filter = filter
        self.file = open('output.txt', 'w')
        self.buffer = []
        self.filtered_buffer = []

    def __enter__(self):
        self.board.analog[0].register_callback(self.myPrintCallback_x)
        #self.board.analog[1].register_callback(self.myPrintCallback_y)
        self.board.samplingOn(10)
        self.board.analog[0].enable_reporting()
        self.board.analog[1].enable_reporting()

    def myPrintCallback_x(self, data):
        filtered = self._filter.filter(data)
        print(f"x = {self.timestamp}, {data}, filtered: {filtered}")
        self.timestamp += (1 / self.samplingRate)
        #y_data = self.board.analog[1].read()
        self.buffer.append(data)
        self.filtered_buffer.append(filtered)
        self.file.write(f'{data}, {filtered} \n')


    def __exit__(self, type, val, tr):
        self.board.samplingOff()
        self.board.exit()
        self.file.close()



if __name__ == "__main__":
    my_iir = return_filter()
    with AnalogPrinter(my_iir) as analogPrinter:
        time_sleep = 10
        time.sleep(time_sleep)


