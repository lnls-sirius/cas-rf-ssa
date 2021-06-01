TOP=..
include $(TOP)/configure/CONFIG
#=======================================

DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing.proto
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing01.db
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing01Alarms.req
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing01Offsets.req
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing02.db
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing02Alarms.req
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing02Offsets.req
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRingAutosave.db

db:
	$(shell ./build-database.sh $(TOP))
#=======================================
include $(TOP)/configure/RULES
