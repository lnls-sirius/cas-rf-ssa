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

dbLoadRecords("db/SSAStorageRing02.db", "P=$(P),R=$(R),RACK=RACK,PORT=L0,A=0")

#save_restoreSet_FilePermissions(0777)

# Autosave settings
set_requestfile_path("$(TOP)", "autosave/SSAStorageRing")
set_savefile_path("$(TOP)/autosave/SSAStorageRing")

save_restoreSet_DatedBackupFiles(2)
save_restoreSet_NumSeqFiles(3)
save_restoreSet_SeqPeriodInSeconds(600)

set_savefile_path("$(TOP)/autosave/SSAStorageRing")

set_pass0_restoreFile("SSAStorageRing02.sav")
set_pass1_restoreFile("SSAStorageRing02.sav")

cd "${TOP}/iocBoot/${IOC}"
iocInit

# Enable debug
#var streamDebug 1

cd "${TOP}"
create_monitor_set("SSAStorageRing02.req",  10)
