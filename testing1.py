import argparse
import time
import numpy as np
import collections
import pyautogui
import pandas as pd
import matplotlib.pyplot as plt
import graph
from pprint import pprint

import brainflow
from brainflow.board_shim import BoardShim, BoardIds, BrainFlowInputParams
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations

def main ():    
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
    parser.add_argument ('--log', action = 'store_true')
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
    pprint(BoardShim.get_board_descr(args.board_id))
    emg_channels = BoardShim.get_emg_channels(args.board_id)

    board.prepare_session()
    board.start_stream(45000, args.streamer_params)

    try:
        while True:
            data = board.get_board_data() # get data
            if(len(data[1]) > 0):
                DataFilter.perform_rolling_filter (data[1], 2, AggOperations.MEAN.value) # denoise data
                df = pd.DataFrame(np.transpose(data))
                print('Data From the Board')
                print(df.head(10))
    
    except KeyboardInterrupt:
        pass

    board.stop_stream ()
    board.release_session ()


if __name__ == "__main__":
    main ()