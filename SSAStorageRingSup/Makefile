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
	python3 $(TOP)/SSAStorageRingSup/ring.py > SSAStorageRing01.db
	cat $(TOP)/SSAStorageRingSup/SSAStorageRing.db | grep record | grep AlarmConfig | grep -Po  '(?<=")(.*?)(?="\){)' > $(TOP)/SSAStorageRingSup/SSAStorageRing01Alarms.req
	cat $(TOP)/SSAStorageRingSup/SSAStorageRing01.db | grep record | grep OffsetConfig | grep -Po  '(?<=")(.*?)(?="\){)' > $(TOP)/SSAStorageRingSup/SSAStorageRing01Offsets.req
	sed -e 's/RA-ToSIA01/RA-ToSIA02/g' SSAStorageRing01.db > SSAStorageRing02.db
	sed -e 's/RA-ToSIA01/RA-ToSIA02/g' SSAStorageRing01Offsets.req > SSAStorageRing02Offsets.req
	sed -e 's/RA-ToSIA01/RA-ToSIA02/g' SSAStorageRing01Alarms.req > SSAStorageRing02Alarms.req
#=======================================
include $(TOP)/configure/RULES
