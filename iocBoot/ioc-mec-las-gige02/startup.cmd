#!/bin/bash

export EPICS_CA_MAX_ARRAY_BYTES=8000000

# Setup the IOC user environment
source /reg/d/iocCommon/All/mec_env.sh

# Make sure the IOC's data directories are ready for use
export IOC="ioc-mec-las-gige02"

$RUNUSER "mkdir -p $IOC_DATA/$IOC/autosave"
$RUNUSER "mkdir -p $IOC_DATA/$IOC/archive"
$RUNUSER "mkdir -p $IOC_DATA/$IOC/iocInfo"

# Make sure permissions are correct
$RUNUSER "chmod ug+w -R $IOC_DATA/$IOC"

# For release
#cd $EPICS_SITE_TOP/ioc/common/gigECam/R0.4.0/iocBoot/$IOC

# For development
cd ~/working/ioc/common/gigECam/from_svn_current/iocBoot/$IOC

# Copy the archive file to iocData
#$RUNUSER "cp ../../archive/$IOC.archive $IOC_DATA/$IOC/archive"

# Launch the IOC
export CREATE_TIME=`date '+%m%d%Y_%H%M%S'`
$RUNUSER "$PROCSERV --logfile $IOC_DATA/$IOC/iocInfo/ioc.log_$CREATE_TIME --name $IOC 32501 ./st.cmd"
