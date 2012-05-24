#! /bin/bash

source /reg/g/pcds/setup/pyca.sh
#LD_LIBRARY_PATH=/reg/common/package/epicsca/3.14.9/lib/x86_64-linux:/reg/common/package/python/2.5.5/lib:/reg/g/pcds/package/qt-4.3.4/lib

#cd /reg/g/pcds/package/epics/3.14/ioc/common/gigECam/R0.19.0/Viewers/gige
cd gigeViewers
/reg/common/package/python/2.5.5/bin/python viewer.pyw --camerapv LAS:GIGE:CAM1 &
