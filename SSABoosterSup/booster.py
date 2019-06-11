#!/usr/bin/python3
import pandas
from string import Template

#V->I   return (4.8321*voltage - 2.4292)
#V->dBm return (10 * math.log10((11.4*(voltage*voltage) + 1.7*voltage + 0.01)))

raw_data = Template('''
record(waveform, "$(P)$(R)RawData-Mon"){
    field(PINI, "YES")
    field(DESC, "SSA Data")
    field(SCAN, "2 second")
    field(DTYP, "stream")
    field(INP,  "@devSSABooster.proto getData($(TORRE=TORRE1)) $(PORT) $(A)")
    field(FTVL, "STRING")
    field(NELM, "310")
}

record(scalcout, "$(P)$(R)EOMCheck"){
    field(CALC, "AA='####FIM!'&BB='NO_ALARM'")
    field(INAA, "$(P)$(R)RawData-Mon.VAL[309] CP MSS")
    field(INBB, "$(P)$(R)EOMCheck.STAT CP")
    field(DESC, "${D}")
}''')

pwr_sts = Template('''
record(scalcout, "${PV}"){
    field(CALC, "AA[7,7]")
    field(INAA, "$(P)$(R)RawData-Mon.VAL[0] CP MSS")
    field(DESC, "${D}")
}''')

ofs = Template('''
record(ao, "${PV}"){
    field(PINI, "YES")
    field(EGU,  "${EGU}")
    field(DESC, "${D}")
}
''')

alarm = Template('''
record(ao, "${PV}"){
    field(PINI, "YES")
    field(EGU,  "${EGU}")
}
''')


"""
:param PV:      PV name
:param HIHI:    Alarm PV name
:param HIGH:    Alarm PV name
:param D:       Description text
:param OFS:     Offset PV name
:param N:       Reading block number
"""
volt = Template('''
record(scalcout, "${PV}_v"){
    field(CALC, "(DBL(AA[4,7])/4095.0) * 5.0")
    field(INAA, "$(P)$(R)RawData-Mon.VAL[${N}] CP MSS")

    field(EGU,  "V")
}

record(calcout, "${PV}_HIHI"){
    field(CALC, "A")
    field(INPA, "${HIHI} CP")

    field(OUT, "${PV}.HIHI")
}

record(calcout, "${PV}_HIGH"){
    field(CALC, "A")
    field(INPA, "${HIGH} CP")

    field(OUT, "${PV}.HIGH")
}

record(calc, "${PV}"){
    field(CALC, "(4.8321*A -2.4292) + B")
    field(INPA, "${PV}_v CP MSS")
    field(INPB, "${OFS} CP")

    field(EGU,  "A")
    field(DESC, "${D}")

    field(HHSV, "MAJOR")
    field(HSV,  "MINOR")
    field(LSV,  "MINOR")
    field(LLSV, "MAJOR")
}
''')


"""
:param PV:      PV name
:param HIHI:    Alarm PV name
:param HIGH:    Alarm PV name
:param D:       Description text
:param OFS:     Offset PV name
:param N:       Reading block number
"""
power = Template('''
record(scalcout, "${PV}_v"){
    field(CALC, "(DBL(AA[4,7])/4095.0) * 5.0")
    field(INAA, "$(P)$(R)RawData-Mon.VAL[${N}] CP MSS")

    field(EGU,  "V")
}

record(calcout, "${PV}_HIHI"){
    field(CALC, "A")
    field(INPA, "${HIHI} CP")

    field(OUT, "${PV}.HIHI")
}

record(calcout, "${PV}_HIGH"){
    field(CALC, "A")
    field(INPA, "${HIGH} CP")

    field(OUT, "${PV}.HIGH")
}

record(calc, "${PV}"){
    field(CALC, "(10 * LOG((11.4*(A*A) + 1.7*A + 0.01))) + B")
    field(INPA, "${PV}_v CP MSS")
    field(INPB, "${OFS} CP ")

    field(EGU,  "dBm")
    field(DESC, "${D}")

    field(HHSV, "MAJOR")
    field(HSV,  "MINOR")
    field(LSV,  "MINOR")
    field(LLSV, "MAJOR")
}
''')

class Data():
    def __init__(self, index, row):
       self.index = index
       self.Tower = row['Tower'] 
       self.HeatSink = row['HeatSink'] 
       self.Reading = row['Reading'] 
       self.Valor = row['Valor'] 
       self.Sec = row['Sec'] 
       self.Sub = row['Sub'] 
       self.Dis = row['Dis'] 
       self.Dev = row['Dev'] 
       self.Idx = row['Idx'] 
       self.Prop = row['Prop'] 
       self.Device = row['Device Name'] 
       self.Indicative = row['Indicative'] 
       self.Module = row['Module'] 


if __name__ == '__main__':
    sheet = '../documentation/SSABooster/Variáveis Aquisição Booster.xlsx'
    entries = []
    sheet = pandas.read_excel(sheet, sheet_name='Plan1', dtype=str)
    sheet = sheet.replace('nan', '')

    for index, row in sheet.iterrows():
       entries.append(Data(index, row))
    
    db = ''
    db += raw_data.safe_substitute()
    
    #@todo: Print OFS and Alarms

    for e in entries:
        if e.Tower != '1':
            continue

        kwargs = {}
        kwargs['PV'] = e.Device
        kwargs['N'] = e.index
        kwargs['D'] = e.Indicative

        if e.index == 0:
            db += pwr_sts.safe_substitute(**kwargs)
            continue
        
        if e.HeatSink == '9':
            # General Power
            db += power.safe_substitute(**kwargs)
            continue

        if int(e.Reading) < 35:
            # Current
            db += volt.safe_substitute(**kwargs)
            continue

        else:
            # Power
            db += power.safe_substitute(**kwargs)
            continue

    print(db)


