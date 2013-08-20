#
# pluginMJPG.cmd
#
# Required env vars
#	CAM			- PV Prefix for all camera related PV's
#	N			- Plugin number, must be unique if more than one MJPG plugin
#	PLUGIN_PORT	- Which port should this plugin get its data from

# Configure the plugin
# ffmpegServerConfigure( serverHttpPort )
# Default server HTTP port is 8080
ffmpegServerConfigure( 8080 )

# ffmpegStreamConfigure( portName, queueSize, blockingCallbacks, NDArrayPort, NDArrayAddr, maxMemory )
# Set maxMemory  to 0 for unlimited memory allocation
ffmpegStreamConfigure( "MJPG$(N)", 2, 0, "$(PLUGIN_PORT)", 0, 0)

# Load the plugin records
dbLoadRecords( "db/pluginMJPG.db",  "CAM=$(CAM),PLUGIN_PORT=$(PLUGIN_PORT),N=$(N)" )
