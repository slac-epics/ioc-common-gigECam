#! /bin/bash

# Setup edm environment
source /reg/g/pcds/setup/epicsenv-3.14.12.sh
export EDMDATAFILES=".:..:areaDetectorScreens"

edm -x -eolc	\
	-m "IOC=TST:R40:IOC:18:GIGE:01,P=TST:GIGE1:,R=CAM1:"	\
	prosilica.edl &
