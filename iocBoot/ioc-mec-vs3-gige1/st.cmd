#! ../../bin/linux-x86_64/gige

# Run common startup commands for linux soft IOC's
< /reg/d/iocCommon/All/pre_linux.cmd

< envPaths

epicsEnvSet( "ENGINEER", "Pavel Stoffel (pstoffel)" )
epicsEnvSet( "LOCATION",  "MEC:B999M64A:IOC:44" )
epicsEnvSet( "IOC",       "ioc-mec-vs3-gige1")
epicsEnvSet( "IOCSH_PS1", "$(IOC)> " )

epicsEnvSet("PREFIX", "MEC:VS3:")
epicsEnvSet("CAM1",   "CAM1")
epicsEnvSet("IMG1",   "IMAGE1")

# ----- Manta G-046B -----
epicsEnvSet("C1_IP",         "192.168.100.2")
epicsEnvSet("C1_XSIZE",      "780")
epicsEnvSet("C1_YSIZE",      "580")
epicsEnvSet("C1_COLORMODE",  "0")        # 0=Mono, 2=RGB1
epicsEnvSet("C1_NELEMENTS",  "452400")   # X * Y

# -----------------------

epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES", "8000000")

cd( "../.." )

# Register all support components
dbLoadDatabase("dbd/gige.dbd")
gige_registerRecordDeviceDriver(pdbbase)

##############################################################
# configure and initialize the camera
#   Args:  port, dummy, ip, nbufers, nbufers x width x height + overhead
prosilicaConfigIp(  "$(CAM1)", 999999, "$(C1_IP)", 50, -1)
epicsThreadSleep(1)

##############################################################

#asynSetTraceMask("$(CAM1)",0,9)
#asynSetTraceIOMask("$(CAM1)",0,2)

dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/ADBase.template",   "P=$(PREFIX),R=$(CAM1):,PORT=$(CAM1),ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDFile.template",   "P=$(PREFIX),R=$(CAM1):,PORT=$(CAM1),ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/prosilica.template","P=$(PREFIX),R=$(CAM1):,PORT=$(CAM1),ADDR=0,TIMEOUT=1")

# Create a standard arrays plugin, set it to get data from first Prosilica driver.
NDStdArraysConfigure("$(IMG1)", 5, 0, "$(CAM1)", 0, -1)
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=$(PREFIX),R=$(IMG1):,PORT=$(IMG1),ADDR=0,TIMEOUT=1,NDARRAY_PORT=$(CAM1),NDARRAY_ADDR=0")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDStdArrays.template", "P=$(PREFIX),R=$(IMG1):,PORT=$(IMG1),ADDR=0,TIMEOUT=1,TYPE=Int8,FTVL=UCHAR,NELEMENTS=$(C1_NELEMENTS)")

# Load record instances
dbLoadRecords( "db/iocAdmin.db",			"IOC=$(LOCATION)" )
dbLoadRecords( "db/save_restoreStatus.db",	"IOC=$(LOCATION)" )

# Setup autosave
set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
set_requestfile_path( "autosave" )
save_restoreSet_status_prefix("$(LOCATION)")
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )
set_pass0_restoreFile( "$(IOC).sav" )
set_pass1_restoreFile( "$(IOC).sav" )

save_restoreSet_NumSeqFiles(5)
save_restoreSet_SeqPeriodInSeconds(30)

# Initialize the IOC and start processing records
iocInit()

dbpf $(PREFIX)$(CAM1):ArrayCallbacks 1
dbpf $(PREFIX)$(IMG1):EnableCallbacks 1
#
dbpf $(PREFIX)$(CAM1):ColorMode $(C1_COLORMODE)         # 0=Mono, 2=RGB1
dbpf $(PREFIX)$(CAM1):DataType 0                        # 0=UInt8, 1=UInt16
dbpf $(PREFIX)$(CAM1):ImageMode 2                       # 0=Single, 1=Multiple, 2=Continuous
dbpf $(PREFIX)$(CAM1):TriggerMode 5                     # 0=Free Run, 1=SyncIn1, 5=Fixed Rate
#
##dbpf $(PREFIX)$(CAM1):AcquirePeriod 1
##dbpf $(PREFIX)$(CAM1):AcquireTime 0.1
##dbpf $(PREFIX)$(CAM1):Gain 0
#
##dbpf $(PREFIX)$(CAM1):Acquire 1                         # Start the camera

# ----------
# Start autosave backups
create_monitor_set("$(IOC).req", 5, "CAM=$(PREFIX)$(CAM1),IMG=$(PREFIX)$(IMG1)")

# All IOCs should dump some common info after initial startup.
< /reg/d/iocCommon/All/post_linux.cmd
