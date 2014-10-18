#!/bin/sh
SRVNAME=$1
NB=$3
RV=$2
MINARGS=3

if [ $# -ne $MINARGS ] ; then
   echo -e ""
   echo -e "Usage:   "$0" <srv_name> <rel_number> <cam_number>"
   echo -e "Example: "$0" ioc-mec-las-gige02 R1.13.1 1"
   echo -e ""
   exit 0 
fi
cat > ${SRVNAME}-${NB}.cfg << _EOF_
#
# CONFIG file for gigE Camera
#

RELEASE		= /reg/g/pcds/package/epics/3.14/ioc/common/gigECam/${RV}

ENGINEER	= "Ernesto Paiser (paiser)"
LOCATION	= "MEC LASER ENCLOSURE"
IOC_PV		= MEC:LAS:GIGE:IOC${NB}

CAM	    	= MEC:LAS:GIGE:CAM${NB}

# Available models are: 
# They are located in: /reg/g/pcds/package/epics/3.14/ioc/common/gigECam/${RV}/setupScripts
# MantaG033B, MantaG046B, MantaG125B, MantaG145B, MantaG146B, MantaG146C, MantaG201B, ProsilicaGC1350C
MODEL		= MantaG033B

# Must be later port to a POE switch with DHCP
CAM_IP		= 192.168.${NB}.10

# Default is pcdsPlugins
PLUGINS		= pcdsPlugins
# All gigE camera iocs on a given host must have their own HTTP port number
HTTP_PORT	= 3260${NB}
_EOF_
