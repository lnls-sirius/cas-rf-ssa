from string import Template


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
