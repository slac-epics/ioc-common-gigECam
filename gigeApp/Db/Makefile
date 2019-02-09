TOP=../..
include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE

DB_INSTALLS += $(EVENT2)/db/devEvrInfo.db

#----------------------------------------------------
# Create and install (or just install)
# databases, templates, substitutions like this
DB += timeStampEventCode.db
DB += netstat.template

DB_INSTALLS += $(AUTOSAVE)/db/save_restoreStatus.db
DB_INSTALLS += $(IOCADMIN)/db/iocSoft.db
DB_INSTALLS += $(IOCADMIN)/db/devIocInfo.db

# Create iocRelease.db
IOCRELEASE_DB	+=	iocRelease.db

ifdef EVENT2
DB_INSTALLS += $(EVENT2)/db/evrPmc230.db
DB_INSTALLS += $(EVENT2)/db/evrSLAC.db
DB_INSTALLS += $(EVENT2)/db/eventCodeDelays.db
ifdef TIMESTAMPFIFO
DB_INSTALLS += $(TIMESTAMPFIFO)/db/timeStampFifo.template
endif
endif

# Install ADStream db files
DB_INSTALLS += $(wildcard $(ADSTREAM)/db/*.db)

# Install ADStream cmd scripts
DB_INSTALLS += $(wildcard $(ADSTREAM)/db/*.cmd)

DB += ffmpegUsed.db
ifdef FFMPEGSERVER
# Install ffmpegServer files
DB_INSTALLS += $(wildcard $(FFMPEGSERVER)/db/plugin*.db)
DB_INSTALLS += $(wildcard $(FFMPEGSERVER)/db/plugin*.cmd)
endif

#
# Create and install Camera DB Files
DB += prosilica.db
ifdef ARAVISGIGE
DB += aravis.db
endif

# Aravis cameras need to have their custom db and env files installed
ARV_MODELS := $(wildcard $(ARAVISGIGE)/db/*.env)
DB_INSTALLS += $(ARV_MODELS)
DB_INSTALLS += $(subst .env,.template,$(ARV_MODELS))

# Prosilica cameras need to have their custom db and env files installed
PR_MODELS := $(wildcard $(ADPROSILICA)/db/*.env)
DB_INSTALLS += $(PR_MODELS)
DB_INSTALLS += $(subst .env,.template,$(PR_MODELS))

#----------------------------------------------------
# Create and install (or just install)
# Archive files, templates, substitutions like this
#
ARCHIVE += gige-ioc.archive

ifdef EVENT2
ARCHIVE += $(EVENT2)/archive/archive_evr_PMC.archive
ARCHIVE += $(EVENT2)/archive/archive_evr_SLAC.archive
endif

#----------------------------------------------------
# Create and install (or just install)
# Autosave request files, templates, substitutions like this
#
REQ += gige-ioc.req

ifdef EVENT2
# Create and install autosave Files
REQ += $(EVENT2)/autosave/eventCodeDelays.req
REQ += $(EVENT2)/autosave/autosave_evr_PMC.req
REQ += $(EVENT2)/autosave/autosave_evr_SLAC.req
endif

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

