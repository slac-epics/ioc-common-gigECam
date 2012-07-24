#! /bin/bash

# Setup edm environment
export EPICS_SITE_TOP=/reg/g/pcds/package/epics/3.14
export EPICS_HOST_ARCH=$($EPICS_SITE_TOP/base/current/startup/EpicsHostArch.pl)

export EDMFILES=$EPICS_SITE_TOP/extensions/current/templates/edm
export EDMFILTERS=$EPICS_SITE_TOP/extensions/current/templates/edm
export EDMHELPFILES=$EPICS_SITE_TOP/extensions/current/src/edm/helpFiles
export EDMLIBS=$EPICS_SITE_TOP/extensions/current/lib/$EPICS_HOST_ARCH
export EDMOBJECTS=$EPICS_SITE_TOP/extensions/current/templates/edm
export EDMPVOBJECTS=$EPICS_SITE_TOP/extensions/current/templates/edm
export EDMUSERLIB=$EPICS_SITE_TOP/extensions/current/lib/$EPICS_HOST_ARCH
export EDMACTIONS=/reg/g/pcds/package/tools/edm/config
export EDMWEBBROWSER=mozilla
export PATH=$PATH:$EPICS_SITE_TOP/extensions/current/bin/$EPICS_HOST_ARCH
export EDMDATAFILES=".:..:$EPICS_SITE_TOP/modules/areaDetector/R1.6.0-0.5.0/ADApp/op/edl"

#edm -x -m "IOC=LAS:R51:IOC:25" -eolc gigeScreens/gige.edl &
edm -x -eolc	\
	-m "IOC=LAS:R51:IOC:25,P=LAS:GIGE1:,R=CAM1:"	\
	-m "EVR=LAS:R51:EVR:25"	\
	ADBase.edl evrscreens/evr.edl &
