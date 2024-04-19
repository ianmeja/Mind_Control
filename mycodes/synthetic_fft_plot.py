import time

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, WindowOperations, AggOperations, NoiseTypes, DetrendOperations

def plot_timeseries(data, emg_channels, sampling_rate, file_name):
    # Convert it to pandas DF
    df = pd.DataFrame(np.transpose(data))
    
    # Calculate time axis based on sampling rate and store emg_channels for this board
    time_axis = np.arange(len(df)) / sampling_rate
    
    # Plot the EMG signals with time on the x-axis
    plt.figure()
    df.index = time_axis  # Set the time as the index
    axes = df[emg_channels].plot(subplots=True)
    for ax in axes:
        #y_min = ax.get_lines()[0].get_ydata().min()
        #y_max = ax.get_lines()[0].get_ydata().max()
        #ax.set_ylim(y_min - abs(y_min)*0.1, y_max + abs(y_max)*0.1)  # Set y-axis limits based on the entire dataframe
        ax.grid(True)
        ax.set_ylabel('Amplitude (μV)')
    plt.xlabel('Time (s)')
    #plt.ylabel('Amplitude (μV)')
    plt.grid(True)
    plt.savefig(file_name)
    
def plot_fft(data, channel, sampling_rate):
    fft_data = np.fft.fft(data)
    
    # Compute the magnitudes of the FFT result
    magnitude = np.abs(fft_data)
    
    # Generate the frequency axis
    N = len(fft_data)
    T = 1/sampling_rate
    freq = np.fft.fftfreq(N, T)
    
    # Filter frequencies and amplitudes above 0
    positive_freq = freq[(freq > 0) & (magnitude > 0)]
    positive_mag = magnitude[(freq > 0) & (magnitude > 0)]
    
    # Filter frequencies and amplitudes above M uV
    M = 10000
    marked_freq = freq[magnitude > M]
    marked_mag = magnitude[magnitude > M]

    # Plot the FFT result
    plt.figure(figsize=(10, 5))
    plt.plot(positive_freq, positive_mag, linestyle='-', linewidth=1)
    plt.scatter(marked_freq, marked_mag, marker='o')  # Plot markers for positive amplitudes
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude (μV)')
    
    # This is to enable logaritmic scale
    #plt.yscale('log')
    #plt.yticks([0.1, 1, 10, 100, 1000], ['0.1', '1', '10', '100', '1000'])
    
    # Set the x-axis limit to 0-100 Hz and the y-axis limit to auto
    plt.xlim(0, 100)
    plt.ylim(0, auto=True)
    plt.title('FFT Channel %d Plot' % channel)
    plt.grid(True)

    # Annotate the most powerful frequencies with their amplitudes
    for f, mag in zip(marked_freq, marked_mag):
        plt.annotate(f'{f:.2f} Hz\n{mag:.2f} μV', xy=(f, mag), xytext=(f + 5, mag),
                    arrowprops=dict(facecolor='black', arrowstyle='->'), bbox=dict(facecolor='white', alpha=0.5))
    
    # Save the plot
    #plt.savefig('fft_channel_%d.png' % channel) 
    

def main():
    BoardShim.enable_dev_board_logger()

    # use synthetic board for demo
    params = BrainFlowInputParams()
    board_id = BoardIds.SYNTHETIC_BOARD.value
    board = BoardShim(board_id, params)
    
    sampling_rate = board.get_sampling_rate(board_id)
    window_size = 4
    num_points = window_size * sampling_rate
    board.prepare_session()
    board.start_stream()
    BoardShim.log_message(LogLevels.LEVEL_INFO.value, 'start sleeping in the main thread')
    time.sleep(10)
    data = board.get_current_board_data(num_points)
    board.stop_stream()
    board.release_session()

    emg_channels = [1,2,3,4]
    print('Sampling Rate: %d' % sampling_rate)
    print('Num of Samples: %d' % num_points)
    print('Len of Data: %d' % len(data[1]))
    
    plot_timeseries(data, emg_channels, sampling_rate, 'original_signals.png')

    for channel in emg_channels:
        # Detrend the signal by removing the mean
        DataFilter.perform_rolling_filter(data[channel], 2, AggOperations.MEAN.value)
        DataFilter.detrend(data[channel], DetrendOperations.LINEAR.value)

        # Denoise data
        DataFilter.remove_environmental_noise(data[channel], sampling_rate, NoiseTypes.FIFTY_AND_SIXTY)
        
        plot_fft(data[channel], channel, sampling_rate)
        
        #psd = DataFilter.get_psd_welch(data[channel], num_points, num_points // 2, sampling_rate,
        #                           WindowOperations.BLACKMAN_HARRIS.value)

        #band_power_delta = DataFilter.get_band_power(psd, 1.0, 4.0)
        #band_power_theta = DataFilter.get_band_power(psd, 4.0, 8.0)
        #band_power_alpha = DataFilter.get_band_power(psd, 8.0, 13.0)
        #band_power_beta = DataFilter.get_band_power(psd, 13.0, 30.0)
        #print('Delta: %.6f Theta: %.6f Alfa: %.6f     Beta: %.6f' % (band_power_delta, band_power_theta, band_power_alpha, band_power_beta))
        
    plot_timeseries(data, emg_channels, sampling_rate, 'processed_signals.png')


if __name__ == "__main__":
    main()