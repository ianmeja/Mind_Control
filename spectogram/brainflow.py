import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# Specify your input and output file paths
input_file_path = './files/brainflow5.csv'
output_file_path = './files/output5.csv'

# Specify the header for the columns
column_header = ['Sample Index', 'EXG Channel 0', 'EXG Channel 1', 'EXG Channel 2', 'EXG Channel 3', 'Accel Channel 0', 'Accel Channel 1', 'Accel Channel 2', 'Other', 'Other', 'Other', 'Other', 'Other', 'Timestamp', 'Other']
# Read the CSV file into a DataFrame, skipping the first 14 rows
df = pd.read_csv(input_file_path, delimiter='\t', skiprows=13)

# Add the specified header
df.columns = column_header

# Write the DataFrame to a new CSV file
df.to_csv(output_file_path, index=False, sep='\t')

df.to_csv(output_file_path, index=False)

# Convert columns to numeric (if needed)
channels = ['EXG Channel 0', 'EXG Channel 1', 'EXG Channel 2', 'EXG Channel 3']

# Configuration parameters
fs = 200  # Sampling rate in Hz
nperseg = 256  # Window size
noverlap = nperseg // 2  # Overlap between windows

# Calculate and show the spectrogram for each channel
for channel in channels:
    f, t, Sxx = signal.spectrogram(df[channel], fs, nperseg=nperseg, noverlap=noverlap)
    plt.figure(figsize=(10, 6))
    plt.pcolormesh(t, f, 10 * np.log10(Sxx), shading='auto')
    plt.colorbar(label='Power (dB)')
    plt.title(f'Spectrogram - {channel}')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.tight_layout()
    plt.show()