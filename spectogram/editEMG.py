import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

# Read the BrainFlow CSV file
data = np.genfromtxt('files/brainflow5_changes.csv', delimiter='\t', skip_header=14)

# Extract the audio signal from the file
audio_signal = data[:, 1]

# Sampling rate (assuming it's constant throughout the signal)
sampling_rate = 1 / (data[1, 0] - data[0, 0])

# Time points
time_points = np.arange(len(audio_signal)) / sampling_rate

start_time = 0  # seconds
duration = 2000  # seconds
frequency = 0.001  # Hz

start_index = int(start_time * sampling_rate)
end_index = int((start_time + duration) * sampling_rate)

# Create a sine wave
t = np.linspace(0, duration, end_index - start_index)
sine_wave = np.sin(2 * np.pi * frequency * t)

# Add the sine wave to the audio signal
audio_signal[start_index:end_index] += sine_wave

# Write the modified signal to a WAV file
wavfile.write('modified_audio.wav', int(sampling_rate), audio_signal.astype(np.int16))

# Plot the spectrogram
plt.specgram(audio_signal, Fs=int(sampling_rate))
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.title('Spectrogram of Modified Audio')
plt.colorbar(label='Intensity (dB)')
plt.show()