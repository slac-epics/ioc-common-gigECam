TOP=../..
include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE

#----------------------------------------------------
#  Optimization of db files using dbst (DEFAULT: NO)
#DB_OPT = YES

#----------------------------------------------------
# Create and install (or just install)
# databases, templates, substitutions like this
##DB += iocAdmin.db

#----------------------------------------------------
# Create and install (or just install)
# Archive files, templates, substitutions like this
#
#ARCHIVE += archive_gige.archive
#ARCHIVE += ioc-xpp-gige-01.archive
#ARCHIVE += ioc-xpp-gige-02.archive

#----------------------------------------------------
# Create and install (or just install)
# Autosave request files, templates, substitutions like this
#
#REQ += autosave_gige.req
#REQ += ioc-xpp-gige-01.req
#REQ += ioc-xpp-gige-02.req
REQ += ioc-tst-gige1.req

# Nothing to build for autosave, just install from $AUTOSAVE/db
DB_INSTALLS += $(AUTOSAVE)/db/save_restoreStatus.db

include $(TOP)/configure/RULES
##include $(TOP)/configure/RULES.archive
##include $(TOP)/configure/RULES.autosave
#----------------------------------------
#  ADD RULES AFTER THIS LINE

