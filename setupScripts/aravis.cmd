# Set the environment, configure, and load the DB
# records for an aravis gigE camera
#
# Each of these required macros must be re-defined
# to unique values each time this script is invoked
# Required macros:
#	CAM			Prefix for all camera PV's
#	CAM_IP		Network IP addr or hostname	for camera

# Camera asyn port is now just CAM, as we only have one camera per IOC
epicsEnvSet( "CAM_PORT", "CAM" )

# Configure and initialize an aravis gigE camera
# aravisCameraConfig( portName, ipName, maxBuffers, maxMemory, priority, stackSize )
# Set maxBuffers to 0 for unlimited buffers
# Set maxMemory  to 0 for unlimited memory allocation
# Set priority   to 0  for default priority
# Set stackSize  to 0  for default stackSize
# Parameters not set explicitly are set to zero
aravisCameraConfig(  "$(CAM_PORT)", "$(CAM_IP)", $(N_AD_BUFFERS=0), 0, 0, 0 )

dbLoadRecords( "db/aravis.db",  "CAM=$(CAM_PV),CAM_PORT=$(CAM_PORT),CAM_TRIG=$(CAM_TRIG=unused)" )
