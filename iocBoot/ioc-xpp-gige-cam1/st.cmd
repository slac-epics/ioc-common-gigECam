#!../../bin/linux-x86_64/gige

epicsEnvSet( "ENGINEER", "Pavel Stoffel" )
epicsEnvSet( "LOCATION", "XPP:R37:IOC:14" )
epicsEnvSet( "IOCSH_PS1", "ioc-xpp-gige-cam1> " )
< envPaths
cd( "../.." )

# Run common startup commands for linux soft IOC's
< /reg/d/iocCommon/All/pre_linux.cmd

# Register all support components
dbLoadDatabase("dbd/gige.dbd")
gige_registerRecordDeviceDriver(pdbbase)


##############################################################
# configure and initialize the camera
prosilicaConfigIp(  "PS1", 116474, "172.21.38.67", 50, 120000000)

# Load record instances
dbLoadRecords( "db/iocAdmin.db",			"IOC=XPP:IOC:CVV:01" )
dbLoadRecords( "db/save_restoreStatus.db",	"IOC=XPP:IOC:CVV:01" )

# Create a standard arrays plugin, set it to get data from first Prosilica driver.
drvNDStdArraysConfigure("PS1Image", 5, 0, "PS1", 0, -1)
# Create a file saving plugin
drvNDFileConfigure("PS1File", 5, 0, "PS1", 0)
# Create an ROI plugin
drvNDROIConfigure("PS1ROI", 5, 0, "PS1", 0, 10, -1)

# Load a prosilica gigE camera
dbLoadRecords( "db/gigE.db",      "P=XPP:USR:CVV:GIGE1" )

# Setup autosave
set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
set_requestfile_path( "$(TOP)/autosave" )
save_restoreSet_status_prefix( "XPP:USR:CVV:GIGE1" )
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )
set_pass0_restoreFile( "autosave_gige.sav" )
set_pass1_restoreFile( "autosave_gige.sav" )

# Initialize the IOC and start processing records
iocInit()

dbpf "XPP:USR:CVV:GIGE1:Image1:EnableCallbacks" 1

# Start autosave backups
create_monitor_set( "autosave_gige.req", 5, "P=XPP:USR:CVV:GIGE1" )

# All IOCs should dump some common info after initial startup.
< /reg/d/iocCommon/All/post_linux.cmd
