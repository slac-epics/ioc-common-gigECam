#! /bin/bash

# Setup edm environment
source /reg/g/pcds/setup/epicsenv-3.14.12.sh
export EDMDATAFILES=".:..:areaDetectorScreens"

edm -x -eolc	\
	-m "IOC=XCS:IOC:GIGE:703:1,P=XCS:GIGE:,R=CAM:703:2:"	\
	prosilica.edl &
