#! /bin/bash

# Setup edm environment
source /reg/g/pcds/setup/epicsenv-3.14.12.sh

export EDMDATAFILES=".:..:$EPICS_SITE_TOP/modules/areaDetector/R1.6.0-0.5.0/ADApp/op/edl"

#edm -x -m "IOC=XCS:R42:IOC:38" -eolc gigeScreens/gige.edl &
edm -x -eolc	\
	-m "IOC=XCS:R42:IOC:38,P=XCS:GIGE:,R=CAM1:"	\
	ADBase.edl &
