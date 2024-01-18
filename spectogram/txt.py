import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

with open('spectogram/files/OpenBCI1.txt', 'r') as file:
    lines = [line.strip() for line in file.readlines() if not line.startswith('%')]

header = lines[0].split(', ')
data_lines = [line.split(', ') for line in lines[1:]]
df = pd.DataFrame(data_lines, columns=header)

channels = ['EXG Channel 0', 'EXG Channel 1', 'EXG Channel 2', 'EXG Channel 3']
df[channels] = df[channels].apply(pd.to_numeric)

# Configuracion parametros
fs = 200  # Tasa de muestreo en Hz
nperseg = 256  # Tamaño de la ventana
noverlap = nperseg // 2  # Solapamiento entre ventanas

# Calcular y mostrar el espectrograma para cada canal
for channel in channels:
    f, t, Sxx = signal.spectrogram(df[channel], fs, nperseg=nperseg, noverlap=noverlap)
    plt.figure(figsize=(10, 6))
    plt.pcolormesh(t, f, 10 * np.log10(Sxx), shading='auto')
    plt.colorbar(label='Potencia (dB)')
    plt.title(f'Espectrograma - {channel}')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Frecuencia (Hz)')
    plt.tight_layout()
    plt.show()
