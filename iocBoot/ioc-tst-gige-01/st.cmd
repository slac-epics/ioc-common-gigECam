#! /reg/g/pcds/package/epics/3.14/ioc/common/gigECam/R0.1.0/bin/linux-x86_64/gige
#! ../../bin/linux-x86_64/gige

# Run common startup commands for linux soft IOC's
< /reg/d/iocCommon/All/pre_linux.cmd

< envPaths

epicsEnvSet( "ENGINEER", "Pavel Stoffel (pstoffel)" )
epicsEnvSet( "LOCATION", "TST:R40:IOC:18:GIGE:01" )
epicsEnvSet( "IOCSH_PS1", "ioc-tst-gige-01> " )

cd( "../.." )

epicsEnvSet("PREFIX", "13PS1:")
epicsEnvSet("CAM1",   "CAM1")
epicsEnvSet("CAM2",   "CAM2")
epicsEnvSet("IMG1",   "IMAGE1")
epicsEnvSet("IMG2",   "IMAGE2")
#epicsEnvSet("PORT",   "PS1")
epicsEnvSet("QSIZE",  "20")
#epicsEnvSet("XSIZE",  "1360")
#epicsEnvSet("YSIZE",  "1024")
epicsEnvSet("XSIZE",  "1388")
epicsEnvSet("YSIZE",  "1038")
#epicsEnvSet("XSIZE",  "1360")
#epicsEnvSet("YSIZE",  "1024")
#epicsEnvSet("XSIZE",  "780")
#epicsEnvSet("YSIZE",  "580")
epicsEnvSet("NCHANS", "2048")
epicsEnvSet("NELEMENTS1", "4177920")
epicsEnvSet("NELEMENTS2", "4177920")
#epicsEnvSet("NELEMENTS2", "452400")
epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES", "8000000")
epicsEnvSet(  "IP1", "192.168.100.10" )
epicsEnvSet(  "IP2", "192.168.0.101" )

# Register all support components
dbLoadDatabase( "dbd/gige.dbd" )
gige_registerRecordDeviceDriver(pdbbase)

##############################################################
# configure and initialize the camera
#   Args:  port, dummy, ip, nbufers, nbufers x width x height + overhead
prosilicaConfigIp(  "PS1", 116474, "$(IP1)", 50, 120000000 )
prosilicaConfigIp(  "PS2", 116474, "$(IP2)", 50, 120000000 )
##############################################################


##asynSetTraceIOMask("PS1",0,2)
#asynSetTraceMask("PS1",0,255)
asynSetTraceIOMask("PS1",0,0)
asynSetTraceIOMask("PS2",0,0)

#asynSetTraceMask("PS1",0,255)
asynSetTraceMask("PS1",0,0)
asynSetTraceMask("PS2",0,0)


dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/ADBase.template",   "P=13PS1:,R=CAM1:,PORT=PS1,ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDFile.template",   "P=13PS1:,R=CAM1:,PORT=PS1,ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/prosilica.template","P=13PS1:,R=CAM1:,PORT=PS1,ADDR=0,TIMEOUT=1")

dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/ADBase.template",   "P=13PS2:,R=CAM1:,PORT=PS2,ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDFile.template",   "P=13PS2:,R=CAM1:,PORT=PS2,ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/prosilica.template","P=13PS2:,R=CAM1:,PORT=PS2,ADDR=0,TIMEOUT=1")

# Create a standard arrays plugin, set it to get data from first Prosilica driver.
NDStdArraysConfigure("Image1", 5, 0, "PS1", 0, -1)
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=13PS1:,R=IMAGE1:,PORT=Image1,ADDR=0,TIMEOUT=1,NDARRAY_PORT=PS1,NDARRAY_ADDR=0")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDStdArrays.template", "P=13PS1:,R=IMAGE1:,PORT=Image1,ADDR=0,TIMEOUT=1,TYPE=Int8,FTVL=UCHAR,NELEMENTS=$(NELEMENTS1)")

NDStdArraysConfigure("Image2", 5, 0, "PS2", 0, -1)
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=13PS2:,R=IMAGE1:,PORT=Image2,ADDR=0,TIMEOUT=1,NDARRAY_PORT=PS2,NDARRAY_ADDR=0")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDStdArrays.template", "P=13PS2:,R=IMAGE1:,PORT=Image2,ADDR=0,TIMEOUT=1,TYPE=Int8,FTVL=UCHAR,NELEMENTS=$(NELEMENTS2)")


# Load record instances
dbLoadRecords( "db/iocAdmin.db",			"IOC=TST:R40:IOC:18:GIGE:01" )
dbLoadRecords( "db/save_restoreStatus.db",	"IOC=TST:R40:IOC:18:GIGE:01" )


# Setup autosave
set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
set_requestfile_path( "autosave" )
save_restoreSet_status_prefix("TST:R40:IOC:18:GIGE:01:")
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )
set_pass0_restoreFile( "tst_gige1.sav" )
set_pass1_restoreFile( "tst_gige1.sav" )

save_restoreSet_NumSeqFiles(5)
save_restoreSet_SeqPeriodInSeconds(30)

# Initialize the IOC and start processing records
iocInit()

dbpf 13PS1:CAM1:ArrayCallbacks 1
dbpf 13PS1:IMAGE1:EnableCallbacks 1

dbpf 13PS2:CAM1:ArrayCallbacks 1
dbpf 13PS2:IMAGE1:EnableCallbacks 1

# Start autosave backups
create_monitor_set("gige.req", 5, "CAM=$(PREFIX)$(CAM1),IMG=$(PREFIX)$(IMG1)")

# All IOCs should dump some common info after initial startup.
< /reg/d/iocCommon/All/post_linux.cmd
