#coding: latin-1

import matplotlib.pyplot as plt
import numpy as np

class Plotter:

    def __init__(self, sample_rate, initial_data):
        # You probably won't need this if you're embedding things in a tkinter plot...
        plt.ion()

        self.x = np.linspace(0, len(initial_data)/sample_rate, num=len(initial_data))
        self.y = initial_data

        self.fig = plt.figure(figsize=(18,6))
        self.ax = self.fig.add_subplot(111)

        self.line1, = self.ax.plot(self.x, self.y, 'b', label='Channel 1')
        self.ax.set_xlim(0, max(self.x))
        self.ax.set_xlabel(r'time (s)')
        self.ax.set_ylabel(r'voltage ($\mu$V)')

    def close(self):
        plt.close()

    def plotdata(self, data):
        # is  a valid message struct
        #print new_values
        self.y = data
        self.line1.set_ydata(self.y)

        self.fig.canvas.draw()
        plt.pause(0.0001)
