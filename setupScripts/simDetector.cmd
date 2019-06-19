# Set the environment, configure, and load the DB
# records for an ADSimDetector simulated camera
#
# Each of these required macros must be re-defined
# to unique values each time this script is invoked
# Required macros:
#	CAM			Prefix for all camera PV's
#	CAM_IP		Network IP addr or hostname	for camera

# Camera asyn port is now just CAM, as we only have one camera per IOC
epicsEnvSet( "CAM_PORT", "CAM" )

# TODO: Parameterize SIM_DATA_TYPE: 0=NDInt8,1=NDUInt8,2=NDInt16,3=NDUInt16,4=NDInt32,5=NDUInt32,6=NDFloat32,7=NDFloat64
epicsEnvSet( "SIM_DATA_TYPE", 3 )

# Configure and initialize an ADSimDetector
# simDetectorConfig( portName, maxSizeX, maxSizeY, dataType, maxBuffers, maxMemory, priority, stackSize )
# Set maxBuffers to 0 for unlimited buffers
# Set maxMemory  to 0 for unlimited memory allocation
# Set priority   to 0  for default priority
# Set stackSize  to 0  for default stackSize
# Parameters not set explicitly are set to zero
simDetectorConfig(  "$(CAM_PORT)", $(IMAGE_XSIZE), $(IMAGE_YSIZE), $(SIM_DATA_TYPE), $(N_AD_BUFFERS=0), 0, 0, 0 )

dbLoadRecords( "db/simDetector.db",  "CAM=$(CAM_PV),CAM_PORT=$(CAM_PORT),CAM_TRIG=$(CAM_TRIG=unused)" )
