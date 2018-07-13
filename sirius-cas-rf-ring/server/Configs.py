#!/usr/bin/python3
# -*- coding: utf-8 -*-
import math
import serial
import traceback

import sys as sys
#########################################################
#########################################################

args = sys.argv
SHOW_DEBUG_INFO = False

print("Parameters {}".format(args))
if len(args) == 2:
    try:
        SHOW_DEBUG_INFO = str(args[1]).upper() == "TRUE"
        print("Show Debug Info {}".format(SHOW_DEBUG_INFO))
    except Exception:
        print("Parameter {} could not be converted to True/False".format(args[1]))

#########################################################
#########################################################
'''
current_lolim = ((5.4054 * ((0 / 4095.0) * 5.0)) - 2.703) * 1.05
current_hilim = ((5.4054 * ((4095 / 4095.0) * 5.0)) - 2.703) * 1.05
current_low = 1.0
current_high = 9.5
current_lolo = 0.0
current_hihi = 10.0

power_lolim = (7.8806 * math.log((1 / 4095.0) * 5.0)) + 11.289
power_hilim = (7.8806 * math.log((4095 / 4095.0) * 5.0)) + 11.289
power_low = 0.0
power_high = 0.0
power_lolo = 0.0
power_hihi = 0.0
power_lolim = (7.8806 * math.log((1 / 4095.0) * 5.0)) + 11.289
'''
DB_FILENAME = "offsets_parameters.db"
ALARM_DB_FILENAME = "alarms_parameters.db"

#########################################################
#########################################################

'''
    Serial Connection
'''
BAUD_RATE = 500000
TIMEOUT = 1
STOP_BITS = serial.STOPBITS_ONE
PARITY = serial.PARITY_NONE
BYTE_SIZE = serial.EIGHTBITS
FLOW_CONTROL = False

TIME_RECONNECT = 1.0


def get_serial(serial_port):
    '''return serial.Serial(serial_port)
    '''
    return serial.Serial(port=serial_port,
                         baudrate=BAUD_RATE,
                         timeout=TIMEOUT,
                         stopbits=STOP_BITS,
                         parity=PARITY,
                         bytesize=BYTE_SIZE)
    

SCAN_TIMER = .25
PORT = {
    1: "/dev/rfRingSerial",
    2: "/dev/ttyUSB1",
    3: "/dev/ttyUSB2",
    4: "/dev/ttyUSB3"
}

porta_0 = get_serial(PORT[1])

READ_MSGS = \
    [[1, "RACK1".encode('utf-8'), porta_0],
     [2, "RACK2".encode('utf-8'), porta_0],
     [3, "RACK3".encode('utf-8'), porta_0],
     [4, "RACK4".encode('utf-8'), porta_0]]

READ_PARAMETERS = "READ_PARAMETERS"
END_OF_STREAM = "####FIM!;"


def refresh_serial_connection():
    """
    Refresh the serial connection.
    return True or False
    """
    try:
        for num, msg, port in READ_MSGS:
            if port and not port.closed:
                try:
                    port.close()
                except:
                    pass
        # Create a new serial connection and update the READ_MSGS array.
        porta_0 = get_serial(PORT[1])
        for i in range(4):
            READ_MSGS[i][2] = porta_0
        return True
    except Exception:
        print('[ERROR] Refresh Serial Exception:\n{}'.format(traceback.format_exc()))
        return False
    


#########################################################
#########################################################
'''
    PVs naming configurations
'''
SEC_SUB_KEY = "RA-ToSIA01"
DIS = "RF"
DEV_STATUS = "SSAmpTower"
DEV_CURRENT = "SSAmp"
DEV_POWER = "HeatSink"
DEV_GENERAL_POWER = "SSAmpTower"

STATES = \
    ["PwrDCR1-Mon",
     "PwrDCR2-Mon",
     "PwrDCR3-Mon",
     "PwrDCR4-Mon"]

OFFSET_CONFIG_KEY = "OffsetConfig"
ALARM_CONFIG_KEY = "AlarmConfig"

SAVE = "Save"
HEATSINK = "H"
READING_ITEM_A = "AM"
READING_ITEM_B = "BM"

CONF_PV = SEC_SUB_KEY + ":" + OFFSET_CONFIG_KEY
ALARM_PV = SEC_SUB_KEY + ":" + ALARM_CONFIG_KEY

#    Usado para rapidas alteracoes na nomeclatura das pvs.
#    Mudancas devem ser feitas aqui !
#
#    O programa busca pvs utilizando suas devidas chaves
STATE_PVS = {}
RACK_PVS = {}

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

