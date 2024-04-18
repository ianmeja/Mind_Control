import argparse
import time
import numpy as np
import logging
import pyautogui
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import brainflow
from brainflow.board_shim import BoardShim, BoardIds, BrainFlowInputParams
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations

def main ():
    BoardShim.enable_dev_board_logger()
    #logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser ()

    # use docs to check which parameters are required for specific board, e.g. for Cyton - set serial port
    parser.add_argument ('--timeout', type = int, help  = 'timeout for device discovery or connection', required = False, default = 0)
    parser.add_argument ('--ip-port', type = int, help  = 'ip port', required = False, default = 0)
    parser.add_argument ('--ip-protocol', type = int, help  = 'ip protocol, check IpProtocolType enum', required = False, default = 0)
    parser.add_argument ('--ip-address', type = str, help  = 'ip address', required = False, default = '')
    parser.add_argument ('--serial-port', type = str, help  = 'serial port', required = False, default = '')
    parser.add_argument ('--mac-address', type = str, help  = 'mac address', required = False, default = '')
    parser.add_argument ('--other-info', type = str, help  = 'other info', required = False, default = '')
    parser.add_argument ('--streamer-params', type = str, help  = 'streamer params', required = False, default = '')
    parser.add_argument ('--serial-number', type = str, help  = 'serial number', required = False, default = '')
    parser.add_argument ('--board-id', type = int, help  = 'board id, check docs to get a list of supported boards', required = True)
    parser.add_argument('--file', type=str, help='file', required=False, default='')
    parser.add_argument('--master-board', type=int, help='master board id for streaming and playback boards', required=False, default=BoardIds.NO_BOARD)
    args = parser.parse_args ()

    params = BrainFlowInputParams ()
    params.ip_port = args.ip_port
    params.serial_port = args.serial_port
    params.mac_address = args.mac_address
    params.other_info = args.other_info
    params.serial_number = args.serial_number
    params.ip_address = args.ip_address
    params.ip_protocol = args.ip_protocol
    params.timeout = args.timeout
    params.file = args.file
    params.master_board = args.master_board

    # initialize calibration and time variables
    time_thres = 100
    sampling_rate = BoardShim.get_sampling_rate(args.board_id)
    window = sampling_rate * 5 # 5 second window   
    flex_thres = 0.8

    board = BoardShim (args.board_id, params)
    emg_channels = BoardShim.get_emg_channels(args.board_id)
    board.prepare_session ()
    board.start_stream (45000, args.streamer_params)
    time.sleep(10) # wait for data to stabilize
    
    # Plot
    data = board.get_current_board_data(window)
    # calculate time window
    timeEMG = np.linspace(0, 5, num=len(data[1]))

    plt.rcParams["figure.figsize"] = [7.50, 3.50]
    plt.rcParams["figure.autolayout"] = True
    fig, ax = plt.subplots()
    plt.xlabel(r'time (s)')
    plt.ylabel(r'voltage ($\mu$V)')
    plt.xlim(0, max(timeEMG))
    line, = ax.plot(timeEMG, data[1], 'b')

    def init():  # give a clean slate to start
        data = board.get_current_board_data(window) # get data
        line.set_ydata(data[1])
        return line,

    def animate(i):  # update the y values (every 5000ms)
        data = board.get_current_board_data(window) # get data
        # Filter & Denoise
        DataFilter.perform_bandpass(data[1], sampling_rate, 0.5, 90.0, 4, 
                                    FilterTypes.BESSEL_ZERO_PHASE, 0) # bandpass
        DataFilter.perform_bandstop(data[1], sampling_rate, 48.0, 52.0, 3,
                                    FilterTypes.BUTTERWORTH_ZERO_PHASE, 0) # notch
        DataFilter.perform_rolling_filter (data[1], 2, AggOperations.MEAN.value) # denoise data
        line.set_ydata(data[1])
        return line,

    ani = animation.FuncAnimation(fig, animate, init_func=init, interval=5000, 
                                  blit=True, save_count=10)

    plt.show()

    while True:
        if KeyboardInterrupt:
            break      
        
    board.stop_stream()
    board.release_session()


if __name__ == "__main__":
    main ()