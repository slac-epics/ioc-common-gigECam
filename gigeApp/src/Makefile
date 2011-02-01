TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#  #=============================

#=============================
# Build an ioc application
# Use PROD_IOC_RTEMS for RTEMS only
# Use PROD_IOC_Linux for Linux only

PROD_IOC = gige

#
# gige.dbd will be created and installed
DBD += gige.dbd
#
# gige.dbd will be made up from these files:
gige_DBD += base.dbd
gige_DBD += iocAdmin.dbd
gige_DBD += autosaveSupport.dbd
gige_DBD += ADSupport.dbd
gige_DBD += abusyRecord.dbd
gige_DBD += pluginSupport.dbd
gige_DBD += prosilicaApp.dbd
gige_DBD += prosilicaSupport.dbd
#
# <name>_registerRecordDeviceDriver.cpp will be created from <name>.dbd
gige_SRCS += gige_registerRecordDeviceDriver.cpp
gige_SRCS_DEFAULT += gigeMain.cpp

#
# Add locally compiled object code
gige_LIBS += devIocStats
gige_LIBS += autosave
gige_LIBS += ImageLib
gige_LIBS += PvAPI
gige_LIBS += prosilica
gige_LIBS += calc
gige_LIBS += sscan
gige_LIBS += asyn
gige_LIBS += $(EPICS_BASE_IOC_LIBS)
#
#===========================
#
include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE
../../../lib/linux-x86_64/libImageLib.a:
	touch ../../../lib/linux-x86_64/libImageLib.a
