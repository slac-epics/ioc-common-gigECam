#! ../../bin/linuxRT_glibc-x86_64/gige

epicsEnvSet( "IOC_COMMON",   "/afs/slac/g/pcds/data/iocCommon" )

# Run common startup commands for linux soft IOC's
< $(IOC_COMMON)/All/pre_linux.cmd

< envPaths
epicsEnvSet( "ENGINEER",	"Bruce Hill (bhill)" )
epicsEnvSet( "LOCATION",	"B84 Camera lab" )

# Network name or IP addr for gigE camera
epicsEnvSet( "CAM_IP",		"CAMR-B084-NW01" )

# PV prefix for gigE camera
epicsEnvSet( "CAM_PV",		"TST:GIGE:01" )

# Choose camera model from db/$(MODEL).env 
epicsEnvSet( "MODEL",		"MantaG046B" )

# Choose which plugins to use from db/$(PLUGINS).cmd 
# If you create a new one, please name it like xyzPlugins.cmd
epicsEnvSet( "PLUGINS",		"pcdsPlugins" )

# Configure EVR
# PV prefix for EVR, if used
epicsEnvSet( "EVR_ENABLED",	"" )				# "" = YES,  "#" = NO
epicsEnvSet( "EVR_CARD",	"0" )
epicsEnvSet( "EVR_TRIG",	"0" )
epicsEnvSet( "EVR_PV",		"TST:EVR:GIGE:01" )
epicsEnvSet( "TRIG_PV",		"$(EVR_PV):TRIG$(EVR_TRIG)" )

# EVR Type: 0=VME, 1=PMC, 15=SLAC
#epicsEnvSet( "EVR_TYPE",	"1" )
#epicsEnvSet( "EVR_DB", "evrPmc230.db" )
epicsEnvSet( "EVR_TYPE",	"15" )
epicsEnvSet( "EVR_DB", "evrSLAC.db" )

# PV prefix for IOC
epicsEnvSet( "IOC_PV",		"TST:IOC:GIGE:01" )
epicsEnvSet( "IOCSH_PS1",	"$(IOC)> " )

# HTTP port for mjpeg
epicsEnvSet( "HTTP_PORT", "7803" )

# Debug settings
epicsEnvSet( "TRACE_MASK",		"1" )
epicsEnvSet( "TRACE_IO_MASK",	"1" )

#cd $(TOP)
cd ../..
##############################################################
# The rest of the startup script is the same for all gigE cameras

# Register all support components
dbLoadDatabase( "dbd/gige.dbd" )
gige_registerRecordDeviceDriver(pdbbase)

# Setup the environment for the specified gigE camera model
< db/$(MODEL).env

# Configure and load a Prosilica camera
< setupScripts/prosilica.cmd

# Set asyn trace flags
asynSetTraceMask(   "$(CAM_PORT)", 0, $(TRACE_MASK) )
asynSetTraceIOMask( "$(CAM_PORT)", 0, $(TRACE_IO_MASK) )

# Configure and load the plugins
< db/$(PLUGINS).cmd

# Initialize EVR
$(EVR_ENABLED) ErDebugLevel( 0 )
$(EVR_ENABLED) ErConfigure( $(EVR_CARD), 0, 0, 0, $(EVR_TYPE) )
$(EVR_ENABLED) dbLoadRecords( "db/$(EVR_DB)", "EVR=$(EVR_PV),CARD=$(EVR_CARD),IP$(EVR_TRIG)E=Enabled,IP1E=Enabled,IP8E=Enabled,IP9E=Enabled" )

# Load ADCore timestamp provider
dbLoadRecords( "db/timeStampFifo.template",  "DEV=$(CAM_PV):TSS,PORT_PV=$(CAM_PV):PortName_RBV,EC_PV=$(EVR_PV):EVENT1CTRL.ENM,DLY=1" )

# Load soft ioc related record instances
dbLoadRecords( "db/iocSoft.db",			"IOC=$(IOC_PV)" )
dbLoadRecords( "db/save_restoreStatus.db",	"IOC=$(IOC_PV)" )

# Setup autosave
set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
set_requestfile_path( "$(TOP)/autosave" )
# Also look in the iocData autosave folder for auto generated req files
set_requestfile_path( "$(IOC_DATA)/$(IOC)/autosave" )
save_restoreSet_status_prefix( "$(IOC_PV):" )
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )
set_pass0_restoreFile( "autoSettings.sav" )
set_pass0_restoreFile( "$(IOC).sav" )
set_pass1_restoreFile( "autoSettings.sav" )
set_pass1_restoreFile( "$(IOC).sav" )

save_restoreSet_NumSeqFiles(5)
save_restoreSet_SeqPeriodInSeconds(30)

# Create autosave files from info directives
makeAutosaveFileFromDbInfo( "$(IOC_DATA)/$(IOC)/autosave/autoSettings.req", "autosaveFields" )

# Initialize the IOC and start processing records
iocInit()

# TODO: Remove these dbpf calls if possible
# Enable callbacks
dbpf $(CAM_PV):ArrayCallbacks 1

# Start acquiring images
dbpf $(CAM_PV):Acquire 1                         # Start the camera

# Start autosave backups
create_monitor_set( "autoSettings.req", 5, "" )
create_monitor_set( "$(IOC).req", 5, "CAM=$(CAM_PV)" )

create_monitor_set( "eventCodeDelays.req", 10, "EVR=$(EVR_PV)" )

# All IOCs should dump some common info after initial startup.
< $(IOC_COMMON)/All/post_linux.cmd
