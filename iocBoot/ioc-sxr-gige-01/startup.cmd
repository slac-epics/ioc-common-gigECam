#!/bin/bash

# Setup the IOC user environment
export IOC="ioc-sxr-gige-01"
source /reg/d/iocCommon/All/sxr_env.sh

# For release
#cd $EPICS_SITE_TOP/ioc/common/gige/R0.1.0/iocBoot/$IOC

# For development
cd ~bhill/wa2/epics/ioc/common/gigECam/current/iocBoot/$IOC

# Copy the archive file to iocData
$RUNUSER "cp ../../archive/$IOC.archive $IOC_DATA/$IOC/archive"

# Launch the IOC
$RUNUSER "$PROCSERV --logfile $IOC_DATA/$IOC/iocInfo/ioc.log --name $IOC 32501 st.cmd"
