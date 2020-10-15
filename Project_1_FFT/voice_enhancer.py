from scipy.io.wavfile import read as read_wav
from scipy.io.wavfile import write as write_wav
from scipy.fft import fft, ifft
import matplotlib.pyplot as plt
import numpy as np


def main():
    #audio_file = r'original.wav'
    audio_file = r'original2.wav'
    #audio_file = r'vowel.wav'
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
    plt.ylabel('Intensity: |FFT()| [-]')

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
    plt.ylabel('Intensity: |FFT()| [-]')
    plt.title('improved.wav')

    improved = ifft(new_fft_y).real #/ scalar_factor
    improved = improved.astype(np.int16)

    plt.subplot(4, 1, 4)
    plt.plot(T, improved)
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude [-]')

    write_wav("improved.wav", rate, improved)
    ex_3_supporting(fft_x, fft_y)
    ex_3_supporting_vowels(fft_x, fft_y)
    ex_3_supporting_artifacts(fft_x, fft_y)
    pass


def ex_3_supporting_vowels(fft_x, fft_y, fundamentals=[101, 130, 167, 228], number_of_harmonics=[5, 5, 5, 4]):
    """
     show spectrum with predefined fundamentals and harmonics
    """
    new_fft_y = fft_y.copy()
    window_size = 100
    for i in range(len(new_fft_y)-window_size):
        new_fft_y[i] = new_fft_y[i:i+window_size].mean()
    plt.plot(fft_x[:3000:20], abs(new_fft_y[:3000:20]), 'r-', label='fft')

    colors = 'bgcmykw'
    ver_line = [max(abs(new_fft_y)) * 0.5, min(abs(new_fft_y))]
    for id, (fund_, harmo_no) in enumerate(zip(fundamentals, number_of_harmonics)):
        plt.plot([fund_] * 2, ver_line, f'{colors[id]}-', label=f'fundamental {fund_} Hz + harmonics', alpha=0.5)
        for harm_id in range(2, harmo_no):
            plt.plot([harm_id * fund_] * 2, ver_line, f'{colors[id]}-', alpha=0.5)
    plt.legend()
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Intensity: |FFT()| [-]')
    plt.savefig("vowels_fundamentals.svg")


def ex_3_supporting(fft_x, fft_y):
    """
     show spectrum with predefined fundamentals and harmonics
    """
    new_fft_y = fft_y.copy()
    window_size = 100
    for i in range(len(new_fft_y)-window_size):
        new_fft_y[i] = new_fft_y[i:i+window_size].mean()
    plt.plot(fft_x[:16000:20], abs(new_fft_y[:16000:20]), 'r-', label='fft')

    plt.legend()
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Intensity: |FFT()| [-]')
    plt.savefig("vowels_consonants.svg")


def ex_3_supporting_artifacts(fft_x, fft_y):
    """
     show spectrum with predefined fundamentals and harmonics
    """
    new_fft_y = fft_y.copy()
    window_size = 100
    for i in range(len(new_fft_y)-window_size):
        new_fft_y[i] = new_fft_y[i:i+window_size].mean()
    plt.plot(fft_x[:len(fft_x)//2:20], abs(new_fft_y[:len(fft_x)//2:20]), 'r-', label='fft')

    plt.legend()
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Intensity: |FFT()| [-]')
    plt.savefig("vowels_filtered.svg")




if __name__ == "__main__":
    main()
