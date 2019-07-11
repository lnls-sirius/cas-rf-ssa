TOP=..
include $(TOP)/configure/CONFIG
#=======================================

# Install .dbd and .db files
# SSAStorageRingAutosave.db
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRingAutosave.db
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing.db
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRing.proto

DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRingAlarms.req
DB_INSTALLS += $(TOP)/SSAStorageRingSup/SSAStorageRingOffsets.req

.PHONY: db
db:
	pip3 install -r requirements.txt
	python3 $(TOP)/SSAStorageRingSup/ring.py > SSAStorageRing.db
	cat $(TOP)/SSAStorageRingSup/SSAStorageRing.db | grep record | grep AlarmConfig | grep -Po  '(?<=")(.*?)(?="\){)' > $(TOP)/SSAStorageRingSup/SSAStorageRingAlarms.req
	cat $(TOP)/SSAStorageRingSup/SSAStorageRing.db | grep record | grep OffsetConfig | grep -Po  '(?<=")(.*?)(?="\){)' > $(TOP)/SSAStorageRingSup/SSAStorageRingOffsets.req

#=======================================
include $(TOP)/configure/RULES
