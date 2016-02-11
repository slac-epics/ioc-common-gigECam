#! /bin/bash

# Setup edm environment
source $SETUP_SITE_TOP/epicsenv-3.14.12.sh
export EPICS_CA_SERVER_PORT=5066
export EPICS_CA_REPEATER_PORT=5067

# Change to a directory that has appropriate screen links
cd ${EPICS_SITE_TOP}-dev/screens/edm/afs/current

export IOC_PV=TST:IOC:GIGE:01
export EVR_PV=TST:EVR:GIGE:01
export CAM=TST:GIGE:01
export CH=0
export HUTCH=tst
export PVLIST=tst.lst
edm -x -eolc	\
	-m "IOC=${IOC_PV}"	\
	-m "EVR=${EVR_PV}"	\
	-m "CAM=${CAM}"	\
	-m "CH=${CH}"	\
	-m "P=${CAM},R=:"	\
	-m "HUTCH=${HUTCH}"	\
	-m "PVLIST=${PVLIST}"	\
	-m "CONFIG_SITE_TOP=${CONFIG_SITE_TOP}"	\
	gigeScreens/gigeTop.edl  &

