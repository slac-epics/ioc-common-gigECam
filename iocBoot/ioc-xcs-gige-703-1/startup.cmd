#!/bin/bash

export EPICS_CA_MAX_ARRAY_BYTES=8000000

# Setup the IOC user environment
export IOC="ioc-xcs-gige-703-1"
source /reg/d/iocCommon/All/xcs_env.sh

# For release
cd $EPICS_SITE_TOP/ioc/common/gige/R0.33.0/iocBoot/$IOC

# For development
#cd ~pstoffel/repo/epics/trunk/ioc/common/gigECam/current/iocBoot/$IOC
#cd ~bhill/wa2/epics/ioc/common/gigECam/current/iocBoot/$IOC

# Copy the archive file to iocData
$RUNUSER "cp ../../archive/$IOC.archive $IOC_DATA/$IOC/archive"

# Launch the IOC
$RUNUSER "$PROCSERV --logfile $IOC_DATA/$IOC/iocInfo/ioc.log --name $IOC 37031 st.cmd"
