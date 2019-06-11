#!../../bin/linux-x86_64/SSA

## You may have to change SSA to something else
## everywhere it appears in this file

< envPaths

cd "${TOP}"

## Register all support components
dbLoadDatabase "dbd/SSA.dbd"
SSA_registerRecordDeviceDriver pdbbase

drvAsynIPPortConfigure("L0", "unix://${TOP}/SSATestingServer/socket")

dbLoadRecords("db/devSSABooster.db","P=Test,R=:,PORT=L0,A=0")

cd "${TOP}/iocBoot/${IOC}"
iocInit

# Enable debug
#var streamDebug 1
