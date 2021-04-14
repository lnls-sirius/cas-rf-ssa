#!/usr/bin/env python
import pandas
import math
from string import Template

"""
:param RACK: Rack read command (RACK1, RACK2, RACK3 or RACK4)
"""
raw_data = Template('''
record(waveform, "$(P)$(R)${RACK}RawData-Mon"){
    field(PINI, "YES")
    field(DESC, "SSA Data")
    field(SCAN, "1 second")
    field(DTYP, "stream")
    field(INP,  "@SSAStorageRing.proto getData($(${RACK}=${RACK})) $(PORT) $(A)")
    field(FTVL, "STRING")
    field(NELM, "82")
}

record(scalcout, "$(P)$(R)${RACK}EOMCheck"){
    field(CALC, "AA='####FIM!'&BB='NO_ALARM'")
    field(INAA, "$(P)$(R)${RACK}RawData-Mon.VAL[81] CP MSS")
    field(INBB, "$(P)$(R)${RACK}RawData-Mon.STAT CP")
}''')

"""
:param RACK: Rack read command (RACK1, RACK2, RACK3 or RACK4)
"""
pwr_sts = Template('''
record(scalcout, "${PV}"){
    field(CALC, "AA[7,7]")
    field(INAA, "$(P)$(R)${RACK}RawData-Mon.VAL[0] CP MSS")
    field(DESC, "${D}")
}''')

"""
:param RACK: Rack read command (RACK1, RACK2, RACK3 or RACK4)
"""
ofs = Template('''
record(ao, "${PV}"){
    field(PINI, "YES")
    field(EGU,  "${EGU}")
    field(PREC, "2")
}
''')

"""
:param RACK: Rack read command (RACK1, RACK2, RACK3 or RACK4)
"""
alarm = Template('''
record(ao, "${PV}"){
    field(PINI, "YES")
    field(EGU,  "${EGU}")
    field(PREC, "2")
}
''')

alarm_record = Template('''
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
''')

"""
:param PV:      PV name
:param RACK:    Rack read command (RACK1, RACK2, RACK3 or RACK4)
:param HIHI:    Alarm PV name
:param HIGH:    Alarm PV name
:param D:       Description text
:param OFS:     Offset PV name
:param N:       Reading block number
"""
current = Template('''
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
''')


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
power = Template('''
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
''')

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
power_general_eq1 = Template('''
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
''')

power_general_eq2 = Template('''
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
''')

class Data():
    def __init__(self, index, row, rack):
       self.index = index
       self.Tower = row['Tower']
       self.HeatSink = row['HeatSink']
       self.Reading = row['Reading']
       self.Valor = row['Valor']
       self.Sec = row['SEC']
       self.Sub = row['SUB']
       self.Dis = row['DIS']
       self.Dev = row['DEV']
       self.Idx = row['IDX']
       self.Prop = row['PROP']
       self.Device = row['Device Name']
       self.Indicative = row['Indicative']
       self.Module = row['Module']
       self.rack = rack


