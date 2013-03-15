# Makefile to install the st.cmd into the correctly location.
# Author: Jason Tiller

TOP = ../..
include $(TOP)/configure/CONFIG
ARCH = linux-x86_64
TARGETS = envPaths

# Make sure these archive files are fully expanded
USR_ARCHIVEFLAGS += -V

#----------------------------------------------------
# Create and install IOC archive file
#
#ARCHIVE += ioc-mec-las-gige02.archive

#----------------------------------------------------
# Create and install IOC autosave file
#
#REQ += ioc-mec-las-gige02.req

# See RULES.copy for more information on these variables.
COPY_ONLY_IF_NON_LOCAL=1
COPY_SUBDIR=iocBoot/ioc-mec-las-gige03
COPY_FILES=st.cmd

include $(TOP)/configure/RULES
include $(TOP)/configure/RULES.ioc-targets
