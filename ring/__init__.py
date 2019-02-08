import serial
import argparse
import logging

parser = argparse.ArgumentParser("Sirius CAS RF - Storage Ring Solid State Amplifiers")

# PVs naming configuration
parser.add_argument("--sec-sub-key", default='RA-ToSIA01', help='Sector-subsector key.', dest="sec_sub_key")

# General Configuration
parser.add_argument("--time-reconnect", default=10., type=float, help='Time between reconnect attempts.', dest="time_reconnect")
parser.add_argument("--debug", help='Show debug info.', dest="debug")

# Serial Comm
parser.add_argument("--baudrate", "-b", default=500000, type=int, help='Serial port baudrate.', dest="baudrate")
parser.add_argument("--device", "-dev", default='/dev/ttyUSB0', help='Serial comm device.', dest="device")
parser.add_argument("--timeout","-t", default=0.1, type=float, help='Serial port timeout.', dest="timeout")
parser.add_argument("--ser-buffer","-serb", default=1024,type=int, help='Serial port read buffer.', dest="ser_buffer")

# TCP Socket
parser.add_argument("--tcp", help='TCP Server communication.', dest="tcp")
parser.add_argument("--port","-p", default=4161, type=int, help='TCP Server port.', dest="port")
parser.add_argument("--tcp-buffer","-tcpb", default=1024, type=int, help='TCP recv buffer', dest="tcp_buffer")
parser.add_argument("--zero-bytes","-zb", default='ZB', help='What to return when a zero lengh response is returned from the serial port.', dest='zb')

args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='%(asctime)-15s [%(levelname)s] %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger()

