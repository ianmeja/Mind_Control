import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# Read the txt file into a DataFrame
input_txt_file = './files/OpenBCI4.txt'
output_csv_file = './files/output4.csv'

with open(input_txt_file, 'r') as file:
    lines = [line.strip() for line in file.readlines() if not line.startswith('%')]

header = lines[0].split(', ')
data_lines = [line.split(', ') for line in lines[1:]]
df = pd.DataFrame(data_lines, columns=header)

# Save the DataFrame to a CSV file
df.to_csv(output_csv_file, index=False)

# Convert columns to numeric (if needed)
channels = ['EXG Channel 0', 'EXG Channel 1', 'EXG Channel 2', 'EXG Channel 3']
df[channels] = df[channels].apply(pd.to_numeric)

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
