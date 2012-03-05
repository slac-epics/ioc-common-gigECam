#! ../../bin/linux-x86_64/gige

# Run common startup commands for linux soft IOC's
< /reg/d/iocCommon/All/pre_linux.cmd

< envPaths

epicsEnvSet( "ENGINEER", "Pavel Stoffel (pstoffel)" )
# FIXME: elevation
epicsEnvSet( "LOCATION",  "TST:R40:IOC:88" )
epicsEnvSet( "IOC",       "ioc-tst-gige3")
epicsEnvSet( "IOCSH_PS1", "$(IOC)> " )

epicsEnvSet("PREFIX", "TST:GIGE:")
epicsEnvSet("CAM1",   "CAM1")
epicsEnvSet("IMG1",   "IMAGE1")
epicsEnvSet("CAM2",   "CAM2")
epicsEnvSet("IMG2",   "IMAGE2")
epicsEnvSet("CAM3",   "CAM3")
epicsEnvSet("IMG3",   "IMAGE3")
epicsEnvSet("CAM4",   "CAM4")
epicsEnvSet("IMG4",   "IMAGE4")

# ----- Manta G046B -----
epicsEnvSet("CAM1_ENABLED",  "")                             # "" = YES,  "#" = NO
epicsEnvSet("C1_IP",         "192.168.101.2")
epicsEnvSet("C1_XSIZE",      "780")
epicsEnvSet("C1_YSIZE",      "580")
epicsEnvSet("C1_COLORMODE",  "0")        # 0=Mono, 2=RGB1
epicsEnvSet("C1_NELEMENTS",  "452400")   # X * Y

# ----- Manta G145B -----
#epicsEnvSet("CAM1_ENABLED",  "")                             # "" = YES,  "#" = NO
#epicsEnvSet("C1_IP",         "192.168.100.10")
#epicsEnvSet("C1_XSIZE",      "1390")
#epicsEnvSet("C1_YSIZE",      "1038")
#epicsEnvSet("C1_COLORMODE",  "0")        # 0=Mono, 2=RGB1
#epicsEnvSet("C1_NELEMENTS",  "1442820")  # X * Y

# ----- Manta G146C -----
#epicsEnvSet("CAM1_ENABLED",  "")                             # "" = YES,  "#" = NO
##epicsEnvSet("C1_IP",         "192.168.0.105")  #XCS
#epicsEnvSet("C1_IP",         "192.168.100.20")
#epicsEnvSet("C1_XSIZE",      "1388")
#epicsEnvSet("C1_YSIZE",      "1038")
#epicsEnvSet("C1_COLORMODE",  "2")        # 0=Mono, 2=RGB1
#epicsEnvSet("C1_NELEMENTS",  "4322232")  # X * Y * 3

# ----- Manta G146C -----
epicsEnvSet("CAM2_ENABLED",  "#")                             # "" = YES,  "#" = NO
epicsEnvSet("C2_IP",         "192.168.100.20")
epicsEnvSet("C2_XSIZE",      "1388")
epicsEnvSet("C2_YSIZE",      "1038")
epicsEnvSet("C2_COLORMODE",  "2")        # 0=Mono, 2=RGB1
epicsEnvSet("C2_NELEMENTS",  "4322232")  # X * Y * 3

# ----- Manta G146C -----
epicsEnvSet("CAM3_ENABLED",  "#")                             # "" = YES,  "#" = NO
epicsEnvSet("C3_IP",         "192.168.100.30")
epicsEnvSet("C3_XSIZE",      "1388")
epicsEnvSet("C3_YSIZE",      "1038")
epicsEnvSet("C3_COLORMODE",  "2")        # 0=Mono, 2=RGB1
epicsEnvSet("C3_NELEMENTS",  "4322232")  # X * Y * 3

# ----- Manta G146C -----
epicsEnvSet("CAM4_ENABLED",  "#")                             # "" = YES,  "#" = NO
epicsEnvSet("C4_IP",         "192.168.100.40")
epicsEnvSet("C4_XSIZE",      "1388")
epicsEnvSet("C4_YSIZE",      "1038")
epicsEnvSet("C4_COLORMODE",  "2")        # 0=Mono, 2=RGB1
epicsEnvSet("C4_NELEMENTS",  "4322232")  # X * Y * 3

