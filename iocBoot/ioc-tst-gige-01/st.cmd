#! ../../bin/linux-x86_64/gige

epicsEnvSet( "ENGINEER", "Pavel Stoffel (pstoffel)" )
epicsEnvSet( "LOCATION", "TST:R40:IOC:18:GIGE:01" )
epicsEnvSet( "IOCSH_PS1", "ioc-tst-gige-01> " )

< envPaths
cd( "../.." )

< /reg/d/iocCommon/All/pre_linux.cmd

dbLoadDatabase("$(AREA_DETECTOR)/dbd/prosilicaApp.dbd")
gige_registerRecordDeviceDriver(pdbbase)

epicsEnvSet("PREFIX", "13PS1:")
epicsEnvSet("PORT",   "PS1")
epicsEnvSet("QSIZE",  "20")
epicsEnvSet("XSIZE",  "1360")
epicsEnvSet("YSIZE",  "1024")
epicsEnvSet("NCHANS", "2048")
epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES", "8000000")

prosilicaConfigIp(  "PS1", 116474, "172.21.42.49", 50, -1)

asynSetTraceIOMask("$(PORT)",0,2)

dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/ADBase.template",   "P=$(PREFIX),R=cam1:,PORT=$(PORT),ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDFile.template",   "P=$(PREFIX),R=cam1:,PORT=$(PORT),ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/prosilica.template","P=$(PREFIX),R=cam1:,PORT=$(PORT),ADDR=0,TIMEOUT=1")

NDStdArraysConfigure("Image1", 5, 0, "$(PORT)", 0, -1)
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=$(PREFIX),R=image1:,PORT=Image1,ADDR=0,TIMEOUT=1,NDARRAY_PORT=$(PORT),NDARRAY_ADDR=0")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDStdArrays.template", "P=$(PREFIX),R=image1:,PORT=Image1,ADDR=0,TIMEOUT=1,TYPE=Int8,FTVL=UCHAR,NELEMENTS=4177920")

# Load record instances
##dbLoadRecords( "db/iocAdmin.db",			"IOC=TST:R40:IOC:18:GIGE:01" )
dbLoadRecords( "db/save_restoreStatus.db",	"IOC=TST:R40:IOC:18:GIGE:01" )

####### Autosave #############

set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
set_requestfile_path( "autosave" )
save_restoreSet_status_prefix("TST:R40:IOC:18:GIGE:01:")
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )
set_pass0_restoreFile( "tst_gige1.sav" )
set_pass1_restoreFile( "tst_gige1.sav" )

save_restoreSet_NumSeqFiles(5)
save_restoreSet_SeqPeriodInSeconds(30)

iocInit()

dbpf $(PREFIX)cam1:ArrayCallbacks 1
dbpf $(PREFIX)image1:EnableCallbacks 1

pwd()
create_monitor_set("tst_gige1.req", 30, "IOC=TST:R40:IOC:18:GIGE:01")

< /reg/d/iocCommon/All/post_linux.cmd
