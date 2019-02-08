#!/usr/bin/python3
# -*- coding: utf-8 -*-

import serial
import math
import traceback

import os  as os
import sys as sys

# Load the serial port name from the enviroment. If it's not set uses the default USB0 connection.
if "RF_BSSA_SERIAL_PORT" in os.environ:  
    SERIAL_PORT_NAME = os.getenv("RF_BSSA_SERIAL_PORT")
else:
    SERIAL_PORT_NAME = "/dev/ttyUSB0"

args = sys.argv
SHOW_DEBUG_INFO = False

print("Parameters {}".format(args))
if len(args) == 2:
    try:
        SHOW_DEBUG_INFO = str(args[1]).upper() == "TRUE"
        print("Show Debug Info {}".format(SHOW_DEBUG_INFO))
    except Exception:
        print("Parameter {} could not be converted to True/False".format(args[1]))


OFFSET_DB_FILENAME = "offsets_parameters.db"
ALARM_DB_FILENAME = "alarms_parameters.db"


'''
    Serial Connection
'''
TIME_RECONNECT = 3.0
SCAN_TIMER = 1. 

BAUD_RATE = 500000
TIMEOUT = .10
STOP_BITS = serial.STOPBITS_ONE
PARITY = serial.PARITY_NONE
BYTE_SIZE = serial.EIGHTBITS
FLOW_CONTROL = False


def get_serial():
    '''
        Serial Connection

        return serial.Serial(serial_port)
    ''' 
    return serial.Serial(port=SERIAL_PORT_NAME,
                         baudrate=BAUD_RATE,
                         timeout=TIMEOUT,
                         stopbits=STOP_BITS,
                         parity=PARITY,
                         bytesize=BYTE_SIZE)


# First attempt to initialize the serial port.
# try block so that the program doesn't die on initialization ...
try :
    SERIAL_PORT = get_serial()
except:
    SERIAL_PORT = None


# A token used on the consumer thread to request readings
READ_PARAMETERS = "READ_PARAMETERS"

# Read Command
READ_MSG = "TORRE" + os.environ.get("TOWER_NUM", "1")
READ_MSG = READ_MSG.encode('utf-8')

# Token that sinals the end of the stream
END_OF_STREAM = "####FIM!;"

def getSerialPort():
    return SERIAL_PORT

def refresh_serial_connection():
    """
    Refresh the serial connection.
    return True or False
    """
    global SERIAL_PORT
    try:

        if not os.path.exists(SERIAL_PORT_NAME):
            # This device doesn't exist! It's disconnected or the socat service is off.
            # Will have to wait inside this loop ...
            if SERIAL_PORT and SERIAL_PORT.is_open:
                try:
                    SERIAL_PORT.close()
                except:
                    pass
            #print("os.path.exists(SERIAL_PORT_NAME) {}".format(os.path.exists(SERIAL_PORT_NAME)))
            return False

        if SERIAL_PORT == None or not SERIAL_PORT.is_open or SERIAL_PORT.portstr != SERIAL_PORT_NAME:
                
                SERIAL_PORT = get_serial()
        
        # if SERIAL_PORT:
        #     if  SERIAL_PORT.portstr != SERIAL_PORT_NAME:
        #         # The wrong port !
        #         try:
        #             SERIAL_PORT.close()
        #         except:
        #             pass
        
        #     if not SERIAL_PORT.is_open:
        #         # Create a new serial connection
        #         SERIAL_PORT = get_serial()
        # else:
        #     SERIAL_PORT = get_serial()

        return True
        # Could not find the serial device ... It's disconnencted
    except serial.serialutil.SerialException:
        # There's nothing to do but wait
        return False
    except:
        print('[ERROR] Refresh Serial Exception:\n{}'.format(traceback.format_exc()))
        return False
    
