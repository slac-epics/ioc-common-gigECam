#! /bin/bash

# Setup edm environment
export EPICS_HOST_ARCH=linux-x86
source /reg/g/pcds/setup/epicsenv-3.14.9.sh
export EPICS_CA_MAX_ARRAY_BYTES=8000000

export IOC_PV=LAS:IOC:GIGE:SXR:01
export CAM_R=01:
export CAM_P=LAS:GIGE:SXR:
edm -x -eolc	\
	-m "IOC=${IOC_PV},P=${CAM_P},R=${CAM_R}	\
	areaDetectorScreens/prosilica.edl &
