import numpy as np
import matplotlib.pyplot as plt
from fir_filter import FIRFilterFactory, FIRFilter


def test_full_flow():
    """ Full flow smoke test"""
    with open(r'ECG_msc_matric_3.dat', 'r') as file:
        ecg_vals = []
        for val in file.readlines():
            ecg_vals.append(float(val))
    fr = 250
    freq = [x / fr for x in [0, 10, 40, 60]]
    my_fir = FIRFilterFactory(30, freq, False)

    output_list = np.zeros(len(ecg_vals))
    for idx, val in enumerate(ecg_vals):
        output_list[idx] = my_fir(val)

    time_s = np.array(range(len(output_list))) / fr
    plt.plot(time_s, output_list, label='filtered signal')
    plt.plot(time_s, ecg_vals, label='origin signal')
    plt.xlabel('Time [s]')
    plt.ylabel('Value [-]')
    plt.title('ECG data')
    plt.legend()
    plt.show()
    #plt.savefig('ECG_data.svg')


if __name__ == '__main__':
    test_full_flow()
