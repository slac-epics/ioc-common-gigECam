TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

#=============================
# Build an ioc application
PROD_NAME = gige

PROD_IOC = $(PROD_NAME)

# $(PROD_NAME).dbd will be created and installed
DBD += $(PROD_NAME).dbd

# $(PROD_NAME).dbd will be made up from these files:
include $(ADCORE)/ADApp/commonDriverMakefile

# Network statistics
$(PROD_NAME)_DBD += netstat.dbd

# std ioc modules
$(PROD_NAME)_DBD += iocAdmin.dbd
$(PROD_NAME)_DBD += caPutLog.dbd

# pvaSrv
#$(PROD_NAME)_DBD += dbPv.dbd

ifdef EVENT2
# Timing and EVR
$(PROD_NAME)_DBD += diagTimer.dbd
$(PROD_NAME)_DBD += evrSupport.dbd
$(PROD_NAME)_DBD += devMrfEr.dbd

# ADCore timeStamp provider
$(PROD_NAME)_DBD += timeStampFifo.dbd
endif

gige_DBD += simDetectorSupport.dbd
gige_DBD += prosilicaSupport.dbd
ifdef ARAVISGIGE
gige_DBD += aravisCameraSupport.dbd
endif

# <name>_registerRecordDeviceDriver.cpp will be created from <name>.dbd
gige_SRCS += gige_registerRecordDeviceDriver.cpp
gige_SRCS_DEFAULT += gigeMain.cpp
gige_SRCS_DEFAULT += netstat.c

# Add locally compiled object code
#gige_SRCS += dbSubExample.c

# Add required libraries
# base and std modules
$(PROD_NAME)_LIBS += devIocStats
$(PROD_NAME)_LIBS += caPutLog

# pvaSrv
#$(PROD_NAME)_LIBS += pvaSrv

ifdef EVENT2
# ADCore Timestamp provider
$(PROD_NAME)_LIBS += timeStampFifo

# Timing and EVR
$(PROD_NAME)_LIBS += evrSupport
$(PROD_NAME)_LIBS += devMrfEr
$(PROD_NAME)_LIBS += drvMrf
$(PROD_NAME)_LIBS_Linux += mrfApi

# Diagnostics
$(PROD_NAME)_LIBS += diagTimer
endif

# Prosilica camera libs
gige_LIBS += prosilica
gige_LIBS += PvAPI

ifdef ARAVISGIGE
# aravis camera libs
gige_LIBS += aravisCamera
gige_LIBS += aravis-0.4
gige_LIBS += gio-2.0
gige_LIBS += gobject-2.0
gige_LIBS += gthread-2.0
gige_LIBS += gmodule-2.0
gige_LIBS += glib-2.0
gige_SYS_LIBS += resolv
PROD_LIBS += pcre
PROD_LIBS += ffi
endif

# areaDetector ADSimDetector
$(PROD_NAME)_LIBS += simDetector

ifdef FFMPEGSERVER
# ffmpegServer
$(PROD_NAME)_DBD += ffmpegServer.dbd
DB_INSTALLS += $(wildcard $(FFMPEGSERVER)/db/plugin*.cmd)
DB_INSTALLS += $(wildcard $(FFMPEGSERVER)/db/plugin*.db)
$(PROD_NAME)_LIBS += avdevice
$(PROD_NAME)_LIBS += ffmpegServer
$(PROD_NAME)_LIBS += swscale
$(PROD_NAME)_LIBS += avformat
$(PROD_NAME)_LIBS += avcodec
$(PROD_NAME)_LIBS += avutil
$(PROD_NAME)_LIBS += swresample
$(PROD_NAME)_LIBS += bz2
$(PROD_NAME)_LIBS += lzma
endif

#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

