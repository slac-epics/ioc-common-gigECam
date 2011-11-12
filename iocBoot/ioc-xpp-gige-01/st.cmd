#! ../../bin/linux-x86_64/gige

epicsEnvSet( "ENGINEER", "Pavel Stoffel (pstoffel)" )
epicsEnvSet( "LOCATION", "IOC:XPP:GIGE:01" )
epicsEnvSet( "IOCSH_PS1", "ioc-xpp-gige-01> " )
< envPaths
cd( "../.." )

# Run common startup commands for linux soft IOC's
< /reg/d/iocCommon/All/pre_linux.cmd

# Register all support components
dbLoadDatabase( "dbd/gige.dbd" )
gige_registerRecordDeviceDriver(pdbbase)


epicsEnvSet("PREFIX", "XPP:GIGE:")
epicsEnvSet("PORT",   "PS1")
epicsEnvSet("QSIZE",  "20")
epicsEnvSet("XSIZE",  "1360")
epicsEnvSet("YSIZE",  "1024")
epicsEnvSet("NCHANS", "2048")
epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES", "8000000")

##############################################################
# configure and initialize the camera
#   Args:  port, dummy, ip, nbufers, nbufers x width x height + overhead
prosilicaConfigIp(  "PS1", 116474, "192.168.100.220", 50, -1)
##############################################################


##asynSetTraceIOMask("$(PORT)",0,2)
asynSetTraceIOMask("$(PORT)",0,0)

dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/ADBase.template",   "P=$(PREFIX),R=cam1:,PORT=$(PORT),ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDFile.template",   "P=$(PREFIX),R=cam1:,PORT=$(PORT),ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/prosilica.template","P=$(PREFIX),R=cam1:,PORT=$(PORT),ADDR=0,TIMEOUT=1")

# Create a standard arrays plugin, set it to get data from first Prosilica driver.
NDStdArraysConfigure("Image1", 5, 0, "$(PORT)", 0, -1)
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=$(PREFIX),R=image1:,PORT=Image1,ADDR=0,TIMEOUT=1,NDARRAY_PORT=$(PORT),NDARRAY_ADDR=0")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDStdArrays.template", "P=$(PREFIX),R=image1:,PORT=Image1,ADDR=0,TIMEOUT=1,TYPE=Int8,FTVL=UCHAR,NELEMENTS=4177920")

#asynSetTraceMask("$(PORT)",0,255)
asynSetTraceMask("$(PORT)",0,0)


# Load record instances
dbLoadRecords( "db/iocAdmin.db",			"IOC=IOC:XPP:GIGE:01" )
dbLoadRecords( "db/save_restoreStatus.db",	"IOC=IOC:XPP:GIGE:01" )

# Setup autosave
set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
set_requestfile_path( "autosave" )
save_restoreSet_status_prefix( "IOC:XPP:GIGE:01:" )
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )
set_pass0_restoreFile( "xpp_gige1.sav" )
set_pass1_restoreFile( "xpp_gige1.sav" )

save_restoreSet_NumSeqFiles(5)
save_restoreSet_SeqPeriodInSeconds(30)

# Initialize the IOC and start processing records
iocInit()

dbpf $(PREFIX)cam1:ArrayCallbacks 1
dbpf $(PREFIX)image1:EnableCallbacks 1

# Start autosave backups
create_monitor_set( "autosave_gige.req", 30, "IOC=IOC:XPP:GIGE:01" )

# All IOCs should dump some common info after initial startup.
< /reg/d/iocCommon/All/post_linux.cmd
