#! ../../bin/linux-x86_64/gige

# Run common startup commands for linux soft IOC's
< /reg/d/iocCommon/All/pre_linux.cmd

< envPaths

epicsEnvSet( "ENGINEER", "Bruce Hill (bhill)" )
epicsEnvSet( "LOCATION",  "SXR GigE 01" )
epicsEnvSet( "IOC_PV",    "SXR:IOC:GIGE:01"
epicsEnvSet( "IOC",       "ioc-sxr-gige-01")
epicsEnvSet( "IOCSH_PS1", "$(IOC)> " )

epicsEnvSet("PREFIX", "SXR:GIGE:")
epicsEnvSet("CAM",    "CAM1")
epicsEnvSet("IMG",    "IMAGE")

# ----- Manta 201B -----
epicsEnvSet("C1_IP",         "gige-sxr-cam01" )
# TODO: Update image size for Manta 201B - These values are for G146C
epicsEnvSet("C1_XSIZE",      "1624")
epicsEnvSet("C1_YSIZE",      "1234")
epicsEnvSet("C1_COLORMODE",  "0")        # 0=Mono, 2=RGB1
epicsEnvSet("C1_NELEMENTS",  "2004016")  # X * Y * 3

# -----------------------

epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES", "8000000")

cd( "../.." )

# Register all support components
dbLoadDatabase("dbd/gige.dbd")
gige_registerRecordDeviceDriver(pdbbase)

##############################################################
# configure and initialize the camera
#   Args:  port, dummy, ip, nbufers, nbufers x width x height + overhead
prosilicaConfig(  "$(CAM)", "$(C1_IP)", 50, -1)
##############################################################

#asynSetTraceMask("$(CAM)",0,9)
#asynSetTraceIOMask("$(CAM)",0,2)

dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/ADBase.template",   "P=$(PREFIX),R=$(CAM):,PORT=$(CAM),ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDFile.template",   "P=$(PREFIX),R=$(CAM):,PORT=$(CAM),ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/prosilica.template","P=$(PREFIX),R=$(CAM):,PORT=$(CAM),ADDR=0,TIMEOUT=1,TRSCAN=1 second")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/cross.template",	 "P=$(PREFIX),R=$(CAM):,PORT=$(CAM),ADDR=0,TIMEOUT=1")

# Create a standard arrays plugin, set it to get data from first Prosilica driver.
NDStdArraysConfigure("$(IMG)", 5, 0, "$(CAM)", 0, -1)
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=$(PREFIX),R=$(IMG):,PORT=$(IMG),ADDR=0,TIMEOUT=1,NDARRAY_PORT=$(CAM),NDARRAY_ADDR=0")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDStdArrays.template", "P=$(PREFIX),R=$(IMG):,PORT=$(IMG),ADDR=0,TIMEOUT=1,TYPE=Int8,FTVL=UCHAR,NELEMENTS=$(C1_NELEMENTS)")

# Create a JPEG File plugin, set it to get data from the camera
NDFileJPEGConfigure( "FileJPEG", 5, 0, "$(CAM)", 0, 0)
dbLoadRecords( "$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template", "P=$(PREFIX)$(CAM):,R=JPEG:,PORT=FileJPEG,ADDR=0,TIMEOUT=1,NDARRAY_PORT=$(CAM),NDARRAY_ADDR=0")
dbLoadRecords( "$(AREA_DETECTOR)/ADApp/Db/NDFile.template",       "P=$(PREFIX)$(CAM):,R=JPEG:,PORT=FileJPEG,ADDR=0,TIMEOUT=1" )
dbLoadRecords( "$(AREA_DETECTOR)/ADApp/Db/NDFileJPEG.template",   "P=$(PREFIX)$(CAM):,R=JPEG:,PORT=FileJPEG,ADDR=0,TIMEOUT=1" )

# Create 2 ROI plugin's
NDROIConfigure( "ROI1", 5, 0, "$(CAM)", 0, 0, 0 )
dbLoadRecords( "$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template", "P=$(PREFIX)$(CAM):,R=ROI1:,PORT=ROI1,ADDR=0,TIMEOUT=1,NDARRAY_PORT=$(CAM),NDARRAY_ADDR=0")
dbLoadRecords( "$(AREA_DETECTOR)/ADApp/Db/NDROI.template",        "P=$(PREFIX)$(CAM):,R=ROI1:,PORT=ROI1,ADDR=0,TIMEOUT=1" )
NDROIConfigure( "ROI2", 5, 0, "$(CAM)", 0, 0, 0 )
dbLoadRecords( "$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template", "P=$(PREFIX)$(CAM):,R=ROI2:,PORT=ROI2,ADDR=0,TIMEOUT=1,NDARRAY_PORT=$(CAM),NDARRAY_ADDR=0")
dbLoadRecords( "$(AREA_DETECTOR)/ADApp/Db/NDROI.template",        "P=$(PREFIX):$(CAM),R=ROI2:,PORT=ROI2,ADDR=0,TIMEOUT=1" )

# Load record instances
dbLoadRecords( "db/iocAdmin.db",			"IOC=$(IOC_PV)" )
dbLoadRecords( "db/save_restoreStatus.db",	"IOC=$(IOC_PV)" )

# Setup autosave
set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
set_requestfile_path( "autosave" )
save_restoreSet_status_prefix("$(IOC_PV)")
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )
set_pass0_restoreFile( "$(IOC).sav" )
set_pass1_restoreFile( "$(IOC).sav" )

save_restoreSet_NumSeqFiles(5)
save_restoreSet_SeqPeriodInSeconds(30)

# Initialize the IOC and start processing records
iocInit()

dbpf $(PREFIX)$(CAM):ArrayCallbacks 1
dbpf $(PREFIX)$(IMG):EnableCallbacks 1
#
dbpf $(PREFIX)$(CAM):ColorMode $(C1_COLORMODE)         # 0=Mono, 2=RGB1
dbpf $(PREFIX)$(CAM):DataType 0                        # 0=UInt8, 1=UInt16
#dbpf $(PREFIX)$(CAM):ImageMode 2                       # 0=Single, 1=Multiple, 2=Continuous
#dbpf $(PREFIX)$(CAM):TriggerMode 5                     # 0=Free Run, 1=SyncIn1, 5=Fixed Rate
#
##dbpf $(PREFIX)$(CAM):AcquirePeriod 1
##dbpf $(PREFIX)$(CAM):AcquireTime 0.1
##dbpf $(PREFIX)$(CAM):Gain 0
#
##dbpf $(PREFIX)$(CAM):Acquire 1                         # Start the camera

# ----------

# Start autosave backups
create_monitor_set("$(IOC).req", 5, "CAM=$(PREFIX)$(CAM),IMG=$(PREFIX)$(IMG)")

# All IOCs should dump some common info after initial startup.
< /reg/d/iocCommon/All/post_linux.cmd