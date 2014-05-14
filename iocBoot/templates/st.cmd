#!$$IOCTOP/bin/linux-x86_64/gige
# Note: as of ioc/common/gigECam R1.11.0, the startup.cmd
# file must use ./gige as the executable,
# as that file is owned by root w/ setuid enabled,
# allowing the prosilica driver to optimize network performance.

# Run common startup commands for linux soft IOC's
< /reg/d/iocCommon/All/pre_linux.cmd

< envPaths
epicsEnvSet("IOCNAME", "$$IOCNAME")
epicsEnvSet("ENGINEER", "$$ENGINEER" )
epicsEnvSet("LOCATION", "$$LOCATION" )
epicsEnvSet("IOCSH_PS1", "$(IOCNAME)> " )
epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES", "$$IF(MAX_ARRAY,$$MAX_ARRAY,8000000)" )
epicsEnvSet("IOC_PV", "$$IOC_PV")
epicsEnvSet("IOCTOP", "$$IOCTOP")
epicsEnvSet("TOP", "$$TOP")


# Choose an HTTP port number for the camera's MPEG stream
# All gigE camera's on the same host must have unique port numbers
epicsEnvSet( "HTTP_PORT",	"$$HTTP_PORT" )

# Setup asyn tracing if specified
epicsEnvSet( "TRACE_MASK",    "$$IF(TRACE_MASK,$$TRACE_MASK,1)" )
epicsEnvSet( "TRACE_IO_MASK", "$$IF(TRACE_IO_MASK,$$TRACE_IO_MASK,0)" )

# EVR not supported yet
epicsEnvSet( "EVR_ENABLED",	"#" )
epicsEnvSet( "EVR_PV",	"" )

cd( "$(IOCTOP)" )

##############################################################

# Register all support components
dbLoadDatabase( "dbd/gige.dbd" )
gige_registerRecordDeviceDriver(pdbbase)

$$LOOP(CAMERA)
# Network name or IP addr for gigE camera
epicsEnvSet( "CAM_IP",		"$$IP" )

# PV prefix for gigE camera
epicsEnvSet( "CAM",			"$$CAM" )

# asyn port name for gigE camera
epicsEnvSet( "CAM_PORT",	"CAM" )

# Choose camera model from setupScripts/$(MODEL).env 
epicsEnvSet( "MODEL",		"$$MODEL" )

# Setup the environment for the specified gigE camera model
< setupScripts/$(MODEL).env

# Configure and load the base Prosilica camera
< setupScripts/prosilica.cmd

# Load the viewers
$$IF(COLOR)
< setupScripts/colorViewers.cmd
$$ELSE(COLOR)
< setupScripts/monoViewers.cmd
$$ENDIF(COLOR)

# Configure and load the plugins, if desired
$$IF(PLUGINS)
< setupScripts/$$PLUGINS.cmd
$$ENDIF(PLUGINS)
$$ENDLOOP(CAMERA)

# Set asyn trace flags
asynSetTraceMask(   "$(CAM_PORT)", $(TRACE_MASK) )
asynSetTraceIOMask( "$(CAM_PORT)", $(TRACE_IO_MASK) )

# Initialize EVR
$(EVR_ENABLED) ErDebugLevel( 0 )
$(EVR_ENABLED) ErConfigure( 0, 0, 0, 0, 1 )
$(EVR_ENABLED) dbLoadRecords( "db/evrPmc230.db",  "IOC=$(IOC_PV),EVR=$(EVR_PV),EVRFLNK=" )

# Load soft ioc related record instances
dbLoadRecords( "db/iocSoft.db",				"IOC=$(IOC_PV)" )
dbLoadRecords( "db/save_restoreStatus.db",	"IOC=$(IOC_PV)" )

# Setup autosave
set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
set_requestfile_path( "$(TOP)/autosave" )
save_restoreSet_status_prefix( "$(IOC_PV):" )
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )
set_pass0_restoreFile( "$(IOC).sav" )
set_pass1_restoreFile( "$(IOC).sav" )

save_restoreSet_NumSeqFiles(5)
save_restoreSet_SeqPeriodInSeconds(30)

# Initialize the IOC and start processing records
iocInit()

# TODO: Remove these dbpf calls if possible
# Enable callbacks
dbpf $(CAM):ArrayCallbacks 1
# dbpf $(CAM):ColorMode $(IMAGE_COLORMODE)

# Start acquiring images
dbpf $(CAM):Acquire 1                         # Start the camera

# ----------

# Start autosave backups
create_monitor_set( "$(IOC).req", 5, "CAM=$(CAM)" )

# All IOCs should dump some common info after initial startup.
< /reg/d/iocCommon/All/post_linux.cmd
