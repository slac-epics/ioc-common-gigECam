#! /bin/bash

# Setup edm environment
export EPICS_HOST_ARCH=linux-x86
source /reg/g/pcds/setup/epicsenv-3.14.9.sh
export EPICS_CA_MAX_ARRAY_BYTES=9000000

edm -x -eolc	\
	-m "IOC=SXR:IOC:GIGE:01,P=SXR:EXP:GIGE:,R=01:"	\
	areaDetectorScreens/prosilica.edl &
