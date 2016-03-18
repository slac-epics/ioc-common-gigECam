#! /bin/bash

# Set up env
export PSPKG_ROOT=/reg/common/package
export PSPKG_RELEASE=controls-0.0.8
source $PSPKG_ROOT/etc/set_env.sh
source /reg/g/pcds/setup/pyca27.sh

python ./gigeScripts/SetupGigeCam.py "$@"