# -----------------------

epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES", "8000000")

cd( "../.." )

# Register all support components
dbLoadDatabase("dbd/gige.dbd")
gige_registerRecordDeviceDriver(pdbbase)

##############################################################
# configure and initialize the camera
#   Args:  port, dummy, ip, nbufers, nbufers x width x height + overhead
$(CAM1_ENABLED) prosilicaConfigIp(  "$(CAM1)", 999999, "$(C1_IP)", 50, -1)
$(CAM1_ENABLED) epicsThreadSleep(1)
$(CAM2_ENABLED) prosilicaConfigIp(  "$(CAM2)", 999999, "$(C2_IP)", 50, -1)
$(CAM2_ENABLED) epicsThreadSleep(1)
$(CAM3_ENABLED) prosilicaConfigIp(  "$(CAM3)", 999999, "$(C3_IP)", 50, -1)
$(CAM3_ENABLED) epicsThreadSleep(1)
$(CAM4_ENABLED) prosilicaConfigIp(  "$(CAM4)", 999999, "$(C4_IP)", 50, -1)
$(CAM4_ENABLED) epicsThreadSleep(1)

##############################################################

#asynSetTraceMask("$(CAM1)",0,9)
#asynSetTraceIOMask("$(CAM1)",0,2)
#asynSetTraceMask("$(CAM2)",0,9)
#asynSetTraceIOMask("$(CAM2)",0,2)
#asynSetTraceMask("$(CAM3)",0,9)
#asynSetTraceIOMask("$(CAM3)",0,2)
#asynSetTraceMask("$(CAM4)",0,9)
#asynSetTraceIOMask("$(CAM4)",0,2)

