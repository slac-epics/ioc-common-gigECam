#!../../bin/linux-x86_64/gige

epicsEnvSet( "ENGINEER", "Pavel Stoffel" )
epicsEnvSet( "LOCATION", "XPP:R37:IOC:14:GIGE:01" )
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
#prosilicaConfigIp( "PS1", 116474, "172.21.42.49", 50, 120000000)
prosilicaConfigIp(  "PS1", 116474, "172.21.38.67", 50, 120000000)

# Load record instances
dbLoadRecords( "db/iocAdmin.db",			"IOC=XPP:USR:IOC:GIG1" )
dbLoadRecords( "db/save_restoreStatus.db",	"IOC=XPP:USR:IOC:GIG1" )

#dbLoadRecords("db/ADBase.template",   "P=XPP:,R=GIGE1:,PORT=PS1,ADDR=0,TIMEOUT=1")
#dbLoadRecords("db/prosilica.template","P=XPP:,R=GIGE1:,PORT=PS1,ADDR=0,TIMEOUT=1")

# Create a standard arrays plugin, set it to get data from first Prosilica driver.
drvNDStdArraysConfigure("PS1Image", 5, 0, "PS1", 0, -1) 
#dbLoadRecords("db/NDPluginBase.template","P=XPP:,R=IMG1,PORT=PS1Image,ADDR=0,TIMEOUT=1,NDARRAY_PORT=PS1,NDARRAY_ADDR=0")
#dbLoadRecords("db/NDStdArrays.template", "P=XPP:,R=IMG1,PORT=PS1Image,ADDR=0,TIMEOUT=1,SIZE=8,FTVL=UCHAR,NELEMENTS=1392640")

# Create a file saving plugin
drvNDFileConfigure("PS1File", 5, 0, "PS1", 0)
#dbLoadRecords("db/NDPluginBase.template","P=XPP:,R=FILE1,PORT=PS1File,ADDR=0,TIMEOUT=1,NDARRAY_PORT=PS1,NDARRAY_ADDR=0")
#dbLoadRecords("db/NDFile.template",      "P=XPP:,R=FILE1,PORT=PS1File,ADDR=0,TIMEOUT=1")

# Create an ROI plugin
drvNDROIConfigure("PS1ROI", 5, 0, "PS1", 0, 10, -1)
#dbLoadRecords("db/NDPluginBase.template","P=XPP:,R=ROI1,  PORT=PS1ROI,ADDR=0,TIMEOUT=1,NDARRAY_PORT=PS1,NDARRAY_ADDR=0")
#dbLoadRecords("db/NDROI.template",       "P=XPP:,R=ROI1,  PORT=PS1ROI,ADDR=0,TIMEOUT=1")
#dbLoadRecords("db/NDROIN.template",      "P=XPP:,R=ROI1:0,PORT=PS1ROI,ADDR=0,TIMEOUT=1,HIST_SIZE=256")
#dbLoadRecords("db/NDROIN.template",      "P=XPP:,R=ROI1:1,PORT=PS1ROI,ADDR=1,TIMEOUT=1,HIST_SIZE=256")
#dbLoadRecords("db/NDROIN.template",      "P=XPP:,R=ROI1:2,PORT=PS1ROI,ADDR=2,TIMEOUT=1,HIST_SIZE=256")
#dbLoadRecords("db/NDROIN.template",      "P=XPP:,R=ROI1:3,PORT=PS1ROI,ADDR=3,TIMEOUT=1,HIST_SIZE=256")


# Load a prosilica gigE camera
dbLoadRecords( "db/gigE.db",      "P=XPP:USR:CVV:GIG1" )

# Setup autosave
set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
## FIXME
set_requestfile_path( "$(TOP)/autosave" )
##save_restoreSet_status_prefix( "XPP:GIGE:01:" )
save_restoreSet_status_prefix( "XPP:GIGE1:" )
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )
set_pass0_restoreFile( "autosave_gige.sav" )
set_pass1_restoreFile( "autosave_gige.sav" )

# Initialize the IOC and start processing records
iocInit()

dbpf "XPP:USR:CVV:GIG1:Image1:EnableCallbacks" 1

# Start autosave backups
create_monitor_set( "autosave_gige.req", 5, "IOC=XPP:USR:IOC:GIG1" )

# All IOCs should dump some common info after initial startup.
< /reg/d/iocCommon/All/post_linux.cmd
