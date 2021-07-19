#!/usr/bin/env python3
import typing
import pandas

from .templates import (
    alarm,
    alarm_record,
    current,
    ofs,
    power,
    pwr_sts,
    raw_data,
    total_dc_current,
)


class Data:
    def __init__(self, index, row):
        self.index = index
        self.Tower = row["Tower"]
        self.HeatSink = row["HeatSink"]
        self.Reading = row["Reading"]
        self.Valor = row["Valor"]
        self.Sec = row["Sec"]
        self.Sub = row["Sub"]
        self.Dis = row["Dis"]
        self.Dev = row["Dev"]
        self.Idx = row["Idx"]
        self.Prop = row["Prop"]
        self.Device = row["Device Name"]
        self.Indicative = row["Indicative"]
        self.Module = row["Module"]


# Alarms
GENERAL_POWER_HIHI = ":AlarmConfig:GeneralPowerLimHiHi"
GENERAL_POWER_HIGH = ":AlarmConfig:GeneralPowerLimHigh"
GENERAL_POWER_LOW = ":AlarmConfig:GeneralPowerLimLow"
GENERAL_POWER_LOLO = ":AlarmConfig:GeneralPowerLimLoLo"

INNER_POWER_HIHI = ":AlarmConfig:InnerPowerLimHiHi"
INNER_POWER_HIGH = ":AlarmConfig:InnerPowerLimHigh"
INNER_POWER_LOW = ":AlarmConfig:InnerPowerLimLow"
INNER_POWER_LOLO = ":AlarmConfig:InnerPowerLimLoLo"

CURRENT_HIHI = ":AlarmConfig:CurrentLimHiHi"
CURRENT_HIGH = ":AlarmConfig:CurrentLimHigh"
CURRENT_LOW = ":AlarmConfig:CurrentLimLow"
CURRENT_LOLO = ":AlarmConfig:CurrentLimLoLo"

# Offset
BAR_UPPER_INCIDENT = ":OffsetConfig:UpperIncidentPower"
BAR_UPPER_REFLECTED = ":OffsetConfig:UpperReflectedPower"
BAR_LOWER_INCIDENT = ":OffsetConfig:LowerIncidentPower"
BAR_LOWER_REFLECTED = ":OffsetConfig:LowerReflectedPower"

INPUT_INCIDENT = ":OffsetConfig:InputIncidentPower"
INPUT_REFLECTED = ":OffsetConfig:InputReflectedPower"
OUTPUT_INCIDENT = ":OffsetConfig:OutputIncidentPower"
OUTPUT_REFLECTED = ":OffsetConfig:OutputReflectedPower"


def load_entries(file_name: str) -> typing.List[Data]:
    entries: typing.List[Data] = []
    sheet = pandas.read_excel(
        file_name, sheet_name="Plan1", dtype=str, engine="openpyxl"
    )
    sheet = sheet.replace("nan", "")

    for index, row in sheet.iterrows():
        entries.append(Data(index, row))
    return entries


def gen_settings(entries: typing.List[Data]) -> str:
    db = ""
    data = [
        # Alarms
        {"sufix": GENERAL_POWER_HIHI, "egu": "dBm"},
        {"sufix": GENERAL_POWER_HIGH, "egu": "dBm"},
        {"sufix": GENERAL_POWER_LOW, "egu": "dBm"},
        {"sufix": GENERAL_POWER_LOLO, "egu": "dBm"},
        {"sufix": INNER_POWER_HIHI, "egu": "dBm"},
        {"sufix": INNER_POWER_HIGH, "egu": "dBm"},
        {"sufix": INNER_POWER_LOW, "egu": "dBm"},
        {"sufix": INNER_POWER_LOLO, "egu": "dBm"},
        {"sufix": CURRENT_HIHI, "egu": "A"},
        {"sufix": CURRENT_HIGH, "egu": "A"},
        {"sufix": CURRENT_LOW, "egu": "A"},
        {"sufix": CURRENT_LOLO, "egu": "A"},
        # Offset
        {"sufix": BAR_UPPER_INCIDENT, "egu": "dBm"},
        {"sufix": BAR_UPPER_REFLECTED, "egu": "dBm"},
        {"sufix": BAR_LOWER_INCIDENT, "egu": "dBm"},
        {"sufix": BAR_LOWER_REFLECTED, "egu": "dBm"},
        {"sufix": INPUT_INCIDENT, "egu": "dBm"},
        {"sufix": INPUT_REFLECTED, "egu": "dBm"},
        {"sufix": OUTPUT_INCIDENT, "egu": "dBm"},
        {"sufix": OUTPUT_REFLECTED, "egu": "dBm"},
    ]
    for d in data:
        db += alarm.safe_substitute(
            **{"PV": f"{entries[0].Sec}-{entries[0].Sub}{d['sufix']}", "EGU": d["egu"]}
        )

    return db


