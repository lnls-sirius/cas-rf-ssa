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
