from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

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