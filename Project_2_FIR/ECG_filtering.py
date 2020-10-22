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
        return np.real(np.sum(np.multiply(self._past_values, self._impulse_response)))


if __name__ == '__main__':
    with open(r'ECG_msc_matric_3.dat', 'r') as file:
        ecg_vals = []
        for val in file.readlines():
            ecg_vals.append(float(val))
    freq = [x / 250 for x in [40, 60]]
    my_fir = FIRFilter(30, freq, False)

    output_list = np.zeros(len(ecg_vals))
    for idx, val in enumerate(ecg_vals):
        output_list[idx] = my_fir(val)

    plt.plot(output_list)
    plt.plot(ecg_vals)
    print('end')
