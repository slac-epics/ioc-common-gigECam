#! ../../bin/linux-x86_64/gige

# Run common startup commands for linux soft IOC's
< /reg/d/iocCommon/All/pre_linux.cmd

< envPaths
epicsEnvSet( "ENGINEER",	"Bruce Hill (bhill)" )
epicsEnvSet( "LOCATION",	"MEC:M64A:43" )

# Network name or IP addr for gigE camera
epicsEnvSet( "CAM_IP",		"192.168.102.2" )

# PV prefix for gigE camera
epicsEnvSet( "CAM",			"MEC:VS3:CAM3" )

# Choose camera model from $(TOP)/setupScripts/$(MODEL).env 
epicsEnvSet( "MODEL",		"MantaG145B" )

# Choose which plugins to use from $(TOP)/setupScripts/$(PLUGINS).cmd 
# Currently only one is commonPlugins.cmd
# If you create a new one, please name it like xyzPlugins.cmd
epicsEnvSet( "PLUGINS",		"commonPlugins" )

# PV prefix for EVR, if used
epicsEnvSet( "EVR_ENABLED",	"#" )				# "" = YES,  "#" = NO
epicsEnvSet( "EVR_PV",		"MEC:EVR:GIGE:01" )

# PV prefix for IOC
epicsEnvSet( "IOC_PV",		"MEC:IOC:VS3:GIGE3" )
epicsEnvSet( "IOCSH_PS1",	"$(IOC)> " )

##############################################################
# The rest of the startup script is the same for all gigE cameras
< $(TOP)/setupScripts/template-st.cmd

