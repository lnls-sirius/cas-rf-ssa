#!/usr/bin/env python
import typing
import pandas
import math
from string import Template

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

"""
:param RACK: Rack read command (RACK1, RACK2, RACK3 or RACK4)
"""
raw_data = Template(
    """
record(waveform, "$(P)$(R)${RACK}RawData-Mon"){
    field(PINI, "YES")
    field(DESC, "SSA Data")
    field(SCAN, "$(SCAN=1) second")
    field(DTYP, "stream")
    field(INP,  "@SSAStorageRing.proto getData($(${RACK}=${RACK})) $(PORT) $(A)")
    field(FTVL, "STRING")
    field(NELM, "82")
    field(PHAS, "${N}")
}

record(scalcout, "$(P)$(R)${RACK}EOMCheck"){
    field(CALC, "AA='####FIM!'&BB='NO_ALARM'")
    field(INAA, "$(P)$(R)${RACK}RawData-Mon.VAL[81] CP MSS")
    field(INBB, "$(P)$(R)${RACK}RawData-Mon.STAT CP")
}"""
)

"""
:param RACK: Rack read command (RACK1, RACK2, RACK3 or RACK4)
"""
pwr_sts = Template(
    """
record(scalcout, "${PV}"){
    field(CALC, "AA[7,7]")
    field(INAA, "$(P)$(R)${RACK}RawData-Mon.VAL[0] CP MSS")
    field(DESC, "${D}")
}"""
)

"""
:param RACK: Rack read command (RACK1, RACK2, RACK3 or RACK4)
"""
ofs = Template(
    """
record(ao, "${PV}"){
    field(PINI, "YES")
    field(EGU,  "${EGU}")
    field(PREC, "2")
}
"""
)

"""
:param RACK: Rack read command (RACK1, RACK2, RACK3 or RACK4)
"""
alarm = Template(
    """
record(ao, "${PV}"){
    field(PINI, "YES")
    field(EGU,  "${EGU}")
    field(PREC, "2")
}
"""
)

alarm_record = Template(
    """
record(ao, "${PV}_HIHI"){
    field(OMSL, "closed_loop")
    field(DOL, "${HIHI} CP")
    field(OUT, "${PV}.HIHI")

    field(FLNK, "${PV}")
}

record(ao, "${PV}_HIGH"){
    field(OMSL, "closed_loop")
    field(DOL, "${HIGH} CP")
    field(OUT, "${PV}.HIGH")

    field(FLNK, "${PV}")
}

record(ao, "${PV}_LOW"){
    field(OMSL, "closed_loop")
    field(DOL, "${LOW} CP")
    field(OUT, "${PV}.LOW")

    field(FLNK, "${PV}")
}

record(ao, "${PV}_LOLO"){
    field(OMSL, "closed_loop")
    field(DOL, "${LOLO} CP")
    field(OUT, "${PV}.LOLO")

    field(FLNK, "${PV}")
}
"""
)

"""
:param PV:      PV name
:param RACK:    Rack read command (RACK1, RACK2, RACK3 or RACK4)
:param HIHI:    Alarm PV name
:param HIGH:    Alarm PV name
:param D:       Description text
:param OFS:     Offset PV name
:param N:       Reading block number
"""
current = Template(
    """
record(scalcout, "${PV}_v"){
    field(CALC, "(DBL(AA[4,7])/4095.0) * 5.0")
    field(INAA, "$(P)$(R)${RACK}RawData-Mon.VAL[${N}] CP MSS")

    field(EGU,  "V")
}

record(calc, "${PV}"){
    field(CALC, "(4.8321*A -2.4292)*1.09")
    field(INPA, "${PV}_v CP MSS")

    field(EGU,  "A")
    field(DESC, "${D}")
    field(PREC, "2")
    field(HHSV, "MAJOR")
    field(HSV,  "MINOR")
    field(LSV,  "MINOR")
    field(LLSV, "MAJOR")
}
"""
)


"""
:param PV:      PV name
:param RACK:    Rack read command (RACK1, RACK2, RACK3 or RACK4)
:param HIHI:    Alarm PV name
:param HIGH:    Alarm PV name
:param LOW:     Alarm PV name
:param LOLO:    Alarm PV name
:param D:       Description text
:param OFS:     Offset PV name
:param N:       Reading block number
"""
power = Template(
    """
record(scalcout, "${PV}_v"){
    field(CALC, "(DBL(AA[4,7])/4095.0) * 5.0")
    field(INAA, "$(P)$(R)${RACK}RawData-Mon.VAL[${N}] CP MSS")

    field(EGU,  "V")
}

record(calc, "${PV}"){
    field(CALC, "(10 * LOG((11.4*(A*A) + 1.7*A + 0.01))) + B")
    field(INPA, "${PV}_v CP MSS")
    field(INPB, "${OFS} CP ")

    field(EGU,  "dBm")
    field(DESC, "${D}")
    field(PREC, "2")

    field(HHSV, "MAJOR")
    field(HSV,  "MINOR")
    field(LSV,  "MINOR")
    field(LLSV, "MAJOR")
}
"""
)

