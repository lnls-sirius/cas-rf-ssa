#!/usr/bin/python3
# -*- coding: utf-8 -*-

import math
import serial
import traceback

import os  as os
import sys as sys
import time
 


# Load the serial port name from the enviroment. If it's not set uses the default USB0 connection.
if "RF_RING_SERIAL_PORT" in os.environ:  
    SERIAL_PORT_NAME = os.getenv("RF_RING_SERIAL_PORT")
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

 
DB_FILENAME = "offsets_parameters.db"
ALARM_DB_FILENAME = "alarms_parameters.db"

#########################################################
#########################################################

# Time between attempts to reconnect the serial port
TIME_RECONNECT = 10.

# Time between scan requests, a single scan is responsible for all racks
SCAN_TIMER = 3.7


BAUD_RATE = 500000
TIMEOUT = .5
STOP_BITS = serial.STOPBITS_ONE
PARITY = serial.PARITY_NONE
BYTE_SIZE = serial.EIGHTBITS

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
    if os.path.exists(SERIAL_PORT_NAME):
        SERIAL_PORT = get_serial()
    else:
        SERIAL_PORT = None
except:
    SERIAL_PORT = None
    
READ_MSGS = \
    [[1, "RACK1".encode('utf-8'), SERIAL_PORT],
     [2, "RACK2".encode('utf-8'), SERIAL_PORT],
     [3, "RACK3".encode('utf-8'), SERIAL_PORT],
     [4, "RACK4".encode('utf-8'), SERIAL_PORT]]

# A token used on the consumer thread to request readings
READ_PARAMETERS = "R"

# Token that sinals the end of the stream
END_OF_STREAM = "####FIM!;"


def refresh_serial_connection():
    """
    Refresh the serial connection.
    return True or False
    """
    global READ_MSGS
    try:
        if not os.path.exists(SERIAL_PORT_NAME):
            # This device doesn't exist ! It's disconnected or the socat service is off.
            # Will have to wait inside this loop ...
            for num, msg, port in READ_MSGS:
                if port and port.is_open:
                    try:
                        port.close()
                    except:
                        pass
                
            return False
        
        # Check if the serial port for each rack is open !
        all_open = True
        for num, msg, port in READ_MSGS:
            if port == None or not port.is_open or port.portstr != SERIAL_PORT_NAME:
                all_open = False
        
        if not all_open:
            for num, msg, port in READ_MSGS:
                if port != None:
                    try:
                        port.close()
                    except:
                        pass

            # Create a new serial connection and update the READ_MSGS array.
            porta_0 = get_serial()

            for i in range(4):
                READ_MSGS[i][2] = porta_0

        return True

    # Could not find the serial device ... It's disconnencted
    except serial.serialutil.SerialException:
        # There's nothing to do but wait
        return False

    except Exception:
        print('[ERROR] Refresh Serial Exception:\n{}'.format(traceback.format_exc()))
        return False
    
