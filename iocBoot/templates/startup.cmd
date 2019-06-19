#!/bin/bash 

export IOC="$$IOCNAME"

# Setup the IOC user environment
source $IOC_COMMON/All/$$(HUTCH)_env.sh

# Change directory to startup dir for ioc version
cd $$(TOP)/iocBoot/$$(IOCNAME)

# Copy the archive files to iocData
cp -f -p ../../archive/*.archive $IOC_DATA/$IOC/archive

# Launch the IOC
/bin/rm -f $IOC_DATA/$IOC/iocInfo/ioc.log
$PROCSERV --logfile $IOC_DATA/$IOC/iocInfo/ioc.log --savefile --name $IOC $$IF(PROCSERV_PORT,$$PROCSERV_PORT,30001) $$(IOCTOP)/bin/$EPICS_HOST_ARCH/gige st.cmd

