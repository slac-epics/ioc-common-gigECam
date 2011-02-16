#!../../bin/linux-x86_64/gige

< envPaths
epicsEnvSet( "ENGINEER", "Pavel Stoffel" )
epicsEnvSet( "LOCATION", "XPP:R37:IOC:14" )
epicsEnvSet( "IOC", "ioc-xpp-gige-cam2" )
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
prosilicaConfigIp(  "PS2", 116474, "172.21.38.67", 50, 70000000)
##############################################################

# Load record instances
dbLoadRecords( "db/iocAdmin.db",			"IOC=XPP:USR:IOC:GIGE2" )
dbLoadRecords( "db/save_restoreStatus.db",	"IOC=XPP:USR:IOC:GIGE2" )
#
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/ADBase.template",   "P=XPP:USR:GIGE2:,R=cam1:,PORT=PS2,ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/prosilica.template","P=XPP:USR:GIGE2:,R=cam1:,PORT=PS2,ADDR=0,TIMEOUT=1")
#
# Create a standard arrays plugin, set it to get data from first Prosilica driver.
drvNDStdArraysConfigure("PS2Image", 5, 0, "PS2", 0, -1)
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=XPP:USR:GIGE2:,R=image1:,PORT=PS2Image,ADDR=0,TIMEOUT=1,NDARRAY_PORT=PS2,NDARRAY_ADDR=0")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDStdArrays.template", "P=XPP:USR:GIGE2:,R=image1:,PORT=PS2Image,ADDR=0,TIMEOUT=1,SIZE=8,FTVL=UCHAR,NELEMENTS=1392640")
#
# Create a file saving plugin
drvNDFileConfigure("PS2File", 5, 0, "PS2", 0)
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=XPP:USR:GIGE2:,R=file1:,PORT=PS2File,ADDR=0,TIMEOUT=1,NDARRAY_PORT=PS2,NDARRAY_ADDR=0")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDFile.template",      "P=XPP:USR:GIGE2:,R=file1:,PORT=PS2File,ADDR=0,TIMEOUT=1")
#
# Create an ROI plugin
drvNDROIConfigure("PS2ROI", 5, 0, "PS2", 0, 10, -1)
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=XPP:USR:GIGE2:,R=ROI1:,  PORT=PS2ROI,ADDR=0,TIMEOUT=1,NDARRAY_PORT=PS2,NDARRAY_ADDR=0")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDROI.template",       "P=XPP:USR:GIGE2:,R=ROI1:,  PORT=PS2ROI,ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDROIN.template",      "P=XPP:USR:GIGE2:,R=ROI1:0:,PORT=PS2ROI,ADDR=0,TIMEOUT=1,HIST_SIZE=256")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDROIN.template",      "P=XPP:USR:GIGE2:,R=ROI1:1:,PORT=PS2ROI,ADDR=1,TIMEOUT=1,HIST_SIZE=256")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDROIN.template",      "P=XPP:USR:GIGE2:,R=ROI1:2:,PORT=PS2ROI,ADDR=2,TIMEOUT=1,HIST_SIZE=256")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDROIN.template",      "P=XPP:USR:GIGE2:,R=ROI1:3:,PORT=PS2ROI,ADDR=3,TIMEOUT=1,HIST_SIZE=256")
#
# Load a prosilica gigE camera
#dbLoadRecords( "db/gigE.db",      "P=XPP:USR:GIGE2,PORT=PS2,IMAGE_PORT=PS2Image,FILE_PORT=PS2File,ROI_PORT=PS2ROI,NDARRAY_PORT=PS2" )
#
# set debug flags
###asynSetTraceMask("PS2",0,255)


# Setup autosave
set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
set_requestfile_path( "$(TOP)/autosave" )
save_restoreSet_status_prefix( "XPP:USR:GIGE2" )
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )
set_pass0_restoreFile( "autosave_prosilica.sav" )
set_pass1_restoreFile( "autosave_prosilica.sav" )

# Initialize the IOC and start processing records
iocInit()

# FIXME - initialize these in the database
dbpf "XPP:USR:GIGE2:cam1:DataType" UInt8
dbpf "XPP:USR:GIGE2:cam1:SizeX" 1360
dbpf "XPP:USR:GIGE2:cam1:SizeY" 1024
dbpf "XPP:USR:GIGE2:image1:EnableCallbacks" 1

# Start autosave backups
create_monitor_set( "autosave_prosilica.req", 5, "P=XPP:USR:GIGE2" )

# All IOCs should dump some common info after initial startup.
< /reg/d/iocCommon/All/post_linux.cmd