"""
:param PV:      PV name
:param RACK:    Rack read command (RACK1, RACK2, RACK3 or RACK4)
:param HIHI:    Alarm PV name
:param HIGH:    Alarm PV name
:param LOW:     Alarm PV name
:param LOLO:    Alarm PV name
:param D:       Description text
:param OFS:     Offset PV name
:param N:       Reading block number
"""
power_general_eq1 = Template(
    """
record(scalcout, "${PV}_v"){
    field(CALC, "(DBL(AA[4,7])/4095.0) * 5.0")
    field(INAA, "$(P)$(R)${RACK}RawData-Mon.VAL[${N}] CP MSS")

    field(EGU,  "V")
}

record(calc, "${PV}_p1"){
    field(CALC, "5.51659e-2*A-7.96536e-3")
    field(INPA, "${PV}_v CP MSS")
}
record(calc, "${PV}"){
    field(CALC, "(10*LOG(((A**2)/100)/1e-3))+B") # EQ. 1 10*log10((((5.51659e-2*V - 7.96536e-3)**2)/100)/1e-3)
    field(INPA, "${PV}_p1 CP MSS")
    field(INPB, "${OFS} CP ")

    field(EGU,  "dBm")
    field(DESC, "${D}")
    field(PREC, "2")

    field(HHSV, "MAJOR")
    field(HSV,  "MINOR")
    field(LSV,  "MINOR")
    field(LLSV, "MAJOR")
}
"""
)

power_general_eq2 = Template(
    """
record(scalcout, "${PV}_v"){
    field(CALC, "(DBL(AA[4,7])/4095.0) * 5.0")
    field(INAA, "$(P)$(R)${RACK}RawData-Mon.VAL[${N}] CP MSS")

    field(EGU,  "V")
}

record(calc, "${PV}_p1"){
    field(CALC, "5.12714e-2*A-6.87733e-3")
    field(INPA, "${PV}_v CP MSS")
}
record(calc, "${PV}"){
    field(CALC, "(10*LOG(((A**2)/100)/1e-3))+B") # EQ. 2 10*log10((((5.12714e-2*V - 6,87733e-3)**2)/100)/1e-3)
    field(INPA, "${PV}_p1 CP MSS")
    field(INPB, "${OFS} CP ")

    field(EGU,  "dBm")
    field(DESC, "${D}")
    field(PREC, "2")

    field(HHSV, "MAJOR")
    field(HSV,  "MINOR")
    field(LSV,  "MINOR")
    field(LLSV, "MAJOR")
}
"""
)


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
            sheet_file, sheet_name=sheet_name, dtype=str, engine="openpyxl"
        )
        sheet = sheet.replace("nan", "")

        for index, row in sheet.iterrows():
            if type(row["Tower"]) == float and math.isnan(row["Tower"]):
                continue

            entries.append(Data(index, row, rack))
    return entries


def gen_raw_acquisition() -> str:
    db = ""
    for i in range(1, 5):
        db += raw_data.safe_substitute(RACK=f"RACK{i}", N=i)
    return db


def gen_settings(entries: typing.List[Data]) -> str:
    db = ""
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
        db += alarm.safe_substitute(
            PV=f"{entries[0].Sec}-{entries[0].Sub}{d['sufix']}", EGU=d["egu"]
        )
    return db


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


def gen_readings(entries: typing.List[Data]) -> str:
    db = ""
    # Readings
    for e in entries:

        kwargs = {}
        kwargs["PV"] = e.Device
        kwargs["N"] = e.index
        kwargs["D"] = e.Indicative
        kwargs["RACK"] = e.rack

        if e.index == 0:
            db += pwr_sts.safe_substitute(**kwargs)
            continue

        if e.HeatSink == "9":
            # General Power
            db += gen_general_power(e=e, kwargs=kwargs)
            continue

        if int(e.Reading) < 35:
            # Current
            db += gen_current(e=e, kwargs=kwargs)
            continue

        # Power
        db += gen_power(e=e, kwargs=kwargs)

    return db


if __name__ == "__main__":
    sheet_file = "../documentation/SSAStorageRing/Variáveis Aquisição Anel.xlsx"

    entries = load_data(file_name=sheet_file)

    db = gen_raw_acquisition()
    db += gen_settings(entries=entries)
    db += gen_readings(entries=entries)

    print(db)
