#!../../bin/linux-arm/SSA

< envPaths

cd "${TOP}"

## Register all support components
dbLoadDatabase "dbd/SSA.dbd"
SSA_registerRecordDeviceDriver pdbbase

drvAsynSerialPortConfigure("L0", "/dev/ttyUSB0")
asynSetOption("L0", 0, "baud", "500000")

epicsEnvSet("P","RA-ToSIA02")
epicsEnvSet("R",":")

dbLoadRecords("db/SSAStorageRingAutosave.db", "P=$(P),R=$(R)")
dbLoadRecords("db/SSAStorageRing.db"        , "P=$(P),R=$(R),RACK=RACK,PORT=L0,A=0")

#save_restoreSet_FilePermissions(0777)

set_savefile_path("$(TOP)/autosave/SSAStorageRing")
 
# Offsets
set_pass0_restoreFile("$(P)Offsets.sav")
set_pass1_restoreFile("$(P)Offsets.sav")

# Alarms
set_pass0_restoreFile("$(P)Alarms.sav")
set_pass1_restoreFile("$(P)Alarms.sav")

cd "${TOP}/iocBoot/${IOC}"
iocInit

# Enable debug
#var streamDebug 1

cd "${TOP}"
create_monitor_set("$(TOP)/db/SSAStorageRingAlarms.req",  10, "TOP=$(TOP), SAVENAMEPV=$(P)$(R)AlarmsSaveName")
create_monitor_set("$(TOP)/db/SSAStorageRingOffsets.req", 10, "TOP=$(TOP), SAVENAMEPV=$(P)$(R)OffsetsSaveName")
