#! /bin/bash

# Setup edm environment
export EPICS_HOST_ARCH=linux-x86
source /reg/g/pcds/setup/epicsenv-3.14.12.sh

export IOC_PV=TST:GIGE:IOC134A
export CAM_PV=TST:GIGE:CAM134A
export HUTCH=TST
export PVLIST=tst.lst
edm -x -eolc	\
	-m "IOC=${IOC_PV}"	\
	-m "CAM=${CAM_PV}"	\
	-m "P=${CAM_PV},R=:"	\
	-m "HUTCH=${HUTCH}"	\
	-m "PVLIST=${PVLIST}"	\
	gigeScreens/gigeTop.edl  &

