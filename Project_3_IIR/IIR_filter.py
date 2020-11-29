from collections import deque
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

class IIRFilter:
    def __init__(self, sos):
        self.filter_chain = [IIR2Filter(i[:3], i[3:]) for i in sos]

    def filter(self, input):
        out = input
        for fil in self.filter_chain:
            out = fil.filter(out)
        return out


class IIR2Filter:
    def __init__(self, b, a):
        """
        :param f: narmalized frequency
        :param r:
        """
        a0, a1, a2, b0, b1, b2 = *a, *b
        self.buffer_m1 = 0
        self.buffer_m2 = 0
        self.a0 = a0
        self.a1 = a1
        self.a2 = a2
        self.b0 = b0
        self.b1 = b1
        self.b2 = b2

    def filter(self, input):
        in_sum = input - self.a1 * self.buffer_m1 - self.a2 * self.buffer_m2
        out_sum = self.b0 * in_sum + self.b1 * self.buffer_m1 + self.b2 * self.buffer_m2
        self.buffer_m2 = self.buffer_m1
        self.buffer_m1 = in_sum
        return out_sum

    @staticmethod
    def notch(f, r):
        b0 = 1
        b1 = -2 * np.cos(2*np.pi*f)
        b2 = 1
        a0 = 1
        a1 = -2 * r* np.cos(2*np.pi*f)
        a2 = r*r
        return a0, a1, a2, b0, b1, b2


if __name__ == "__main__":
    with open('output.txt', 'r') as f:
        a = f.readlines()
    data = list(map(float, a))

    sampling_rate = 100  # Hzimp
    noise_frequency = 5  # Hz
    r = 0.99
    temp = IIR2Filter.notch(noise_frequency/sampling_rate, r)
    my_iir = IIR2Filter(temp[3:], temp[:3])

    b, a = signal.cheby2(6, 40, 0.05*2)
    w, h = signal.freqz(b, a)
    # plt.plot(w / np.pi / 2, 20 * np.log10(np.abs(h)))


    freq = 5 / 50
    sos = signal.cheby2(6, 40, freq*2, output='sos')

    my_iir = IIR2Filter(sos[0, :3], sos[0, 3:])
    my_factory = IIRFilter(sos)

    out = [my_factory.filter(x) for x in data]
    scalar = np.mean(out[1000:-1000]) / np.mean(data[1000:-1000])
    out_mod = [x/scalar for x in out]
    filtered = signal.sosfilt(sos, data)


    plt.plot(out_mod, label=f'freq = {freq}')
    #plt.plot(filtered, label=f'ref')
    plt.legend()

    plt.plot(data, label='row')
    plt.legend()
    print('end')

