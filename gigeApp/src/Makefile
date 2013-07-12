TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

#=============================
# Build an ioc application

PROD_IOC = gige

# gige.dbd will be created and installed
DBD += gige.dbd

# gige.dbd will be made up from these files:
gige_DBD += base.dbd
gige_DBD += iocAdmin.dbd
gige_DBD += ADSupport.dbd
gige_DBD += asyn.dbd
gige_DBD += autosaveSupport.dbd
gige_DBD += busyRecord.dbd
gige_DBD += busySupport.dbd
gige_DBD += prosilicaApp.dbd
gige_DBD += prosilicaSupport.dbd
gige_DBD += sscan.dbd
gige_DBD += evrSupport.dbd
gige_DBD += devMrfEr.dbd

# <name>_registerRecordDeviceDriver.cpp will be created from <name>.dbd
gige_SRCS += gige_registerRecordDeviceDriver.cpp
gige_SRCS_DEFAULT += gigeMain.cpp

# Add locally compiled object code
#gige_SRCS += dbSubExample.c

# Add required libraries
gige_LIBS += prosilica
gige_LIBS += NDPlugin
gige_LIBS += ADBase
gige_LIBS += netCDF
gige_LIBS += calc
gige_LIBS += busy
gige_LIBS += sscan
gige_LIBS += autosave
gige_LIBS += asyn
gige_LIBS += recIoc
gige_LIBS += softDevIoc
gige_LIBS += miscIoc
gige_LIBS += rsrvIoc
gige_LIBS += dbtoolsIoc
gige_LIBS += asIoc
gige_LIBS += dbIoc
gige_LIBS += registryIoc
gige_LIBS += dbStaticIoc
gige_LIBS += ca
gige_LIBS += Com
gige_LIBS += PvAPI
gige_LIBS += NeXus
gige_LIBS += hdf5
gige_LIBS += sz
gige_SYS_LIBS += X11
gige_SYS_LIBS += xml2
gige_SYS_LIBS += tiff
gige_SYS_LIBS += jpeg
gige_SYS_LIBS += z

gige_LIBS += devIocStats
gige_LIBS += evrSupport
gige_LIBS += devMrfEr
gige_LIBS += drvMrf
gige_LIBS_Linux += mrfApi

gige_LIBS += $(EPICS_BASE_IOC_LIBS)

#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

