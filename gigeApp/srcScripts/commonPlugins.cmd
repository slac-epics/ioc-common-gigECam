#
# commonPlugins.cmd
#
# This script creates, configures, and loads db records for our
# default set of plugins

# Create a Std Image plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_PORT", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/iocBoot/pluginImage.cmd

# Create a JPEG File plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_PORT", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/iocBoot/pluginJPEG.cmd

# Create an HDF5 File plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_PORT", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/iocBoot/pluginHDF5.cmd

# Create an MJPG plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_PORT", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/iocBoot/pluginMJPG.cmd

# Create a FileMPEG plugin, set it to get data from the camera
epicsEnvSet( "PLUGIN_PORT", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/iocBoot/pluginFileMPEG.cmd

# Create 4 ROI plugins
# Set them to get data from the camera
epicsEnvSet( "PLUGIN_PORT", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
< $(TOP)/iocBoot/pluginROI.cmd
epicsEnvSet( "N", "2" )
< $(TOP)/iocBoot/pluginROI.cmd
epicsEnvSet( "N", "3" )
< $(TOP)/iocBoot/pluginROI.cmd
epicsEnvSet( "N", "4" )
< $(TOP)/iocBoot/pluginROI.cmd


