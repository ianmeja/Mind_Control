import time
import argparse
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, NoiseTypes, AggOperations, WindowOperations

def main():
    parser = argparse.ArgumentParser ()

    # use docs to check which parameters are required for specific board, e.g. for Cyton - set serial port
    parser.add_argument ('--timeout', type = int, help  = 'timeout for device discovery or connection', required = False, default = 15)
    parser.add_argument ('--ip-port', type = int, help  = 'ip port', required = False, default = 0)
    parser.add_argument ('--ip-protocol', type = int, help  = 'ip protocol, check IpProtocolType enum', required = False, default = 0)
    parser.add_argument ('--ip-address', type = str, help  = 'ip address', required = False, default = '')
    parser.add_argument ('--serial-port', type = str, help  = 'serial port', required = False, default = '/dev/cu.usbmodem11')
    parser.add_argument ('--mac-address', type = str, help  = 'mac address', required = False, default = '')
    parser.add_argument ('--other-info', type = str, help  = 'other info', required = False, default = '')
    parser.add_argument ('--streamer-params', type = str, help  = 'streamer params', required = False, default = '')
    parser.add_argument ('--serial-number', type = str, help  = 'serial number', required = False, default = '')
    parser.add_argument ('--board-id', type = int, help  = 'board id, check docs to get a list of supported boards', required = False, default = BoardIds.GANGLION_BOARD)
    parser.add_argument ('--file', type=str, help='file', required=False, default='')
    parser.add_argument ('--master-board', type=int, help='master board id for streaming and playback boards', required=False, default=BoardIds.NO_BOARD)
    parser.add_argument ('--log', action = 'store_true')
    parser.add_argument ('--file-name', type = str, help = 'file name for recorded data', required = False, default = 'no_name')

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

    if (args.log):
        BoardShim.enable_dev_board_logger()
    else:
        BoardShim.disable_board_logger()

    board = BoardShim(args.board_id, params)
    board.prepare_session()
    print("Starting...")
    sampling_rate = BoardShim.get_sampling_rate(args.board_id)
    print("Sampling rate:", sampling_rate)
    board.start_stream(45000, args.streamer_params)

    print("Prepare for test...")
    duration = 20
    # wait for data to stabilize
    for i in range(5):
        print(5-i)
        time.sleep(1)
    clear = board.get_board_data() # clear buffer
    
    print("Start")
    for j in range(duration):
        print(duration-j)
        time.sleep(1)
    print("Stop")
    
    data = board.get_board_data()

    board.stop_stream()
    board.release_session()
    print("Session ended.")
    
    # Sava data from session for later access
    DataFilter.write_file(data, args.file_name + '(unfiltered).csv', 'w')

    df = pd.DataFrame(np.transpose(data))
    plt.figure()
    df[1].plot(subplots=True)
    plt.savefig(args.file_name + '-before.png')

    DataFilter.perform_rolling_filter (data[1], 2, AggOperations.MEAN.value)
    DataFilter.perform_bandpass(data[1], sampling_rate, 0.5, 10.0, 4, FilterTypes.BUTTERWORTH, 0)
    DataFilter.remove_environmental_noise(data[1], sampling_rate, NoiseTypes.FIFTY.value)
    
    # Sava data from session for later access
    DataFilter.write_file(data, args.file_name + '.csv', 'w')

    df2 = pd.DataFrame(np.transpose(data))
    plt.figure()
    df2[1].plot(subplots=True)
    plt.savefig(args.file_name + '-after.png')
    

if __name__ == "__main__":
    main()