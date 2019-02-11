#!/usr/bin/python3
import sys
import os

dir_name = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(dir_name, '../'))

import serial
import argparse
import logging

parser = argparse.ArgumentParser("Sirius CAS RF - Storage Ring Solid State Amplifiers",
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)

# PVs naming configuration
parser.add_argument("--tower-num", default='01', choices=['01', '02'], help='Tower num.', dest="tower_num")

# General Configuration
parser.add_argument("--show-pvs", help='Show PVs info and exit.', action='store_true', dest="show_pvs")
parser.add_argument("--time-reconnect", default=10., type=float, help='Time between reconnect attempts.', dest="time_reconnect")
parser.add_argument("--debug", help='Show debug info.', action='store_true', dest="debug")
parser.add_argument("--buffer", default=1024, type=int, help='Read buffer.', dest="buffer")

# Serial Comm
parser.add_argument("--baudrate", "-b", default=500000, type=int, help='Serial port baudrate.', dest="baudrate")
parser.add_argument("--device", "-dev", default='/dev/ttyUSB0', help='Serial comm device.', dest="device")
parser.add_argument("--timeout","-t", default=0.1, type=float, help='Serial port timeout.', dest="timeout")

# TCP Socket
parser.add_argument("--tcp", help='TCP Server communication.', action='store_true', dest="tcp")
parser.add_argument("--port","-p", default=4161, type=int, help='TCP Server port.', dest="port")
parser.add_argument("--zero-bytes","-zb", default='ZB', help='What to expect from TCP recv() when a zero lengh response is returned from the serial port.', dest='zb')

args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='%(asctime)-15s [%(levelname)s] %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger()

# Paths
db_dir = os.path.join(dir_name, 'db')
if not os.path.isdir(db_dir):
    print(db_dir)
    os.makedirs(db_dir)

OFFSET_DB = os.path.join(db_dir, 'offset_parameters.db')
ALARM_DB = os.path.join(db_dir, 'alarms_parameters.db')

# General Arguments
TOWER_NUM = args.tower_num
BUFFER = args.buffer
SHOW_DEBUG_INFO = args.debug

# Token that sinals the end of the stream
END_OF_STREAM = "####FIM!;"

# Serial commands
READ_MSGS =[[i, "RACK{}".format(i).encode('utf-8')] for i in range(1, 5)]

# Serial Port Config
BAUDRATE = args.baudrate
DEVICE = args.device
TIMEOUT = args.timeout

if __name__ == '__main__':

    if args.show_pvs:
        # Show PV info
        from pv import show_pvs
        show_pvs()
        exit(0)

    # Run IOC
    from ioc import run_ioc
    run_ioc()