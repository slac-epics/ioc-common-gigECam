#
# colorViewers.cmd
#
# This script creates, configures, and loads
# a full set of color viewers
#
# Color viewers are used to view images from a color camera,
# although each viewer may be configured for either B/W or color.
#
# Required ENV variables:
#	CAM_PORT	- Name of camera asyn port

# Create a full size non-binned color image named $(CAM):Image
epicsEnvSet( "IMAGE_NAME",	"Image"	)
epicsEnvSet( "BINNING",		"1"		)
epicsEnvSet( "COLOR_MODE",	"RGB1"		)
< setupScripts/colorViewer.cmd

# Note: If desired we can create color binned and
# thumbnail images.   If we do, they should be named
# $(CAM):Binned and $(CAM):Thumbnail.

# Create a 1/4 size binned 8 bit mono image named $(CAM):MonoBinned
epicsEnvSet( "IMAGE_NAME",	"MonoBinned"	)
epicsEnvSet( "BINNING",		"2"		)
epicsEnvSet( "COLOR_MODE",	"Mono"		)
< setupScripts/colorViewer.cmd

# Create a thumbnail mono image named $(CAM):MonoThumbnail
epicsEnvSet( "IMAGE_NAME",	"MonoThumbnail"	)
epicsEnvSet( "BINNING",		"4"		)
epicsEnvSet( "COLOR_MODE",	"Mono"		)
< setupScripts/colorViewer.cmd

