#! /bin/bash

# Setup edm environment
export EPICS_HOST_ARCH=linux-x86
source /reg/g/pcds/setup/epicsenv-3.14.9.sh
export EPICS_CA_MAX_ARRAY_BYTES=9000000

export IOC_PV=MEC:LAS:GIGE:IOC5
export CAM=MEC:LAS:GIGE:CAM5
export HUTCH=MEC
export PVLIST=mec.lst
edm -x -eolc	\
	-m "IOC=${IOC_PV}"	\
	-m "CAM=${CAM}"		\
	-m "P=${CAM},R=:"	\
	-m "HUTCH=${HUTCH}"	\
	-m "PVLIST=${PVLIST}"	\
	gigeScreens/gigeTop.edl  &
