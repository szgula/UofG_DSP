from ecg_gudb_database import GUDb
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
from fir_filter import FIRDetector, FIRFilterFactory


class HeartbeatsDetector(FIRDetector):
    def __init__(self, fs=250):
        """
        Heart beats template based on the FIRDetector class
        It uses predefined/hardcoded heart beat shape as the template base
        :param fs: sampling frequency (to calculate time between beats)
        """
        # single_peak_range = (1170, 1200)
        values = np.array(
            [-2.22810372e-04, -2.39728147e-04, -2.56649948e-04, -2.66944121e-04,
             -2.55091646e-04, -2.82744064e-04, -2.75640369e-04, -2.83856690e-04,
             -2.41320108e-04, -2.34271600e-04, -2.14147065e-04, -1.64292148e-04,
             -1.38330570e-04, -1.36223466e-04, -1.10100576e-04, -9.95941213e-05,
             -7.31425922e-05, -5.70053840e-05, -2.07566317e-05, 1.41124442e-05,
             -5.75160332e-07, -7.93870659e-05, -2.17743132e-04, -3.11713559e-04,
             -4.43628182e-04, -5.89962427e-04, -6.74583967e-04, -7.23436156e-04,
             -7.46469319e-04, -7.35359383e-04, -4.77638220e-04, -5.65740806e-05,
             2.78727232e-04, 6.73170119e-04, 8.93254660e-04, 6.97064807e-04,
             3.47992714e-04, -6.22294667e-05, -4.30642062e-04, -6.42892980e-04,
             -6.69740291e-04, -5.81140779e-04, -5.22548704e-04, -4.60380262e-04,
             -3.99605363e-04, -3.54068200e-04, -2.92999105e-04, -1.92964742e-04,
             -1.45894186e-04, -1.00865863e-04, -1.21077438e-04, -1.40184192e-04,
             -1.20383251e-04, -1.22370280e-04, -1.45199095e-04, -1.88362713e-04,
             -1.84759906e-04, -1.40900153e-04, -1.78750993e-04, -5.73116219e-05])
        values = values[::-1]
        self.heart_rate = 0
        self.average_heart_rate = 0
        self.heart_rate_history = deque(maxlen=10)
        self.fs = fs
        super().__init__(values)

    def __call__(self, *args, **kwargs):
        """
        Extends FIRDetector callable functionality with heart beat postprocessing
        :param args: inherited
        :param kwargs: inherited
        :return: inherited
        """
        samples_since_last_peak = self.since_last_peak
        heart_beat_detected = super().__call__(*args, **kwargs)
        if heart_beat_detected:
            self.heart_rate = 60 * self.fs / samples_since_last_peak
            self.heart_rate_history.append(self.heart_rate)
            self.average_heart_rate = np.mean(self.heart_rate_history)
        return heart_beat_detected

    def get_heart_rate(self):
        """ just interface """
        return self.heart_rate, self.average_heart_rate


if __name__ == '__main__':
    ecg_class = GUDb(13,  'walking')
    heart_rate = []
    freq = [x / 250 for x in [0, 10, 40, 60]]
    my_fir = FIRFilterFactory(300, freq, False)
    my_detector = HeartbeatsDetector()

    output_list = np.zeros(len(ecg_class.einthoven_II))
    output_piks = np.zeros(len(ecg_class.einthoven_II))
    for idx, val in enumerate(ecg_class.einthoven_II):
        output_list[idx] = my_fir(val)
        output_piks[idx] = my_detector(output_list[idx])
        if output_piks[idx] > 0:
            hr, ahr = my_detector.get_heart_rate()
            heart_rate.append(hr)
            if idx % 20 == 0:
                print(f' beats per minute (bpm) = {hr:.2f}, \t mean bpm (10 cycles) = {ahr:.2f}')

    plt.plot(heart_rate)
    plt.title('Graph of the momentary heartrate (in BPM: beats-per-minute) against time')
    plt.xlabel('time step [unit step]')
    plt.ylabel('momentary hear rate [bpm]')
    plt.show()
    print('end')
