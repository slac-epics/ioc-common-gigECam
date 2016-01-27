TOP=../..
include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE

#----------------------------------------------------
# Create and install (or just install)
# databases, templates, substitutions like this

# Create and install Camera DB Files
DB += prosilica.db

# Prosilica cameras need to have their custom db and env files installed
PR_MODELS := $(wildcard $(ADPROSILICA)/db/*.env)
DB_INSTALLS += $(PR_MODELS)
DB_INSTALLS += $(subst .env,.template,$(PR_MODELS))

DB_INSTALLS += $(AUTOSAVE)/db/save_restoreStatus.db
DB_INSTALLS += $(EVENT2)/db/evrPmc230.db
DB_INSTALLS += $(EVENT2)/db/evrSLAC.db
DB_INSTALLS += $(IOCADMIN)/db/iocSoft.db
DB_INSTALLS += $(TIMESTAMPFIFO)/db/timeStampFifo.template

# Install ADStream db files
DB_INSTALLS += $(wildcard $(ADSTREAM)/db/*.db)

# Install ADStream cmd scripts
DB_INSTALLS += $(wildcard $(ADSTREAM)/db/*.cmd)

#----------------------------------------------------
# Create and install (or just install)
# Archive files, templates, substitutions like this
#
ARCHIVE += gige-ioc.archive

# Create and install archive Files
ARCHIVE += cross.tpl-arch
ARCHIVE += archive_evr_PMC.archive
ARCHIVE += archive_evr_SLAC.archive

#----------------------------------------------------
# Create and install (or just install)
# Autosave request files, templates, substitutions like this
#
REQ += gige-ioc.req

REQ += $(EVENT2)/autosave/eventCodeDelays.req

# Create and install autosave Files
REQ += cross.tpl-req
REQ += autosave_evr_PMC.req
REQ += autosave_evr_SLAC.req

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

