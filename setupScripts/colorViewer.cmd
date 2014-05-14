#
# colorViewer.cmd
#
# This script creates, configures, and loads
# db records for one color viewer
#
# Color viewers are used to view images from a color camera,
# although each viewer may be configured for either B/W or color.
#
# Required ENV variables:
#	CAM_PORT		- Name of camera asyn port
#	IMAGE_NAME		- Name of viewer image, ex. $(CAM):Image
#	COLOR_MODE	- Mono or RGB1
#

# For convenience
epicsEnvSet( "IMG", "$(IMAGE_NAME)" )

########## Color viewers start w/ a color conversion from bayer
# to the desired format
# Create an ROI plugin for our standard image
NDColorConvertConfigure( "$(IMG):CC",    5, 0, "$(CAM_PORT)", 0 )
NDROIConfigure(          "$(IMG):ROI",   5, 0, "$(IMG):CC",   0 )
NDOverlayConfigure(      "$(IMG):Over", 16, 0, "$(IMG):ROI",  0, 8 )
NDStdArraysConfigure(    "$(IMG)",       5, 0, "$(IMG):Over", 0, -1 )

dbLoadRecords( "db/colorViewer.db",  "BINNING=$(BINNING),CAM=$(CAM),CAM_PORT=$(CAM_PORT),IMG=$(IMG),IMAGE_BIT_DEPTH=$(IMAGE_BIT_DEPTH),IMAGE_FTVL=$(IMAGE_FTVL),IMAGE_NELM=$(IMAGE_NELM),IMAGE_TYPE=$(IMAGE_TYPE),COLOR_MODE=$(COLOR_MODE)" )

########## Color viewer $(IMG) loaded

