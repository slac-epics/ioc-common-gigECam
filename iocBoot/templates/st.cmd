#!$$IOCTOP/bin/$$IF(TARGET_ARCH,$$TARGET_ARCH,linux-x86_64)/gige

# Run common startup commands for linux soft IOC's
< $(IOC_COMMON)/All/pre_linux.cmd

< envPaths
epicsEnvSet( "IOCNAME",      "$$IOCNAME" )
epicsEnvSet( "ENGINEER",     "$$ENGINEER" )
epicsEnvSet( "LOCATION",     "$$LOCATION" )
epicsEnvSet( "IOCSH_PS1",    "$(IOCNAME)> " )
epicsEnvSet( "IOC_PV",       "$$IOC_PV" )
epicsEnvSet( "IOCTOP",       "$$IOCTOP" )
epicsEnvSet( "BUILD_TOP",    "$$TOP" )
epicsEnvSet( "EPICS_PVA_AUTO_ADDR_LIST",         "TRUE" )
epicsEnvSet( "EPICS_PVAS_AUTO_BEACON_ADDR_LIST", "TRUE" )
cd( "$(IOCTOP)" )

# Set Max array size
epicsEnvSet( "EPICS_CA_MAX_ARRAY_BYTES", "$$IF(MAX_ARRAY,$$MAX_ARRAY,20000000)" )

# Setup EVR env vars
epicsEnvSet( "EVR_PV",       "$$IF(EVR_PV,$$EVR_PV,$$CAM_PV:NoEvr)" )
epicsEnvSet( "TRIG_PV",      "$(EVR_PV):TRIG$$IF(EVR_TRIG,$$EVR_TRIG,0)" )
epicsEnvSet( "EVR_CARD",     "$$IF(EVR_CARD,$$EVR_CARD,0)" )
# EVR Type: 0=VME, 1=PMC, 15=SLAC
epicsEnvSet( "EVRID_PMC",    "1" )
epicsEnvSet( "EVRID_SLAC",   "15" )
epicsEnvSet( "EVRDB_PMC",    "db/evrPmc230.db" )
epicsEnvSet( "EVRDB_SLAC",   "db/evrSLAC.db" )
$$IF(EVR_TYPE)
epicsEnvSet( "EVRID",        "$(EVRID_$$EVR_TYPE)" )
epicsEnvSet( "EVRDB",        "$(EVRDB_$$EVR_TYPE)" )
$$ENDIF(EVR_TYPE)
epicsEnvSet( "EVR_DEBUG",    "$$IF(EVR_DEBUG,$$EVR_DEBUG,0)" )

# Specify camera env variables
epicsEnvSet( "CAM_IP",       "$$CAM_IP" )
$$IF(CAM_PV)
epicsEnvSet( "CAM_PV",       "$$CAM_PV" )
$$ELSE(CAM_PV)
errlog( "CAM_PV not defined" )
exit()
$$ENDIF(CAM_PV)
epicsEnvSet( "CAM_PORT",     "$$IF(PORT,$$PORT,CAM)" )
epicsEnvSet( "MODEL",        "$$MODEL" )
epicsEnvSet( "HTTP_PORT",    "$$IF(HTTP_PORT,$$HTTP_PORT,7800)" )
epicsEnvSet( "N_AD_BUFFERS", "$$IF(N_AD_BUFFERS,$$N_AD_BUFFERS,0)" )
$$IF(ARV_DEBUG)
epicsEnvSet( "ARV_DEBUG",    "$$ARV_DEBUG" )
$$ELSE(ARV_DEBUG)
epicsEnvSet( "ARV_DEBUG",    "genicam:1,device:1,chunk:1,dom:1,evaluator:1,stream_thread:1,interface:1,misc:1" )
$$ENDIF(ARV_DEBUG)

# Diagnostic settings
epicsEnvSet( "ST_CMD_DELAYS",		"$$IF(ST_CMD_DELAYS,$$ST_CMD_DELAYS,1)" )
epicsEnvSet( "CAM_TRACE_MASK",		"$$IF(CAM_TRACE,$$CAM_TRACE,1)" )
epicsEnvSet( "CAM_TRACE_IO_MASK",	"$$IF(CAM_TRACE_IO,$$CAM_TRACE_IO,0)" )

