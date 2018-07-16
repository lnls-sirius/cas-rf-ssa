#!/usr/bin/python3
# -*- coding: utf-8 -*-
 
# Python modules required for this software
from pcaspy import Driver, Alarm, Severity, SimpleServer
from queue import Queue

from Calc import calc_I, calc_Pdbm, convert_adc_to_voltage

import time
import os
import pickle
import threading

from Configs import *


# PVs related to the solid-state amplifiers
PVs = {}

# System on/off state
PVs[STATE_PV] = {"type": "enum", "enums": ["OFF", "ON"]}
for bar in range(1, 7):

    for bar_item in range(1, 35):

        # Parameters 1 and 2 of bars 2 and 5 are meaningless. So this application won't provide PVs
        # associated with these parameters.
        if (bar in [2, 5]) and (bar_item in [1, 2]):
            pass
        else:
            PVs[get_bar_pv_name(heatsink_num=bar, reading_item_num=bar_item)] = {"type": "float", "prec": 2,
                                                                                 "unit": "A"}

    for bar_item in range(35, 39):
        PVs[get_bar_pv_name(heatsink_num=bar, reading_item_num=bar_item)] = {"type": "float", "prec": 2, "unit": "dBm"}

for bar_item in range(1, 5):
    PVs[get_bar_pv_name(heatsink_num=9, reading_item_num=bar_item)] = {"type": "float", "prec": 2, "unit": "dBm"}

PVs[OFFSET_PVS_DIC["bar_upper_incident_power"]] = {"type": "float", "prec": 2, "unit": "dB"}
PVs[OFFSET_PVS_DIC["bar_upper_reflected_power"]] = {"type": "float", "prec": 2, "unit": "dB"}
PVs[OFFSET_PVS_DIC["bar_lower_incident_power"]] = {"type": "float", "prec": 2, "unit": "dB"}
PVs[OFFSET_PVS_DIC["bar_lower_reflected_power"]] = {"type": "float", "prec": 2, "unit": "dB"}
PVs[OFFSET_PVS_DIC["input_incident_power"]] = {"type": "float", "prec": 2, "unit": "dB"}
PVs[OFFSET_PVS_DIC["input_reflected_power"]] = {"type": "float", "prec": 2, "unit": "dB"}
PVs[OFFSET_PVS_DIC["output_incident_power"]] = {"type": "float", "prec": 2, "unit": "dB"}
PVs[OFFSET_PVS_DIC["output_reflected_power"]] = {"type": "float", "prec": 2, "unit": "dB"}


PVs[ALARMS_PVS_DIC["general_power_lim_high"]] = {"type": "float", "prec": 4, "unit": "dB"}
PVs[ALARMS_PVS_DIC["general_power_lim_low"]] = {"type": "float", "prec": 4, "unit": "dB"}
PVs[ALARMS_PVS_DIC["inner_power_lim_high"]] = {"type": "float", "prec": 4, "unit": "dB"}
PVs[ALARMS_PVS_DIC["inner_power_lim_low"]] = {"type": "float", "prec": 4, "unit": "dB"}
PVs[ALARMS_PVS_DIC["current_lim_high"]] = {"type": "float", "prec": 4, "unit": "A"}
PVs[ALARMS_PVS_DIC["current_lim_low"]] = {"type": "float", "prec": 4, "unit": "A"}

PVs[CONF_PV + ":" + SAVE] = {"type": "int"}

if SHOW_DEBUG_INFO:
    print("###################")
    print("###### PVS !!!#####")
    for k, v in PVs.items():
        print("{}".format(k))
    print("###################")


