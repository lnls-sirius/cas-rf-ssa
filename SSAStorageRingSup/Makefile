TOP=..
include $(TOP)/configure/CONFIG
#=======================================

# Install .dbd and .db files
# SSAStorageRingAutosave.db
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRingAutosave.db
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing.proto
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing01.db
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing01Alarms.req
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing01Offsets.req
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing02.db
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing02Alarms.req
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing02Offsets.req

# It's expected a python3 virtual environent here './env/' !

db:
	$(shell ./build-database.sh $(TOP))
#=======================================
include $(TOP)/configure/RULES
