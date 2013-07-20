#! /bin/bash

# Setup edm environment
source /reg/g/pcds/setup/epicsenv-3.14.12.sh
export EDMDATAFILES=".:..:areaDetectorScreens"

edm -x -eolc	\
	-m "IOC=XCS:R42:IOC:38,P=XCS:GIGE:,R=CAM1:"	\
	prosilica.edl ADBase.edl &