class RF_BSSA_Driver(Driver):
    '''
        pcaspy driver class for this application
    '''

    def __init__(self):
        '''
            Superclass constructor
        '''

        Driver.__init__(self)

        # Try to load power offset parameters from the "parameters.db" file. If it fails, a new file
        # is created.

        if os.path.isfile(OFFSET_DB_FILENAME):
            self.power_offsets = pickle.load(open(OFFSET_DB_FILENAME, "rb"))
            self.alarm_offsets = pickle.load(open(ALARM_DB_FILENAME, "rb"))
        else:
            self.power_offsets = {"bar_upper_incident_power": 0.0,
                                  "bar_upper_reflected_power": 0.0,
                                  "bar_lower_incident_power": 0.0,
                                  "bar_lower_reflected_power": 0.0,
                                  "input_incident_power": 0.0,
                                  "input_reflected_power": 0.0,
                                  "output_incident_power": 0.0,
                                  "output_reflected_power": 0.0}

            self.alarm_offsets = {
                "general_power_lim_high": 100.0,
                "general_power_lim_low": -100.0,
                "inner_power_lim_high": 50.0,
                "inner_power_lim_low": -50.0,
                "current_lim_high": 100.0,
                "current_lim_low": -100.0
            }

            pickle.dump(self.power_offsets, open(OFFSET_DB_FILENAME, "wb+"))
            pickle.dump(self.alarm_offsets, open(ALARM_DB_FILENAME, "wb+"))

        # Here all PVs related to power offset parameters are initialized
        self.resetDbParams()
        self.setParam(OFFSET_PVS_DIC["bar_upper_incident_power"],
                      self.power_offsets["bar_upper_incident_power"])
        self.setParam(OFFSET_PVS_DIC["bar_upper_reflected_power"],
                      self.power_offsets["bar_upper_reflected_power"])
        self.setParam(OFFSET_PVS_DIC["bar_lower_incident_power"],
                      self.power_offsets["bar_lower_incident_power"])
        self.setParam(OFFSET_PVS_DIC["bar_lower_reflected_power"],
                      self.power_offsets["bar_lower_reflected_power"])
        self.setParam(OFFSET_PVS_DIC["input_incident_power"],
                      self.power_offsets["input_incident_power"])
        self.setParam(OFFSET_PVS_DIC["input_reflected_power"],
                      self.power_offsets["input_reflected_power"])
        self.setParam(OFFSET_PVS_DIC["output_incident_power"],
                      self.power_offsets["output_incident_power"])
        self.setParam(OFFSET_PVS_DIC["output_reflected_power"],
                      self.power_offsets["output_reflected_power"])

        self.setParam(ALARMS_PVS_DIC["general_power_lim_high"], self.alarm_offsets["general_power_lim_high"])
        self.setParam(ALARMS_PVS_DIC["general_power_lim_low"], self.alarm_offsets["general_power_lim_low"])
        self.setParam(ALARMS_PVS_DIC["inner_power_lim_high"], self.alarm_offsets["inner_power_lim_high"])
        self.setParam(ALARMS_PVS_DIC["inner_power_lim_low"], self.alarm_offsets["inner_power_lim_low"])
        self.setParam(ALARMS_PVS_DIC["current_lim_high"], self.alarm_offsets["current_lim_high"])
        self.setParam(ALARMS_PVS_DIC["current_lim_low"], self.alarm_offsets["current_lim_low"])
        # Queue with all operations that must be executed over the data acquisition system of Sirius
        # booster RF system. In practice, there is only one type of operation: the one that reads
        # all the parameters of the amplifiers in a single request.

        self.queue = Queue()

        # Event object for operations timing

        self.event = threading.Event()

        # Two auxiliary threads are created and launched

        self.process = threading.Thread(target=self.processThread)
        self.scan = threading.Thread(target=self.scanThread)

        self.TIME_NOW = time.time()
        self.sec_per_f = 0
        self.transmission_failures = 0
        self.timeouts = 0
        self.oks = 0

        self.process.setDaemon(True)
        self.scan.setDaemon(True)

        self.process.start()
        self.scan.start()

    def resetDbParams(self):
        for k, pv_name in OFFSET_PVS_DIC.items():
            self.setParamStatus(pv_name, Alarm.NO_ALARM, Severity.NO_ALARM)
            pass
        for k, pv_name in ALARMS_PVS_DIC.items():
            self.setParamStatus(pv_name, Alarm.NO_ALARM, Severity.NO_ALARM)
            pass

    # This thread adds to the queue a new reading procedure once a second
    def scanThread(self):

        while True:
            self.queue.put(READ_PARAMETERS)
            self.event.wait(SCAN_TIMER)

    # Thread for queue processing

    def processThread(self):

        # Serial interface initialization
        while True:

            # Here the next operation in queue is obtained and processed
            queue_item = self.queue.get(block=True)

            # Operation for parameters reading
            if queue_item == READ_PARAMETERS:
                try:
                    # A new request is sent to the data acquisition hardware of the solid-state
                    # amplifiers.

                    get_serial_interface.write(READ_MSG)

                    # This routine reads the stream returned by the data acquisition hardware until a
                    # timeout of 100 ms (approximately) is exceeded.
                    answer = ""
                    byte = get_serial_interface.read(1)
                    stop = False
                        while not stop:
                        answer += byte.decode('utf-8')
                        byte = get_serial_interface.read(1)
                        stop = answer.endswith(END_OF_STREAM)

                    if SHOW_DEBUG_INFO:
                        if self.oks + self.transmission_failures != 0:
                            print("ok={} f={} s/f={} tout={} ok%={}").format(self.oks, self.transmission_failures,
                                                                            self.sec_per_f, self.timeouts,
                                                                            self.oks * 100 / (
                                                                                    self.oks + self.transmission_failures))

                    # If the device didn't answer, "TIMETOUT INVALID" is defined as the alarm state for
                    # all device monitoring PVs.
                    if len(answer) == 0:
                        if SHOW_DEBUG_INFO:
                            self.timeouts += 1
                        if SHOW_DEBUG_INFO:
                            self.timeouts += 1
                        for pv_key, pv_name in BAR_PVS.items():
                            if ((self.pvDB[pv_name].alarm != Alarm.TIMEOUT_ALARM)
                                    or (self.pvDB[pv_name].severity != Severity.INVALID_ALARM)):
                                # This is used only to update the PV timestamp
                                self.setParam(pv_name, self.getParam(pv_name))
                                # Then the alarm condition is set for the PV
                                self.setParamStatus(pv_name, Alarm.TIMEOUT_ALARM, Severity.INVALID_ALARM)
                            pass
                    else:

                        # Received message verification and processing
                        parameters = self.verifyStream(answer)
                        if not parameters:
                            if SHOW_DEBUG_INFO:
                                self.transmission_failures += 1
                                self.sec_per_f = (time.time() - self.TIME_NOW) / self.transmission_failures

                            # If the device answered, but the received message doesn't match the
                            # expected pattern, "READ INVALID" is defined as the alarm state for all
                            # device monitoring PVs.
                            for pv_key, pv_name in BAR_PVS.items():
                                if ((self.pvDB[pv_name].alarm != Alarm.READ_ALARM) or (
                                        self.pvDB[pv_name].severity != Severity.INVALID_ALARM)):
                                    # This is used only to update the PV timestamp
                                    self.setParam(pv_name, self.getParam(pv_name))

                                    # Then the alarm condition is set for the PV
                                    self.setParamStatus(pv_name, Alarm.READ_ALARM, Severity.INVALID_ALARM)

                        else:
                            if SHOW_DEBUG_INFO:
                                self.oks += 1
                            # Otherwise, it's time to update all PV values and alarm states
                            self.setParam(STATE_PV, parameters[0])

                            for bar in range(1, 7):
                                base_index = ((bar - 1) * 38)
                                for bar_item in range(1, 39):
                                    if (bar in [2, 5]) and (bar_item in [1, 2]):
                                        continue
                                    pv_name = get_bar_pv_name(heatsink_num=bar, reading_item_num=bar_item)
                                    new_value = parameters[base_index + bar_item]
                                    if bar_item == 35:
                                        new_value += self.getParam(OFFSET_PVS_DIC["bar_lower_reflected_power"])
                                    elif bar_item == 36:
                                        new_value += self.getParam(OFFSET_PVS_DIC["bar_lower_incident_power"])
                                    elif bar_item == 37:
                                        new_value += self.getParam(OFFSET_PVS_DIC["bar_upper_reflected_power"])
                                    elif bar_item == 38:
                                        new_value += self.getParam(OFFSET_PVS_DIC["bar_upper_incident_power"])
                                    if ((self.pvDB[pv_name].severity == Severity.INVALID_ALARM) or (
                                            self.pvDB[pv_name].value != new_value)):
                                        self.setParam(pv_name, new_value)

                                    if bar_item in range(1, 35):
                                        low, high = self.getParam(
                                            ALARMS_PVS_DIC["current_lim_low"]), self.getParam(
                                            ALARMS_PVS_DIC["current_lim_high"])
                                    else:
                                        low, high = self.getParam(
                                            ALARMS_PVS_DIC["inner_power_lim_low"]), self.getParam(
                                            ALARMS_PVS_DIC["inner_power_lim_high"])

                                    low, high = flip_low_high(low,high)

                                    if not low < new_value < high:
                                        self.setParamStatus(pv_name, Alarm.READ_ALARM, Severity.MAJOR_ALARM)
                                    else:
                                        self.setParamStatus(pv_name, Alarm.NO_ALARM, Severity.NO_ALARM)

                            for bar_item in range(1, 5):
                                pv_name = get_bar_pv_name(heatsink_num=9, reading_item_num=bar_item)

                                low, high = self.getParam(ALARMS_PVS_DIC["general_power_lim_low"]), self.getParam(
                                    ALARMS_PVS_DIC["general_power_lim_high"])
                                
                                low, high = flip_low_high(low,high)

                                new_value = parameters[(-1) * bar_item]
                                if bar_item == 1:
                                    new_value += self.getParam(OFFSET_PVS_DIC["output_incident_power"])
                                elif bar_item == 2:
                                    new_value += self.getParam(OFFSET_PVS_DIC["output_reflected_power"])
                                elif bar_item == 3:
                                    new_value += self.getParam(OFFSET_PVS_DIC["input_incident_power"])
                                elif bar_item == 4:
                                    new_value += self.getParam(OFFSET_PVS_DIC["input_reflected_power"])
                                if ((self.pvDB[pv_name].severity == Severity.INVALID_ALARM) or (
                                        self.pvDB[pv_name].value != new_value)):
                                    self.setParam(pv_name, new_value)

                                    if not low < new_value < high:
                                        self.setParamStatus(pv_name, Alarm.READ_ALARM, Severity.MAJOR_ALARM)
                                    else:
                                        self.setParamStatus(pv_name, Alarm.NO_ALARM, Severity.NO_ALARM)

                    # Finally, all connected clients are notified if something changed
                    self.updatePVs()
                except:
                    # Exception has been raised! Try to refresh the serial connection
                    print('[ERROR] Main Loop Exception:\n{}'.format(traceback.format_exc()))

                    while not refresh_serial_connection():
                        # Loop untill success
                        time.sleep(TIME_RECONNECT)

    # This thread is used to save new offset parameters to the database ("parameters.db" file)
    def saveThread(self):
        self.power_offsets["bar_upper_incident_power"] = self.getParam(
            OFFSET_PVS_DIC["bar_upper_incident_power"])
        self.power_offsets["bar_upper_reflected_power"] = self.getParam(
            OFFSET_PVS_DIC["bar_upper_reflected_power"])
        self.power_offsets["bar_lower_incident_power"] = self.getParam(
            OFFSET_PVS_DIC["bar_lower_incident_power"])
        self.power_offsets["bar_lower_reflected_power"] = self.getParam(
            OFFSET_PVS_DIC["bar_lower_reflected_power"])
        self.power_offsets["input_incident_power"] = self.getParam(
            OFFSET_PVS_DIC["input_incident_power"])
        self.power_offsets["input_reflected_power"] = self.getParam(
            OFFSET_PVS_DIC["input_reflected_power"])
        self.power_offsets["output_incident_power"] = self.getParam(
            OFFSET_PVS_DIC["output_incident_power"])
        self.power_offsets["output_reflected_power"] = self.getParam(
            OFFSET_PVS_DIC["output_reflected_power"])

        pickle.dump(self.power_offsets, open(OFFSET_DB_FILENAME, "wb"))

        self.alarm_offsets["general_power_lim_high"] = self.getParam(
            ALARMS_PVS_DIC["general_power_lim_high"])
        self.alarm_offsets["general_power_lim_low"] = self.getParam(
            ALARMS_PVS_DIC["general_power_lim_low"])
        self.alarm_offsets["inner_power_lim_high"] = self.getParam(
            ALARMS_PVS_DIC["inner_power_lim_high"])
        self.alarm_offsets["inner_power_lim_low"] = self.getParam(
            ALARMS_PVS_DIC["inner_power_lim_low"])
        self.alarm_offsets["current_lim_high"] = self.getParam(
            ALARMS_PVS_DIC["current_lim_high"])
        self.alarm_offsets["current_lim_low"] = self.getParam(
            ALARMS_PVS_DIC["current_lim_low"])

        pickle.dump(self.alarm_offsets, open(ALARM_DB_FILENAME, "wb"))

    # Method for verifying the received stream and also for some calculations. It returns a Python
    # list with all the parameters of the RF system. If an empty list is returned, this means that
    # the received stream didn't match the expected pattern.

    def verifyStream(self, stream):

        # List with all parameters of the RF system
        parameters_list = []

        # First of all, the length of the received stream is verified
        if len(stream) != 2790:
            return []

        # The first token contains information about the on/off state of the system
        if (stream[:7] != "1S01000") or (stream[8] != ";"):
            return []
        else:
            if stream[7] == "0":
                parameters_list.append(0)
            elif stream[7] == "1":
                parameters_list.append(1)
            else:
                return []

        # The last token contains a signaling message
        if stream[-9:] != END_OF_STREAM:
            return []

        # Here all the other tokens of the stream are processed
        stream = stream[9:-9]

        # The ';' is used as a separator
        stream_list = stream.split(';')
        try:
            for chunk in stream_list:
                if chunk and len(chunk) > 0:
                    if len(chunk) != 8:
                        # Every piece must have 8 chars
                        print('[ERROR] Verify Stream Exception:\n{}'.format('not chunk or len(chunk) != 8'))
                        return []

                    if chunk[0] != '1':
                        # Must start with '1'
                        print('[ERROR] Verify Stream Exception:\n{}'.format('chunk[0] != \'1\''))
                        return []

                    bar_num = int(chunk[1])
                    bar_item = int(chunk[2:4])
                    adc_code = int(chunk[4:])

                    # If it's greater than this, something really wrong happened during the data transmission
                    if adc_code > 4095 or adc_code < 0:
                        print('[ERROR] Verify Stream Exception:\n{}'.format('adc_code > 4095'))
                        return []
                    
                    # Raw to voltage
                    voltage = convert_adc_to_voltage(adc_code=adc_code)

                    # Voltage to ...
                    if (bar_item <= 34) and (bar_num < 9):
                        # Current
                        # If the bar item is less or equal 34, this is a current reading! For every other case i'm reading Pdbm
                        parameters_list.append(calc_I(voltage))
                    else:
                        # P dbm
                        parameters_list.append(calc_Pdbm(voltage))

        except:
            # If anything is raised the stream is corrupted
            print('[ERROR] Verify Stream Exception:\n{}'.format(traceback.format_exc()))
            return []

        return parameters_list

    # This method is used only for power offset parameters configuration
    def write(self, reason, value):

        # OFFSET
        if reason == OFFSET_PVS_DIC["bar_upper_incident_power"]:
            self.setParam(reason, value)
            return True
        elif reason == OFFSET_PVS_DIC["bar_upper_reflected_power"]:
            self.setParam(reason, value)
            return True
        elif reason == OFFSET_PVS_DIC["bar_lower_incident_power"]:
            self.setParam(reason, value)
            return True
        elif reason == OFFSET_PVS_DIC["bar_lower_reflected_power"]:
            self.setParam(reason, value)
            return True
        elif reason == OFFSET_PVS_DIC["input_incident_power"]:
            self.setParam(reason, value)
            return True
        elif reason == OFFSET_PVS_DIC["input_reflected_power"]:
            self.setParam(reason, value)
            return True
        elif reason == OFFSET_PVS_DIC["output_incident_power"]:
            self.setParam(reason, value)
            return True
        elif reason == OFFSET_PVS_DIC["output_reflected_power"]:
            self.setParam(reason, value)
            return True

        # ALARMS
        elif reason == ALARMS_PVS_DIC["general_power_lim_high"]:
            self.setParam(reason, value)
            return True
        elif reason == ALARMS_PVS_DIC["general_power_lim_low"]:
            self.setParam(reason, value)
            return True
        elif reason == ALARMS_PVS_DIC["inner_power_lim_high"]:
            self.setParam(reason, value)
            return True
        elif reason == ALARMS_PVS_DIC["inner_power_lim_low"]:
            self.setParam(reason, value)
            return True
        elif reason == ALARMS_PVS_DIC["current_lim_high"]:
            self.setParam(reason, value)
            return True
        elif reason == ALARMS_PVS_DIC["current_lim_low"]:
            self.setParam(reason, value)
            return True

        elif reason == CONF_PV + ":" + SAVE:
            self.setParam(reason, self.getParam(CONF_PV + ":" + SAVE) + 1)
            self.save = threading.Thread(target=self.saveThread)
            self.save.setDaemon(True)
            self.save.start()
            return True
        else:
            return False


# Main routine
if __name__ == '__main__':
    CAserver = SimpleServer()
    CAserver.createPV("", PVs)
    driver = RF_BSSA_Driver()

    while True:
        CAserver.process(0.1)
