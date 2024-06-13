import numpy as np
import pandas as pd
from scipy.signal import find_peaks, savgol_filter
import matplotlib.pyplot as plt
from brainflow.data_filter import DataFilter, FilterTypes, NoiseTypes, AggOperations, DetrendOperations, WindowOperations
from brainflow.board_shim import BoardShim, BoardIds

np.set_printoptions(suppress=True, precision=6, threshold=np.inf)
bandpass_low_limit = 0.5
bandpass_high_limit = 40.0
sampling_rate = BoardShim.get_sampling_rate(BoardIds.GANGLION_BOARD.value)
peak_treshold = 15

def main():
    # Read .csv data file and get sampling rate
    test_name = "Justi-TA-3.1"
    data_file = f"../official-tests/{test_name}(unfiltered).csv"
    data = DataFilter.read_file(data_file)
    data_ch1 = data[1]
    
    # Bandwidth limits recommended for the OpenBCI Ganglion Board
    # https://openbci.com/forum/index.php?p=/discussion/3858/emg-bandwidth-to-calculate-shannon-hartley-theorem#latest
    bandwidth = bandpass_high_limit - bandpass_low_limit
    print("Bandwidth: %.2f\n" % bandwidth)
    
    # Plot the original signal
    min_value, max_value = min(data_ch1), max(data_ch1)
    plt.figure()
    pd.DataFrame(data_ch1).plot(legend=False)
    plt.xlabel('Nº Sample')
    plt.ylabel('Amplitude (μV)')
    plt.xlim(0, len(data_ch1))
    plt.ylim(min_value, max_value)
    plt.savefig('original_signal.png')

    # First filtering step of original signal
    # https://la.mathworks.com/help/signal/ug/peak-analysis.html
    DataFilter.perform_rolling_filter(data_ch1, 2, AggOperations.MEAN.value)
    DataFilter.detrend(data_ch1, DetrendOperations.CONSTANT.value)
    DataFilter.perform_bandpass(data_ch1, sampling_rate, bandpass_low_limit, bandpass_high_limit, 7, FilterTypes.BUTTERWORTH_ZERO_PHASE, 0)
    DataFilter.remove_environmental_noise(data_ch1, sampling_rate, NoiseTypes.FIFTY.value)
    savgol_filter(data_ch1, 20, 5)

    # Plot the signal after filtering
    plt.figure()
    pd.DataFrame(data_ch1).plot(legend=False)
    plt.xlabel('Nº Sample')
    plt.ylabel('Amplitude (μV)')
    plt.xlim(0, len(data_ch1))
    plt.ylim(min_value, max_value)
    plt.savefig('filtered_signal.png')
    
    # Plot the FFT signal
    plot_fft(data_ch1, 1, 200)

    # Calculate the channel capacity using Shannon–Hartley theorem
    SNR = calculate_snr(data_ch1)
    channel_capacity = calculate_channel_capacity(bandwidth, SNR)

    print("\nChannel Capacity: %.3f bps" % channel_capacity)


