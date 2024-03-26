import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt


def main():
    input_txt_file = '../utils/testFeb.txt'
    output_csv_file = '../utils/output.csv'

    process_file(input_txt_file, output_csv_file)

    channels = ['EXG Channel 0', 'EXG Channel 1', 'EXG Channel 2', 'EXG Channel 3']
    signal = load_signal(output_csv_file, channels)
    channel_0 = signal['EXG Channel 0']
    channel_1 = signal['EXG Channel 1']
    channel_2 = signal['EXG Channel 2']
    channel_3 = signal['EXG Channel 3']
    print("channel_1:", channel_1)

    SNR = calculate_snr(output_csv_file)
    b = calculate_bandwidth(channel_1)
    print("Data Rate =", calculate_data_rate(b, SNR))


def process_file(input_file, output_file):
    # Lectura del archivo TXT y escritura en CSV
    with open(input_file, 'r') as file:
        lines = [line.strip() for line in file.readlines() if not line.startswith('%')]

    header = lines[0].split(', ')
    data_lines = [line.split(', ') for line in lines[1:]]
    df = pd.DataFrame(data_lines, columns=header)

    df.to_csv(output_file, index=False)


def load_signal(csv_file, channels):
    data = pd.read_csv(csv_file)
    signal = {}
    for channel in channels:
        signal[channel] = data[channel].values
    return signal


def calculate_snr(csv_file):
    df = pd.read_csv(csv_file)
    channels = ['EXG Channel 0', 'EXG Channel 1', 'EXG Channel 2', 'EXG Channel 3']
    df = df[channels]
    signal = df.to_numpy().flatten().astype(float)

    # señal
   # plt.figure(figsize=(10, 6))
   # plt.plot(signal)
   # plt.show()

    peaks, _ = find_peaks(signal)
    print("Posición de los picos:", peaks)

    # Desvío estándar de los picos
    peak_std = np.std(signal[peaks])

    # Array booleano donde picos = False
    mask = np.ones(len(signal), dtype=bool)
    mask[peaks] = False

    # Desvío estándar de la señal excluyendo los picos (ruido)
    noise_signal = signal[mask]
    noise_signal_std = np.std(noise_signal)

    # Desvío estándar de la señal entera
    signal_std = np.std(signal)

    SNR = signal_std / noise_signal_std

    print("Desvío estándar de los picos:", peak_std)
    print("Desvío estándar de la señal:", signal_std)
    print("Desvío estándar del ruido:", noise_signal_std)
    print("SNR:", SNR)
    return SNR


def calculate_bandwidth(signal):
    # TODO hacer con un solo canal!
    # Aplicar la Transformada de Fourier (FFT) a la señal
    fft_signal = np.fft.fft(signal)
    freq = np.fft.fftfreq(len(signal), 1/200)
    print("fft =", fft_signal)
    print("freq =", freq)

    # potencia espectral
    spectral_power = np.abs(fft_signal) ** 2

    # Ordenar los índices de frecuencia según la potencia espectral
    sorted_indices = np.argsort(spectral_power)[::-1]

    # Calcular el índice que representa el 95% de la señal
    total_power = np.sum(spectral_power)
    cumulative_power = 0
    index_95_percent = 0
    for i in range(len(sorted_indices)):
        cumulative_power += spectral_power[sorted_indices[i]]
        if cumulative_power >= 0.95 * total_power:
            index_95_percent = i
            break

    # Frecuencias que representan el 95% de la señal
    frequencies_95_percent = freq[sorted_indices[:index_95_percent]]

    bandwidth = frequencies_95_percent[-1] - frequencies_95_percent[0]
    print("B =", bandwidth)
    return bandwidth


def calculate_data_rate(bandwidth, snr):
    data_rate = bandwidth * np.log2(1 + snr)
    return data_rate


if __name__ == "__main__":
    main()

