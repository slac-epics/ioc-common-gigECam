#
# pluginImage.cmd
#
# Required env vars
#	CAM			- PV Prefix for all camera related PV's
#	N			- Plugin number, must be unique if more than one Image plugin
#	PLUGIN_PORT	- Which port should this plugin get its data from
#	IMAGE_NELM	- How many elements in the image (x*y for b/w, x*y*3 for color)

# Configure the plugin
NDStdArraysConfigure( "Image$(N)", 5, 0, "$(PLUGIN_PORT)", 0, -1)

# Load the plugin records
dbLoadRecords( "db/pluginImage.db",  "CAM=$(CAM),PLUGIN_PORT=$(PLUGIN_PORT),N=1,IMAGE_NELM=$(IMAGE_NELM)" )
