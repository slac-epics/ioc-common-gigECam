#! /bin/bash

source /reg/g/pcds/setup/pyca.sh
#LD_LIBRARY_PATH=/reg/common/package/epicsca/3.14.9/lib/x86_64-linux:/reg/common/package/python/2.5.5/lib:/reg/g/pcds/package/qt-4.3.4/lib

cd Viewers/gige

#/reg/common/package/python/2.5.5/bin/python viewer.pyw --camerapv XCS:GIGE:CAM1 &
python viewer.pyw --camerapv XCS:GIGE:CAM1 &
