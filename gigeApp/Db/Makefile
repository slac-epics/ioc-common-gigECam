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
#DB += xxx.db

# Generate db files from substitutions
##DB += iocAdmin.db

# Nothing to build, just install from autosave/db
DB_INSTALLS += $(AUTOSAVE)/db/save_restoreStatus.db

#----------------------------------------------------
# Create and install (or just install)
# Autosave request files, templates, substitutions like this
#
#REQ += autosave_gige.req
#REQ += ioc-xpp-gige-01.req
#REQ += ioc-xpp-gige-02.req
REQ += tst_gige1.req


#----------------------------------------------------
# Create and install (or just install)
# Archive files, templates, substitutions like this
#
ARCHIVE += archive_gige.archive

# This one gets installed from the edt_unix module so it
# can be used by msi expansion in iocBoot/<iocname>/Makefile
#ARCHIVE += ioc-xpp-gige-01.archive
#ARCHIVE += ioc-xpp-gige-02.archive

#----------------------------------------------------
# If <anyname>.db template is not named <anyname>*.template add
# <anyname>_template = <templatename>

include $(TOP)/configure/RULES
##include $(TOP)/configure/RULES.archive
##include $(TOP)/configure/RULES.autosave
#----------------------------------------
#  ADD RULES AFTER THIS LINE

