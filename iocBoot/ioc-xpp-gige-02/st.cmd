#!../../bin/linux-x86_64/gige

## ToDo: The following substitutions can be done via makeBaseApp.pl
## If they weren't, do them before releasing your IOC
##
## Replace _ USER _ with your userid
##
## Replace _ APPNAME _ with the name of the application
##
## Replace _ IOC _ with the network name of the IOC
##
## Replace _ IOCPVROOT _ with the PV prefix used for
## iocAdmin PV's on this IOC
## ex. AMO:R15:IOC:23
##

epicsEnvSet( "ENGINEER", "your_name (pstoffel)" )
epicsEnvSet( "LOCATION", "IOC:XPP:GIGE:02" )
epicsEnvSet( "IOCSH_PS1", "ioc-xpp-gige-02> " )
< envPaths
cd( "../.." )

# Run common startup commands for linux soft IOC's
< /reg/d/iocCommon/All/pre_linux.cmd

# Register all support components
dbLoadDatabase("dbd/gige.dbd")
gige_registerRecordDeviceDriver(pdbbase)

# Load record instances
dbLoadRecords( "db/iocAdmin.db",			"IOC=IOC:XPP:GIGE:02" )
dbLoadRecords( "db/save_restoreStatus.db",	"IOC=IOC:XPP:GIGE:02" )

# Setup autosave
set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
set_requestfile_path( "$(TOP)/autosave" )
save_restoreSet_status_prefix( "IOC:XPP:GIGE:02:" )
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )
set_pass0_restoreFile( "autosave_gige.sav" )
set_pass1_restoreFile( "autosave_gige.sav" )

# Initialize the IOC and start processing records
iocInit()

# Start autosave backups
create_monitor_set( "autosave_gige.req", 5, "IOC=IOC:XPP:GIGE:02" )

# All IOCs should dump some common info after initial startup.
< /reg/d/iocCommon/All/post_linux.cmd
