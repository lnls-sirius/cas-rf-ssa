TOP=..
include $(TOP)/configure/CONFIG
#=======================================

# Install .dbd and .db files SSABoosterAutosave.db
DB_INSTALLS += $(TOP)/SSABoosterSup/SSABooster.db
DB_INSTALLS += $(TOP)/SSABoosterSup/SSABooster.proto
DB_INSTALLS += $(TOP)/SSABoosterSup/SSABoosterAlarms.req
DB_INSTALLS += $(TOP)/SSABoosterSup/SSABoosterAutosave.db
DB_INSTALLS += $(TOP)/SSABoosterSup/SSABoosterOffsets.req

db-xlsx:
	$(shell ./build-database.sh $(TOP))

#=======================================
include $(TOP)/configure/RULES
