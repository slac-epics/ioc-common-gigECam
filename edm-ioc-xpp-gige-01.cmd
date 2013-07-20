#! /bin/bash

# Setup edm environment
source /reg/g/pcds/setup/epicsenv-3.14.12.sh
export EDMDATAFILES=".:..:areaDetectorScreens"

edm -x -eolc	\
	-m "IOC=IOC:XPP:GIGE:01,P=XPP:GIGE1:,R=CAM1:"	\
	prosilica.edl ADBase.edl &
