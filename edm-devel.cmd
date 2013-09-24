#! /bin/bash

# Setup edm environment
source /reg/g/pcds/setup/epicsenv-3.14.12.sh
export EDMDATAFILES=".:..:areaDetectorScreens"

edm -eolc	\
	-m "IOC=SXR:IOC:GIGE:01,P=SXR:GIGE:,R=CAM1:"	\
	areaDetectorScreens/NDStdArraysBig.edl	\
	areaDetectorScreens/prosilica.edl &
