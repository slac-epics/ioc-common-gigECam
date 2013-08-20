#
# pluginFileMPEG.cmd
#
# Required env vars
#	CAM			- PV Prefix for all camera related PV's
#	N			- Plugin number, must be unique if more than one FileMPEG plugin
#	PLUGIN_PORT	- Which port should this plugin get its data from

# Configure the plugin
ffmpegFileConfigure( "FileMPEG$(N)", 16, 0, "$(PLUGIN_PORT)", 0, 0)

# Load the plugin records
dbLoadRecords( "db/pluginFileMPEG.db",  "CAM=$(CAM),PLUGIN_PORT=$(PLUGIN_PORT),N=$(N)" )
