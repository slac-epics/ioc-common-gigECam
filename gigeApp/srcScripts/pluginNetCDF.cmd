#
# pluginNetCDF.cmd
#
# Required env vars
#	CAM			- PV Prefix for all camera related PV's
#	N			- Plugin number, must be unique if more than one NetCDF plugin
#	PLUGIN_PORT	- Which port should this plugin get its data from

# Configure the plugin
# NDFileNetCDFConfigure( portName, queueSize, blockingCallbacks, dataSrcPortName, addr, priority, stackSize )
# Set priority   to 0  for default priority
# Set stackSize  to 0  for default stackSize
NDFileNetCDFConfigure( "NetCDF$(N)", 5, 0, "$(PLUGIN_PORT)", 0 )

# Load the plugin records
dbLoadRecords( "db/pluginNetCDF.db",  "CAM=$(CAM),PLUGIN_PORT=$(PLUGIN_PORT),N=$(N)" )
