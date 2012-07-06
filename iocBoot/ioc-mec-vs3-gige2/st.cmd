#! ../../bin/linux-x86_64/gige

# Run common startup commands for linux soft IOC's
< /reg/d/iocCommon/All/pre_linux.cmd

< envPaths

epicsEnvSet( "ENGINEER", "Pavel Stoffel (pstoffel)" )
epicsEnvSet( "LOCATION",  "MEC:M64A:43" )
epicsEnvSet( "IOC",       "ioc-mec-vs3-gige2")
epicsEnvSet( "IOCSH_PS1", "$(IOC)> " )

epicsEnvSet("PREFIX", "MEC:VS3:")
epicsEnvSet("CAM2",   "CAM2")
epicsEnvSet("IMG2",   "IMAGE2")

# ----- Manta G-145B -----
epicsEnvSet("C2_IP",         "192.168.101.2")
epicsEnvSet("C2_XSIZE",      "780")
epicsEnvSet("C2_YSIZE",      "580")
epicsEnvSet("C3_COLORMODE",  "0")        # 0=Mono, 2=RGB1
epicsEnvSet("C2_NELEMENTS",  "452400")   # X * Y

# -----------------------

epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES", "8000000")

cd( "../.." )

# Register all support components
dbLoadDatabase("dbd/gige.dbd")
gige_registerRecordDeviceDriver(pdbbase)

##############################################################
# configure and initialize the camera
#   Args:  port, dummy, ip, nbufers, nbufers x width x height + overhead
prosilicaConfigIp(  "$(CAM2)", 999999, "$(C2_IP)", 50, -1)
epicsThreadSleep(1)

##############################################################

#asynSetTraceMask("$(CAM2)",0,9)
#asynSetTraceIOMask("$(CAM2)",0,2)

dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/ADBase.template",   "P=$(PREFIX),R=$(CAM2):,PORT=$(CAM2),ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDFile.template",   "P=$(PREFIX),R=$(CAM2):,PORT=$(CAM2),ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/prosilica.template","P=$(PREFIX),R=$(CAM2):,PORT=$(CAM2),ADDR=0,TIMEOUT=1")

# Create a standard arrays plugin, set it to get data from first Prosilica driver.
NDStdArraysConfigure("$(IMG2)", 5, 0, "$(CAM2)", 0, -1)
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=$(PREFIX),R=$(IMG2):,PORT=$(IMG2),ADDR=0,TIMEOUT=1,NDARRAY_PORT=$(CAM2),NDARRAY_ADDR=0")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDStdArrays.template", "P=$(PREFIX),R=$(IMG2):,PORT=$(IMG2),ADDR=0,TIMEOUT=1,TYPE=Int8,FTVL=UCHAR,NELEMENTS=$(C2_NELEMENTS)")

# Load record instances
dbLoadRecords( "db/iocAdmin.db",		"IOC=IOC:MEC:VS3:GIGE2" )
dbLoadRecords( "db/save_restoreStatus.db",	"IOC=IOC:MEC:VS3:GIGE2" )

# Setup autosave
set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
set_requestfile_path( "autosave" )
save_restoreSet_status_prefix("IOC:MEC:VS3:GIGE2")
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )
set_pass0_restoreFile( "$(IOC).sav" )
set_pass1_restoreFile( "$(IOC).sav" )

save_restoreSet_NumSeqFiles(5)
save_restoreSet_SeqPeriodInSeconds(30)

# Initialize the IOC and start processing records
iocInit()

dbpf $(PREFIX)$(CAM2):ArrayCallbacks 1
dbpf $(PREFIX)$(IMG2):EnableCallbacks 1
#
dbpf $(PREFIX)$(CAM2):ColorMode $(C2_COLORMODE)         # 0=Mono, 2=RGB1
dbpf $(PREFIX)$(CAM2):DataType 0                        # 0=UInt8, 1=UInt16
dbpf $(PREFIX)$(CAM2):ImageMode 2                       # 0=Single, 1=Multiple, 2=Continuous
dbpf $(PREFIX)$(CAM2):TriggerMode 5                     # 0=Free Run, 1=SyncIn1, 5=Fixed Rate
#
##dbpf $(PREFIX)$(CAM2):AcquirePeriod 1
##dbpf $(PREFIX)$(CAM2):AcquireTime 0.1
##dbpf $(PREFIX)$(CAM2):Gain 0
#
##dbpf $(PREFIX)$(CAM2):Acquire 1                         # Start the camera

# ----------
# Start autosave backups
create_monitor_set("$(IOC).req", 5, "CAM=$(PREFIX)$(CAM2),IMG=$(PREFIX)$(IMG2)")

# All IOCs should dump some common info after initial startup.
< /reg/d/iocCommon/All/post_linux.cmd