for rack_num in range(1, 5):
    gen_status_aux = "{}:{}-{}:{}".format(SEC_SUB_KEY, DIS, DEV_STATUS, STATES[rack_num - 1])
    STATE_PVS[str(rack_num)] = gen_status_aux
    if SHOW_DEBUG_INFO:
        print(gen_status_aux)

    if rack_num == 1:
        min, max = 1, 3
        pass
    elif rack_num == 2:
        min, max = 3, 5
        pass
    elif rack_num == 3:
        min, max = 5, 7
        pass
    else:
        min, max = 7, 9
        pass

    for heatsink_num in range(min, max):
        bar_item_pair_num = 1
        bar_item_odd_num = 1
        for reading_item_num in range(1, 35):
            # Retornar Corrente
            if reading_item_num % 2 != 0:
                # Corrente 1
                bar_item_num_aux = bar_item_odd_num
                bar_item_odd_num += 1
                PROP = "Current1-Mon"
                pass
            else:
                # Corrente 2
                bar_item_num_aux = bar_item_pair_num
                bar_item_pair_num += 1
                PROP = "Current2-Mon"
                pass

            if reading_item_num == 33 or reading_item_num == 34:
                RACK_PVS[str(rack_num) + ":" + str(heatsink_num) + ":" + str(reading_item_num)] = \
                    "{0}:{1}-{2}-{3}{4:0>2}{5}:{6}".format(SEC_SUB_KEY, DIS, DEV_CURRENT, HEATSINK, heatsink_num,
                                                           "PreAmp", PROP)
                if SHOW_DEBUG_INFO:
                    print(
                        "{0}:{1}-{2}-{3}{4:0>2}{5}:{6}".format(SEC_SUB_KEY, DIS, DEV_CURRENT, HEATSINK,
                                                               heatsink_num,
                                                               "PreAmp", PROP))
                pass
            else:
                if 1 <= reading_item_num <= 16:
                    # AM
                    BAR_ITEM = READING_ITEM_A
                    pass
                else:
                    # BM
                    BAR_ITEM = READING_ITEM_B
                    bar_item_num_aux = bar_item_num_aux - 8
                    pass
                RACK_PVS[str(rack_num) + ":" + str(heatsink_num) + ":" + str(reading_item_num)] = \
                    "{0}:{1}-{2}-{3}{4:0>2}{5}{6:0>2}:{7}".format(SEC_SUB_KEY, DIS, DEV_CURRENT, HEATSINK,
                                                                  heatsink_num,
                                                                  BAR_ITEM,
                                                                  bar_item_num_aux, PROP)
                if SHOW_DEBUG_INFO:
                    print(
                        "{0}:{1}-{2}-{3}{4:0>2}{5}{6:0>2}:{7}".format(SEC_SUB_KEY, DIS, DEV_CURRENT, HEATSINK,
                                                                      heatsink_num,
                                                                      BAR_ITEM, bar_item_num_aux, PROP))
                pass

        for reading_item_num in range(35, 39):
            # Retornar Potencia
            if reading_item_num == 35:
                prop = "PwrRevBot-Mon"
            elif reading_item_num == 36:
                prop = "PwrFwdBot-Mon"
            elif reading_item_num == 37:
                prop = "PwrRevTop-Mon"
            else:
                prop = "PwrFwdTop-Mon"

            RACK_PVS[str(rack_num) + ":" + str(heatsink_num) + ":" + str(reading_item_num)] = \
                "{0}:{1}-{2}-{3}{4:0>2}:{5}".format(SEC_SUB_KEY, DIS, DEV_POWER, HEATSINK, heatsink_num, prop)
            if SHOW_DEBUG_INFO:
                print(
                    "{0}:{1}-{2}-{3}{4:0>2}:{5}".format(SEC_SUB_KEY, DIS, DEV_POWER, HEATSINK, heatsink_num, prop))

    for reading_item_num in range(1, 5):
        # Retornar potência Geral
        if reading_item_num == 1 or reading_item_num == 2:
            if reading_item_num % 2 == 0:
                general_power_pv = "{}:{}:{}".format(SEC_SUB_KEY, DIS + "-" + DEV_GENERAL_POWER, "PwrFwdOut" + str(rack_num) +"-Mon")
            else:
                general_power_pv = "{}:{}:{}".format(SEC_SUB_KEY, DIS + "-" + DEV_GENERAL_POWER, "PwrRevOut" + str(rack_num) +"-Mon")
        else:
            if reading_item_num % 2 == 0:
                general_power_pv = "{}:{}:{}".format(SEC_SUB_KEY, DIS + "-" + DEV_GENERAL_POWER, "PwrFwdIn" + str(rack_num) +"-Mon")
            else:
                general_power_pv = "{}:{}:{}".format(SEC_SUB_KEY, DIS + "-" + DEV_GENERAL_POWER, "PwrRevIn" + str(rack_num) +"-Mon")

        RACK_PVS[str(rack_num) + ":" + "9" + ":" + str(reading_item_num)] = general_power_pv
        if SHOW_DEBUG_INFO:
            print(general_power_pv)


#########################################################

def get_state_pv(rack_num):
    return STATE_PVS[str(rack_num)]


def get_heatsink_pv_name(rack_num, heatsink_num, reading_item_num):
    return RACK_PVS[str(rack_num) + ":" + str(heatsink_num) + ":" + str(reading_item_num)]

#########################################################
