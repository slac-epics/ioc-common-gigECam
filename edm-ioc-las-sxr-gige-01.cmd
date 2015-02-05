#! /bin/bash

# Setup edm environment
#export EPICS_HOST_ARCH=linux-x86
#source /reg/g/pcds/setup/epicsenv-3.14.9.sh
source /reg/g/pcds/setup/epicsenv-3.14.12.sh

export IOC_PV=LAS:IOC:GIGE:SXR:01
export CAM=LAS:GIGE:SXR:01
export HUTCH=LAS
export PVLIST=las.lst
edm -x -eolc	\
	-m "IOC=${IOC_PV}"	\
	-m "CAM=${CAM}"		\
	-m "P=${CAM},R=:"	\
	-m "HUTCH=${HUTCH}"	\
	-m "PVLIST=${PVLIST}"	\
	gigeScreens/gigeTop.edl  &

