import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt


def main():
    output_csv_file = '../utils/data_rate_2.csv'

    np.set_printoptions(suppress=True, precision=6)     # para que no aparezca el exponencial

    signal = load_signal(output_csv_file)
    channel_0 = signal[:, 1]
    # channel_1 = signal[:, 2]
    # channel_2 = signal[:, 3]
    # channel_3 = signal[:, 4]
    # print("channel_0:", channel_0)

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(channel_0)
    plt.title('EMG Signal Over Time - Channel 0')
    plt.show()

    SNR = calculate_snr(channel_0)
    b1 = calculate_bandwidth(channel_0)
    b2 = calcular_ancho_banda(channel_0)
    # TODO Hernan dijo de agarrarlo del UI
    print("Bandwidth A = ", b1)
    print("Bandwidth B = ", b2)
    print("Data Rate = ", calculate_data_rate(b1, SNR))

def load_signal(csv_file):
    data = pd.read_csv(csv_file, delimiter='\t')
    matrix = data.values
    return matrix


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

    print("Desvío estándar de los picos:", peak_std)
    print("Desvío estándar de la señal:", signal_std)
    print("Desvío estándar del ruido:", noise_signal_std)
    print("SNR:", SNR)
    return SNR


def calculate_bandwidth(channel):
    # Aplicar la Transformada de Fourier (FFT) a la señal
    fft_signal = np.fft.fft(channel)
    freq = np.fft.fftfreq(len(channel), 1/200)
    # print("fft =", fft_signal)
    # print("freq =", freq)

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
    return bandwidth


def calcular_ancho_banda(frecuencias):
    # FFT
    fft_resultado = np.fft.fft(frecuencias)

    # Amplitudes de las frecuencias
    amplitudes = np.abs(fft_resultado)
    amplitudes_ordenadas = np.sort(amplitudes)[::-1]

    # Calculamos el porcentaje acumulado de las amplitudes
    porcentaje_acumulado = np.cumsum(amplitudes_ordenadas) / np.sum(amplitudes_ordenadas)

    # Frecuencias que representan el 95% de la señal
    frecuencias_seleccionadas = np.where(porcentaje_acumulado >= 0.95)[0]

    # Obtenemos la frecuencia mínima y máxima que explican el 95%
    frecuencia_minima = frecuencias_seleccionadas.min()
    frecuencia_maxima = frecuencias_seleccionadas.max()

    ancho_banda = frecuencias[frecuencia_maxima] - frecuencias[frecuencia_minima]
    return ancho_banda


def calculate_data_rate(bandwidth, snr):
    data_rate = bandwidth * np.log2(1 + snr)
    return data_rate


if __name__ == "__main__":
    main()

