TOP=..
include $(TOP)/configure/CONFIG
#=======================================

# Install .dbd and .db files SSABoosterAutosave.db
DB_INSTALLS += $(TOP)/SSABoosterSup/SSABooster.db
DB_INSTALLS += $(TOP)/SSABoosterSup/SSABooster.proto
DB_INSTALLS += $(TOP)/SSABoosterSup/SSABoosterAlarms.req
DB_INSTALLS += $(TOP)/SSABoosterSup/SSABoosterAutosave.db
DB_INSTALLS += $(TOP)/SSABoosterSup/SSABoosterOffsets.req

.PHONY: db
db:
	pip3 install -r requirements.txt
	python3 $(TOP)/SSABoosterSup/booster.py > SSABooster.db

	cat $(TOP)/SSABoosterSup/SSABooster.db | grep record | grep AlarmConfig | grep -Po  '(?<=")(.*?)(?="\){)'\
		>$(TOP)/SSABoosterSup/SSABoosterAlarms.req

	cat $(TOP)/SSABoosterSup/SSABooster.db | grep record | grep OffsetConfig | grep -Po  '(?<=")(.*?)(?="\){)'\
		>$(TOP)/SSABoosterSup/SSABoosterOffsets.req

#=======================================
include $(TOP)/configure/RULES