if __name__ == '__main__':
    sheet_file = '../documentation/SSAStorageRing/Variáveis Aquisição Anel.xlsx'

    entries = []
    db = ''

    for i in range(1,5):
        rack, sheet_name  ='RACK{}'.format(i), 'Rack{}'.format(i)
        sheet = pandas.read_excel(sheet_file, sheet_name=sheet_name, dtype=str)
        sheet = sheet.replace('nan', '')

        for index, row in sheet.iterrows():
            if type(row['Tower']) == float and math.isnan(row['Tower']):
                continue

            entries.append(Data(index, row, rack))

        db += raw_data.safe_substitute(RACK=rack)

    # Alarms
    GENERAL_POWER_HIHI  = ':AlarmConfig:GeneralPowerLimHiHi'
    GENERAL_POWER_HIGH  = ':AlarmConfig:GeneralPowerLimHigh'
    GENERAL_POWER_LOW   = ':AlarmConfig:GeneralPowerLimLow'
    GENERAL_POWER_LOLO  = ':AlarmConfig:GeneralPowerLimLoLo'

    INNER_POWER_HIHI    = ':AlarmConfig:InnerPowerLimHiHi'
    INNER_POWER_HIGH    = ':AlarmConfig:InnerPowerLimHigh'
    INNER_POWER_LOW     = ':AlarmConfig:InnerPowerLimLow'
    INNER_POWER_LOLO    = ':AlarmConfig:InnerPowerLimLoLo'

    CURRENT_HIHI        = ':AlarmConfig:CurrentLimHiHi'
    CURRENT_HIGH        = ':AlarmConfig:CurrentLimHigh'
    CURRENT_LOW         = ':AlarmConfig:CurrentLimLow'
    CURRENT_LOLO        = ':AlarmConfig:CurrentLimLoLo'


    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + GENERAL_POWER_HIHI, 'EGU': 'dBm'})
    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + GENERAL_POWER_HIGH, 'EGU': 'dBm'})
    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + GENERAL_POWER_LOW , 'EGU': 'dBm'})
    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + GENERAL_POWER_LOLO, 'EGU': 'dBm'})

    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + INNER_POWER_HIHI  , 'EGU': 'dBm'})
    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + INNER_POWER_HIGH  , 'EGU': 'dBm'})
    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + INNER_POWER_LOW   , 'EGU': 'dBm'})
    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + INNER_POWER_LOLO  , 'EGU': 'dBm'})

    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + CURRENT_HIHI      , 'EGU': 'A'})
    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + CURRENT_HIGH      , 'EGU': 'A'})
    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + CURRENT_LOW       , 'EGU': 'A'})
    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + CURRENT_LOLO      , 'EGU': 'A'})

    # Offset
    BAR_UPPER_INCIDENT  = ":OffsetConfig:UpperIncidentPower"
    BAR_UPPER_REFLECTED = ":OffsetConfig:UpperReflectedPower"
    BAR_LOWER_INCIDENT  = ":OffsetConfig:LowerIncidentPower"
    BAR_LOWER_REFLECTED = ":OffsetConfig:LowerReflectedPower"

    INPUT_INCIDENT      = ":OffsetConfig:InputIncidentPower"
    INPUT_REFLECTED     = ":OffsetConfig:InputReflectedPower"
    OUTPUT_INCIDENT     = ":OffsetConfig:OutputIncidentPower"
    OUTPUT_REFLECTED    = ":OffsetConfig:OutputReflectedPower"

    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + BAR_UPPER_INCIDENT , 'EGU': 'dBm'})
    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + BAR_UPPER_REFLECTED, 'EGU': 'dBm'})
    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + BAR_LOWER_INCIDENT , 'EGU': 'dBm'})
    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + BAR_LOWER_REFLECTED, 'EGU': 'dBm'})

    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + INPUT_INCIDENT     , 'EGU': 'dBm'})
    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + INPUT_REFLECTED    , 'EGU': 'dBm'})
    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + OUTPUT_INCIDENT    , 'EGU': 'dBm'})
    db += alarm.safe_substitute(**{'PV': entries[0].Sec + '-' + entries[0].Sub + OUTPUT_REFLECTED   , 'EGU': 'dBm'})

    # Readings
    for e in entries:

        kwargs = {}
        kwargs['PV']    = e.Device
        kwargs['N']     = e.index
        kwargs['D']     = e.Indicative
        kwargs['RACK']  = e.rack

        if e.index == 0:
            db += pwr_sts.safe_substitute(**kwargs)
            continue

        if e.HeatSink == '9':
            # General Power
            kwargs['HIHI'] = e.Sec + '-' + e.Sub + GENERAL_POWER_HIHI
            kwargs['HIGH'] = e.Sec + '-' + e.Sub + GENERAL_POWER_HIGH
            kwargs['LOW']  = e.Sec + '-' + e.Sub + GENERAL_POWER_LOW
            kwargs['LOLO'] = e.Sec + '-' + e.Sub + GENERAL_POWER_LOLO

            if int(e.Reading) in [1, 5, 9, 13]:
                kwargs['OFS'] = e.Sec + '-' + e.Sub + INPUT_INCIDENT
                db += power_general_eq1.safe_substitute(**kwargs)
            elif int(e.Reading) in [2, 6, 10, 14]:
                kwargs['OFS'] = e.Sec + '-' + e.Sub + INPUT_REFLECTED
                db += power_general_eq2.safe_substitute(**kwargs)

            elif int(e.Reading) in [3, 7, 11, 15]:
                kwargs['OFS'] = e.Sec + '-' + e.Sub + OUTPUT_INCIDENT
                db += power_general_eq2.safe_substitute(**kwargs)
            elif int(e.Reading) in [4, 8, 12, 16]:
                kwargs['OFS'] = e.Sec + '-' + e.Sub + OUTPUT_REFLECTED
                db += power_general_eq2.safe_substitute(**kwargs)

            db += alarm_record.safe_substitute(**kwargs)
            continue

        if int(e.Reading) < 35:
            # Current
            kwargs['HIHI'] = e.Sec + '-' + e.Sub + CURRENT_HIHI
            kwargs['HIGH'] = e.Sec + '-' + e.Sub + CURRENT_HIGH
            kwargs['LOW']  = e.Sec + '-' + e.Sub + CURRENT_LOW
            kwargs['LOLO'] = e.Sec + '-' + e.Sub + CURRENT_LOLO
            db += alarm_record.safe_substitute(**kwargs)
            db += current.safe_substitute(**kwargs)
            continue

        else:
            # Power
            if int(e.Reading) == 35:
                kwargs['OFS'] = e.Sec + '-' + e.Sub + BAR_LOWER_REFLECTED
            elif int(e.Reading) == 36:
                kwargs['OFS'] = e.Sec + '-' + e.Sub + BAR_LOWER_INCIDENT
            elif int(e.Reading) == 37:
                kwargs['OFS'] = e.Sec + '-' + e.Sub + BAR_UPPER_REFLECTED
            elif int(e.Reading) == 38:
                kwargs['OFS'] = e.Sec + '-' + e.Sub + BAR_UPPER_INCIDENT

            kwargs['HIHI'] = e.Sec + '-' + e.Sub + INNER_POWER_HIHI
            kwargs['HIGH'] = e.Sec + '-' + e.Sub + INNER_POWER_HIGH
            kwargs['LOW']  = e.Sec + '-' + e.Sub + INNER_POWER_LOW
            kwargs['LOLO'] = e.Sec + '-' + e.Sub + INNER_POWER_LOLO
            db += alarm_record.safe_substitute(**kwargs)
            db += power.safe_substitute(**kwargs)
            continue

    print(db)


