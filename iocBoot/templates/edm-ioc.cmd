#! /bin/bash

# Setup the common directory env variables
if [ -e      /reg/g/pcds/pyps/config/common_dirs.sh ]; then
	source   /reg/g/pcds/pyps/config/common_dirs.sh
elif [ -e    /afs/slac/g/pcds/pyps/config/common_dirs.sh ]; then
	source   /afs/slac/g/pcds/pyps/config/common_dirs.sh
fi

# Setup edm environment
if [ -f    ${SETUP_SITE_TOP}/epicsenv-cur.sh ]; then
	source ${SETUP_SITE_TOP}/epicsenv-cur.sh
fi

export EVR_PV=$$IF(EVR_PV,$$EVR_PV,$$CAM_PV:NoEvr)
export IOC_PV=$$IOC_PV
export CAM=$$CAM_PV
export TRIG_CH=$$IF(EVR_TRIG,$$EVR_TRIG,0)
export HUTCH=$$IF(HUTCH,$$HUTCH,tst)

export IF=$$IF(NET_IF,$$NET_IF,ETH0)

EDM_TOP=gigeScreens/gigeTop.edl
$$IF(SCREENS_TOP)
SCREENS_TOP=$$SCREENS_TOP
$$ELSE(SCREENS_TOP)
SCREENS_TOP=${EPICS_SITE_TOP}-dev/screens/edm/${HUTCH}/current
$$ENDIF(SCREENS_TOP)

#pushd ${SCREENS_TOP}
# Now launching edm from new screenLinks directory under each IOCTOP release
# so each ioc can have it's own custom set of screens that matches which
# set of module depedencies that ioc was built with. 
pushd $$IOCTOP/screenLinks
edm -x -eolc	\
	-m "IOC=${IOC_PV}"		\
	-m "EVR=${EVR_PV}"		\
	-m "CAM=${CAM}"			\
	-m "CH=${TRIG_CH}"		\
	-m "P=${CAM},R=:"		\
	-m "EDM_TOP=${EDM_TOP}"	\
	-m "HUTCH=${HUTCH}"		\
	-m "IF=${IF}"			\
	${EDM_TOP} &

