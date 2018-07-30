#!/usr/bin/python3
# -*- coding: utf-8 -*-
from Configs import SHOW_DEBUG_INFO as SHOW_DEBUG_INFO

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
    print("###### PVS !!!#####")
    for k, v in PVs.items():
        print("{}".format(k))
    print("###################")