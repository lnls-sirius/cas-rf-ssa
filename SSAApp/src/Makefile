TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

#=============================
# Build the IOC application

PROD_IOC = SSA
# SSA.dbd will be created and installed
DBD += SSA.dbd

# SSA.dbd will be made up from these files:
SSA_DBD += base.dbd

SSA_DBD += asSupport.dbd
SSA_DBD += calcSupport.dbd
SSA_DBD += asyn.dbd
SSA_DBD += stream.dbd
SSA_DBD += drvAsynSerialPort.dbd
SSA_DBD += drvAsynIPPort.dbd
SSA_DBD += menuScan.dbd
 
SSA_LIBS += autosave
SSA_LIBS += stream
SSA_LIBS += asyn
SSA_LIBS += calc

# SSA_registerRecordDeviceDriver.cpp derives from SSA.dbd
SSA_SRCS += SSA_registerRecordDeviceDriver.cpp

# Build the main IOC entry point on workstation OSs.
SSA_SRCS_DEFAULT += SSAMain.cpp
SSA_SRCS_vxWorks += -nil-

# Add support from base/src/vxWorks if needed
#SSA_OBJS_vxWorks += $(EPICS_BASE_BIN)/vxComLibrary

# Finally link to the EPICS Base libraries
SSA_LIBS += $(EPICS_BASE_IOC_LIBS)

#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