$(CAM1_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/ADBase.template",   "P=$(PREFIX),R=$(CAM1):,PORT=$(CAM1),ADDR=0,TIMEOUT=1")
$(CAM1_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDFile.template",   "P=$(PREFIX),R=$(CAM1):,PORT=$(CAM1),ADDR=0,TIMEOUT=1")
$(CAM1_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/prosilica.template","P=$(PREFIX),R=$(CAM1):,PORT=$(CAM1),ADDR=0,TIMEOUT=1")
$(CAM2_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/ADBase.template",   "P=$(PREFIX),R=$(CAM2):,PORT=$(CAM2),ADDR=0,TIMEOUT=1")
$(CAM2_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDFile.template",   "P=$(PREFIX),R=$(CAM2):,PORT=$(CAM2),ADDR=0,TIMEOUT=1")
$(CAM2_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/prosilica.template","P=$(PREFIX),R=$(CAM2):,PORT=$(CAM2),ADDR=0,TIMEOUT=1")
$(CAM3_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/ADBase.template",   "P=$(PREFIX),R=$(CAM3):,PORT=$(CAM3),ADDR=0,TIMEOUT=1")
$(CAM3_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDFile.template",   "P=$(PREFIX),R=$(CAM3):,PORT=$(CAM3),ADDR=0,TIMEOUT=1")
$(CAM3_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/prosilica.template","P=$(PREFIX),R=$(CAM3):,PORT=$(CAM3),ADDR=0,TIMEOUT=1")
$(CAM4_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/ADBase.template",   "P=$(PREFIX),R=$(CAM4):,PORT=$(CAM4),ADDR=0,TIMEOUT=1")
$(CAM4_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDFile.template",   "P=$(PREFIX),R=$(CAM4):,PORT=$(CAM4),ADDR=0,TIMEOUT=1")
$(CAM4_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/prosilica.template","P=$(PREFIX),R=$(CAM4):,PORT=$(CAM4),ADDR=0,TIMEOUT=1")

# Create a standard arrays plugin, set it to get data from first Prosilica driver.
$(CAM1_ENABLED) NDStdArraysConfigure("$(IMG1)", 5, 0, "$(CAM1)", 0, -1)
$(CAM1_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=$(PREFIX),R=$(IMG1):,PORT=$(IMG1),ADDR=0,TIMEOUT=1,NDARRAY_PORT=$(CAM1),NDARRAY_ADDR=0")
$(CAM1_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDStdArrays.template", "P=$(PREFIX),R=$(IMG1):,PORT=$(IMG1),ADDR=0,TIMEOUT=1,TYPE=Int8,FTVL=UCHAR,NELEMENTS=$(C1_NELEMENTS)")

# Create a standard arrays plugin, set it to get data from first Prosilica driver.
$(CAM2_ENABLED) NDStdArraysConfigure("$(IMG2)", 5, 0, "$(CAM2)", 0, -1)
$(CAM2_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=$(PREFIX),R=$(IMG2):,PORT=$(IMG2),ADDR=0,TIMEOUT=1,NDARRAY_PORT=$(CAM2),NDARRAY_ADDR=0")
$(CAM2_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDStdArrays.template", "P=$(PREFIX),R=$(IMG2):,PORT=$(IMG2),ADDR=0,TIMEOUT=1,TYPE=Int8,FTVL=UCHAR,NELEMENTS=$(C2_NELEMENTS)")

# Create a standard arrays plugin, set it to get data from first Prosilica driver.
$(CAM3_ENABLED) NDStdArraysConfigure("$(IMG3)", 5, 0, "$(CAM3)", 0, -1)
$(CAM3_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=$(PREFIX),R=$(IMG3):,PORT=$(IMG3),ADDR=0,TIMEOUT=1,NDARRAY_PORT=$(CAM3),NDARRAY_ADDR=0")
$(CAM3_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDStdArrays.template", "P=$(PREFIX),R=$(IMG3):,PORT=$(IMG3),ADDR=0,TIMEOUT=1,TYPE=Int8,FTVL=UCHAR,NELEMENTS=$(C3_NELEMENTS)")

# Create a standard arrays plugin, set it to get data from first Prosilica driver.
$(CAM4_ENABLED) NDStdArraysConfigure("$(IMG4)", 5, 0, "$(CAM4)", 0, -1)
$(CAM4_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=$(PREFIX),R=$(IMG4):,PORT=$(IMG4),ADDR=0,TIMEOUT=1,NDARRAY_PORT=$(CAM4),NDARRAY_ADDR=0")
$(CAM4_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDStdArrays.template", "P=$(PREFIX),R=$(IMG4):,PORT=$(IMG4),ADDR=0,TIMEOUT=1,TYPE=Int8,FTVL=UCHAR,NELEMENTS=$(C4_NELEMENTS)")

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

$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1):ArrayCallbacks 1
$(CAM1_ENABLED) dbpf $(PREFIX)$(IMG1):EnableCallbacks 1
#
$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1):ColorMode $(C1_COLORMODE)         # 0=Mono, 2=RGB1
$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1):DataType 0                        # 0=UInt8, 1=UInt16
$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1):ImageMode 2                       # 0=Single, 1=Multiple, 2=Continuous
$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1):TriggerMode 5                     # 0=Free Run, 1=SyncIn1, 5=Fixed Rate
#
$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1):AcquirePeriod 1
$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1):AcquireTime 0.1
$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1):Gain 0
#
$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1):Acquire 1                         # Start the camera
#
$(CAM1_ENABLED) dbpr $(PREFIX)$(CAM1):ArrayCounter_RBV

# ----------

$(CAM2_ENABLED) dbpf $(PREFIX)$(CAM2):ArrayCallbacks 1
$(CAM2_ENABLED) dbpf $(PREFIX)$(IMG2):EnableCallbacks 1
#
$(CAM2_ENABLED) dbpf $(PREFIX)$(CAM2):ColorMode $(C2_COLORMODE)         # 0=Mono, 2=RGB1
$(CAM2_ENABLED) dbpf $(PREFIX)$(CAM2):DataType 0                        # 0=UInt8, 1=UInt16
$(CAM2_ENABLED) dbpf $(PREFIX)$(CAM2):ImageMode 2                       # 0=Single, 1=Multiple, 2=Continuous
$(CAM2_ENABLED) dbpf $(PREFIX)$(CAM2):TriggerMode 5                     # 0=Free Run, 1=SyncIn1, 5=Fixed Rate
#
$(CAM2_ENABLED) dbpf $(PREFIX)$(CAM2):AcquirePeriod 1
$(CAM2_ENABLED) dbpf $(PREFIX)$(CAM2):AcquireTime 0.1
$(CAM2_ENABLED) dbpf $(PREFIX)$(CAM2):Gain 0
#
$(CAM2_ENABLED) dbpf $(PREFIX)$(CAM2):Acquire 1                         # Start the camera
#
$(CAM2_ENABLED) dbpr $(PREFIX)$(CAM2):ArrayCounter_RBV

# ----------

$(CAM3_ENABLED) dbpf $(PREFIX)$(CAM3):ArrayCallbacks 1
$(CAM3_ENABLED) dbpf $(PREFIX)$(IMG3):EnableCallbacks 1
#
$(CAM3_ENABLED) dbpf $(PREFIX)$(CAM3):ColorMode $(C3_COLORMODE)         # 0=Mono, 2=RGB1
$(CAM3_ENABLED) dbpf $(PREFIX)$(CAM3):DataType 0                        # 0=UInt8, 1=UInt16
$(CAM3_ENABLED) dbpf $(PREFIX)$(CAM3):ImageMode 2                       # 0=Single, 1=Multiple, 2=Continuous
$(CAM3_ENABLED) dbpf $(PREFIX)$(CAM3):TriggerMode 5                     # 0=Free Run, 1=SyncIn1, 5=Fixed Rate
#
$(CAM3_ENABLED) dbpf $(PREFIX)$(CAM3):AcquirePeriod 1
$(CAM3_ENABLED) dbpf $(PREFIX)$(CAM3):AcquireTime 0.1
$(CAM3_ENABLED) dbpf $(PREFIX)$(CAM3):Gain 0
#
$(CAM3_ENABLED) dbpf $(PREFIX)$(CAM3):Acquire 1                         # Start the camera
#
$(CAM3_ENABLED) dbpr $(PREFIX)$(CAM3):ArrayCounter_RBV

# ----------

$(CAM4_ENABLED) dbpf $(PREFIX)$(CAM4):ArrayCallbacks 1
$(CAM4_ENABLED) dbpf $(PREFIX)$(IMG4):EnableCallbacks 1
#
$(CAM4_ENABLED) dbpf $(PREFIX)$(CAM4):ColorMode $(C4_COLORMODE)         # 0=Mono, 2=RGB1
$(CAM4_ENABLED) dbpf $(PREFIX)$(CAM4):DataType 0                        # 0=UInt8, 1=UInt16
$(CAM4_ENABLED) dbpf $(PREFIX)$(CAM4):ImageMode 2                       # 0=Single, 1=Multiple, 2=Continuous
$(CAM4_ENABLED) dbpf $(PREFIX)$(CAM4):TriggerMode 5                     # 0=Free Run, 1=SyncIn1, 5=Fixed Rate
#
$(CAM4_ENABLED) dbpf $(PREFIX)$(CAM4):AcquirePeriod 1
$(CAM4_ENABLED) dbpf $(PREFIX)$(CAM4):AcquireTime 0.1
$(CAM4_ENABLED) dbpf $(PREFIX)$(CAM4):Gain 0
#
$(CAM4_ENABLED) dbpf $(PREFIX)$(CAM4):Acquire 1                         # Start the camera
#
$(CAM4_ENABLED) dbpr $(PREFIX)$(CAM4):ArrayCounter_RBV

# ----------

# Start autosave backups
$(CAM1_ENABLED) create_monitor_set("$(IOC).req", 5, "CAM=$(PREFIX)$(CAM1),IMG=$(PREFIX)$(IMG1)")
$(CAM2_ENABLED) create_monitor_set("$(IOC).req", 5, "CAM=$(PREFIX)$(CAM2),IMG=$(PREFIX)$(IMG2)")
$(CAM3_ENABLED) create_monitor_set("$(IOC).req", 5, "CAM=$(PREFIX)$(CAM3),IMG=$(PREFIX)$(IMG3)")
$(CAM4_ENABLED) create_monitor_set("$(IOC).req", 5, "CAM=$(PREFIX)$(CAM4),IMG=$(PREFIX)$(IMG4)")

# All IOCs should dump some common info after initial startup.
< /reg/d/iocCommon/All/post_linux.cmd
