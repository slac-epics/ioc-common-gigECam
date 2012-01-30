#! ../../bin/linux-x86_64/gige

epicsEnvSet( "ENGINEER", "Pavel Stoffel (pstoffel)" )
epicsEnvSet( "LOCATION", "IOC:XPP:GIGE:02" )
epicsEnvSet( "IOCSH_PS1", "ioc-xpp-gige-02> " )
< envPaths
cd( "../.." )

# Run common startup commands for linux soft IOC's
< /reg/d/iocCommon/All/pre_linux.cmd

# Register all support components
dbLoadDatabase( "dbd/gige.dbd" )
gige_registerRecordDeviceDriver(pdbbase)


epicsEnvSet("PREFIX", "XPP:GIGE:")
epicsEnvSet("CAM1",   "cam2")
epicsEnvSet("IMG1",   "image2")
epicsEnvSet("PORT",   "PS2")
epicsEnvSet("QSIZE",  "20")
epicsEnvSet("XSIZE",  "1360")
epicsEnvSet("YSIZE",  "1024")
epicsEnvSet("NCHANS", "2048")
epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES", "8000000")

##############################################################
# configure and initialize the camera
#   Args:  port, dummy, ip, nbufers, nbufers x width x height + overhead
prosilicaConfigIp(  "PS2", 116474, "192.168.100.221", 50, -1)
##############################################################


##asynSetTraceIOMask("$(PORT)",0,2)
asynSetTraceIOMask("$(PORT)",0,0)

dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/ADBase.template",   "P=$(PREFIX),R=cam2:,PORT=$(PORT),ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDFile.template",   "P=$(PREFIX),R=cam2:,PORT=$(PORT),ADDR=0,TIMEOUT=1")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/prosilica.template","P=$(PREFIX),R=cam2:,PORT=$(PORT),ADDR=0,TIMEOUT=1")

# Create a standard arrays plugin, set it to get data from first Prosilica driver.
NDStdArraysConfigure("Image2", 5, 0, "$(PORT)", 0, -1)
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDPluginBase.template","P=$(PREFIX),R=image2:,PORT=Image2,ADDR=0,TIMEOUT=1,NDARRAY_PORT=$(PORT),NDARRAY_ADDR=0")
dbLoadRecords("$(AREA_DETECTOR)/ADApp/Db/NDStdArrays.template", "P=$(PREFIX),R=image2:,PORT=Image2,ADDR=0,TIMEOUT=1,TYPE=Int8,FTVL=UCHAR,NELEMENTS=4177920")

#asynSetTraceMask("$(PORT)",0,255)
asynSetTraceMask("$(PORT)",0,0)


# Load record instances
dbLoadRecords( "db/iocAdmin.db",			"IOC=IOC:XPP:GIGE:02" )
dbLoadRecords( "db/save_restoreStatus.db",	"IOC=IOC:XPP:GIGE:02" )

# Setup autosave
set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
set_requestfile_path( "autosave" )
save_restoreSet_status_prefix( "IOC:XPP:GIGE:02:" )
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )
set_pass0_restoreFile( "xpp_gige2.sav" )
set_pass1_restoreFile( "xpp_gige2.sav" )

save_restoreSet_NumSeqFiles(5)
save_restoreSet_SeqPeriodInSeconds(30)

# Initialize the IOC and start processing records
iocInit()

dbpf $(PREFIX)cam2:ArrayCallbacks 1
dbpf $(PREFIX)image2:EnableCallbacks 1

# Start autosave backups
create_monitor_set("gige.req", 5, "CAM=$(PREFIX)$(CAM1),IMG=$(PREFIX)$(IMG1)")

# All IOCs should dump some common info after initial startup.
< /reg/d/iocCommon/All/post_linux.cmd
