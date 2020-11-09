from collections import deque
import numpy as np
import unittest


class FIRFilter:
    def __init__(self, impulse_response_coef: np.array) -> None:
        """
        FIR filter setup method, that converts class into function like (callable) object
        :param impulse_response_coef: FIR filter coefficients
        """
        self._num_of_taps = len(impulse_response_coef)
        self._past_values = deque([0] * self._num_of_taps, maxlen=self._num_of_taps)
        self._impulse_response = impulse_response_coef

    def __call__(self, new_val: float) -> float:
        """
        Filter object executable method
        :param new_val: new input value
        :return: filtered output (delayed compared to input)
        """
        self._past_values.append(new_val)
        return self.do_filter()

    def do_filter(self):
        """
        Filter execution for given past states and filter coefficients
        :return: single step filtered output
        """
        return np.sum(np.multiply(self._past_values, self._impulse_response))


class FIRFilterFactory(FIRFilter):
    def __init__(self, num_taps: int, norm_freq_list: list, pass_zero: bool, window_type: 'str' = 'triangle') -> None:
        """
        FIR filter designed (based on the FIRFilter class)
        :param num_taps: number of tabs in the FIR filter
        :param norm_freq_list: list of frequencies to remove
        :param pass_zero: flag if first given frequency is passed or removed
        :param window_type: filter window type
        """
        self._num_of_taps = num_taps
        self._freq_list = np.array(norm_freq_list)
        self._pass_zero = pass_zero
        self._window_type = window_type

        self._impulse_response = self._initialize_impulse_response()
        self._window = self._initialize_window()
        super().__init__(self._impulse_response * self._window)

    def _initialize_impulse_response(self) -> np.array:
        """
        Based on the defined cutoff frequency - design the FIR filter coefficients
        :return: raw filter coefficients
        """
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
        """
        Initialized the window coefficients for given window type
        :return: window coefficients
        """
        if self._window_type == 'triangle':
            norm_range = np.arange(0, 1, 1 / (self._num_of_taps // 2))
            norm_range = np.array([*norm_range, *norm_range[::-1]])
        else:
            raise NotImplemented('Currently only triangle method is implemented - please use it')
        return norm_range


class FIRDetector(FIRFilter):
    def __init__(self, values, threshold_value=2.5e-11):
        """
        Factory for the FIR detector using templates
        :param values: the templates coefficients
        :param threshold_value: event detector threshold (for squared convolution)
        """
        self.threshold_value = threshold_value
        super().__init__(values)
        self.since_last_peak = self._num_of_taps
        self._debug = []

    def __call__(self, *args, **kwargs):
        """
        Execute template convolution with historical signal;
        This method also ensures that signal is triggered at maximum once per len(template) inputs
        :param args: inherited
        :param kwargs: inherited
        :return: event signal
        """
        out = super().__call__(*args, **kwargs)
        out **= 2
        self._debug.append(out)
        out = int(out > self.threshold_value)
        if out and self.since_last_peak > self._num_of_taps:
            self.since_last_peak = -1
        else:
            out = 0
        self.since_last_peak += 1
        return out


class TestFIR(unittest.TestCase):
    """
    Testing area
    """
    def test_initialization(self):
        """Smoke unit test """
        freq = [x / 250 for x in [40, 60]]
        my_fir = FIRFilterFactory(30, freq, False)

    def test_fir_base_class(self):
        """ Test FIR base on the impulse"""
        coef = np.array([0, 0.5, 1, 0.5, 0])
        my_fir = FIRFilter(coef)
        impuls = [1, 0, 0, 0, 0]
        out = [my_fir(i) for i in impuls]
        np.testing.assert_array_almost_equal(coef, out)


if __name__ == '__main__':
    unittest.main()

