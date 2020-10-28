from collections import deque
import numpy as np


class FIRFilter:
    # TODO -> refactor: num_taps not needed
    def __init__(self, impulse_response_coef: np.array) -> None:

        self._num_of_taps = len(impulse_response_coef)
        self._past_values = deque([0] * self._num_of_taps, maxlen=self._num_of_taps)
        self._impulse_response = impulse_response_coef

    def __call__(self, new_val):
        self._past_values.append(new_val)
        return self.do_filter()

    def do_filter(self):
        return np.sum(np.multiply(self._past_values, self._impulse_response))


class FIRFilterFactory(FIRFilter):
    def __init__(self, num_taps: int, norm_freq_list: list, pass_zero: bool, window_type: 'str' = 'triangle') -> None:
        self._num_of_taps = num_taps
        self._freq_list = np.array(norm_freq_list)
        self._pass_zero = pass_zero
        self._window_type = window_type

        self._impulse_response = self._initialize_impulse_response()
        self._window = self._initialize_window()
        super().__init__(self._impulse_response * self._window)

    def _initialize_impulse_response(self) -> np.array:
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
        return resp_ifft

    def _initialize_window(self) -> np.array:
        if self._window_type == 'triangle':
            norm_range = np.arange(0, 1, 1 / (self._num_of_taps // 2))
            norm_range = np.array([*norm_range, *norm_range[::-1]])
        else:
            raise NotImplemented('Currently only triangle method is implemented - please use it')
        return norm_range


class FIRDetector(FIRFilter):
    def __init__(self, values):
        self.threshold_value = 2.0e-6
        super().__init__(values)
        self.since_last_peak = self._num_of_taps
        self._debug = []

    def __call__(self, *args, **kwargs):
        out = super().__call__(*args, **kwargs)
        self._debug.append(out)
        out = int(out > self.threshold_value)
        if out and self.since_last_peak > self._num_of_taps:
            self.since_last_peak = -1
        else:
            out = 0
        self.since_last_peak += 1
        return out


