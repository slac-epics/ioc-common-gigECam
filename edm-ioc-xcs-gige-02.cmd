#! /bin/bash

# Setup edm environment
source /reg/g/pcds/setup/epicsenv-3.14.12.sh
export EDMDATAFILES=".:..:areaDetectorScreens"

edm -x -eolc	\
	-m "IOC=XCS:XXX:IOC:XX,P=XCS:GIGE:,R=CAM2:"	\
	prosilica.edl &
