#
# pluginOverlay.cmd
#
# Required env vars
#	CAM			- PV Prefix for all camera related PV's
#	N			- Plugin number, must be unique if more than one Overlay plugin
#	PLUGIN_PORT	- Which port should this plugin get its data from

# Configure the plugin
# NDOverlayConfigure( portName, queueSize, blockingCallbacks, dataSrcPortName, addr, maxOverlays, maxBuffers, maxMemory )
# Set maxBuffers to 0 for unlimited buffers
# Set maxMemory  to 0 for unlimited memory allocation
NDOverlayConfigure( "Over$(N)", 16, 0, "$(PLUGIN_PORT)", 0, 8 )

# Load the plugin records
dbLoadRecords( "db/pluginOverlay.db",  "CAM=$(CAM),PLUGIN_PORT=$(PLUGIN_PORT),N=$(N)" )
