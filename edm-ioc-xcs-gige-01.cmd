#! /bin/bash

# Setup edm environment
source /reg/g/pcds/setup/epicsenv-3.14.12.sh
export EPICS_CA_MAX_ARRAY_BYTES=9000000

export IOC_PV=XCS:R42:IOC:38
export CAM=XCS:GIGE:CAM1
export HUTCH=XCS
export PVLIST=xcs.lst
edm -x -eolc	\
	-m "IOC=${IOC_PV}"	\
	-m "CAM=${CAM}"		\
	-m "P=${CAM},R=:"	\
	-m "HUTCH=${HUTCH}"	\
	-m "PVLIST=${PVLIST}"	\
	gigeScreens/gigeTop.edl  &

