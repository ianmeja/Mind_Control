import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt


def main():
    output_csv_file = '../utils/data_rate_1.csv'

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
    #b1 = calculate_bandwidth(channel_0)
    #b2 = calcular_ancho_banda(channel_0)
    #plot_fft(channel_0, 1, 200)
    # TODO Hernan dijo de agarrarlo del UI
#    print("Bandwidth A = ", b1)
#    print("Bandwidth B = ", b2)
    print("Data Rate = ", calculate_data_rate(6, SNR))


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


def plot_fft(data, channel, sampling_rate):
    fft_data = np.fft.fft(data)

    # Compute the magnitudes of the FFT result
    magnitude = np.abs(fft_data)

    # Generate the frequency axis
    N = len(fft_data)
    T = 1 / sampling_rate
    freq = np.fft.fftfreq(N, T)

    # Filter frequencies and amplitudes above 0
    positive_freq = freq[(freq > 0) & (magnitude > 0)]
    positive_mag = magnitude[(freq > 0) & (magnitude > 0)]

    # Find the index where 95% of the signal is accumulated
    sorted_mag = np.sort(positive_mag)[::-1]  # Sort magnitudes in descending order
    cum_sum = np.cumsum(sorted_mag)  # Compute cumulative sum
    threshold = 0.3 * cum_sum[-1]  # 95% of the total sum
    index_95 = np.searchsorted(cum_sum, threshold)  # Find the index where cumulative sum exceeds the threshold

    # Filter frequencies and amplitudes above M uV
    M = 100000
    marked_freq = freq[magnitude > M]
    marked_mag = magnitude[magnitude > M]

    # Plot the FFT result
    plt.figure(figsize=(10, 5))
    plt.plot(positive_freq, positive_mag, linestyle='-', linewidth=1)
    plt.scatter(marked_freq, marked_mag, marker='o')  # Plot markers for positive amplitudes
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude (μV)')

    # Set the x-axis limit to 0-100 Hz and the y-axis limit to auto
    plt.xlim(0, 100)
    plt.ylim(0, auto=True)
    plt.title('FFT Channel %d Plot' % channel)
    plt.grid(True)

    # Annotate the most powerful frequencies with their amplitudes
    for f, mag in zip(marked_freq, marked_mag):
        plt.annotate(f'{f:.2f} Hz\n{mag:.2f} μV', xy=(f, mag), xytext=(f + 5, mag),
                     arrowprops=dict(facecolor='black', arrowstyle='->'), bbox=dict(facecolor='white', alpha=0.5))

    freq_95 = positive_freq[index_95]

    # Annotate the 95% accumulation point with its frequency
    plt.annotate(f'95% Accumulation\n{sorted_mag[index_95]:.2f} μV\n{freq_95:.2f} Hz',
                 xy=(freq_95, sorted_mag[index_95]),
                 xytext=(freq_95 + 5, sorted_mag[index_95]),
                 arrowprops=dict(facecolor='red', arrowstyle='->'),
                 bbox=dict(facecolor='white', alpha=0.5))
    # Save the plot
    plt.savefig('fft_channel_%d_2_2.png' % channel)


if __name__ == "__main__":
    main()

