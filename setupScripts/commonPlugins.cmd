#
# commonPlugins.cmd
#
# This script creates, configures, and loads db records for our
# default set of plugins
epicsEnvSet( "QSIZE", "5" )

# Create a couple of Std Image plugins, set to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "IMAGE_NAME", "IMAGE2" )
< $(TOP)/setupScripts/pluginImage.cmd
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "IMAGE_NAME", "IMAGE3" )
< $(TOP)/setupScripts/pluginImage.cmd

# Create a couple of Color Conversion plugins
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/setupScripts/pluginColorConvert.cmd
epicsEnvSet( "N", "2" )
< $(TOP)/setupScripts/pluginColorConvert.cmd

# Create an HDF5 File plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/setupScripts/pluginHDF5.cmd

# Create a JPEG File plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/setupScripts/pluginJPEG.cmd

# GraphicsMagick not supported in areaDetector 1.9 for RHEL due to compiler issues
# Create a Magick plugin, set it to get data from the camera
#epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
#epicsEnvSet( "N", "1" )
#< $(TOP)/setupScripts/pluginMagick.cmd

# Create a NetCDF plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/setupScripts/pluginNetCDF.cmd

# Create a Nexus plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/setupScripts/pluginNexus.cmd

# Create an Overlay plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/setupScripts/pluginOverlay.cmd

# Create a Process plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/setupScripts/pluginProcess.cmd

# Create 4 ROI plugins
# Set them to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/setupScripts/pluginROI.cmd
epicsEnvSet( "N", "2" )
< $(TOP)/setupScripts/pluginROI.cmd
epicsEnvSet( "N", "3" )
< $(TOP)/setupScripts/pluginROI.cmd
epicsEnvSet( "N", "4" )
< $(TOP)/setupScripts/pluginROI.cmd

# Create 5 Statistics plugins
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/setupScripts/pluginStats.cmd
epicsEnvSet( "N", "2" )
< $(TOP)/setupScripts/pluginStats.cmd
epicsEnvSet( "N", "3" )
< $(TOP)/setupScripts/pluginStats.cmd
epicsEnvSet( "N", "4" )
< $(TOP)/setupScripts/pluginStats.cmd
epicsEnvSet( "N", "5" )
< $(TOP)/setupScripts/pluginStats.cmd

# Create a TIFF plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/setupScripts/pluginTIFF.cmd

# Create a Transform plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/setupScripts/pluginTransform.cmd
