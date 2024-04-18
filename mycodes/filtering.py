import time
import numpy as np
import pandas as pd

from plotting import plot_timeseries
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, AggOperations, DetrendOperations, NoiseTypes, FilterTypes

def main():
    data = DataFilter.read_file('prueba2.csv')
    sampling_rate = BoardShim.get_sampling_rate(BoardIds.GANGLION_BOARD)
    emg_channels = [1,2,3,4]
    
    plot_timeseries(data, emg_channels, sampling_rate, 'before_processing')
    
    for channel in emg_channels:
        # Detrend the signal by removing the mean
        #DataFilter.perform_rolling_filter(data[channel], 2, AggOperations.MEAN.value)
        #DataFilter.detrend(data[channel], DetrendOperations.LINEAR.value)

        #Denoise data
        DataFilter.remove_environmental_noise(data[channel], sampling_rate, NoiseTypes.FIFTY_AND_SIXTY)

        # Remove ECG artifacts
        DataFilter.perform_bandpass(data[channel], sampling_rate, 4, 7, 4, FilterTypes.BUTTERWORTH, 0) # notch
        
    plot_timeseries(data, emg_channels, sampling_rate, 'after_processing')
    bands = DataFilter.get_avg_band_powers

if __name__ == "__main__":
    main()