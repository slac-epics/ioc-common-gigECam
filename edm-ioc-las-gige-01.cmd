#! /bin/bash

# Setup edm environment
source /reg/g/pcds/setup/epicsenv-3.14.12.sh
export EDMDATAFILES=".:..:areaDetectorScreens"

edm -x -eolc	\
	-m "IOC=LAS:R51:IOC:25,P=LAS:GIGE1:,R=CAM1:"	\
	-m "EVR=LAS:R51:EVR:25"	\
	prosilica.edl evrscreens/evr.edl &
