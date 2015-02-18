#! /bin/bash

# Setup edm environment
source /reg/g/pcds/setup/epicsenv-3.14.12.sh

export IOC_PV=AMO:IOC:GIGE:01
export CAM=AMO:EXP:GIGE:01
export HUTCH=amo
edm -x -eolc	\
	-m "IOC=${IOC_PV}"	\
	-m "CAM=${CAM}"		\
	-m "P=${CAM},R=:"	\
	-m "HUTCH=${HUTCH}"	\
	gigeScreens/gigeTop.edl  &

