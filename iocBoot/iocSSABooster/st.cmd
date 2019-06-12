#!../../bin/linux-x86_64/SSA

## You may have to change SSA to something else
## everywhere it appears in this file

< envPaths

cd "${TOP}"

## Register all support components
dbLoadDatabase "dbd/SSA.dbd"
SSA_registerRecordDeviceDriver pdbbase

drvAsynIPPortConfigure("L0", "unix://${TOP}/SSATestingServer/socket")

epicsEnvSet("P","RA-ToBO")
epicsEnvSet("R",":")

dbLoadRecords("db/SSABoosterAutosave.db","P=$(P),R=$(R)")
dbLoadRecords("db/SSABooster.db","P=$(P),R=$(R),TORRE=TORRE1,PORT=L0,A=0")

# Offsets
set_pass0_restoreFile("autosave/SSABooster/$(P)$(R)Offsets.sav")
set_pass1_restoreFile("autosave/SSABooster/$(P)$(R)Offsets.sav")

# Alarms
set_pass0_restoreFile("autosave/SSABooster/$(P)$(R)Alarms.sav")
set_pass1_restoreFile("autosave/SSABooster/$(P)$(R)Alarms.sav")

cd "${TOP}/iocBoot/${IOC}"
iocInit

# Enable debug
#var streamDebug 1

cd "${TOP}"
create_monitor_set("$(TOP)/db/SSABoosterAlarms.req",  10, "TOP=$(TOP), SAVENAMEPV=$(P)$(R)AlarmsSaveName")
create_monitor_set("$(TOP)/db/SSABoosterOffsets.req", 10, "TOP=$(TOP), SAVENAMEPV=$(P)$(R)OffsetsSaveName")
