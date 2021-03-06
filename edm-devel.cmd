#! /bin/bash

# Setup edm environment
export EPICS_HOST_ARCH=linux-x86
source /reg/g/pcds/setup/epicsenv-3.14.12.sh
source ~bhill/bin/epicsenv.bh.sh

export IOC_PV=SXR:EXP:IOC:GIGE:01
export CAM=SXR:EXP:GIGE:01
export HUTCH=SXR
export PVLIST=sxr.lst
edm -x -eolc	\
	-m "IOC=${IOC_PV}"	\
	-m "CAM=${CAM}"		\
	-m "P=${CAM},R=:"	\
	-m "HUTCH=${HUTCH}"	\
	-m "PVLIST=${PVLIST}"	\
	gigeScreens/gigeTop.edl  \
	areaDetectorScreens/prosilica.edl  &

#	gigeScreens/gigeTop.edl  \