def calculate_snr(data):
    # Find peaks in signal
    positive_peaks, _ = find_peaks(data, height=(peak_treshold, None))
    negative_peaks, _ = find_peaks(-data, height=(peak_treshold, None))
    peaks = np.concatenate((positive_peaks, negative_peaks))
    
    # Plot peaks found in signal
    plt.figure()
    plt.plot(data)
    plt.xlabel('Nº Sample')
    plt.ylabel('Amplitude (μV)')
    plt.plot(positive_peaks, data[positive_peaks], "x", label="positive")
    plt.plot(negative_peaks, data[negative_peaks], "x", label="negative")
    plt.plot(np.zeros_like(data), "--", color="gray")
    plt.legend(loc="upper right")
    plt.xlim(0, len(data))
    plt.ylim(auto=True)
    plt.savefig("peaks.png")

    # Boolean peaks mask
    mask = np.ones(len(data), dtype=bool)
    mask[peaks] = False
    plt.figure()
    plt.plot(~mask)
    plt.xlabel('Nº Sample')
    plt.ylabel('Value')
    plt.xlim(0, len(mask))
    plt.yticks([True, False], ["Peak", "No Peak"])
    plt.ylim(False,True)
    plt.savefig('mask.png')

    # Get noisy signal after excluding peaks
    min_peak = np.min(abs(data[peaks]))
    print("Max Noise Amplitude: %.3f μV" % min_peak)
    no_peaks = data[mask]
    noise = (no_peaks < min_peak) & (no_peaks > -min_peak)
    noise_signal = no_peaks[noise]
    plt.figure()
    plt.plot(noise_signal)
    plt.xlim(0, len(noise_signal))
    plt.ylim(-400, 400)
    plt.xlabel('Nº Sample')
    plt.ylabel('Amplitude (μV)')
    plt.savefig('noise_signal.png')

    # Calculate SNR (expressed as a linear power ratio, not as logarithmic decibels)
    # https://en.wikipedia.org/wiki/Shannon%E2%80%93Hartley_theorem
    nfft = DataFilter.get_nearest_power_of_two(sampling_rate)
    psd_s = DataFilter.get_psd_welch(data[peaks], nfft, nfft // 2, sampling_rate,
                                   WindowOperations.BLACKMAN_HARRIS.value)
    psd_n = DataFilter.get_psd_welch(noise_signal, nfft, nfft // 2, sampling_rate,
                                   WindowOperations.BLACKMAN_HARRIS.value)
    Ps = DataFilter.get_band_power(psd_s, bandpass_low_limit, bandpass_high_limit)
    Pn = DataFilter.get_band_power(psd_n, bandpass_low_limit, bandpass_high_limit)
    SNR = Ps/Pn
    logSNR = 10*np.log10(Ps/Pn) # SNR in logarithmic decibels for printing
    
    print("Signal Power: %.3f μW" % Ps)
    print("Noise Power: %.3f μW" % Pn)
    print("SNR: %.3f dB" % logSNR)
    
    return SNR


def calculate_channel_capacity(bandwidth, snr):
    return bandwidth * np.log2(1 + snr)


def plot_fft(data, channel, sampling_rate):
    # Calculate FFT values
    fft_data = np.fft.fft(data)
    magnitude = np.abs(fft_data)

    # Generate the frequency axis
    N = len(fft_data)
    T = 1 / sampling_rate
    freq = np.fft.fftfreq(N, T)

    # Filter positive frequencies
    positive_freq = freq[(freq > 0)]
    positive_mag = magnitude[(freq > 0)]

    # Find the index where xx% of the signal is accumulated
    # acc_percentage = 0.99
    # sorted_mag = np.sort(positive_mag)[::-1]  # Sort magnitudes in descending order
    # cum_sum = np.cumsum(sorted_mag)  # Compute cumulative sum
    # threshold = acc_percentage * cum_sum[-1]
    # index = np.searchsorted(cum_sum, threshold)  # Find the index where cumulative sum exceeds the threshold

    # Plot the FFT result
    plt.figure(figsize=(10, 5))
    plt.plot(positive_freq, positive_mag, linestyle='-', linewidth=1)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude (μV)')
    plt.xlim(0, auto=True)
    plt.ylim(0, auto=True)
    plt.title('FFT Channel %d Plot' % channel)
    plt.grid(True)

    # Annotate the % accumulation point with its frequency
    # bandwidth = positive_freq[index]
    # plt.annotate(f'{int(acc_percentage*100)}% Accumulation\n{sorted_mag[index]:.2f} μV\n{bandwidth:.2f} Hz',
    #              xy=(bandwidth, sorted_mag[index]),
    #              xytext=(bandwidth + 5, sorted_mag[index]),
    #              arrowprops=dict(facecolor='red', arrowstyle='->'),
    #              bbox=dict(facecolor='white', alpha=0.5))
    
    plt.savefig('fft.png')

if __name__ == "__main__":
    main()

