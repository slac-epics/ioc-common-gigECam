#! /bin/bash

# Setup edm environment
export EPICS_HOST_ARCH=linux-x86
source /reg/g/pcds/setup/epicsenv-3.14.9.sh
export EPICS_CA_MAX_ARRAY_BYTES=8000000

edm -x -eolc	\
	-m "IOC=LAS:IOC:GIGE:SXR:01,P=LAS:GIGE:SXR:,R=01:"	\
	prosilica.edl &
