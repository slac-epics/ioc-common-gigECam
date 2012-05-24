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
export EDMDATAFILES=".:.."

export EPICS_CA_AUTO_ADDR_LIST="NO"
export EPICS_CA_ADDR_LIST="$(hostname)"
echo EPICS_CA_ADDR_LIST = $EPICS_CA_ADDR_LIST

source /reg/g/pcds/setup/pyca.sh
#cd ~pstoffel/py/work2
cd viewer-color
./prosilica1350.pyw --camera 13PS2 &
#cd ../viewer
cd ~pstoffel/py/work2
./prosilica1350.pyw --camera 13PS1 &
#python -m pdb ./prosilica1350.pyw --camera 13PS2
