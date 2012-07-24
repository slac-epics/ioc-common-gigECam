#! /bin/bash

source /reg/g/pcds/setup/pyca.sh

#cd /reg/g/pcds/package/epics/3.14/ioc/common/gigECam/R0.19.0/Viewers/gige
cd gigeViewers
/reg/common/package/python/2.5.5/bin/python viewer.pyw --camerapv LAS:GIGE1:CAM1 &
