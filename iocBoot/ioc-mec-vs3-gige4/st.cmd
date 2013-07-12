#! ../../bin/linux-x86_64/gige

# Run common startup commands for linux soft IOC's
< /reg/d/iocCommon/All/pre_linux.cmd

< envPaths

epicsEnvSet( "ENGINEER", "Pavel Stoffel (pstoffel)" )
epicsEnvSet( "LOCATION",  "MEC:M64A:43" )
epicsEnvSet( "IOC",       "ioc-mec-vs3-gige4")
epicsEnvSet( "IOCSH_PS1", "$(IOC)> " )

epicsEnvSet("PREFIX", "MEC:VS3:")
epicsEnvSet("CAM4",   "CAM4")
epicsEnvSet("IMG4",   "IMAGE4")

# ----- Manta G-145B -----
epicsEnvSet("C4_IP",         "192.168.103.2")
epicsEnvSet("C4_XSIZE",      "780")
epicsEnvSet("C4_YSIZE",      "580")
epicsEnvSet("C4_COLORMODE",  "0")        # 0=Mono, 2=RGB1
epicsEnvSet("C4_NELEMENTS",  "452400")   # X * Y

# -----------------------

epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES", "8000000")

cd( "../.." )

# Register all support components
dbLoadDatabase("dbd/gige.dbd")
gige_registerRecordDeviceDriver(pdbbase)

##############################################################
# configure and initialize the camera
#   Args:  port, dummy, ip, nbufers, nbufers x width x height + overhead
prosilicaConfigIp(  "$(CAM4)", 999999, "$(C4_IP)", 50, -1)
epicsThreadSleep(1)

##############################################################

#asynSetTraceMask("$(CAM4)",0,9)
#asynSetTraceIOMask("$(CAM4)",0,2)

dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/ADBase.template",   "P=$(PREFIX),R=$(CAM4):,PORT=$(CAM4),ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDFile.template",   "P=$(PREFIX),R=$(CAM4):,PORT=$(CAM4),ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/prosilica.template","P=$(PREFIX),R=$(CAM4):,PORT=$(CAM4),ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/cross.template",	 "P=$(PREFIX),R=$(CAM4):,PORT=$(CAM4),ADDR=0,TIMEOUT=1")

# Create a standard arrays plugin, set it to get data from first Prosilica driver.
NDStdArraysConfigure("$(IMG4)", 5, 0, "$(CAM4)", 0, -1)
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=$(PREFIX),R=$(IMG4):,PORT=$(IMG4),ADDR=0,TIMEOUT=1,NDARRAY_PORT=$(CAM4),NDARRAY_ADDR=0")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDStdArrays.template", "P=$(PREFIX),R=$(IMG4):,PORT=$(IMG4),ADDR=0,TIMEOUT=1,TYPE=Int8,FTVL=UCHAR,NELEMENTS=$(C4_NELEMENTS)")

# Load record instances
dbLoadRecords( "db/iocAdmin.db",		"IOC=IOC:MEC:VS3:GIGE4" )
dbLoadRecords( "db/save_restoreStatus.db",	"IOC=IOC:MEC:VS3:GIGE4" )

# Setup autosave
set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
set_requestfile_path( "autosave" )
save_restoreSet_status_prefix("IOC:MEC:VS3:GIGE4")
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )
set_pass0_restoreFile( "$(IOC).sav" )
set_pass1_restoreFile( "$(IOC).sav" )

save_restoreSet_NumSeqFiles(5)
save_restoreSet_SeqPeriodInSeconds(30)

# Initialize the IOC and start processing records
iocInit()

dbpf $(PREFIX)$(CAM4):ArrayCallbacks 1
dbpf $(PREFIX)$(IMG4):EnableCallbacks 1
#
dbpf $(PREFIX)$(CAM4):ColorMode $(C4_COLORMODE)         # 0=Mono, 2=RGB1
dbpf $(PREFIX)$(CAM4):DataType 0                        # 0=UInt8, 1=UInt16
dbpf $(PREFIX)$(CAM4):ImageMode 2                       # 0=Single, 1=Multiple, 2=Continuous
dbpf $(PREFIX)$(CAM4):TriggerMode 5                     # 0=Free Run, 1=SyncIn1, 5=Fixed Rate
#
##dbpf $(PREFIX)$(CAM4):AcquirePeriod 1
##dbpf $(PREFIX)$(CAM4):AcquireTime 0.1
##dbpf $(PREFIX)$(CAM4):Gain 0
#
##dbpf $(PREFIX)$(CAM4):Acquire 1                         # Start the camera

# ----------
# Start autosave backups
create_monitor_set("$(IOC).req", 5, "CAM=$(PREFIX)$(CAM4),IMG=$(PREFIX)$(IMG4)")

# All IOCs should dump some common info after initial startup.
< /reg/d/iocCommon/All/post_linux.cmd
