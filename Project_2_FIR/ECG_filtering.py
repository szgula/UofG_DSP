import numpy as np
import matplotlib.pyplot as plt
from fir_filter import FIRFilterFactory

import unittest

class TestFIR(unittest.TestCase):
    def test_full_flow(self):
        with open(r'ECG_msc_matric_3.dat', 'r') as file:
            ecg_vals = []
            for val in file.readlines():
                ecg_vals.append(float(val))
        freq = [x / 250 for x in [40, 60]]
        my_fir = FIRFilterFactory(30, freq, False)

        output_list = np.zeros(len(ecg_vals))
        for idx, val in enumerate(ecg_vals):
            output_list[idx] = my_fir(val)

        plt.plot(output_list, label='filtered signal')
        plt.plot(ecg_vals, label='origin signal')
        plt.xlabel('Time [s]')
        plt.ylabel('Value [-]')
        plt.legend()
        return True

    def test_initialization(self):
        freq = [x / 250 for x in [40, 60]]
        my_fir = FIRFilterFactory(30, freq, False)

if __name__ == '__main__':
    unittest.main()
