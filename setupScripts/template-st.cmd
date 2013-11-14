#
# template-st.cmd
#
# Setup commands for all gigE cameras
#
# -----------------------

# Register all support components
dbLoadDatabase( "dbd/gige.dbd" )
gige_registerRecordDeviceDriver(pdbbase)

# Setup the environment for the specified gigE camera model
< setupScripts/$(MODEL).env

# Configure and load a Prosilica camera
< setupScripts/prosilica.cmd

# Configure and load the plugins
< setupScripts/$(PLUGINS).cmd

# Initialize EVR
$(EVR_ENABLED) ErDebugLevel( 0 )
$(EVR_ENABLED) ErConfigure( 0, 0, 0, 0, 1 )
$(EVR_ENABLED) dbLoadRecords( "db/evrPmc230.db",  "IOC=$(IOC_PV),EVR=$(EVR_PV),EVRFLNK=" )

# Load soft ioc related record instances
dbLoadRecords( "db/iocAdmin.db",			"IOC=$(IOC_PV)" )
dbLoadRecords( "db/save_restoreStatus.db",	"IOC=$(IOC_PV)" )

# Setup autosave
set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
set_requestfile_path( "autosave" )
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
dbpf $(CAM):Image1:EnableCallbacks 1

# Start acquiring images
dbpf $(CAM):Acquire 1                         # Start the camera

# ----------

# Start autosave backups
create_monitor_set( "$(IOC).req", 5, "CAM=$(CAM)" )

# All IOCs should dump some common info after initial startup.
< /reg/d/iocCommon/All/post_linux.cmd
