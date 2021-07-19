TOP=..
include $(TOP)/configure/CONFIG
#=======================================

DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing.proto
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing01Alarms.req
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing01Offsets.req
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing02Alarms.req
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing02Offsets.req
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRingAutosave.db

DB_INSTALLS += SIRack1.db
DB_INSTALLS += SIRack2.db
DB_INSTALLS += SIRack3.db
DB_INSTALLS += SIRack4.db
DB_INSTALLS += SISettings.db
DB_INSTALLS += SITotalDcCurrent.db

db:
	$(shell ./build-database.sh $(TOP))
#=======================================
include $(TOP)/configure/RULES
