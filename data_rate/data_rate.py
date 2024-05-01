import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from brainflow.data_filter import DataFilter


def main():
    data_file = "../official-tests/" + input("File path:")

    np.set_printoptions(suppress=True, precision=6)     # para que no aparezca el exponencial

    data = DataFilter.read_file(data_file)
    channel_1 = data[1]

    # Plot
    bandwidth = plot_fft(channel_1, 1, 200)
    #bandwidth = 9.7
    print("Bandwidth: %f" % bandwidth)

    SNR = calculate_snr(channel_1)
    channel_capacity = calculate_channel_capacity(bandwidth, SNR)
    
    print("\nChannel Capacity: %.5f bps" % channel_capacity)


def calculate_snr(channel):

    peaks, _ = find_peaks(channel)
    # print("Posición de los picos:", peaks)

    # Desvío estándar de los picos
    peak_std = np.std(channel[peaks])

    # Array booleano donde picos = False
    mask = np.ones(len(channel), dtype=bool)
    mask[peaks] = False

    # Desvío estándar de la señal excluyendo los picos (ruido)
    noise_signal = channel[mask]
    noise_signal_std = np.std(noise_signal)

    # Desvío estándar de la señal entera
    signal_std = np.std(channel)

    SNR = signal_std / noise_signal_std

    print("Desvío estándar de los picos: %.5f" % peak_std)
    print("Desvío estándar de la señal: %.5f" % signal_std)
    print("Desvío estándar del ruido: %.5f" % noise_signal_std)
    print("SNR: %.5f" % SNR)
    return SNR


def calculate_channel_capacity(bandwidth, snr):
    return bandwidth * np.log2(1 + snr)


def plot_fft(data, channel, sampling_rate):
    fft_data = np.fft.fft(data)

    # Compute the magnitudes of the FFT result
    magnitude = np.abs(fft_data)

    # Generate the frequency axis
    N = len(fft_data)
    T = 1 / sampling_rate
    freq = np.fft.fftfreq(N, T)

    # Filter frequencies and amplitudes above 0
    positive_freq = freq[(freq > 0) & (magnitude > 0)]
    positive_mag = magnitude[(freq > 0) & (magnitude > 0)]

    # Find the index where xx% of the signal is accumulated
    acc_percentage = 0.75
    sorted_mag = np.sort(positive_mag)[::-1]  # Sort magnitudes in descending order
    cum_sum = np.cumsum(sorted_mag)  # Compute cumulative sum
    threshold = acc_percentage * cum_sum[-1]
    index = np.searchsorted(cum_sum, threshold)  # Find the index where cumulative sum exceeds the threshold

    # Plot the FFT result
    plt.figure(figsize=(10, 5))
    plt.plot(positive_freq, positive_mag, linestyle='-', linewidth=1)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude (μV)')

    # Set the x-axis limit to 0-100 Hz and the y-axis limit to auto
    plt.xlim(0, 100)
    plt.ylim(0, auto=True)
    plt.title('FFT Channel %d Plot' % channel)
    plt.grid(True)

    bandwidth = positive_freq[index]

    # Annotate the % accumulation point with its frequency
    plt.annotate(f'{acc_percentage*100}% Accumulation\n{sorted_mag[index]:.2f} μV\n{bandwidth:.2f} Hz',
                 xy=(bandwidth, sorted_mag[index]),
                 xytext=(bandwidth + 5, sorted_mag[index]),
                 arrowprops=dict(facecolor='red', arrowstyle='->'),
                 bbox=dict(facecolor='white', alpha=0.5))
    # Save the plot
    plt.savefig('fft_channel_%d_2_2.png' % channel)
    
    return bandwidth


if __name__ == "__main__":
    main()

