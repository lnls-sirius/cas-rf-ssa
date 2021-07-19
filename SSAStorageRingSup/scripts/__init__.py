#!/usr/bin/env python
import enum
import math
import typing

import pandas

from .consts import (
    GENERAL_POWER_HIHI,
    GENERAL_POWER_HIGH,
    GENERAL_POWER_LOW,
    GENERAL_POWER_LOLO,
    INNER_POWER_HIHI,
    INNER_POWER_HIGH,
    INNER_POWER_LOW,
    INNER_POWER_LOLO,
    CURRENT_HIHI,
    CURRENT_HIGH,
    CURRENT_LOW,
    CURRENT_LOLO,
    # Offset
    BAR_UPPER_INCIDENT,
    BAR_UPPER_REFLECTED,
    BAR_LOWER_INCIDENT,
    BAR_LOWER_REFLECTED,
    INPUT_INCIDENT,
    INPUT_REFLECTED,
    OUTPUT_INCIDENT,
    OUTPUT_REFLECTED,
)
from .templates import (
    alarm,
    alarm_record,
    current,
    power,
    power_general_eq1,
    power_general_eq2,
    pwr_sts,
    total_dc_current,
    raw_data,
)


@enum.unique
class DatabaseType(str, enum.Enum):
    RACK1 = "RACK1"
    RACK2 = "RACK2"
    RACK3 = "RACK3"
    RACK4 = "RACK4"
    TOTAL_DC_CURRENT = "TOTAL_DC_CURRENT"
    SETTINGS = "SETTINGS"


class FileManager:
    def __init__(self):
        self._rack1 = open("SIRack1.db", "w+")
        self._rack2 = open("SIRack2.db", "w+")
        self._rack3 = open("SIRack3.db", "w+")
        self._rack4 = open("SIRack4.db", "w+")
        self._settings = open("SISettings.db", "w+")
        self._total_dc_current = open("SITotalDcCurrent.db", "w+")

    def write(self, data: str, database_type: typing.Union[str, DatabaseType]):
        io_obj: typing.Optional[typing.IO] = None
        if database_type == DatabaseType.RACK1:
            io_obj = self._rack1
        elif database_type == DatabaseType.RACK2:
            io_obj = self._rack2
        elif database_type == DatabaseType.RACK3:
            io_obj = self._rack3
        elif database_type == DatabaseType.RACK4:
            io_obj = self._rack4
        elif database_type == DatabaseType.SETTINGS:
            io_obj = self._settings
        elif database_type == DatabaseType.TOTAL_DC_CURRENT:
            io_obj = self._total_dc_current

        if not io_obj:
            raise RuntimeError("IO not defined")

        io_obj.writelines(data)
        print(database_type, io_obj)

    def close(self):
        self._rack1.close()
        self._rack2.close()
        self._rack3.close()
        self._rack4.close()
        self._settings.close()
        self._total_dc_current.close()


fm = FileManager()


class Data:
    def __init__(self, index, row, rack):
        self.index = index
        self.Tower = row["Tower"]
        self.HeatSink = row["HeatSink"]
        self.Reading = row["Reading"]
        self.Valor = row["Valor"]
        self.Sec = row["SEC"]
        self.Sub = row["SUB"]
        self.Dis = row["DIS"]
        self.Dev = row["DEV"]
        self.Idx = row["IDX"]
        self.Prop = row["PROP"]
        self.Device = row["Device Name"]
        self.Indicative = row["Indicative"]
        self.Module = row["Module"]
        self.rack = rack


def load_data(file_name: str) -> typing.List[Data]:
    entries: typing.List[Data] = []
    for i in range(1, 5):
        rack, sheet_name = "RACK{}".format(i), "Rack{}".format(i)
        sheet = pandas.read_excel(
            file_name, sheet_name=sheet_name, dtype=str, engine="openpyxl"
        )
        sheet = sheet.replace("nan", "")

        for index, row in sheet.iterrows():
            if type(row["Tower"]) == float and math.isnan(row["Tower"]):
                continue

            entries.append(Data(index, row, rack))
    return entries


def gen_raw_acquisition() -> None:
    for i in range(1, 5):
        rack = f"RACK{i}"
        data = raw_data.safe_substitute(RACK=rack, N=i)
        fm.write(data, rack)


