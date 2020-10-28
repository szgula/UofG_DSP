from ecg_gudb_database import GUDb
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
from fir_filter import FIRDetector, FIRFilterFactory


class HeartbeatsDetector(FIRDetector):
    def __init__(self, fs=250):
        # single_peak_range = (1170, 1200)
        values = np.array(
            [1.24022673e-04, 1.32435258e-04, 1.50092448e-04, 1.58069893e-04, 1.64454361e-04, 1.60667208e-04,
             1.61647662e-04, 1.55677007e-04, 1.47999996e-04, 1.37994913e-04, 1.17840109e-04, 1.15812473e-04,
             1.11899390e-04, 1.08061889e-04, 1.19508330e-04, 1.34116178e-04, 1.55282046e-04, 1.70107293e-04,
             1.91011808e-04, 2.15745538e-04, 2.26796469e-04, 2.29995624e-04, 2.20063436e-04, 2.03596942e-04,
             1.85005368e-04, 1.45969714e-04, 8.72085272e-05, -1.87393328e-06, -1.19951871e-04, -2.58033255e-04,
             -3.73071143e-04, -3.66276667e-04, -2.19602050e-04, 3.73990508e-05, 3.73224064e-04, 7.25512358e-04,
             9.22222978e-04, 9.37162745e-04, 7.64882308e-04, 5.15439476e-04, 2.34927075e-04, -5.25910049e-05,
             -1.84480913e-04, -1.77381560e-04, -1.64764144e-04, -1.12907342e-04, -3.52399996e-05, 1.61537511e-05,
             3.62378064e-05, 5.87792881e-05, 1.08183458e-04, 1.49314334e-04, 1.68665232e-04, 1.85869963e-04,
             2.04935610e-04, 2.04288338e-04, 1.95325891e-04, 1.94443213e-04, 1.94097434e-04, 1.81260730e-04,
             1.68835490e-04, 1.55281639e-04, 1.47015008e-04, 1.38063681e-04, 1.36418945e-04, 1.33263888e-04,
             1.29081617e-04, 1.28068395e-04, 1.28176252e-04, 1.22683107e-04, 1.28081861e-04, 1.29656378e-04,
             1.33947846e-04, 1.33843339e-04, 1.31842848e-04])
        values = values[::-1]
        self.hear_rate = 0
        self.average_hear_rate = 0
        self.hear_rate_history = deque(maxlen=10)
        self.fs = fs
        super().__init__(values)

    def __call__(self, *args, **kwargs):
        samples_since_last_peak = self.since_last_peak
        out = super().__call__(*args, **kwargs)
        if out:
            self.hear_rate = 60 * self.fs / samples_since_last_peak
            self.hear_rate_history.append(self.hear_rate)
            self.average_hear_rate = np.mean(self.hear_rate_history)
        return out

    def get_heart_rate(self):
        return self.hear_rate, self.average_hear_rate


if __name__ == '__main__':
    ecg_class = GUDb(2,  'walking')
    hear_rate = []
    freq = [x / 250 for x in [1, 10, 40, 60]]
    my_fir = FIRFilterFactory(100, freq, False)
    my_detector = HeartbeatsDetector()

    output_list = np.zeros(len(ecg_class.cs_V2_V1))
    output_piks = np.zeros(len(ecg_class.cs_V2_V1))
    for idx, val in enumerate(ecg_class.cs_V2_V1):
        output_list[idx] = my_fir(val)
        output_piks[idx] = my_detector(output_list[idx])
        if output_piks[idx] > 0:
            hr, ahr = my_detector.get_heart_rate()
            hear_rate.append(hr)
            print(f' beats per minute (bpm) = {hr:.2f}, \t mean bpm (10 cycles) = {ahr:.2f}')


    #plt.plot(output_list)
    #plt.plot(ecg_class.cs_V2_V1)
    #plt.plot(output_piks)
    plt.plot(hear_rate)
    print('end')