# Register all support components
dbLoadDatabase( "dbd/gige.dbd" )
gige_registerRecordDeviceDriver(pdbbase)

# Set a prefix for the iocLog
iocLogPrefix( "$(IOCNAME): " )

# Bump up scanOnce queue size for evr invariant timing
scanOnceSetQueueSize( $$IF(SCAN_ONCE_QUEUE_SIZE,$$SCAN_ONCE_QUEUE_SIZE,4000) )

$$IF(CPU_AFFINITY_SET)
# Set MCoreUtils rules for cpu affinity
mcoreThreadRuleAdd CAM_cpu * * $$CPU_AFFINITY_SET CAM.*
mcoreThreadRuleAdd evr_cpu * * $$CPU_AFFINITY_SET evr.*
$$ENDIF(CPU_AFFINITY_SET)

# Set iocsh debug variables
var DEBUG_TS_FIFO $$IF(DEBUG_TS_FIFO,$$DEBUG_TS_FIFO,1)
var save_restoreLogMissingRecords $$IF(save_restoreLogMissingRecords,$$save_restoreLogMissingRecords,0)

# Setup the environment for the specified camera model
< db/$(MODEL).env

# =========================================================
# Setup environment for this gigE type: aravis or prosilica
# =========================================================
epicsEnvSet( "CAM_TYPE", "$$IF(CAM_TYPE,$$CAM_TYPE,prosilica)" )
< setupScripts/$(CAM_TYPE).cmd

# Set asyn trace flags
asynSetTraceMask(   "$(CAM_PORT)",      0, $(CAM_TRACE_MASK) )
asynSetTraceIOMask( "$(CAM_PORT)",      0, $(CAM_TRACE_IO_MASK) )
$$IF(USE_TRACE_FILES)
asynSetTraceFile(	"$(CAM_PORT)",		0, "$(IOC_DATA)/$(IOC)/$(CAM_PORT).log" )
$$ENDIF(USE_TRACE_FILES)

$$IF(NO_ST_CMD_DELAY)
$$ELSE(NO_ST_CMD_DELAY)
# Comment/uncomment/change delay as desired so you can see messages during boot
epicsThreadSleep $(ST_CMD_DELAYS)
$$ENDIF(NO_ST_CMD_DELAY)

# Load the camera model specific template
dbLoadRecords( db/$(MODEL).template, "P=$(CAM_PV),R=:,PORT=$(CAM_PORT),TYPE=$(CAM_TYPE)" )

$$IF(EVR_PV)
# Load timestamp plugin
dbLoadRecords("db/timeStampFifo.template",  "DEV=$(CAM_PV):TSS,PORT_PV=$(CAM_PV):PortName_RBV,EC_PV=$(CAM_PV):CamEventCode_RBV,DLY_PV=$(CAM_PV):TrigToTS_Calc NMS CPP" )
$$ENDIF(EVR_PV)
#dbLoadRecords("db/timeStampEventCode.db",  "CAM=$(CAM_PV),CAM_TRIG=$(TRIG_PV),TSS=$(CAM_PV):TSS" )

$$IF(NO_ST_CMD_DELAY)
$$ELSE(NO_ST_CMD_DELAY)
epicsThreadSleep $(ST_CMD_DELAYS)
$$ENDIF(NO_ST_CMD_DELAY)

# Provide some reasonable defaults for plugin macros
# May be overridden by $(PLUGINS).cmd
epicsEnvSet( "PLUGIN_SRC", "$(CAM_PORT)" )
epicsEnvSet( "N", "1" )
epicsEnvSet( "QSIZE", "10" )

# Configure and load any image streams
$$LOOP(STREAM)
$$IF(NAME,data)
epicsEnvSet( "IMAGE_NAME",   "$$IF(IMAGE_NAME,$$IMAGE_NAME,DATA1)" )
$$ENDIF(NAME)
$$IF(NAME,viewer)
epicsEnvSet( "IMAGE_NAME",   "$$IF(IMAGE_NAME,$$IMAGE_NAME,IMAGE1)" )
$$ENDIF(NAME)
$$IF(NAME,thumbnail)
epicsEnvSet( "IMAGE_NAME",   "$$IF(IMAGE_NAME,$$IMAGE_NAME,THUMBNAIL)" )
$$ENDIF(NAME)
$$IF(STREAM_NELM)
epicsEnvSet( "STREAM_NELM",  "$$STREAM_NELM" )
$$ELSE(STREAM_NELM)
epicsEnvSet( "STREAM_NELM",  "$(IMAGE_NELM)" )
$$ENDIF(STREAM_NELM)
< db/$$(NAME)Stream.cmd
$$ENDLOOP(STREAM)

