#!/usr/bin/env python3
import typing
import pandas
from string import Template

# V->I   return (4.8321*voltage - 2.4292)
# V->dBm return (10 * math.log10((11.4*(voltage*voltage) + 1.7*voltage + 0.01)))

raw_data = Template(
    """
record(waveform, "$(P)$(R)RawData-Mon"){
    field(PINI, "YES")
    field(DESC, "SSA Data")
    field(SCAN, "1 second")
    field(DTYP, "stream")
    field(INP,  "@SSABooster.proto getData($(TORRE=TORRE1)) $(PORT) $(A)")
    field(FTVL, "STRING")
    field(NELM, "310")
}

record(scalcout, "$(P)$(R)EOMCheck"){
    field(CALC, "AA='####FIM!'&BB='NO_ALARM'")
    field(INAA, "$(P)$(R)RawData-Mon.VAL[309] CP MSS")
    field(INBB, "$(P)$(R)EOMCheck.STAT CP")
}"""
)

pwr_sts = Template(
    """
record(scalcout, "${PV}"){
    field(CALC, "AA[7,7]")
    field(INAA, "$(P)$(R)RawData-Mon.VAL[0] CP MSS")
    field(DESC, "${D}")
}"""
)

ofs = Template(
    """
record(ao, "${PV}"){
    field(PINI, "YES")
    field(EGU,  "${EGU}")
    field(PREC, "2")
}
"""
)

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
    field(INAA, "$(P)$(R)RawData-Mon.VAL[${N}] CP MSS")

    field(EGU,  "V")
}

record(calc, "${PV}"){
    field(CALC, "(4.8321*A -2.4292)*1.2")
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
    field(INAA, "$(P)$(R)RawData-Mon.VAL[${N}] CP MSS")

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

total_dc_current = Template(
    """
record(ai, "${prefix}:RF-SSAmpTower:DCCurrent-Mon") {
    field(EGU,  "A")
    field(DESC, "Total DC Current")
    field(PREC, "2")
    field(SCAN, "Passive")
    field(PINI, "NO")
}
"""
)


class Data:
    def __init__(self, index, row):
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


if __name__ == "__main__":
    sheet = "../documentation/SSABooster/BO.xlsx"
    entries = load_entries(file_name=sheet)

    db = ""
    db += raw_data.safe_substitute()
    db += gen_settings(entries=entries)

    # Readings
    for e in entries:

        if e.Tower != "1":
            continue

        if e.Device == "" or type(e.Device) == float:
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
