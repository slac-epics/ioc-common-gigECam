#!../../bin/linux-x86_64/gige

< envPaths
epicsEnvSet( "ENGINEER", "Pavel Stoffel" )
epicsEnvSet( "LOCATION", "XPP:R37:IOC:14" )
epicsEnvSet( "IOC", "ioc-xpp-gige-cam1" )
epicsEnvSet( "IOCSH_PS1", "$(IOC)> " )
cd( "../.." )

# Run common startup commands for linux soft IOC's
< /reg/d/iocCommon/All/pre_linux.cmd

# Register all support components
dbLoadDatabase("dbd/gige.dbd")
gige_registerRecordDeviceDriver(pdbbase)


##############################################################
# configure and initialize the camera
#   Args:  port, dummy, ip, nbufers, nbufers x width x height + overhead
prosilicaConfigIp(  "PS1", 116474, "172.21.38.66", 50, 70000000)
##############################################################

# Load record instances
dbLoadRecords( "db/iocAdmin.db",			"IOC=XPP:USR:IOC:GIGE1" )
dbLoadRecords( "db/save_restoreStatus.db",	"IOC=XPP:USR:IOC:GIGE1" )
#
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/ADBase.template",   "P=XPP:USR:GIGE1:,R=cam1:,PORT=PS1,ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/prosilica.template","P=XPP:USR:GIGE1:,R=cam1:,PORT=PS1,ADDR=0,TIMEOUT=1")
#
# Create a standard arrays plugin, set it to get data from first Prosilica driver.
drvNDStdArraysConfigure("PS1Image", 5, 0, "PS1", 0, -1)
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=XPP:USR:GIGE1:,R=image1:,PORT=PS1Image,ADDR=0,TIMEOUT=1,NDARRAY_PORT=PS1,NDARRAY_ADDR=0")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDStdArrays.template", "P=XPP:USR:GIGE1:,R=image1:,PORT=PS1Image,ADDR=0,TIMEOUT=1,SIZE=8,FTVL=UCHAR,NELEMENTS=1392640")
#
# Create a file saving plugin
drvNDFileConfigure("PS1File", 5, 0, "PS1", 0)
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=XPP:USR:GIGE1:,R=file1:,PORT=PS1File,ADDR=0,TIMEOUT=1,NDARRAY_PORT=PS1,NDARRAY_ADDR=0")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDFile.template",      "P=XPP:USR:GIGE1:,R=file1:,PORT=PS1File,ADDR=0,TIMEOUT=1")
#
# Create an ROI plugin
drvNDROIConfigure("PS1ROI", 5, 0, "PS1", 0, 10, -1)
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=XPP:USR:GIGE1:,R=ROI1:,  PORT=PS1ROI,ADDR=0,TIMEOUT=1,NDARRAY_PORT=PS1,NDARRAY_ADDR=0")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDROI.template",       "P=XPP:USR:GIGE1:,R=ROI1:,  PORT=PS1ROI,ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDROIN.template",      "P=XPP:USR:GIGE1:,R=ROI1:0:,PORT=PS1ROI,ADDR=0,TIMEOUT=1,HIST_SIZE=256")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDROIN.template",      "P=XPP:USR:GIGE1:,R=ROI1:1:,PORT=PS1ROI,ADDR=1,TIMEOUT=1,HIST_SIZE=256")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDROIN.template",      "P=XPP:USR:GIGE1:,R=ROI1:2:,PORT=PS1ROI,ADDR=2,TIMEOUT=1,HIST_SIZE=256")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDROIN.template",      "P=XPP:USR:GIGE1:,R=ROI1:3:,PORT=PS1ROI,ADDR=3,TIMEOUT=1,HIST_SIZE=256")
#
# Load a prosilica gigE camera
#dbLoadRecords( "db/gigE.db",      "P=XPP:USR:GIGE1,PORT=PS1,IMAGE_PORT=PS1Image,FILE_PORT=PS1File,ROI_PORT=PS1ROI,NDARRAY_PORT=PS1" )
#
# set debug flags
###asynSetTraceMask("PS1",0,255)
#
# Setup autosave
set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
set_requestfile_path( "$(TOP)/autosave" )
save_restoreSet_status_prefix( "XPP:USR:GIGE1" )
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )
set_pass0_restoreFile( "autosave_prosilica.sav" )
set_pass1_restoreFile( "autosave_prosilica.sav" )

# Initialize the IOC and start processing records
iocInit()

# FIXME - initialize these in the database
dbpf "XPP:USR:GIGE1:cam1:DataType" UInt8
dbpf "XPP:USR:GIGE1:cam1:SizeX" 1360
dbpf "XPP:USR:GIGE1:cam1:SizeY" 1024
dbpf "XPP:USR:GIGE1:image1:EnableCallbacks" 1

# Start autosave backups
create_monitor_set( "autosave_prosilica.req", 5, "P=XPP:USR:GIGE1" )

# All IOCs should dump some common info after initial startup.
< /reg/d/iocCommon/All/post_linux.cmd