# Configure and load any desired viewers (deprecated)
$$LOOP(VIEWER)
epicsEnvSet( "IMAGE_NAME",   "$$IF(IMAGE_NAME,$$IMAGE_NAME,IMAGE1)" )
< db/$$(NAME)Viewer.cmd
$$ENDLOOP(VIEWER)

# Configure and load plugin sets
$$IF(PLUGINS)
< db/$$(PLUGINS).cmd
$$ENDIF(PLUGINS)

# Configure and load selected plugins, if any
$$LOOP(PLUGIN)
epicsEnvSet( "N",            "$$IF(NUM,$$NUM,1)" )
epicsEnvSet( "PLUGIN_SRC",   "$$IF(SRC,$$SRC,CAM)" )
< db/plugin$$(NAME).cmd
$$ENDLOOP(PLUGIN)

$$LOOP(BLD)
# TODO: Reconfigure BLD as Spectrometer plugin
# Configure and load BLD plugin
epicsEnvSet( "N",            "$$CALC{INDEX+1}" )
epicsEnvSet( "PLUGIN_SRC",   "CAM" )
< db/pluginBldSpectrometer.cmd
$$IF(HIST)
# Load history records
# TODO: Fix me!  bld_hist.substitutions should become something
# along the lines of
# dbLoadRecords( "db/plugin$$(NAME)Hist.db 
dbLoadRecords("db/bld_hist.db",     "P=$(CAM_PV),R=:" )
$$ENDIF(HIST)
$$ENDLOOP(BLD)

$$IF(NO_ST_CMD_DELAY)
$$ELSE(NO_ST_CMD_DELAY)
epicsThreadSleep $(ST_CMD_DELAYS)
$$ENDIF(NO_ST_CMD_DELAY)

$$IF(EVR_PV)
# Configure the EVR
ErDebugLevel( $$IF(ErDebug,$$ErDebug,0) )
ErConfigure( $(EVR_CARD), 0, 0, 0, $(EVRID_$$EVR_TYPE) )
dbLoadRecords( "$(EVRDB)", "IOC=$(IOC_PV),EVR=$(EVR_PV),CARD=$(EVR_CARD)$$IF(EVR_TRIG),IP$$(EVR_TRIG)E=Enabled$$ENDIF(EVR_TRIG)$$LOOP(EXTRA_TRIG),IP$$(TRIG)E=Enabled$$ENDLOOP(EXTRA_TRIG)" )
dbLoadRecords( "db/devEvrInfo.db",				"DEV=$(CAM_PV),IOC=$(IOC_PV),EVR=$(EVR_PV),TRIG_CH=$$IF(EVR_TRIG,$$EVR_TRIG,0),EVR_USED=1" )
$$ELSE(EVR_PV)
dbLoadRecords( "db/devEvrInfo.db",				"DEV=$(CAM_PV),EVR=$(EVR_PV),EVR_USED=0" )
$$ENDIF(EVR_PV)

# Load netstat records
dbLoadRecords("db/netstat.template", "P=$(IOC_PV),IF=$$IF(NET_IF,$$NET_IF,ETH0),IF_NUM=$$IF(NET_IF_NUM,$$NET_IF_NUM,1)" )

# Load soft ioc related record instances
dbLoadRecords( "db/iocSoft.db",				"IOC=$(IOC_PV)" )
dbLoadRecords( "db/iocRelease.db",			"IOC=$(IOC_PV)" )
epicsEnvSet( "DEV_INFO", "DEV=$(CAM_PV),IOC=$(IOC_PV),IOCNAME=$(IOCNAME)" )
epicsEnvSet( "DEV_INFO", "$(DEV_INFO),COM_TYPE=camLink,COM_PORT=eNet $CAM_IP" )
$$IF(POWER)
epicsEnvSet( "DEV_INFO", "$(DEV_INFO),POWER=$$POWER" )
$$ENDIF(POWER)
$$IF(WEB_URL)
epicsEnvSet( "DEV_INFO", "$(DEV_INFO),WEB_URL=$$WEB_URL" )
$$ENDIF(WEB_URL)
$$IF(CAPTAR)
epicsEnvSet( "DEV_INFO", "$(DEV_INFO),CAPTAR=$$CAPTAR" )
$$ENDIF(CAPTAR)
dbLoadRecords( "db/devIocInfo.db",			"$(DEV_INFO)" )

