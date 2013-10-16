#! ../../bin/linux-x86_64/gige

# Run common startup commands for linux soft IOC's
< /reg/d/iocCommon/All/pre_linux.cmd

< envPaths
epicsEnvSet( "ENGINEER",	"Bruce Hill (bhill)" )
epicsEnvSet( "LOCATION",	"Laser Room SXR GigE Cams" )

# Network name or IP addr for gigE camera
epicsEnvSet( "CAM_IP",		"gige-las-sxr1" )

# PV prefix for gigE camera
epicsEnvSet( "CAM",			"LAS:GIGE:SXR:01" )

# Choose camera model from $(TOP)/setupScripts/$(MODEL).env 
epicsEnvSet( "MODEL",		"MantaG046B" )

# Choose which plugin's to use from $(TOP)/setupScripts/$(PLUGINS).cmd 
# If you create a new one, please name it like xyzPlugins.cmd
epicsEnvSet( "PLUGINS",		"pcdsPlugins" )

# PV prefix for EVR, if used
epicsEnvSet( "EVR_ENABLED",	"" )				# "" = YES,  "#" = NO
epicsEnvSet( "EVR_PV",		"LAS:EVR:GIGE:SXR:01" )

# PV prefix for IOC
epicsEnvSet( "IOC_PV",		"LAS:IOC:GIGE:SXR:01" )
epicsEnvSet( "IOCSH_PS1",	"$(IOC)> " )

##############################################################
# The rest of the startup script is the same for all gigE cameras
< $(TOP)/setupScripts/template-st.cmd

