import matplotlib.pyplot as plt
from scipy.fft import fft
import numpy as np
from math import floor

# Question: is the iterative chunk approach proper one? or should we first clip "distinguish" sounds and then apply
# digit recognition  for each (full) sequence

# in the exercise the dat file is rename - should we keep the name or change to follow the project tree structure
# (it is harder to match ordinal file)

def get_button_by_frequency(fft_val: np.array, f_sample: float, f_step_: float) -> object:
    """
    Decode digit/symbol from sound chunk
    :param fft_val: nd.array of fft values
    :param f_sample: sampling frequency
    :param f_step_: frequency step between fft values
    :return: decoded symbol/digit if any, None otherwise
    """
    rows_fs = f_sample - np.array([697, 770, 852, 941])   # hardcoded keyboard rows frequencies
    columns_fs = np.array([1209, 1336, 1477]) - f_sample  # hardcoded keyboard columns frequencies
    map_id_to_key = {0: {0: 1, 1: 2, 2: 3},               # hardcoded map from row + column to symbol
            1: {0: 4, 1: 5, 2: 6},
            2: {0: 7, 1: 8, 2: 9},
            3: {0: '*', 1: 0, 2: '#'}}

    frequency_lookup_range = 10  # hardcoded frequency where signal is encoded (should be 1.5% according to documentation)
    value_threshold = 10         # hardcoded fft threshold value where given frequency is detected
    found_row_idx = None
    found_col_idx = None

    for row_idx, row_fs in enumerate(rows_fs):
        lower_boundary_idx = int((row_fs - frequency_lookup_range) / f_step_)
        upper_boundary_idx = int((row_fs + frequency_lookup_range) / f_step_)
        if np.max(fft_val[lower_boundary_idx:upper_boundary_idx]) > value_threshold:
            if found_row_idx is not None: return None
            found_row_idx = row_idx
    if found_row_idx is None: return None

    for col_idx, col_fs in enumerate(columns_fs):
        lower_boundary_idx = int((col_fs - frequency_lookup_range) / f_step_)
        upper_boundary_idx = int((col_fs + frequency_lookup_range) / f_step_)
        if np.max(fft_val[lower_boundary_idx:upper_boundary_idx]) > value_threshold:
            if found_col_idx is not None: return None
            found_col_idx = col_idx
    if found_col_idx is None: return None

    return map_id_to_key[found_row_idx][found_col_idx]


def decode_signal(stream_val: np.array, T: float, N: int, fs: float, window_size: int):
    """
    Decoded signal by chunks of size 'window_size'
    :param stream_val: loaded signal values
    :param T: sample time
    :param N: number of samples
    :param fs: sampling frequency
    :param window_size: chunk size
    :return: decoded sequence
    """
    last_none = True
    sequence = []
    for i in range(floor(N / window_size) + 1):
        chunk = stream_val[i * window_size:(i + 1) * window_size]
        n = len(chunk)
        f_step = fs / n
        xf = np.linspace(0.0, 1.0 / (2.0 * T), n // 2)[1:]
        yf = fft(chunk)
        yf = 2.0 * np.abs(yf[1:n // 2]) / n
        symbol = get_button_by_frequency(yf, fs, f_step)
        if symbol is not None:
            if last_none:
                sequence.append(symbol)
                last_none = False
        else:
            last_none = True
    return sequence


def main(file_path=r'msc_matric_3.dat'):
    stream_ids = []
    stream_val = []
    with open(file_path, "r") as file:
        for line in file.readlines():
            idx, val = line.split()
            stream_ids.append(idx)
            stream_val.append(val)

    stream_ids = np.array(stream_ids)
    stream_val = np.array(stream_val)

    window_size = 150

    N = len(stream_val)
    fs = 1000
    T = 1 / fs

    decoded = decode_signal(stream_val, T, N, fs, window_size)
    print(f'decoded digits: {decoded}, total length {len(decoded)}')


if __name__ == '__main__':
    main()
