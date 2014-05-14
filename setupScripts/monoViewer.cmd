#
# monoViewer.cmd
#
# This script creates, configures, and loads
# db records for one mono viewer
#
# Mono viewers are used to view images from a mono camera,
#
# Required ENV variables:
#	CAM_PORT		- Name of camera asyn port
#	IMAGE_NAME		- Name of viewer image, ex. $(CAM):Image
#	IMAGE_BIT_DEPTH	- Typically 8, 10, or 12, but we should be able to handle up to 16
#	IMAGE_FTVL		- CHAR, UCHAR, SHORT, USHORT
#	IMAGE_TYPE		- Int8 or Int16
#

# For convenience
epicsEnvSet( "IMG", "$(IMAGE_NAME)" )

# Create an ROI plugin for our standard image
NDROIConfigure(          "$(IMG):ROI",   5, 0, "$(CAM_PORT)", 0 )
NDOverlayConfigure(      "$(IMG):Over", 16, 0, "$(IMG):ROI",  0, 8 )
NDStdArraysConfigure(    "$(IMG)",       5, 0, "$(IMG):Over", 0, -1 )

dbLoadRecords( "db/monoViewer.db",  "BINNING=$(BINNING),CAM=$(CAM),CAM_PORT=$(CAM_PORT),IMG=$(IMG),IMAGE_BIT_DEPTH=$(IMAGE_BIT_DEPTH),IMAGE_FTVL=$(IMAGE_FTVL),IMAGE_NELM=$(IMAGE_NELM),IMAGE_TYPE=$(IMAGE_TYPE),COLOR_MODE=$(COLOR_MODE)" )