def gen_general_power(e: Data, kwargs: dict) -> str:
    """
    PwrRevOut-Mon
    PwrFwdOut-Mon
    PwrRevIn-Mon
    PwrFwdIn-Mon
    """
    db = ""
    if int(e.Reading) == 1:
        kwargs["OFS"] = e.Sec + "-" + e.Sub + INPUT_REFLECTED
    elif int(e.Reading) == 2:
        kwargs["OFS"] = e.Sec + "-" + e.Sub + INPUT_INCIDENT
    elif int(e.Reading) == 3:
        kwargs["OFS"] = e.Sec + "-" + e.Sub + OUTPUT_REFLECTED
    elif int(e.Reading) == 4:
        kwargs["OFS"] = e.Sec + "-" + e.Sub + OUTPUT_INCIDENT
    kwargs["HIHI"] = e.Sec + "-" + e.Sub + GENERAL_POWER_HIHI
    kwargs["HIGH"] = e.Sec + "-" + e.Sub + GENERAL_POWER_HIGH
    kwargs["LOW"] = e.Sec + "-" + e.Sub + GENERAL_POWER_LOW
    kwargs["LOLO"] = e.Sec + "-" + e.Sub + GENERAL_POWER_LOLO
    db += alarm_record.safe_substitute(**kwargs)
    db += power.safe_substitute(**kwargs)
    return db


def gen_current(e: Data, kwargs: dict) -> str:
    db = ""
    kwargs["HIHI"] = e.Sec + "-" + e.Sub + CURRENT_HIHI
    kwargs["HIGH"] = e.Sec + "-" + e.Sub + CURRENT_HIGH
    kwargs["LOW"] = e.Sec + "-" + e.Sub + CURRENT_LOW
    kwargs["LOLO"] = e.Sec + "-" + e.Sub + CURRENT_LOLO
    db += alarm_record.safe_substitute(**kwargs)
    db += current.safe_substitute(**kwargs)
    return db


def gen_power(e: Data, kwargs: dict) -> str:
    db = ""
    if int(e.Reading) == 35:
        kwargs["OFS"] = e.Sec + "-" + e.Sub + BAR_LOWER_REFLECTED
    elif int(e.Reading) == 36:
        kwargs["OFS"] = e.Sec + "-" + e.Sub + BAR_LOWER_INCIDENT
    elif int(e.Reading) == 37:
        kwargs["OFS"] = e.Sec + "-" + e.Sub + BAR_UPPER_REFLECTED
    elif int(e.Reading) == 38:
        kwargs["OFS"] = e.Sec + "-" + e.Sub + BAR_UPPER_INCIDENT

    kwargs["HIHI"] = e.Sec + "-" + e.Sub + INNER_POWER_HIHI
    kwargs["HIGH"] = e.Sec + "-" + e.Sub + INNER_POWER_HIGH
    kwargs["LOW"] = e.Sec + "-" + e.Sub + INNER_POWER_LOW
    kwargs["LOLO"] = e.Sec + "-" + e.Sub + INNER_POWER_LOLO
    db += alarm_record.safe_substitute(**kwargs)
    db += power.safe_substitute(**kwargs)
    return db


def main():
    sheet = "../documentation/BO.xlsx"
    entries = load_entries(file_name=sheet)

    db = ""
    db += raw_data.safe_substitute()
    db += gen_settings(entries=entries)

    # Readings
    for e in entries:
        if e.Tower != "1":
            continue

        kwargs = {}
        kwargs["PV"] = e.Device
        kwargs["N"] = e.index
        kwargs["D"] = e.Indicative

        if e.index == 0:
            db += pwr_sts.safe_substitute(**kwargs)
            continue

        if e.HeatSink == "9":
            # General Power
            db += gen_general_power(e, kwargs=kwargs)
            continue

        if int(e.Reading) < 35:
            # Current
            db += gen_current(e, kwargs=kwargs)
            continue

        else:
            # Power
            db += gen_power(e, kwargs=kwargs)
            continue

    db += total_dc_current.safe_substitute(prefix=f"{entries[0].Sec}-{entries[0].Sub}")

    print(db)
