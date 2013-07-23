#! /bin/bash

# Setup edm environment
source /reg/g/pcds/setup/epicsenv-3.14.12.sh
export EDMDATAFILES=".:..:areaDetectorScreens"

edm -x -eolc	\
	-m "IOC=IOC:XPP:GIGE:02,P=XPP:GIGE2:,R=CAM2:"	\
	prosilica.edl &
