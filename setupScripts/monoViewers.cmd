#
# monoViewers.cmd
#
# This script creates, configures, and loads
# db records for full set of mono camera viewers
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

# Create a full size non-binned mono image named $(CAM):MonoImage
epicsEnvSet( "IMAGE_NAME",	"MonoImage"	)
epicsEnvSet( "BINNING",		"1"			)
epicsEnvSet( "COLOR_MODE",	"Mono"		)
< setupScripts/monoViewer.cmd

# Note: If desired we can create mono binned and
# thumbnail images.   If we do, they should be named
# $(CAM):Binned and $(CAM):Thumbnail.

# Create a 1/4 size binned 8 bit mono image named $(CAM):MonoBinned
epicsEnvSet( "IMAGE_NAME",	"MonoBinned"	)
epicsEnvSet( "BINNING",		"2"		)
epicsEnvSet( "COLOR_MODE",	"Mono"		)
< setupScripts/monoViewer.cmd

# Create a thumbnail mono image named $(CAM):MonoThumbnail
epicsEnvSet( "IMAGE_NAME",	"MonoThumbnail"	)
epicsEnvSet( "BINNING",		"4"		)
epicsEnvSet( "COLOR_MODE",	"Mono"		)
< setupScripts/monoViewer.cmd

