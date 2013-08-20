#
# pluginNexus.cmd
#
# Required env vars
#	CAM			- PV Prefix for all camera related PV's
#	N			- Plugin number, must be unique if more than one Nexus plugin
#	PLUGIN_PORT	- Which port should this plugin get its data from

# Configure the plugin
# NDFileNexusConfigure( portName, queueSize, blockingCallbacks, dataSrcPortName, addr, priority, stackSize )
# Set priority   to 0  for default priority
# Set stackSize  to 0  for default stackSize
NDFileNexusConfigure( "Nexus$(N)", 5, 0, "$(PLUGIN_PORT)", 0 )

# Load the plugin records
dbLoadRecords( "db/pluginNexus.db",  "CAM=$(CAM),PLUGIN_PORT=$(PLUGIN_PORT),N=$(N)" )