def gen_settings(entries: typing.List[Data]) -> None:
    data = [
        # Limits
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
        _data = alarm.safe_substitute(
            PV=f"{entries[0].Sec}-{entries[0].Sub}{d['sufix']}", EGU=d["egu"]
        )
        fm.write(data=_data, database_type=DatabaseType.SETTINGS)


def gen_general_power(e: Data, kwargs: typing.Dict) -> str:
    db = ""
    # General Power
    kwargs["HIHI"] = f"{e.Sec}-{e.Sub}{GENERAL_POWER_HIHI}"
    kwargs["HIGH"] = f"{e.Sec}-{e.Sub}{GENERAL_POWER_HIGH}"
    kwargs["LOW"] = f"{e.Sec}-{e.Sub}{GENERAL_POWER_LOW}"
    kwargs["LOLO"] = f"{e.Sec}-{e.Sub}{GENERAL_POWER_LOLO}"

    if int(e.Reading) in [1, 5, 9, 13]:
        kwargs["OFS"] = f"{e.Sec}-{e.Sub}{INPUT_INCIDENT}"
        db += power_general_eq1.safe_substitute(**kwargs)
    elif int(e.Reading) in [2, 6, 10, 14]:
        kwargs["OFS"] = f"{e.Sec}-{e.Sub}{INPUT_REFLECTED}"
        db += power_general_eq2.safe_substitute(**kwargs)

    elif int(e.Reading) in [3, 7, 11, 15]:
        kwargs["OFS"] = f"{e.Sec}-{e.Sub}{OUTPUT_INCIDENT}"
        db += power_general_eq2.safe_substitute(**kwargs)
    elif int(e.Reading) in [4, 8, 12, 16]:
        kwargs["OFS"] = f"{e.Sec}-{e.Sub}{OUTPUT_REFLECTED}"
        db += power_general_eq2.safe_substitute(**kwargs)

    db += alarm_record.safe_substitute(**kwargs)
    return db


def gen_current(e: Data, kwargs: typing.Dict) -> str:
    db = ""
    kwargs["HIHI"] = f"{e.Sec}-{e.Sub}{CURRENT_HIHI}"
    kwargs["HIGH"] = f"{e.Sec}-{e.Sub}{CURRENT_HIGH}"
    kwargs["LOW"] = f"{e.Sec}-{e.Sub}{CURRENT_LOW}"
    kwargs["LOLO"] = f"{e.Sec}-{e.Sub}{CURRENT_LOLO}"
    db += alarm_record.safe_substitute(**kwargs)
    db += current.safe_substitute(**kwargs)
    return db


def gen_power(e: Data, kwargs: typing.Dict) -> str:
    db = ""
    if int(e.Reading) == 35:
        kwargs["OFS"] = f"{e.Sec}-{e.Sub}{BAR_LOWER_REFLECTED}"
    elif int(e.Reading) == 36:
        kwargs["OFS"] = f"{e.Sec}-{e.Sub}{BAR_LOWER_INCIDENT}"
    elif int(e.Reading) == 37:
        kwargs["OFS"] = f"{e.Sec}-{e.Sub}{BAR_UPPER_REFLECTED}"
    elif int(e.Reading) == 38:
        kwargs["OFS"] = f"{e.Sec}-{e.Sub}{BAR_UPPER_INCIDENT}"

    kwargs["HIHI"] = f"{e.Sec}-{e.Sub}{INNER_POWER_HIHI}"
    kwargs["HIGH"] = f"{e.Sec}-{e.Sub}{INNER_POWER_HIGH}"
    kwargs["LOW"] = f"{e.Sec}-{e.Sub}{INNER_POWER_LOW}"
    kwargs["LOLO"] = f"{e.Sec}-{e.Sub}{INNER_POWER_LOLO}"
    db += alarm_record.safe_substitute(**kwargs)
    db += power.safe_substitute(**kwargs)
    return db


def gen_readings(entries: typing.List[Data]) -> None:
    # Readings
    for e in entries:
        db = ""

        kwargs = {}
        kwargs["PV"] = e.Device
        kwargs["N"] = e.index
        kwargs["D"] = e.Indicative
        kwargs["RACK"] = e.rack

        if e.index == 0:
            db += pwr_sts.safe_substitute(**kwargs)
            fm.write(db, database_type=kwargs["RACK"])
            continue

        if e.HeatSink == "9":
            # General Power
            db += gen_general_power(e=e, kwargs=kwargs)
            fm.write(db, database_type=kwargs["RACK"])
            continue

        if int(e.Reading) < 35:
            # Current
            db += gen_current(e=e, kwargs=kwargs)
            fm.write(db, database_type=kwargs["RACK"])
            continue

        # Power
        db += gen_power(e=e, kwargs=kwargs)
        fm.write(db, database_type=kwargs["RACK"])


def gen_total_dc_current(entries):
    fm.write(
        total_dc_current.safe_substitute(prefix=f"{entries[0].Sec}-{entries[0].Sub}"),
        DatabaseType.TOTAL_DC_CURRENT,
    )
