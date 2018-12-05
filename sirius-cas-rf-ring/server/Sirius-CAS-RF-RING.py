#!/usr/bin/python3
# -*- coding: utf-8 -*-

class AtomicInteger():
    def __init__(self, value=0):
        self._value = value
        self._lock = threading.Lock()

    def inc(self):
        with self._lock:
            self._value += 1
            return self._value

    def dec(self):
        with self._lock:
            self._value -= 1
            return self._value


    @property
    def value(self):
        with self._lock:
            return self._value

    @value.setter
    def value(self, v):
        with self._lock:
            self._value = v
            return self._value

"""
SIRIUS-CAS-RF-RING

Channel Access server for the solid-state amplifiers of Sirius booster RF system.

This application sould run on the server side. 

"""
from pcaspy import Driver, Alarm, Severity, SimpleServer
from queue import Queue

from Calc import calc_I, calc_Pdbm, convert_adc_to_voltage, flip_low_high

import traceback
import time
import os
import pickle
import threading

import datetime

 
# This must be imported before pv.py !
from Configs import SHOW_DEBUG_INFO, READ_MSGS, \
    DB_FILENAME, ALARM_DB_FILENAME, END_OF_STREAM, \
    READ_PARAMETERS, SCAN_TIMER, TIME_RECONNECT, refresh_serial_connection
    


from pv import OFFSET_CONFIG_KEY,OFFSET_PVS_DIC, ALARMS_PVS_DIC, CONF_PV, STATE_PVS, \
    get_state_pv, get_heatsink_pv_name, RACK_PVS, SAVE, PVs

queue_counter = AtomicInteger()

