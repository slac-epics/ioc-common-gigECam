#! ../../bin/linux-x86_64/gige

# Run common startup commands for linux soft IOC's
< /reg/d/iocCommon/All/pre_linux.cmd

< envPaths

epicsEnvSet( "ENGINEER", "Pavel Stoffel (pstoffel)" )
epicsEnvSet( "LOCATION",  "MEC:M64A:43" )
epicsEnvSet( "IOC",       "ioc-mec-vs3-gige3")
epicsEnvSet( "IOCSH_PS1", "$(IOC)> " )

epicsEnvSet("PREFIX", "MEC:VS3:")
epicsEnvSet("CAM3",   "CAM3")
epicsEnvSet("IMG3",   "IMAGE3")

# ----- Manta G-145B -----
epicsEnvSet("C3_IP",         "192.168.102.2")
epicsEnvSet("C3_XSIZE",      "780")
epicsEnvSet("C3_YSIZE",      "580")
epicsEnvSet("C3_COLORMODE",  "0")        # 0=Mono, 2=RGB1
epicsEnvSet("C3_NELEMENTS",  "452400")   # X * Y

# -----------------------

epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES", "8000000")

cd( "../.." )

# Register all support components
dbLoadDatabase("dbd/gige.dbd")
gige_registerRecordDeviceDriver(pdbbase)

##############################################################
# configure and initialize the camera
#   Args:  port, dummy, ip, nbufers, nbufers x width x height + overhead
prosilicaConfigIp(  "$(CAM3)", 999999, "$(C3_IP)", 50, -1)
epicsThreadSleep(1)

##############################################################

#asynSetTraceMask("$(CAM3)",0,9)
#asynSetTraceIOMask("$(CAM3)",0,2)

dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/ADBase.template",   "P=$(PREFIX),R=$(CAM3):,PORT=$(CAM3),ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDFile.template",   "P=$(PREFIX),R=$(CAM3):,PORT=$(CAM3),ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/prosilica.template","P=$(PREFIX),R=$(CAM3):,PORT=$(CAM3),ADDR=0,TIMEOUT=1")

# Create a standard arrays plugin, set it to get data from first Prosilica driver.
NDStdArraysConfigure("$(IMG3)", 5, 0, "$(CAM3)", 0, -1)
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=$(PREFIX),R=$(IMG3):,PORT=$(IMG3),ADDR=0,TIMEOUT=1,NDARRAY_PORT=$(CAM3),NDARRAY_ADDR=0")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDStdArrays.template", "P=$(PREFIX),R=$(IMG3):,PORT=$(IMG3),ADDR=0,TIMEOUT=1,TYPE=Int8,FTVL=UCHAR,NELEMENTS=$(C3_NELEMENTS)")

# Load record instances
dbLoadRecords( "db/iocAdmin.db",		"IOC=IOC:MEC:VS3:GIGE3" )
dbLoadRecords( "db/save_restoreStatus.db",	"IOC=IOC:MEC:VS3:GIGE3" )

# Setup autosave
set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
set_requestfile_path( "autosave" )
save_restoreSet_status_prefix("IOC:MEC:VS3:GIGE3")
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )
set_pass0_restoreFile( "$(IOC).sav" )
set_pass1_restoreFile( "$(IOC).sav" )

save_restoreSet_NumSeqFiles(5)
save_restoreSet_SeqPeriodInSeconds(30)

# Initialize the IOC and start processing records
iocInit()

dbpf $(PREFIX)$(CAM3):ArrayCallbacks 1
dbpf $(PREFIX)$(IMG3):EnableCallbacks 1
#
dbpf $(PREFIX)$(CAM3):ColorMode $(C3_COLORMODE)         # 0=Mono, 2=RGB1
dbpf $(PREFIX)$(CAM3):DataType 0                        # 0=UInt8, 1=UInt16
dbpf $(PREFIX)$(CAM3):ImageMode 2                       # 0=Single, 1=Multiple, 2=Continuous
dbpf $(PREFIX)$(CAM3):TriggerMode 5                     # 0=Free Run, 1=SyncIn1, 5=Fixed Rate
#
##dbpf $(PREFIX)$(CAM3):AcquirePeriod 1
##dbpf $(PREFIX)$(CAM3):AcquireTime 0.1
##dbpf $(PREFIX)$(CAM3):Gain 0
#
##dbpf $(PREFIX)$(CAM3):Acquire 1                         # Start the camera

# ----------
# Start autosave backups
create_monitor_set("$(IOC).req", 5, "CAM=$(PREFIX)$(CAM3),IMG=$(PREFIX)$(IMG3)")

# All IOCs should dump some common info after initial startup.
< /reg/d/iocCommon/All/post_linux.cmd
