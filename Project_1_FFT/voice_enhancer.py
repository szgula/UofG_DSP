from scipy.io.wavfile import read as read_wav
from scipy.io.wavfile import write as write_wav
from scipy.fft import fft, ifft
import matplotlib.pyplot as plt
import numpy as np


def main():
    #audio_file = r'original.wav'
    audio_file = r'original2.wav'
    rate, samples_numpy = read_wav(audio_file)

    single_channel = samples_numpy[:, 0]
    N = len(single_channel)
    T = np.linspace(0, N / rate, N)

    plt.subplot(4, 1, 1)
    plt.plot(T, single_channel)
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude [-]')
    plt.title('original.wav')

    fft_y = fft(single_channel)
    fft_x = np.linspace(0, rate, len(fft_y))

    plt.subplot(4, 1, 2)
    plt.plot(fft_x[:len(fft_x)//2], abs(fft_y[:len(fft_x)//2]))
    #plt.semilogy(fft_x[:len(fft_x)//2], abs(fft_y[:len(fft_x)//2]))
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Intensity: |FFT(time_signal)| [-]')

    # Question: should we increase the whole voice spectrum or just peaks?
    # iterate over regions to modify
    new_fft_y = fft_y.copy()
    for lower_freq_, upper_fred_, scalar_factor in ((85, 250, 1.25), (6000, 10000, 10.0)):
        x_low = abs((fft_x - lower_freq_)).argmin()
        x_upp = abs((fft_x - upper_fred_)).argmin()
        new_fft_y[x_low:x_upp+1] *= scalar_factor
        new_fft_y[N - x_upp:N - x_low+1] *= scalar_factor

    plt.subplot(4, 1, 3)
    plt.plot(fft_x[:len(fft_x)//2], abs(new_fft_y[:len(fft_x)//2]))
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Intensity: |FFT(time_signal)| [-]')
    plt.title('improved.wav')

    improved = ifft(new_fft_y).real #/ scalar_factor
    improved = improved.astype(np.int16)

    plt.subplot(4, 1, 4)
    plt.plot(T, improved)
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude [-]')

    write_wav("improved.wav", rate, improved)


if __name__ == "__main__":
    main()
