#!/usr/bin/python3
# -*- coding: utf-8 -*-
import serial
import math

#########################################################
#########################################################
import sys as sys

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
#########################################################
#########################################################

'''
    Serial Connection
'''
TIME_RECONNECT = 1.0

PORT = "/dev/rfBssaSerial"
BAUD_RATE = 500000
TIMEOUT = .10
STOP_BITS = serial.STOPBITS_ONE
PARITY = serial.PARITY_NONE
BYTE_SIZE = serial.EIGHTBITS
FLOW_CONTROL = False

SCAN_TIMER = 1

READ_PARAMETERS = "READ_PARAMETERS"
READ_MSG = "TORRE1"
END_OF_STREAM = "####FIM!;"

serial_interface = None

def get_serial_interface():
    if not serial_interface:
        serial_interface = serial.Serial(port=PORT,
                                            baudrate=BAUD_RATE,
                                            timeout=TIMEOUT,
                                            stopbits=STOP_BITS,
                                            parity=PARITY,
                                            bytesize=BYTE_SIZE)
    else:
        return serial_interface

def refresh_serial_connection():
    """
    Refresh the serial connection.
    return True or False
    """
    try:
        if serial_interface:
            try:
                serial_interface.close()
            except:
                pass
        
        # Create a new serial connection
        serial_interface = None 

        get_serial_interface()
        return True
    except:
        print('[ERROR] Refresh Serial Exception:\n{}'.format(traceback.format_exc()))
        return False
    

#########################################################
#########################################################
'''
    PVs naming configurations
'''
SEC_SUB_KEY = "RF-BO"
DIS = "RF"
DEV_STATUS = "SSAmpTower"
DEV_CURRENT = "SSAmp"
DEV_POWER = "HeatSink"
DEV_GENERAL_POWER = "SSAmpTower"

STATE = "DCPwr-Cmd"

STATE_PV = SEC_SUB_KEY + ":" + DIS + "-" + DEV_STATUS + ":" + STATE

OFFSET_CONFIG_KEY = "OffsetConfig"
ALARM_CONFIG_KEY = "AlarmConfig"

SAVE = "Save"
BAR = "H"
BAR_ITEM = "M"

CONF_PV = SEC_SUB_KEY + ":" + OFFSET_CONFIG_KEY
ALARM_PV = SEC_SUB_KEY + ":" + ALARM_CONFIG_KEY
 

#    Usado para rapidas alteracoes na nomeclatura das pvs.
#    Mudancas devem ser feitas aqui !
#
#    O programa busca pvs utilizando suas devidas chaves
BAR_PVS = {}
for heatsink_num in range(1, 7):
    bar_item_pair_num = 1
    bar_item_odd_num = 1

    for reading_item_num in range(1, 35):

        if reading_item_num % 2 != 0:
            bar_item_aux = bar_item_odd_num
            bar_item_odd_num += 1
            prop_aux = "Current1-Mon"
            pass
        else:
            bar_item_aux = bar_item_pair_num
            bar_item_pair_num += 1
            prop_aux = "Current2-Mon"
            pass

        # Parameters 1 and 2 of bars 2 and 5 are meaningless. So this application won't provide PVs
        # associated with these parameters.
        if (heatsink_num in [2, 5]) and (reading_item_num in [1, 2]):
            pass
        else:
            bar_pv_aux = "{0}:{1}-{2}-{3}{4:0>2}{5}{6:0>2}:{7}".format(SEC_SUB_KEY, DIS, DEV_CURRENT, BAR, heatsink_num,
                                                                       BAR_ITEM, reading_item_num, prop_aux)
            BAR_PVS[str(heatsink_num) + ":" + str(reading_item_num)] = bar_pv_aux
            if SHOW_DEBUG_INFO:
                print(bar_pv_aux)

    for reading_item_num in range(35, 39):
        # Retornar Potencia
        prop = ""
        if reading_item_num == 35:
            prop = "BotPwrRev-Mon"
        elif reading_item_num == 36:
            prop = "BotPwrFwd-Mon"
        elif reading_item_num == 37:
            prop = "TopPwrRev-Mon"
        else:
            prop = "TopPwrFwd-Mon"

        BAR_PVS[str(heatsink_num) + ":" + str(reading_item_num)] = \
            "{0}:{1}-{2}-{3}{4:0>2}:{5}".format(SEC_SUB_KEY, DIS, DEV_POWER, BAR, heatsink_num, prop)
        if SHOW_DEBUG_INFO:
            print("{0}:{1}-{2}-{3}{4:0>2}:{5}".format(SEC_SUB_KEY, DIS, DEV_POWER, BAR, heatsink_num, prop))

for reading_item_num in range(1, 5):
    # Retornar potência Geral
    gen_pv_aux = ""
    if reading_item_num == 1 or reading_item_num == 2:
        if reading_item_num % 2 == 0:
            gen_pv_aux = \
                SEC_SUB_KEY + ":" + DIS + "-" + DEV_GENERAL_POWER + "-" + "OutPwr" + ":" + "PwrFwd-Mon"
        else:
            gen_pv_aux = \
                SEC_SUB_KEY + ":" + DIS + "-" + DEV_GENERAL_POWER + "-" + "OutPwr" + ":" + "PwrRev-Mon"
    else:
        if reading_item_num % 2 == 0:
            gen_pv_aux = \
                SEC_SUB_KEY + ":" + DIS + "-" + DEV_GENERAL_POWER + "-" + "InPwr" + ":" + "PwrFwd-Mon"
        else:
            gen_pv_aux = \
                SEC_SUB_KEY + ":" + DIS + "-" + DEV_GENERAL_POWER + "-" + "InPwr" + ":" + "PwrRev-Mon"

    BAR_PVS["9" + ":" + str(reading_item_num)] = gen_pv_aux
    if SHOW_DEBUG_INFO:
        print(gen_pv_aux)
        pass

ALARMS_PVS_DIC = {"general_power_lim_high": ALARM_PV + ":" + "GeneralPowerLimHigh",
                  "general_power_lim_low": ALARM_PV + ":" + "GeneralPowerLimLow",
                  "inner_power_lim_high": ALARM_PV + ":" + "InnerPowerLimHigh",
                  "inner_power_lim_low": ALARM_PV + ":" + "InnerPowerLimLow",
                  "current_lim_high": ALARM_PV + ":" + "CurrentLimHigh",
                  "current_lim_low": ALARM_PV + ":" + "CurrentLimLow"}

OFFSET_PVS_DIC = {"bar_upper_incident_power": CONF_PV + ":" + "UpperIncidentPower",
                  "bar_upper_reflected_power": CONF_PV + ":" + "UpperReflectedPower",
                  "bar_lower_incident_power": CONF_PV + ":" + "LowerIncidentPower",
                  "bar_lower_reflected_power": CONF_PV + ":" + "LowerReflectedPower",
                  "input_incident_power": CONF_PV + ":" + "InputIncidentPower",
                  "input_reflected_power": CONF_PV + ":" + "InputReflectedPower",
                  "output_incident_power": CONF_PV + ":" + "OutputIncidentPower",
                  "output_reflected_power": CONF_PV + ":" + "OutputReflectedPower"}
if SHOW_DEBUG_INFO:
    for k, v in OFFSET_PVS_DIC.items():
        print("{}".format(v))


def get_bar_pv_name(heatsink_num, reading_item_num):
    return BAR_PVS[str(heatsink_num) + ":" + str(reading_item_num)]

#########################################################
#########################################################
def flip_low_high(low,high):
    """
    Flip if needed
    return low, high
    """
    if low > high:
        aux = low
        low = high
        high = aux
    
    return low, high

