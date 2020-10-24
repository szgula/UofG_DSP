from ecg_gudb_database import GUDb
import numpy as np
from collections import deque
import matplotlib.pyplot as plt

# Question - h(n) and w(s) should have length of M
# when apply window function: the 'newest' value should be multiply with 'zero'?

## TODO: split into filter and desing class
class FIRFilter:
    def __init__(self, num_taps: int, norm_freq_list: list, pass_zero: bool, window_type: 'str' = 'triangle') -> None:
        self._num_of_taps = num_taps
        self._freq_list = np.array(norm_freq_list)
        self._pass_zero = pass_zero
        self._window_type = window_type

        self._past_values = deque([0] * self._num_of_taps, maxlen=self._num_of_taps)
        self._impulse_response = self._initialize_impulse_response()
        self._window = self._initialize_window()
        self._impulse_response = self._impulse_response * self._window

    def _initialize_impulse_response(self) -> np.array:
        # TODO: need to mirrot the ideal_fre_resp
        ideal_fre_resp = np.ones(self._num_of_taps//2)
        state_toggle = int(not self._pass_zero)
        left_end = 0
        for freq in self._freq_list:
            right_end = int(freq * self._num_of_taps)
            ideal_fre_resp[left_end:right_end+1] = state_toggle
            left_end = right_end
            state_toggle = 1 - state_toggle

        ideal_fre_resp = np.array([*ideal_fre_resp, *ideal_fre_resp[::-1]])
        resp_ifft = np.fft.ifft(ideal_fre_resp)
        temp = resp_ifft.copy()
        resp_ifft[len(resp_ifft)//2:], resp_ifft[:len(resp_ifft)//2] = temp[:len(resp_ifft)//2], temp[len(resp_ifft)//2:]
        return resp_ifft # [125:-125]

    def _initialize_window(self) -> np.array:
        if self._window_type == 'triangle':
            norm_range = np.arange(0, 1, 1 / (self._num_of_taps // 2))
            norm_range = np.array([*norm_range, *norm_range[::-1]])
        else:
            raise NotImplemented('Currently only triangle method is implemented - please use it')
        return norm_range

    def __call__(self, new_val):
        self._past_values.append(new_val)
        return self.do_filter()

    def do_filter(self):
        # TODO: remove np.real
        return np.real(np.sum(np.multiply(self._past_values, self._impulse_response)))


if __name__ == '__main__':
    #single_peak_range = (1170, 1200)
    values = np.array([ 1.24022673e-04,  1.32435258e-04,  1.50092448e-04,  1.58069893e-04,
        1.64454361e-04,  1.60667208e-04,  1.61647662e-04,  1.55677007e-04,
        1.47999996e-04,  1.37994913e-04,  1.17840109e-04,  1.15812473e-04,
        1.11899390e-04,  1.08061889e-04,  1.19508330e-04,  1.34116178e-04,
        1.55282046e-04,  1.70107293e-04,  1.91011808e-04,  2.15745538e-04,
        2.26796469e-04,  2.29995624e-04,  2.20063436e-04,  2.03596942e-04,
        1.85005368e-04,  1.45969714e-04,  8.72085272e-05, -1.87393328e-06,
       -1.19951871e-04, -2.58033255e-04, -3.73071143e-04, -3.66276667e-04,
       -2.19602050e-04,  3.73990508e-05,  3.73224064e-04,  7.25512358e-04,
        9.22222978e-04,  9.37162745e-04,  7.64882308e-04,  5.15439476e-04,
        2.34927075e-04, -5.25910049e-05, -1.84480913e-04, -1.77381560e-04,
       -1.64764144e-04, -1.12907342e-04, -3.52399996e-05,  1.61537511e-05,
        3.62378064e-05,  5.87792881e-05,  1.08183458e-04,  1.49314334e-04,
        1.68665232e-04,  1.85869963e-04,  2.04935610e-04,  2.04288338e-04,
        1.95325891e-04,  1.94443213e-04,  1.94097434e-04,  1.81260730e-04,
        1.68835490e-04,  1.55281639e-04,  1.47015008e-04,  1.38063681e-04,
        1.36418945e-04,  1.33263888e-04,  1.29081617e-04,  1.28068395e-04,
        1.28176252e-04,  1.22683107e-04,  1.28081861e-04,  1.29656378e-04,
        1.33947846e-04,  1.33843339e-04,  1.31842848e-04])
    match_buffer = deque([0] * len(values), maxlen=len(values))
    values = values[::-1]
    last_bps = deque(maxlen=10)
    ecg_class = GUDb(13,  'walking')

    freq = [x / 250 for x in [1, 10, 40, 60]]
    my_fir = FIRFilter(100, freq, False)

    output_list = np.zeros(len(ecg_class.cs_V2_V1))
    output_piks = np.zeros(len(ecg_class.cs_V2_V1))
    last_peak = 0
    for idx, val in enumerate(ecg_class.cs_V2_V1):
        output_list[idx] = my_fir(val)
        match_buffer.append(output_list[idx])
        output_piks[idx] = max(ecg_class.cs_V2_V1) if np.sum(np.multiply(match_buffer, values)) > 2.0e-6 else 0
        if idx < last_peak + len(values):
            output_piks[idx] = 0
        if output_piks[idx] > 0:
            bs = (idx - last_peak)/ecg_class.fs
            bpm = 60 / bs
            last_bps.append(bpm)
            print(f'beats separation = {bs:.2f} s, \t beats per minute (bpm) = {bpm:.2f}, \t mean bpm (10 cycles) = {np.mean(last_bps):.2f}')
            last_peak = idx


    plt.plot(output_list)
    plt.plot(ecg_class.cs_V2_V1)
    plt.plot(output_piks)
    print('end')
