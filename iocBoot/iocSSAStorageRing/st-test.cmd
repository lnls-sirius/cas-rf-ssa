#!../../bin/linux-x86_64/SSA

< envPaths

cd "${TOP}"

## Register all support components
dbLoadDatabase "dbd/SSA.dbd"
SSA_registerRecordDeviceDriver pdbbase

drvAsynIPPortConfigure("L0", "unix://${TOP}/SSATestingServer/socket")

epicsEnvSet("P","RA-ToSIA01")
epicsEnvSet("R",":")

dbLoadRecords("db/SSAStorageRing01.db", "P=$(P),R=$(R),RACK=RACK,PORT=L0,A=0")

cd "${TOP}/iocBoot/${IOC}"
iocInit

# Enable debug
#var streamDebug 1

cd "${TOP}"

seq &SSAStorageRingCurrentCalc "prefix=$(P)"
