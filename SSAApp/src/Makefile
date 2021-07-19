TOP=../..

include $(TOP)/configure/CONFIG

PROD_IOC = SSA
# SSA.dbd will be created and installed
DBD += SSA.dbd

# SSA.dbd will be made up from these files:
SSA_DBD += base.dbd

SSA_DBD += asSupport.dbd
SSA_DBD += asyn.dbd
SSA_DBD += calcSupport.dbd
SSA_DBD += drvAsynIPPort.dbd
SSA_DBD += drvAsynSerialPort.dbd
SSA_DBD += editSseq.dbd
SSA_DBD += menuScan.dbd
SSA_DBD += stream.dbd
 
SSA_LIBS += asyn
SSA_LIBS += autosave
SSA_LIBS += calc
SSA_LIBS += pv
SSA_LIBS += seq
SSA_LIBS += stream

SSA_SNCFLAGS += -a # Synchronous pvGet: the program waits for completion.
SSA_SNCFLAGS += +c # Wait for process variables to connect before allowing the program to begin execution.
SSA_SNCFLAGS += +s # Safe Mode: variables are local to state set and must be communicated explicitly.

SSA_DBD  += SSAStorageRingCurrentCalc.dbd
SSA_SRCS += SSAStorageRingCurrentCalc.st

SSA_DBD  += SSABoosterCurrentCalc.dbd
SSA_SRCS += SSABoosterCurrentCalc.st

# SSA_registerRecordDeviceDriver.cpp derives from SSA.dbd
SSA_SRCS += SSA_registerRecordDeviceDriver.cpp

# Build the main IOC entry point on workstation OSs.
SSA_SRCS_DEFAULT += SSAMain.cpp
SSA_SRCS_vxWorks += -nil-

# Finally link to the EPICS Base libraries
SSA_LIBS += $(EPICS_BASE_IOC_LIBS)

#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

