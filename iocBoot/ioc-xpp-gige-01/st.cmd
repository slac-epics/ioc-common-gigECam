#! ../../bin/linux-x86_64/gige

epicsEnvSet( "ENGINEER", "Pavel Stoffel (pstoffel)" )
epicsEnvSet( "LOCATION", "IOC:XPP:GIGE:01" )
epicsEnvSet( "IOCSH_PS1", "ioc-xpp-gige-01> " )
< envPaths

# Run common startup commands for linux soft IOC's
< /reg/d/iocCommon/All/pre_linux.CD

epicsEnvSet("PREFIX", "XPP:GIGE:")
epicsEnvSet("CAM1",   "cam1")
epicsEnvSet("IMG1",   "image1")
epicsEnvSet("CAM3",   "CAM3")
epicsEnvSet("IMG3",   "IMAGE3")

##prosilica
#epicsEnvSet("CAM1_ENABLED",  "")                             # "" = YES,  "#" = NO
#epicsEnvSet("C1_IP",     "192.168.100.220")
#epicsEnvSet("C1_XSIZE",  "1360")
#epicsEnvSet("C1_YSIZE",  "1024")
#epicsEnvSet("C1_COLORMODE",  "2")
#epicsEnvSet("C1_NELEMENTS",  "4177920")  # X * Y * 3

# ----- Manta G046B -----
epicsEnvSet("CAM1_ENABLED",  "")                             # "" = YES,  "#" = NO
epicsEnvSet("C1_IP",         "192.168.100.30")
epicsEnvSet("C1_XSIZE",      "1388")
epicsEnvSet("C1_YSIZE",      "1038")
epicsEnvSet("C1_COLORMODE",  "2")        # 0=Mono, 2=RGB1
epicsEnvSet("C1_NELEMENTS",  "4322232")  # X * Y * 3


epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES", "8000000")

cd( "../.." )

# Register all support components
dbLoadDatabase( "dbd/gige.dbd" )
gige_registerRecordDeviceDriver(pdbbase)

##############################################################
# configure and initialize the camera
#   Args:  port, dummy, ip, nbufers, nbufers x width x height + overhead
$(CAM1_ENABLED) prosilicaConfig(  "$(CAM1)", "$(C1_IP)", 50, -1)
$(CAM1_ENABLED) epicsThreadSleep(1)
##############################################################


#asynSetTraceIOMask("$(CAM1)",0,2)
#asynSetTraceIOMask("$(CAM1)",0,0)

$(CAM1_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/ADBase.template",   "P=$(PREFIX),R=$(CAM1):,PORT=$(CAM1),ADDR=0,TIMEOUT=1")
$(CAM1_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDFile.template",   "P=$(PREFIX),R=$(CAM1):,PORT=$(CAM1),ADDR=0,TIMEOUT=1")
$(CAM1_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/prosilica.template","P=$(PREFIX),R=$(CAM1):,PORT=$(CAM1),ADDR=0,TIMEOUT=1")
$(CAM1_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/cross.template",	 "P=$(PREFIX),R=$(CAM1):,PORT=$(CAM1),ADDR=0,TIMEOUT=1")

# Create a standard arrays plugin, set it to get data from first Prosilica driver.
$(CAM1_ENABLED) NDStdArraysConfigure("$(IMG1)", 5, 0, "$(CAM1)", 0, -1)
$(CAM1_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=$(PREFIX),R=$(IMG1):,PORT=$(IMG1),ADDR=0,TIMEOUT=1,NDARRAY_PORT=$(CAM1),NDARRAY_ADDR=0")
$(CAM1_ENABLED) dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDStdArrays.template", "P=$(PREFIX),R=$(IMG1):,PORT=$(IMG1),ADDR=0,TIMEOUT=1,TYPE=Int8,FTVL=UCHAR,NELEMENTS=$(C1_NELEMENTS)")

#asynSetTraceMask("$(CAM1)",0,255)
#asynSetTraceMask("$(CAM1)",0,0)

# Load record instances
dbLoadRecords( "db/iocAdmin.db",		"IOC=IOC:XPP:GIGE:01" )
dbLoadRecords( "db/save_restoreStatus.db",	"IOC=IOC:XPP:GIGE:01" )

## Setup autosave
set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
set_requestfile_path( "$(TOP)/autosave" )
save_restoreSet_status_prefix( "IOC:XPP:GIGE:01:" )
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )
set_pass0_restoreFile( "xpp_gige1.sav" )
set_pass1_restoreFile( "xpp_gige1.sav" )

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
##$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1):AcquirePeriod 1
##$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1):AcquireTime 0.1
##$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1):Gain 0
#
##$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1):Acquire 1                         # Start the camera

## Start autosave backups
$(CAM1_ENABLED) create_monitor_set("$(IOC).req", 5, "PRE=$(PREFIX),CAM=$(CAM1),IMG=$(IMG1)")

# All IOCs should dump some common info after initial startup.
< /reg/d/iocCommon/All/post_linux.cmd
