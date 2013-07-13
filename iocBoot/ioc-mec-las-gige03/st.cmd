#! ../../bin/linux-x86_64/gige

# Run common startup commands for linux soft IOC's
< /reg/d/iocCommon/All/pre_linux.cmd

< envPaths

epicsEnvSet("ENGINEER",        "Ernesto Paiser (paiser)" )
epicsEnvSet("LOCATION",        "MEC:M64A:44" )  # TODO: correct LOCATION!
epicsEnvSet("IOC",             "ioc-mec-las-gige03")
epicsEnvSet("IOCSH_PS1",       "$(IOC)> " )
epicsEnvSet("PREFIX",          "MEC:LAS:GIGE:")

# ----- Manta G-033B Common settings -----
epicsEnvSet("ENABLECALLBACKS", "1"             # 0=Disable, 1=Enable Image cb
epicsEnvSet("ARRAYCALLBACKS",  "1"             # 0=Disable, 1=Enable Controls cb
epicsEnvSet("COLORMODE",       "0"             # 0=Mono, 2=RGB1
epicsEnvSet("DATATYPE",        "0"             # 0=Int8, 1=UInt16
epicsEnvSet("IMAGEMODE",       "2"             # 0=Single,1=Multi,2=Continuous
epicsEnvSet("TRIGGERMODE",     "5"             # 0=Free Run,1=SyncIn1,5=FixdRate
epicsEnvSet("ACQUIREPERIOD",   "1"             # Acquire Period (default 1 s)
epicsEnvSet("ACQUIRETIME",     "0.01"          # Exposure time (default 0.01 s)
epicsEnvSet("GAIN",            "20"            # Gain (default 20)
epicsEnvSet("ACQUIRE",         "1"             # 0=Stop, 1=1Start the camera
epicsEnvSet("XSIZE",           "654")
epicsEnvSet("YSIZE",           "492")
epicsEnvSet("NELEMENTS",       "321768")       # X * Y

# ----- Manta G-033B specific -----------------------------------------
epicsEnvSet("CAM1_ENABLED",    "")              # "" = YES,  "#" = NO
epicsEnvSet("CAM1_IMAGE",      "IMAGE5")
epicsEnvSet("CAM1_CAM",        "CAM5")
epicsEnvSet("CAM1_IP",         "192.168.5.10")

epicsEnvSet("CAM2_ENABLED",    "")              # "" = YES,  "#" = NO
epicsEnvSet("CAM2_IMAGE",      "IMAGE6")
epicsEnvSet("CAM2_CAM",        "CAM6")
epicsEnvSet("CAM2_IP",         "192.168.6.10")

epicsEnvSet("CAM3_ENABLED",    "")              # "" = YES,  "#" = NO
epicsEnvSet("CAM3_IMAGE",      "IMAGE7")
epicsEnvSet("CAM3_CAM",        "CAM7")
epicsEnvSet("CAM3_IP",         "192.168.7.10")

epicsEnvSet("CAM4_ENABLED",    "#")             # "" = YES,  "#" = NO
epicsEnvSet("CAM4_IMAGE",      "IMAGE8")
epicsEnvSet("CAM4_CAM",        "CAM8")
epicsEnvSet("CAM4_IP",         "192.168.8.10")
# ---------------------------------------------------------------------

epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES", "8388608")

cd( "../.." )

# Register all support components
dbLoadDatabase("dbd/gige.dbd")
gige_registerRecordDeviceDriver(pdbbase)

##############################################################
# configure and initialize the cameras
#   Args:  port, dummy, ip, nbufers, nbufers x width x height + overhead
$(CAM1_ENABLED) prosilicaConfig(  "$(CAM1_CAM)", "$(CAM1_IP)", 50, -1)
$(CAM1_ENABLED) epicsThreadSleep(1)

$(CAM2_ENABLED) prosilicaConfig(  "$(CAM2_CAM)", "$(CAM2_IP)", 50, -1)
$(CAM2_ENABLED) epicsThreadSleep(1)

$(CAM3_ENABLED) prosilicaConfig(  "$(CAM3_CAM)", "$(CAM3_IP)", 50, -1)
$(CAM3_ENABLED) epicsThreadSleep(1)

$(CAM4_ENABLED) prosilicaConfig(  "$(CAM4_CAM)", "$(CAM4_IP)", 50, -1)
$(CAM4_ENABLED) epicsThreadSleep(1)

##############################################################

#$(CAM1_ENABLED) asynSetTraceMask(  "$(CAM1_CAM)",0,9)
#$(CAM1_ENABLED) asynSetTraceIOMask("$(CAM1_CAM)",0,2)
#$(CAM2_ENABLED) asynSetTraceMask(  "$(CAM2_CAM)",0,9)
#$(CAM2_ENABLED) asynSetTraceIOMask("$(CAM2_CAM)",0,2)
#$(CAM3_ENABLED) asynSetTraceMask(  "$(CAM3_CAM)",0,9)
#$(CAM3_ENABLED) asynSetTraceIOMask("$(CAM3_CAM)",0,2)
#$(CAM4_ENABLED) asynSetTraceMask(  "$(CAM4_CAM)",0,9)
#$(CAM4_ENABLED) asynSetTraceIOMask("$(CAM4_CAM)",0,2)

$(CAM1_ENABLED) dbLoadRecords("db/prosilica_gige.template", "P=$(PREFIX),CAM=5,ADDR=0,TIMEOUT=1,TYPE=Int8,FTVL=UCHAR,NELEMENTS=$(NELEMENTS),NDARRAY_ADDR=0")
$(CAM1_ENABLED) NDStdArraysConfigure($(CAM1_IMAGE), 5, 0, $(CAM1_CAM), 0, -1)

$(CAM2_ENABLED) dbLoadRecords("db/prosilica_gige.template", "P=$(PREFIX),CAM=6,ADDR=0,TIMEOUT=1,TYPE=Int8,FTVL=UCHAR,NELEMENTS=$(NELEMENTS),NDARRAY_ADDR=0")
$(CAM2_ENABLED) NDStdArraysConfigure($(CAM2_IMAGE), 5, 0, $(CAM2_CAM), 0, -1)

$(CAM3_ENABLED) dbLoadRecords("db/prosilica_gige.template", "P=$(PREFIX),CAM=7,ADDR=0,TIMEOUT=1,TYPE=Int8,FTVL=UCHAR,NELEMENTS=$(NELEMENTS),NDARRAY_ADDR=0")
$(CAM3_ENABLED) NDStdArraysConfigure($(CAM3_IMAGE), 5, 0, $(CAM3_CAM), 0, -1)

$(CAM4_ENABLED) dbLoadRecords("db/prosilica_gige.template", "P=$(PREFIX),CAM=8,ADDR=0,TIMEOUT=1,TYPE=Int8,FTVL=UCHAR,NELEMENTS=$(NELEMENTS),NDARRAY_ADDR=0")
$(CAM4_ENABLED) NDStdArraysConfigure($(CAM4_IMAGE), 5, 0, $(CAM4_CAM), 0, -1)

# Load record instances
dbLoadRecords( "db/iocAdmin.db",           "IOC=IOC:MEC:LAS:GIGE03" )
dbLoadRecords( "db/save_restoreStatus.db", "IOC=IOC:MEC:LAS:GIGE03" )

# Setup autosave
set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
set_requestfile_path( "autosave" )
save_restoreSet_status_prefix("IOC:MEC:LAS:GIGE03")
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )
set_pass0_restoreFile( "$(IOC).sav" )
set_pass1_restoreFile( "$(IOC).sav" )

save_restoreSet_NumSeqFiles(5)
save_restoreSet_SeqPeriodInSeconds(30)

# Initialize the IOC and start processing records
iocInit()

#
$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1_IMAGE):EnableCallbacks $(ENABLECALLBACKS) # 0=Disable, 1=Enable Image cb
$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1_CAM):ArrayCallbacks $(ARRAYCALLBACKS)     # 0=Disable, 1=Enable Controls cb
$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1_CAM):ColorMode $(COLORMODE)               # 0=Mono, 2=RGB1
$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1_CAM):DataType $(DATATYPE)                 # 0=UInt8, 1=UInt16
$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1_CAM):ImageMode $(IMAGEMODE)               # 0=Single, 1=Multiple, 2=Continuous
$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1_CAM):TriggerMode $(TRIGGERMODE)           # 0=Free Run, 1=SyncIn1, 5=Fixed Rate
$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1_CAM):AcquirePeriod $(ACQUIREPERIOD)       # Acquire Period (default 1 s)
$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1_CAM):AcquireTime $(ACQUIRETIME)           # Exposure time (default 0.01 s)
$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1_CAM):Gain $(GAIN)                         # Gain (default 20)
$(CAM1_ENABLED) dbpf $(PREFIX)$(CAM1_CAM):Acquire $(ACQUIRE)                   # 0=Stop, 1=1Start the camera
#
$(CAM2_ENABLED) dbpf $(PREFIX)$(CAM2_IMAGE):EnableCallbacks $(ENABLECALLBACKS) # 0=Disable, 1=Enable Image cb
$(CAM2_ENABLED) dbpf $(PREFIX)$(CAM2_CAM):ArrayCallbacks $(ARRAYCALLBACKS)     # 0=Disable, 1=Enable Controls cb
$(CAM2_ENABLED) dbpf $(PREFIX)$(CAM2_CAM):ColorMode $(COLORMODE)               # 0=Mono, 2=RGB1
$(CAM2_ENABLED) dbpf $(PREFIX)$(CAM2_CAM):DataType $(DATATYPE)                 # 0=UInt8, 1=UInt16
$(CAM2_ENABLED) dbpf $(PREFIX)$(CAM2_CAM):ImageMode $(IMAGEMODE)               # 0=Single, 1=Multiple, 2=Continuous
$(CAM2_ENABLED) dbpf $(PREFIX)$(CAM2_CAM):TriggerMode $(TRIGGERMODE)           # 0=Free Run, 1=SyncIn1, 5=Fixed Rate
$(CAM2_ENABLED) dbpf $(PREFIX)$(CAM2_CAM):AcquirePeriod $(ACQUIREPERIOD)       # Acquire Period (default 1 s)
$(CAM2_ENABLED) dbpf $(PREFIX)$(CAM2_CAM):AcquireTime $(ACQUIRETIME)           # Exposure time (default 0.01 s)
$(CAM2_ENABLED) dbpf $(PREFIX)$(CAM2_CAM):Gain $(GAIN)                         # Gain (default 20)
$(CAM2_ENABLED) dbpf $(PREFIX)$(CAM2_CAM):Acquire $(ACQUIRE)                   # 0=Stop, 1=1Start the camera
#
$(CAM3_ENABLED) dbpf $(PREFIX)$(CAM3_IMAGE):EnableCallbacks $(ENABLECALLBACKS) # 0=Disable, 1=Enable Image cb
$(CAM3_ENABLED) dbpf $(PREFIX)$(CAM3_CAM):ArrayCallbacks $(ARRAYCALLBACKS)     # 0=Disable, 1=Enable Controls cb
$(CAM3_ENABLED) dbpf $(PREFIX)$(CAM3_CAM):ColorMode $(COLORMODE)               # 0=Mono, 2=RGB1
$(CAM3_ENABLED) dbpf $(PREFIX)$(CAM3_CAM):DataType $(DATATYPE)                 # 0=UInt8, 1=UInt16
$(CAM3_ENABLED) dbpf $(PREFIX)$(CAM3_CAM):ImageMode $(IMAGEMODE)               # 0=Single, 1=Multiple, 2=Continuous
$(CAM3_ENABLED) dbpf $(PREFIX)$(CAM3_CAM):TriggerMode $(TRIGGERMODE)           # 0=Free Run, 1=SyncIn1, 5=Fixed Rate
$(CAM3_ENABLED) dbpf $(PREFIX)$(CAM3_CAM):AcquirePeriod $(ACQUIREPERIOD)       # Acquire Period (default 1 s)
$(CAM3_ENABLED) dbpf $(PREFIX)$(CAM3_CAM):AcquireTime $(ACQUIRETIME)           # Exposure time (default 0.01 s)
$(CAM3_ENABLED) dbpf $(PREFIX)$(CAM3_CAM):Gain $(GAIN)                         # Gain (default 20)
$(CAM3_ENABLED) dbpf $(PREFIX)$(CAM3_CAM):Acquire $(ACQUIRE)                   # 0=Stop, 1=1Start the camera
#
$(CAM4_ENABLED) dbpf $(PREFIX)$(CAM4_IMAGE):EnableCallbacks $(ENABLECALLBACKS) # 0=Disable, 1=Enable Image cb
$(CAM4_ENABLED) dbpf $(PREFIX)$(CAM4_CAM):ArrayCallbacks $(ARRAYCALLBACKS)     # 0=Disable, 1=Enable Controls cb
$(CAM4_ENABLED) dbpf $(PREFIX)$(CAM4_CAM):ColorMode $(COLORMODE)               # 0=Mono, 2=RGB1
$(CAM4_ENABLED) dbpf $(PREFIX)$(CAM4_CAM):DataType $(DATATYPE)                 # 0=UInt8, 1=UInt16
$(CAM4_ENABLED) dbpf $(PREFIX)$(CAM4_CAM):ImageMode $(IMAGEMODE)               # 0=Single, 1=Multiple, 2=Continuous
$(CAM4_ENABLED) dbpf $(PREFIX)$(CAM4_CAM):TriggerMode $(TRIGGERMODE)           # 0=Free Run, 1=SyncIn1, 5=Fixed Rate
$(CAM4_ENABLED) dbpf $(PREFIX)$(CAM4_CAM):AcquirePeriod $(ACQUIREPERIOD)       # Acquire Period (default 1 s)
$(CAM4_ENABLED) dbpf $(PREFIX)$(CAM4_CAM):AcquireTime $(ACQUIRETIME)           # Exposure time (default 0.01 s)
$(CAM4_ENABLED) dbpf $(PREFIX)$(CAM4_CAM):Gain $(GAIN)                         # Gain (default 20)
$(CAM4_ENABLED) dbpf $(PREFIX)$(CAM4_CAM):Acquire $(ACQUIRE)                   # 0=Stop, 1=1Start the camera
#

# ---------------------------------------------------------------------------

# Start autosave backups
#$(CAM1_ENABLED) create_monitor_set("$(IOC).req", 5, "CAM=$(PREFIX)$(CAM1_CAM),IMG=$(PREFIX)$(CAM1_IMAGE)")
#$(CAM2_ENABLED) create_monitor_set("$(IOC).req", 5, "CAM=$(PREFIX)$(CAM2_CAM),IMG=$(PREFIX)$(CAM2_IMAGE)")
#$(CAM3_ENABLED) create_monitor_set("$(IOC).req", 5, "CAM=$(PREFIX)$(CAM3_CAM),IMG=$(PREFIX)$(CAM3_IMAGE)")
#$(CAM4_ENABLED) create_monitor_set("$(IOC).req", 5, "CAM=$(PREFIX)$(CAM4_CAM),IMG=$(PREFIX)$(CAM4_IMAGE)")

# All IOCs should dump some common info after initial startup.
< /reg/d/iocCommon/All/post_linux.cmd
