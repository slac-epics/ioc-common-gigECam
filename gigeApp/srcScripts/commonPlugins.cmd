#
# commonPlugins.cmd
#
# This script creates, configures, and loads db records for our
# default set of plugins
epicsEnvSet( "QSIZE", "5" )

# Create a Std Image plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/scripts/pluginImage.cmd

# Create a couple of Color Conversion plugins
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/scripts/pluginColorConvert.cmd
epicsEnvSet( "N", "2" )
< $(TOP)/scripts/pluginColorConvert.cmd

# Create a FileMPEG plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/scripts/pluginFileMPEG.cmd

# Create an HDF5 File plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/scripts/pluginHDF5.cmd

# Create a JPEG File plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/scripts/pluginJPEG.cmd

# GraphicsMagick not supported in areaDetector 1.9 for RHEL due to compiler issues
# Create a Magick plugin, set it to get data from the camera
#epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
#epicsEnvSet( "N", "1" )
#< $(TOP)/scripts/pluginMagick.cmd

# Create an MJPG plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/scripts/pluginMJPG.cmd

# Create a NetCDF plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/scripts/pluginNetCDF.cmd

# Create a Nexus plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/scripts/pluginNexus.cmd

# Create an Overlay plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/scripts/pluginOverlay.cmd

# Create a Process plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/scripts/pluginProcess.cmd

# Create 4 ROI plugins
# Set them to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/scripts/pluginROI.cmd
epicsEnvSet( "N", "2" )
< $(TOP)/scripts/pluginROI.cmd
epicsEnvSet( "N", "3" )
< $(TOP)/scripts/pluginROI.cmd
epicsEnvSet( "N", "4" )
< $(TOP)/scripts/pluginROI.cmd

# Create 5 Statistics plugins
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/scripts/pluginStats.cmd
epicsEnvSet( "N", "2" )
< $(TOP)/scripts/pluginStats.cmd
epicsEnvSet( "N", "3" )
< $(TOP)/scripts/pluginStats.cmd
epicsEnvSet( "N", "4" )
< $(TOP)/scripts/pluginStats.cmd
epicsEnvSet( "N", "5" )
< $(TOP)/scripts/pluginStats.cmd

# Create a TIFF plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/scripts/pluginTIFF.cmd

# Create a Transform plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/scripts/pluginTransform.cmd

