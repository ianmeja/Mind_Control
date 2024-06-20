import argparse
import time
import numpy as np
import matplotlib.pyplot as plt

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, NoiseTypes, DetrendOperations

DELTA = 0 # 1-4 Hz
THETA = 1 # 4-8 Hz
ALPHA = 2 # 8-13 Hz
BETA = 3 # 13-30 Hz
GAMMA = 4 # 30-55 Hz
NUM_BANDS = 5

CUSTOM_BETA_BAND = (18.0, 22.0)
CUSTOM_LOW_BAND = (1.0, 7.0)

APPLY_CUSTOM_BANDS = False
APPLY_CUSTOM_FILTERS = True

MAX_X = 20
MAX_Y = 20
MAX_STEPS = 50
# Points for experiment: P1 --> (3, 12) color=b ; P2 --> (10, 8) color=m; P3 --> (12, 3) color=r
POINT_X = 12
POINT_Y = 3
COLOR = 'r'

CALIBRATION_TIME = 10

def main ():
    parser = argparse.ArgumentParser ()
    
    # use docs to check which parameters are required for specific board, e.g. for Cyton - set serial port
    parser.add_argument ('--timeout', type = int, help  = 'timeout for device discovery or connection', required = False, default = 0)
    parser.add_argument ('--ip-port', type = int, help  = 'ip port', required = False, default = 0)
    parser.add_argument ('--ip-protocol', type = int, help  = 'ip protocol, check IpProtocolType enum', required = False, default = 0)
    parser.add_argument ('--ip-address', type = str, help  = 'ip address', required = False, default = '')
    parser.add_argument ('--serial-port', type = str, help  = 'serial port', required = False, default = '/dev/cu.usbmodem11')
    parser.add_argument ('--mac-address', type = str, help  = 'mac address', required = False, default = '')
    parser.add_argument ('--other-info', type = str, help  = 'other info', required = False, default = '')
    parser.add_argument ('--streamer-params', type = str, help  = 'streamer params', required = False, default = '')
    parser.add_argument ('--serial-number', type = str, help  = 'serial number', required = False, default = '')
    parser.add_argument ('--board-id', type = int, help  = 'board id, check docs to get a list of supported boards', required = False, default = BoardIds.GANGLION_BOARD.value)
    parser.add_argument ('--log', action = 'store_true')
    parser.add_argument ('--file-name', type = str, help  = 'file name', required = False, default = 'default')
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

    sampling_rate = BoardShim.get_sampling_rate(BoardIds.GANGLION_BOARD.value)

    if (args.log):
        BoardShim.enable_dev_board_logger()
    else:
        BoardShim.disable_board_logger()

    board = BoardShim (args.board_id, params)
    board.prepare_session ()

    board.start_stream (45000, args.streamer_params)

    ### Calibrate ###

    print("Starting calibration...")
    time.sleep(10) # wait for data to stabilize
    board.get_board_data() # clear buffer

    print("Hold tight your muscle for a few seconds.")
    for i in range(CALIBRATION_TIME):
        print(CALIBRATION_TIME-i)
        time.sleep(1)

    data = board.get_board_data() # get data
    
    # Filter & Denoise
    if(APPLY_CUSTOM_FILTERS):
        DataFilter.detrend(data[1], DetrendOperations.CONSTANT.value)
        DataFilter.perform_bandpass(data[1], sampling_rate, 0.5, 40.0, 4, FilterTypes.BUTTERWORTH_ZERO_PHASE, 0)
        DataFilter.remove_environmental_noise(data[1], sampling_rate, NoiseTypes.FIFTY.value)
    
    if(APPLY_CUSTOM_BANDS):
        ### Custom Band Powers
        avg_bps = DataFilter.get_custom_band_powers(data, [CUSTOM_LOW_BAND, CUSTOM_BETA_BAND], [1], sampling_rate, not APPLY_CUSTOM_FILTERS)
        avg_low_bp = avg_bps[0][0]
        avg_beta_bp = avg_bps[0][1]
    else:
        ### Brainflow default Band Powers
        avg_bps = DataFilter.get_avg_band_powers(data, [1], sampling_rate, not APPLY_CUSTOM_FILTERS)
        avg_beta_bp = avg_bps[0][BETA]
        avg_low_bp = sum(avg_bps[0][:BETA])
    

    print("Avg Beta Band Power")
    print(avg_beta_bp)
    print("Avg Low Band Powers")
    print(avg_beta_bp)

    ### MAIN LOOP ###
    
    plt.ion() # turning interactive mode on
    
    # plotting the first frame
    x = [0]
    y = [0]
    graph = plt.plot(x,y)[0]
    circle = plt.Circle((POINT_X, POINT_Y), radius=4, color=COLOR, fill=False, linewidth=2)
    plt.gca().add_artist(circle)
    plt.plot(POINT_X, POINT_Y, '+', color='black')
    plt.ylim(0,MAX_X)
    plt.xlim(0,MAX_Y)
    plt.xlabel('Low frequency')
    plt.ylabel('High frequency')
    plt.pause(1)

    print("Calibration complete. Start!")
    print("Try to get into the circle. Press 'Ctrl+C' to quit.")
    try:
        while True:
            if(len(x) > MAX_STEPS): break
            time.sleep(2)
            data = board.get_board_data() # get data 
            
            if(APPLY_CUSTOM_FILTERS):
                # Filter & Denoise
                DataFilter.detrend(data[1], DetrendOperations.CONSTANT.value)
                DataFilter.perform_bandpass(data[1], sampling_rate, 0.5, 40.0, 4, FilterTypes.BUTTERWORTH_ZERO_PHASE, 0)
                DataFilter.remove_environmental_noise(data[1], sampling_rate, NoiseTypes.FIFTY.value)
            
            if(APPLY_CUSTOM_BANDS):
                ### Custom Band Powers
                new_avg_bps = DataFilter.get_custom_band_powers(data, [CUSTOM_LOW_BAND, CUSTOM_BETA_BAND], [1], sampling_rate, not APPLY_CUSTOM_FILTERS)
                new_avg_low_bp = new_avg_bps[0][0]
                new_avg_beta_bp = new_avg_bps[0][1]
            else:
                ### Brainflow default Band Powers
                new_avg_bps = DataFilter.get_avg_band_powers(data, [1], sampling_rate, not APPLY_CUSTOM_FILTERS)
                new_avg_low_bp = sum(new_avg_bps[0][:BETA])
                new_avg_beta_bp = new_avg_bps[0][BETA]
                
            # checking if new low band avg is above threshold
            if(new_avg_low_bp >= avg_low_bp):
                print("Bigger low band x++")
                x.append(x[-1]+1) if x[-1]+1 < MAX_X else x.append(x[-1])
            else:
                print("Lower low band x--")
                x.append(x[-1]-1) if x[-1]-1 >= 0 else x.append(x[-1])
                
            # checking if new beta band avg is above threshold
            if(new_avg_beta_bp >= avg_beta_bp):
                print("Bigger beta band y++")
                y.append(y[-1]+1) if y[-1]+1 < MAX_Y else y.append(y[-1])
            else:
                print("Lower beta band y--")
                y.append(y[-1]-1) if y[-1]-1 >= 0 else y.append(y[-1])
            
            print("Step {}: [{}, {}]".format(len(x)-1, x[-1], y[-1]))
            
            # removing the older graph
            graph.remove()
            
            # plotting newer graph
            graph = plt.plot(x,y,color = COLOR, linewidth = 2)[0]
            
            # calling pause function for 0.25 seconds
            plt.pause(0.25)
            
    except KeyboardInterrupt:
        pass

    plt.savefig(args.file_name + ".png")
    
    board.stop_stream ()
    board.release_session ()


if __name__ == "__main__":
    main ()
