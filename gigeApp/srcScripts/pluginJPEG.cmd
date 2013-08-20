#
# pluginJPEG.cmd
#
# Required env vars
#	CAM			- PV Prefix for all camera related PV's
#	N			- Plugin number, must be unique if more than one JPEG plugin
#	PLUGIN_PORT	- Which port should this plugin get its data from

# Configure the plugin
NDFileJPEGConfigure( "FileJPEG$(N)", 5, 0, "$(PLUGIN_PORT)", 0, 0)

# Load the plugin records
dbLoadRecords( "db/pluginJPEG.db",  "CAM=$(CAM),PLUGIN_PORT=$(PLUGIN_PORT),N=$(N)" )
