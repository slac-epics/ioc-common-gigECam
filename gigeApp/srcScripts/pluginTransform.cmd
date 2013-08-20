#
# pluginTransform.cmd
#
# Required env vars
#	CAM			- PV Prefix for all camera related PV's
#	N			- Plugin number, must be unique if more than one Trans plugin
#	PLUGIN_PORT	- Which port should this plugin get its data from

# Configure the plugin
# NDTransformConfigure( portName, queueSize, blockingCallbacks, dataSrcPortName, addr, maxBuffers, maxMemory, priority, stackSize )
# Set maxBuffers to 0 for unlimited buffers
# Set maxMemory  to 0 for unlimited memory allocation
# Set priority   to 0  for default priority
# Set stackSize  to 0  for default stackSize
NDTransformConfigure( "Trans$(N)", 5, 0, "$(PLUGIN_PORT)", 0 )

# Load the plugin records
dbLoadRecords( "db/pluginTransform.db",  "CAM=$(CAM),PLUGIN_PORT=$(PLUGIN_PORT),N=$(N)" )
