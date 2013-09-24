#
# pluginImage.cmd
#
# Required env vars
#	CAM			- PV Prefix for all camera related PV's
#	N			- Plugin number, must be unique if more than one Image plugin
#	PLUGIN_SRC	- Which port should this plugin get its data from
#	IMAGE_NELM	- How many elements in the image (x*y for b/w, x*y*3 for color)

# Configure the plugin
NDStdArraysConfigure( "Image$(N)", $(QSIZE), 0, "$(PLUGIN_SRC)", 0, -1)

# Load the plugin records
dbLoadRecords( "db/pluginImage.db",  "CAM=$(CAM),CAM_PORT=$(CAM_PORT),PLUGIN_SRC=$(PLUGIN_SRC),N=1,IMAGE_NELM=$(IMAGE_NELM),IMAGE_BIT_DEPTH=$(IMAGE_BIT_DEPTH)" )
