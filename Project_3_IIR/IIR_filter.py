import numpy as np
import matplotlib.pyplot as plt


class IIRFilter:
    """ Iterator for the chain of second order IIR filters"""
    def __init__(self, sos):
        """
        :param sos: SOS format according to the SciPy Signal notation standard
        """
        self.filter_chain = [IIR2Filter(i[:3], i[3:]) for i in sos]

    def filter(self, input):
        """
        Execute the chain of 2'nd order IIR filers
        :param input: single instance value to filter
        :return: filtered value
        """
        out = input
        for fil in self.filter_chain:
            out = fil.filter(out)
        return out


class IIR2Filter:
    """ Second order IIR filter implementation """
    def __init__(self, b, a):
        """
        :param b: iir nominator coefficients
        :param a:iir denominator coefficients
        """
        self.a0, self.a1, self.a2, self.b0, self.b1, self.b2 = *a, *b
        self.buffer_m1 = 0
        self.buffer_m2 = 0

    def filter(self, input):
        """
        Calculate output of the second order IIR filter
        :param input: single instance value
        :return: filtered value
        """
        in_sum = input - self.a1 * self.buffer_m1 - self.a2 * self.buffer_m2
        out_sum = self.b0 * in_sum + self.b1 * self.buffer_m1 + self.b2 * self.buffer_m2
        self.buffer_m2 = self.buffer_m1
        self.buffer_m1 = in_sum
        return out_sum

    @staticmethod
    def notch(f, r):
        b0, b1, b2= 1, -2 * np.cos(2*np.pi*f), 1
        a0, a1, a2 = 1,  -2 * r* np.cos(2*np.pi*f), r*r
        return a0, a1, a2, b0, b1, b2


def return_filter():
    """ Return chain of three second order IIR filter for accelerometer data"""
    freq = 2.5 / 50
    try:
        from scipy import signal
        sos = signal.cheby2(6, 40, freq * 2, output='sos')
    except ModuleNotFoundError:
        sos = np.array([[0.00919895, -0.00837274,  0.00919895,  1., -1.49146173, 0.56295521],
                        [1., -1.80890255,  1.,  1., -1.68684556, 0.74404189],
                        [1., -1.89526908,  1.,  1., -1.87056254, 0.91962919]])
    my_factory = IIRFilter(sos)
    return my_factory


if __name__ == "__main__":
    from scipy import signal
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
    freq = 5 / 50
    sos = signal.cheby2(6, 40, freq*2, output='sos')

    my_iir = IIR2Filter(sos[0, :3], sos[0, 3:])
    my_factory = IIRFilter(sos)

    out = [my_factory.filter(x) for x in data]
    scalar = np.mean(out[1000:-1000]) / np.mean(data[1000:-1000])
    out_mod = [x/scalar for x in out]
    filtered = signal.sosfilt(sos, data)


    plt.plot(out_mod, label=f'freq = {freq}')
    plt.legend()

    plt.plot(data, label='row')
    plt.legend()
    print('end')

