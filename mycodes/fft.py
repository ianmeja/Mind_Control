import time
import argparse
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, DetrendOperations, FilterTypes, NoiseTypes, AggOperations, WindowOperations

def plot_timeseries(data, emg_channels, sample_rate, file_name):
    # Convert it to pandas DF
    df = pd.DataFrame(np.transpose(data))
    
    # Calculate time axis based on sampling rate and store emg_channels for this board
    time_axis = np.arange(len(df)) / sample_rate
    
    # Plot the EMG signals with time on the x-axis
    plt.figure()
    df.index = time_axis  # Set the time as the index
    axes = df[emg_channels].plot(subplots=True)
    for ax in axes:
        ax.grid(True)
        ax.set_ylabel('Amplitude (μV)')
    plt.xlabel('Time (s)')
    #plt.ylabel('Amplitude (μV)')
    plt.grid(True)
    plt.savefig(file_name)
    
def plot_fft(data, channel, sampling_rate, file_name):
    fft_data = DataFilter.perform_fft(data, WindowOperations.NO_WINDOW.value)

    # Compute the magnitudes of the FFT result
    magnitude = np.abs(fft_data)

    # Generate the frequency axis
    N = len(fft_data)
    freq = np.fft.fftfreq(N, d=1/sampling_rate)
    
    # Filter frequencies and amplitudes
    positive_freq = freq[(freq > 0) & (freq < 50) & (magnitude > 0)]
    positive_mag = magnitude[(freq > 0) & (freq < 50) & (magnitude > 0)]
    
    # Filter frequencies and amplitudes above 30% of max value
    #max_mag = magnitude.max()
    #marked_freq = freq[magnitude > max_mag*0.5]
    #marked_mag = magnitude[magnitude > max_mag*0.5]
    
    # Find the three most powerful frequencies and their amplitudes
    marked_indices = np.argsort(positive_mag)[-3:]
    marked_freq = positive_freq[marked_indices]
    marked_mag = positive_mag[marked_indices]

    # Plot the FFT result
    plt.figure(figsize=(10, 5))
    plt.plot(positive_freq, positive_mag, linestyle='-', linewidth=1)
    plt.scatter(marked_freq, marked_mag, marker='o')  # Plot markers for positive amplitudes
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude (μV)')
    # Set the x-axis limit to 0-100 Hz and the y-axis limit to auto
    plt.xlim(0, 50)
    plt.ylim(0, auto=True)
    plt.title('FFT Channel %d Plot' % channel)
    plt.grid(True)

    # Annotate the three most powerful frequencies with their amplitudes
    for f, mag in zip(marked_freq, marked_mag):
        plt.annotate(f'{f:.2f} Hz\n{mag:.2f} μV', xy=(f, mag), xytext=(f + 5, mag),
                    arrowprops=dict(facecolor='black', arrowstyle='->'), bbox=dict(facecolor='white', alpha=0.5))
    
    plt.savefig(file_name + '_fft_channel_%d.png' % channel)
    
    
def main():
    parser = argparse.ArgumentParser ()

    # use docs to check which parameters are required for specific board, e.g. for Cyton - set serial port
    parser.add_argument ('--timeout', type = int, help  = 'timeout for device discovery or connection', required = False, default = 15)
    parser.add_argument ('--ip-port', type = int, help  = 'ip port', required = False, default = 0)
    parser.add_argument ('--ip-protocol', type = int, help  = 'ip protocol, check IpProtocolType enum', required = False, default = 0)
    parser.add_argument ('--ip-address', type = str, help  = 'ip address', required = False, default = '')
    parser.add_argument ('--serial-port', type = str, help  = 'serial port', required = False, default = '/dev/cu.usbmodem11')
    parser.add_argument ('--mac-address', type = str, help  = 'mac address', required = False, default = '')
    parser.add_argument ('--other-info', type = str, help  = 'other info', required = False, default = '')
    parser.add_argument ('--streamer-params', type = str, help  = 'streamer params', required = False, default = '')
    parser.add_argument ('--serial-number', type = str, help  = 'serial number', required = False, default = '')
    parser.add_argument ('--board-id', type = int, help  = 'board id, check docs to get a list of supported boards', required = False, default = BoardIds.GANGLION_BOARD)
    parser.add_argument ('--file', type=str, help='file', required=False, default='')
    parser.add_argument ('--master-board', type=int, help='master board id for streaming and playback boards', required=False, default=BoardIds.NO_BOARD)
    parser.add_argument ('--log', action = 'store_true')
    parser.add_argument ('--file-name', type = str, help = 'file name for recorded data', required = False, default = 'default')
    args = parser.parse_args ()

    params = BrainFlowInputParams()
    params.ip_port = args.ip_port
    params.serial_port = args.serial_port
    params.mac_address = args.mac_address
    params.other_info = args.other_info
    params.serial_number = args.serial_number
    params.ip_address = args.ip_address
    params.ip_protocol = args.ip_protocol
    params.timeout = args.timeout
    params.file = args.file
    params.master_board = args.master_board

    if (args.log):
        BoardShim.enable_dev_board_logger()
    else:
        BoardShim.disable_board_logger()

    board = BoardShim(args.board_id, params)
    board.prepare_session()
    board.start_stream(45000, args.streamer_params)
    
    print("Starting...")
    for i in range(5):
        print(5-i)
        time.sleep(1)
    aux = board.get_board_data # Empty data buffer

    print("Relax")
    time.sleep(5)
    
    print("Move")
    time.sleep(5)
    
    print("Stop")
    time.sleep(0.25)

    data = board.get_current_board_data(2048)
    
    board.stop_stream()
    board.release_session()
    print("Session ended.")
    
    # Sava data from session for later access
    DataFilter.write_file(data, args.file_name + '.csv', 'w')

    emg_channels = BoardShim.get_emg_channels(args.board_id)
    sampling_rate = BoardShim.get_sampling_rate(args.board_id)
    print("EMG channels:", emg_channels)
    print("Sampling rate:", sampling_rate)
    
    plot_timeseries(data, emg_channels, sampling_rate, args.file_name + '_original_signals.png')

    for channel in emg_channels:
        # Detrend the signal by removing the mean
        DataFilter.perform_rolling_filter(data[channel], 2, AggOperations.MEAN.value)
        DataFilter.detrend(data[channel], DetrendOperations.LINEAR.value)

        #Denoise data
        DataFilter.remove_environmental_noise(data[channel], sampling_rate, NoiseTypes.FIFTY_AND_SIXTY)
        DataFilter.perform_highpass(data[channel], sampling_rate, 10, 4, FilterTypes.BUTTERWORTH, 0)

        # Remove ECG artifacts
        DataFilter.perform_bandstop(data[channel], sampling_rate, 0.5, 1.5, 4, FilterTypes.BUTTERWORTH_ZERO_PHASE, 0) # notch
        
        # Calculate FFT on the detrended signal, len of data must be a power of 2 (256 in this case)
        first_array = data[channel][:1024]
        second_array = data[channel][1024:]
        plot_fft(first_array, channel, sampling_rate, args.file_name + '_relax')
        plot_fft(second_array, channel, sampling_rate, args.file_name + '_move')

    plot_timeseries(data, emg_channels, sampling_rate, args.file_name + '_processed_signals.png')
    
    bands = DataFilter.get_avg_band_powers(data, emg_channels, sampling_rate, False)
    print(bands)
    


if __name__ == "__main__":
    main()