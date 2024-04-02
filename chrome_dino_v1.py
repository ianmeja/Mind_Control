import argparse
import time
import numpy as np
import collections
import pyautogui
import pandas as pd
import matplotlib.pyplot as plt
import graph

import brainflow
from brainflow.board_shim import BoardShim, BoardIds, BrainFlowInputParams
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--timeout', type=int, help='timeout for device discovery or connection', required=False,
                        default=0)
    parser.add_argument('--serial-port', type=str, help='serial port', required=True)  # Make serial port required
    parser.add_argument('--mac-address', type=str, help='mac address', required=False, default='')
    parser.add_argument('--file', type=str, help='file', required=False, default='')
    parser.add_argument('--log', action='store_true')
    parser.add_argument('--board-id', type=int, help='board id, check docs to get a list of supported boards',
                        required=True)  # Add board-id argument
    parser.add_argument('--streamer-params', type=str, help='streamer params', required=False,
                        default='')  # Add streamer-params argument
    args = parser.parse_args()

    params = BrainFlowInputParams()
    params.serial_port = args.serial_port  # Set the serial port
    params.mac_address = args.mac_address  # Optionally, set the MAC address
    params.timeout = args.timeout  # Optionally, set a timeout

    # initialize calibration and time variables
    time_thres = 100
    max_val = -100000000000
    vals_mean = 0
    num_samples = 2000
    samples = 0

    if args.log:
        BoardShim.enable_dev_board_logger()
    else:
        BoardShim.disable_board_logger()

    board = BoardShim(args.board_id, params)
    board.prepare_session()

    board.start_stream(45000, args.streamer_params)

    # start calibration

    print("Starting calibration")
    time.sleep(5)  # wait for data to stabilize
    data = board.get_board_data()  # clear buffer

    print("Relax and flex your arm a few times")

    while samples < num_samples:

        data = board.get_board_data()  # get data
        if len(data[1]) > 0:
            DataFilter.perform_rolling_filter(data[1], 2, AggOperations.MEAN.value)  # denoise data
            vals_mean += sum([data[1, i] / num_samples for i in range(len(data[1]))])  # update mean
            samples += len(data[1])
            if np.amax(data[1]) > max_val:
                max_val = np.amax(data[1])  # update max

    flex_thres = 0.4 * ((max_val - vals_mean) ** 2)  # calculate flex threshold - percentage needs to be set per person

    print("Mean Value")
    print(vals_mean)
    print("Max Value")
    print(max_val)
    print("Threshold")
    print(flex_thres)

    # end calibration

    # start game

    print("Calibration complete. Start!")
    prev_time = int(round(time.time() * 1000))

    while True:

        data = board.get_board_data()  # get data

        if len(data[1]) > 0:
            DataFilter.perform_rolling_filter(data[1], 2, AggOperations.MEAN.value)  # denoise data
            if (int(round(
                    time.time() * 1000)) - time_thres) > prev_time:  # if enough time has gone by since the last flex
                prev_time = int(round(time.time() * 1000))  # update time
                for element in data[1]:
                    if ((element - vals_mean) ** 2) >= flex_thres:  # if above threshold
                        pyautogui.press('space')  # jump
                        break

    board.stop_stream()
    board.release_session()

    DataFilter.write_file(data[1], chrome + '.csv', 'w')


if __name__ == "__main__":
    main()
