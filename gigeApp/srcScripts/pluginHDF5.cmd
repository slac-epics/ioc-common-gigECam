#
# pluginHDF5.cmd
#
# Required env vars
#	CAM			- PV Prefix for all camera related PV's
#	N			- Plugin number, must be unique if more than one HDF5 plugin
#	PLUGIN_PORT	- Which port should this plugin get its data from

# Configure the plugin
# NDFileHDF5Configure( portName, queueSize, blockingCallbacks, dataSrcPortName, addr, priority, stackSize )
NDFileHDF5Configure( "FileHDF5$(N)", 5, 0, "$(PLUGIN_PORT)", 0, 0)

# Load the plugin records
dbLoadRecords( "db/pluginHDF5.db",  "CAM=$(CAM),PLUGIN_PORT=$(PLUGIN_PORT),N=$(N)" )
