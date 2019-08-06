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

.PHONY: db
db:
	pip3 install -r requirements.txt
	python3 ring.py > SSAStorageRing01.db
	cat SSAStorageRing01.db | grep record | grep AlarmConfig | grep -Po  '(?<=")(.*?)(?="\){)' > SSAStorageRing01Alarms.req
	cat SSAStorageRing01.db | grep record | grep OffsetConfig | grep -Po  '(?<=")(.*?)(?="\){)' > SSAStorageRing01Offsets.req
	sed -e 's/RA-ToSIA01/RA-ToSIA02/g' SSAStorageRing01.db > SSAStorageRing02.db
	sed -e 's/RA-ToSIA01/RA-ToSIA02/g' SSAStorageRing01Offsets.req > SSAStorageRing02Offsets.req
	sed -e 's/RA-ToSIA01/RA-ToSIA02/g' SSAStorageRing01Alarms.req > SSAStorageRing02Alarms.req
#=======================================
include $(TOP)/configure/RULES