# Setup autosave
dbLoadRecords( "db/save_restoreStatus.db",	"P=$(IOC_PV),IOC=$(IOC_PV)" )
set_savefile_path( "$(IOC_DATA)/$(IOC)/autosave" )
set_requestfile_path( "$(BUILD_TOP)/autosave" )
# Also look in the iocData autosave folder for auto generated req files
set_requestfile_path( "$(IOC_DATA)/$(IOC)/autosave" )
save_restoreSet_status_prefix( "$(IOC_PV):" )
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )
# pass0 autosave restore IS needed for cameras and slows IOC boot
set_pass0_restoreFile( "autoSettings.sav" )
#set_pass0_restoreFile( "$(IOC).sav" )
# Is pass1 needed?
set_pass1_restoreFile( "autoSettings.sav" )
#set_pass1_restoreFile( "$(IOC).sav" )

#
# iocInit: Initialize the IOC and start processing records
#
$$IF(NO_ST_CMD_DELAY)
$$ELSE(NO_ST_CMD_DELAY)
epicsThreadSleep $(ST_CMD_DELAYS)
$$ENDIF(NO_ST_CMD_DELAY)
iocInit()

# iocInit done
$$IF(NO_ST_CMD_DELAY)
$$ELSE(NO_ST_CMD_DELAY)
epicsThreadSleep $(ST_CMD_DELAYS)
$$ENDIF(NO_ST_CMD_DELAY)

# Start PVAccess Server
#startPVAServer()

# Create autosave files from info directives
makeAutosaveFileFromDbInfo( "$(IOC_DATA)/$(IOC)/autosave/autoSettings.req", "autosaveFields" )

# Start autosave backups
create_monitor_set( "autoSettings.req",  5,  "" )
create_monitor_set( "$(IOCNAME).req",    5,  "" )

# All IOCs should dump some common info after initial startup.
< $(IOC_COMMON)/All/post_linux.cmd

$$LOOP(BLD)
$$IF(BLD_SRC)
# Configure the BLD client
epicsEnvSet( "BLD_IP",      "239.255.24.$$BLD_SRC" )
epicsEnvSet( "BLD_XTC",     "$$IF(XTC,$$XTC,0x10048)" ) # XTC Type, Id_Spectrometer
epicsEnvSet( "BLD_SRC",     "$$SRC" ) # Src Id
epicsEnvSet( "BLD_PORT",    "$$IF(PORT,$$PORT,10148)" )
epicsEnvSet( "BLD_MAX",     "$$IF(MAX,$$MAX,8980)" )    # 9000 MTU - 20 byte header
BldSetID( "$$IF(BLD_ID,$$BLD_ID,0)" )
BldConfigSend( "239.255.24.$$BLD_SRC", "$$IF(PORT,$$PORT,10148)", "$$IF(MAX,$$MAX,8980)", "$$IF(BLD_IF,$$BLD_IF,)" )
#BldConfigSend( "$(BLD_IP)", $(BLD_PORT), $(BLD_MAX) )
$$IF(BLD_AUTO_START)
# Autostart plugin specific BLD
BldStart()
$$ENDIF(BLD_AUTO_START)

BldIsStarted()
$$ENDIF(BLD_SRC)
$$ENDLOOP(BLD)

$$IF(NO_ST_CMD_DELAY)
$$ELSE(NO_ST_CMD_DELAY)
epicsThreadSleep $(ST_CMD_DELAYS)
$$ENDIF(NO_ST_CMD_DELAY)

# TODO: Remove these dbpf calls if possible
# Enable callbacks
dbpf $(CAM_PV):ArrayCallbacks 1
dbpf $(CAM_PV):LAUNCH_EDM "$$TOP/iocBoot/$(IOCNAME)/edm-$(IOCNAME).cmd"

$$IF(AUTO_START)
# Final delay before auto-start image acquisition
epicsThreadSleep 3
dbpf $(CAM_PV):Acquire $$AUTO_START
$$ENDIF(AUTO_START)