class RF_BSSA_Driver(Driver):
    """
        pcaspy driver class for this application
    """

    def __init__(self):
        # Superclass constructor

        Driver.__init__(self)

        # Try to load power offset parameters from the "parameters.db" file. If it fails, a new file
        # is created.

        if os.path.isfile(DB_FILENAME):
            self.power_offsets = pickle.load(open(DB_FILENAME, "rb"))
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

            pickle.dump(self.power_offsets, open(DB_FILENAME, "wb+"))
            pickle.dump(self.alarm_offsets, open(ALARM_DB_FILENAME, "wb+"))

        self.resetAlarmStatus()

        # Here all PVs related to power offset parameters are initialized
        self.setParam(OFFSET_PVS_DIC["bar_upper_incident_power"], self.power_offsets["bar_upper_incident_power"])
        self.setParam(OFFSET_PVS_DIC["bar_upper_reflected_power"], self.power_offsets["bar_upper_reflected_power"])
        self.setParam(OFFSET_PVS_DIC["bar_lower_incident_power"], self.power_offsets["bar_lower_incident_power"])
        self.setParam(OFFSET_PVS_DIC["bar_lower_reflected_power"], self.power_offsets["bar_lower_reflected_power"])
        self.setParam(OFFSET_PVS_DIC["input_incident_power"], self.power_offsets["input_incident_power"])
        self.setParam(OFFSET_PVS_DIC["input_reflected_power"], self.power_offsets["input_reflected_power"])
        self.setParam(OFFSET_PVS_DIC["output_incident_power"], self.power_offsets["output_incident_power"])
        self.setParam(OFFSET_PVS_DIC["output_reflected_power"], self.power_offsets["output_reflected_power"])

        # Here PVs related to the alarm limits are set
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

        

 
    # This thread adds to the queue a new reading procedure once a second
    def scanThread(self):
        while True:
            self.queue.put(READ_PARAMETERS)
            # print('Inc={}'.format(queue_counter.inc()))
            self.event.wait(SCAN_TIMER)
 
    # Raise a timeout alarm for all monitoring variables
    def raiseTimoutAlarm(self):
        if SHOW_DEBUG_INFO:
            self.timeouts += 1
        for pv_key, pv_name in RACK_PVS.items():
            if ((self.pvDB[pv_name].alarm != Alarm.TIMEOUT_ALARM) or (self.pvDB[pv_name].severity != Severity.INVALID_ALARM)):
                # This is used only to update the PV timestamp
                self.setParam(pv_name, self.getParam(pv_name))
                # Then the alarm condition is set for the PV
                self.setParamStatus(pv_name, Alarm.TIMEOUT_ALARM, Severity.INVALID_ALARM)

    # Raise an invalid alarm for all monitoring variables
    def raiseInvalidAlarm(self):
        if SHOW_DEBUG_INFO:
            self.transmission_failures += 1
            self.sec_per_f = (time.time() - self.TIME_NOW) / self.transmission_failures

        # If the device answered, but the received message doesn't match the
        # expected pattern, "READ INVALID" is defined as the alarm state for all
        # device monitoring PVs.
        for pv_key, pv_name in RACK_PVS.items():
            if ((self.pvDB[pv_name].alarm != Alarm.READ_ALARM) or (self.pvDB[pv_name].severity != Severity.INVALID_ALARM)):
                # This is used only to update the PV timestamp
                self.setParam(pv_name, self.getParam(pv_name))

                # Then the alarm condition is set for the PV
                self.setParamStatus(pv_name, Alarm.READ_ALARM, Severity.INVALID_ALARM)

    # Thread for queue processing
    def processThread(self):
        while True:

            # tini = datetime.datetime.now()
            # Here the next operation in queue is obtained and processed
            queue_item = self.queue.get(block=True)
            # print('Dec={}'.format(queue_counter.dec()))

            # Operation for parameters reading
            if queue_item == READ_PARAMETERS:
                try:
                    for rack_message_num, rack_message, serial_interface in READ_MSGS:

                        if not serial_interface:
                            ''' 
                            "serial_interface" == None (not serial_interface) means that the serial
                            connection could not be established during the program initialization.
                            As this exception is raised, the timeout alarm is set and every x seconds, the program
                            will try to establish the required connection.
                            '''
                            raise Exception('Serial Interface == None')

                        # A new request is sent to the data acquisition hardware of the solid-state amplifiers.
                        if SHOW_DEBUG_INFO:
                           print("Serial Write {}".format(rack_message))
                        serial_interface.write(rack_message)

                        # This routine reads the stream returned by the data acquisition hardware until a timeout of 100 ms (approximately) is exceeded.
                        answer = ""                                                                                                                                                                                                                             
                        byte = (serial_interface.read(1)).decode('utf-8')
                        
                        stop = False
                        while not stop:
                            
                            answer += byte
                            byte = (serial_interface.read(1)).decode('utf-8')
                            # byte == "" is to support direct serial connections and answer.endswith(END_OF_STREAM) is used alongside socat
                            #stop = (byte == "" or answer.endswith(END_OF_STREAM))
                            stop = (byte == "" or answer.endswith(END_OF_STREAM))
                        
                        if SHOW_DEBUG_INFO:
                            print('{}'.format(answer))
                            if self.oks + self.transmission_failures != 0:
                                print("ok={}\tf={}\ts/f={}\ttout={}\tok%={}".format(self.oks, self.transmission_failures,
                                                                                self.sec_per_f, self.timeouts,
                                                                                self.oks * 100 / (self.oks + self.transmission_failures)))

                        
                        if len(answer) == 0:
                            # If the device didn't answer, "TIMETOUT INVALID" is defined as the alarm state for all device monitoring PVs.
                            self.raiseTimoutAlarm()
                        else:
                            # Received message verification and processing
                            parameters = self.verifyStream(answer, rack_message_num)

                            
                            if not parameters:
                                # If not, raise data invalid alarm
                                self.raiseInvalidAlarm()
                            else:
                                if SHOW_DEBUG_INFO:
                                    self.oks += 1

                                # Otherwise, it's time to update all PV values and alarm states
                                self.setParam(get_state_pv(rack_message_num), parameters[0])
                                if rack_message_num == 1:
                                    min, max = 1, 3
                                elif rack_message_num == 2:
                                    min, max = 3, 5
                                elif rack_message_num == 3:
                                    min, max = 5, 7
                                else:
                                    min, max = 7, 9

                                bar_aux = 1
                                for heatsink in range(min, max):
                                    base_index = ((bar_aux - 1) * 38)
                                    for bar_item in range(1, 39):
                                        pv_name = get_heatsink_pv_name(rack_num=rack_message_num, heatsink_num=heatsink, reading_item_num=bar_item)
                                        new_value = parameters[base_index + bar_item]
                                        if bar_item == 35:
                                            new_value += self.getParam(OFFSET_PVS_DIC["bar_upper_incident_power"])
                                            #new_value += self.getParam(OFFSET_PVS_DIC["bar_lower_reflected_power"])
                                        elif bar_item == 36:
                                            new_value += self.getParam(OFFSET_PVS_DIC["bar_upper_reflected_power"])
                                            #new_value += self.getParam(OFFSET_PVS_DIC["bar_lower_incident_power"])
                                        elif bar_item == 37:
                                            new_value += self.getParam(OFFSET_PVS_DIC["bar_lower_incident_power"])
                                            #new_value += self.getParam(OFFSET_PVS_DIC["bar_upper_reflected_power"])
                                        elif bar_item == 38:
                                            new_value += self.getParam(OFFSET_PVS_DIC["bar_lower_reflected_power"])
                                            #new_value += self.getParam(OFFSET_PVS_DIC["bar_upper_incident_power"])
                                        
                                        if ((self.pvDB[pv_name].severity == Severity.INVALID_ALARM) or (self.pvDB[pv_name].value != new_value)):
                                            
                                            self.setParam(pv_name, new_value)
                                        
                                            # Current Alarm
                                            if bar_item in range(1, 35):
                                                low, high = self.getParam(
                                                    ALARMS_PVS_DIC["current_lim_low"]), self.getParam(ALARMS_PVS_DIC["current_lim_high"])
                                            # Power Alarm
                                            else:
                                                low, high = self.getParam(ALARMS_PVS_DIC["inner_power_lim_low"]), self.getParam(ALARMS_PVS_DIC["inner_power_lim_high"])
                                            
                                            low, high = flip_low_high(low, high)

                                            # Set or reset the alarm status.
                                            if (new_value < low ) or (new_value > high):
                                                self.setParamStatus(pv_name, Alarm.READ_ALARM, Severity.MAJOR_ALARM)
                                            else:
                                                self.setParamStatus(pv_name, Alarm.NO_ALARM, Severity.NO_ALARM)
                                        # self.setParam(pv_name, new_value)
                                    
                                        # # Current Alarm
                                        # if bar_item in range(1, 35):
                                        #     low, high = self.getParam(
                                        #         ALARMS_PVS_DIC["current_lim_low"]), self.getParam(ALARMS_PVS_DIC["current_lim_high"])
                                        # # Power Alarm
                                        # else:
                                        #     low, high = self.getParam(ALARMS_PVS_DIC["inner_power_lim_low"]), self.getParam(ALARMS_PVS_DIC["inner_power_lim_high"])
                                        
                                        # low, high = flip_low_high(low, high)

                                        # # Set or reset the alarm status.
                                        # if (new_value < low ) or (new_value > high):
                                        #     self.setParamStatus(pv_name, Alarm.READ_ALARM, Severity.MAJOR_ALARM)
                                        # else:
                                        #     self.setParamStatus(pv_name, Alarm.NO_ALARM, Severity.NO_ALARM)
                                    bar_aux += 1

                                for bar_item in range(1, 5):
                                    # Read the overall power of the specified rack. This information os pesent on the 
                                    # 9th heatsink items [1,5[
                                    pv_name = get_heatsink_pv_name(rack_num=rack_message_num, heatsink_num=9,reading_item_num=bar_item)
                                    
                                    low, high = self.getParam(ALARMS_PVS_DIC["general_power_lim_low"]), self.getParam(
                                        ALARMS_PVS_DIC["general_power_lim_high"])
                                    
                                    low, high = flip_low_high(low, high)

                                    new_value = parameters[(-1) * bar_item]

                                    # Adding the required offsets
                                    if bar_item == 1:
                                        #new_value += self.getParam(OFFSET_PVS_DIC["input_incident_power"])
                                        new_value += self.getParam(OFFSET_PVS_DIC["output_reflected_power"])
                                    elif bar_item == 2:
                                        #new_value += self.getParam(OFFSET_PVS_DIC["input_reflected_power"])
                                        new_value += self.getParam(OFFSET_PVS_DIC["output_incident_power"])
                                    elif bar_item == 3:
                                        new_value += self.getParam(OFFSET_PVS_DIC["input_reflected_power"])
                                        #new_value += self.getParam(OFFSET_PVS_DIC["output_incident_power"])
                                    elif bar_item == 4:
                                        new_value += self.getParam(OFFSET_PVS_DIC["input_incident_power"])
                                        #new_value += self.getParam(OFFSET_PVS_DIC["output_reflected_power"])
                                    
                                    if ((self.pvDB[pv_name].severity == Severity.INVALID_ALARM) or (self.pvDB[pv_name].value != new_value)):

                                        self.setParam(pv_name, new_value)
                                        # Set or reset the alarm status
                                        if  (new_value < low ) or (new_value > high):
                                            self.setParamStatus(pv_name, Alarm.READ_ALARM, Severity.MAJOR_ALARM)
                                        else:
                                            self.setParamStatus(pv_name, Alarm.NO_ALARM, Severity.NO_ALARM) 
                                        


                                    # self.setParam(pv_name, new_value)

                                    # # Set or reset the alarm status
                                    # if  (new_value < low ) or (new_value > high):
                                    #     self.setParamStatus(pv_name, Alarm.READ_ALARM, Severity.MAJOR_ALARM)
                                    # else:
                                    #     self.setParamStatus(pv_name, Alarm.NO_ALARM, Severity.NO_ALARM) 
                                      
                    
                        # Finally, all connected clients are notified if something changed
                        self.updatePVs()

                except:
                    # Set the alarms
                    self.raiseTimoutAlarm()
                    self.updatePVs()
                    
                    while not refresh_serial_connection():
                        # Loop untill success
                        time.sleep(TIME_RECONNECT)
            
            # print('t={}'.format(datetime.datetime.now() - tini))

    # This thread is used to save new offset parameters to the database (.db files)
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

        pickle.dump(self.power_offsets, open(DB_FILENAME, "wb"))

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
    def verifyStream(self, stream, rack_message_num):

        # List with all parameters of the RF system
        parameters_list = []

        # First of all, the length of the received stream is verified
        if len(stream) != 738:
            return []

        # Some known characters in a healthy stream
        # if stream[8] != ";" or stream[3] != str(rack_message_num) or (
        #         stream[3] != "1" and stream[3] != "2" and stream[3] != "3" and stream[3] != "4"):
        #     return []
        # else:
        #     if stream[7] == "0":
        #         parameters_list.append(0)
        #     elif stream[7] == "1":
        #         parameters_list.append(1)
        #     else:
        #         return []
        # if stream[8] != ";" or stream[3] != str(rack_message_num) or (
        #         stream[3] != "1" and stream[3] != "2" and stream[3] != "3" and stream[3] != "4"):
        #     return []
        # else:
        if stream[7] == "0":
            parameters_list.append(0)
        elif stream[7] == "1":
            parameters_list.append(1)
        else:
            return []

        # The last token contains a signaling message
        # if stream[-9:] != END_OF_STREAM:
            # return []
        if not stream.endswith(END_OF_STREAM):
            return []

        # Here all the other tokens of the stream are processed
        stream = stream[9:-9]

        # Min and Max values are set according to wich rack is responding. 
        if rack_message_num == 1:
            # Bar 1,2 on Rack 1
            bars = [1,2,9]
        elif rack_message_num == 2:
            # Bar 3,4 on Rack 2
            bars = [3,4,9]
        elif rack_message_num == 3:
            # Bar 5,6 on Rack 3
            bars = [5,6,9]
        else:
            # Bar 7,8 on Rack 4
            bars = [7,8,9]

        # The ';' is used as a separator
        stream_list = stream.split(';')
        try:
            for chunk in stream_list:
                if chunk and len(chunk) > 0:
                    if len(chunk) != 8:
                        # Every piece must have 8 chars
                        print('[ERROR] Verify Stream Exception:\n{}'.format('not chunk or len(chunk) != 8'))
                        return []

                    if chunk[0] != '1' and chunk[0] != '2':
                        # Must start with '1' or '2'
                        print('[ERROR] Verify Stream Exception:\n{}'.format('chunk[0] != \'1\' and chunk[0] != \'2\' '))
                        return []

                    bar_num = int(chunk[1])
                    
                    # The bar is wrong
                    if not bar_num in bars:
                        print('[ERROR] Verify Stream Exception:\n{}'.format(' not bar_num in bars'))
                        return []

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
        
        # The length of a healthy stream is always 81
        if len(parameters_list) != 81:
            print('[ERROR] Verify Stream Exception:\n{}'.format('The paramters list does not have 81 items as expected.'))
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
    
    # Reset the alarm status
    def resetAlarmStatus(self):
        for k, pv_name in OFFSET_PVS_DIC.items():
            self.setParamStatus(pv_name, Alarm.NO_ALARM, Severity.NO_ALARM)
        for k, pv_name in ALARMS_PVS_DIC.items():
            self.setParamStatus(pv_name, Alarm.NO_ALARM, Severity.NO_ALARM)

# Main routine
if __name__ == '__main__':
    CAserver = SimpleServer()
    CAserver.createPV("", PVs)
    driver = RF_BSSA_Driver()

    while True:
        CAserver.process(0.1)
