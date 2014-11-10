#! /bin/env python
import sys, os
import socket # for getting hostname
import logging
from options import Options

from PyQt4 import QtGui 

from Viewer import Viewer

DEBUG = True

logger=logging.getLogger('mviewer')

if len(logging.root.handlers) == 0:
    logger_console_handler = logging.StreamHandler()
    logger_console_handler.setFormatter( logging.Formatter("LOG %(name)s %(levelno)s: %(message)s") )
    logger.addHandler( logger_console_handler )


if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.ERROR)



## ----------------------------------------------------------
## Working version (paiser):
## ~/workspace/PY_MEC_LAS_CAM/src/CA/gigeViewers/mviewer
## ----------------------------------------------------------
## command to run: ------------------------------------------ 
## ./run_mviewer.csh --instr mec --pvlist camera.lst
## ----------------------------------------------------------
## RELEASES: ------------------------------------------------
## on 03/14/2013 ~/dhz_release.sh ioc/common/gigECam R0.30.1
## ----------------------------------------------------------
## to compile mantaGiGE.so library: -------------------------
## source ./COMPILE
## ---------------------------------------------------------
## to move eclipse project to svn sandbox:
## cp -r ../mviewer ~/working/ioc/common/gigECam/current/Viewers/pyqt/mviewer2.0/
## ---------------------------------------------------------
## pvlist file (option --pvlist camera.lst): ----------------
## Device type, Camera PV, EVR PV prefix, Description, Lens PV(opt)
## Notes:
##   Device types: GE (gigeCams), MM (ims motors)
#GE,  MEC:LAS:GIGE:IMAGE1, None,  MEC Camera 1 #on ioc-mec-las-gige02
##GE,  MEC:LAS:GIGE:IMAGE2, None,  MEC Camera 2 #on ioc-mec-las-gige02
#GE,  MEC:LAS:GIGE:IMAGE3, None,  MEC Camera 3 #on ioc-mec-las-gige02
#GE,  MEC:LAS:GIGE:IMAGE4, None,  MEC Camera 4 # on ioc-mec-las-gige02
##GE,  MEC:LAS:GIGE:IMAGE5, None,  MEC Camera 5 #on ioc-mec-las-gige03
##GE,  MEC:LAS:GIGE:IMAGE6, None,  MEC Camera 6 #on ioc-mec-las-gige03
##GE,  MEC:LAS:GIGE:IMAGE7, None,  MEC Camera 7 #on ioc-mec-las-gige03
##GE,  TST:SWT:GIGE:IMAGE1, None,  TST CAM on switch-tst-b901
##MM,  TST:SWT:GIGE:MMS1, None,  Phantom motor on switch-tst-b901
##MM,  TST:SWT:GIGE:MOT2, None,  TST Motor on switch-tst-b901
## ----------------------------------------------------------

# some notes:
# passing arg to slots using lambda
#self.connect(self.rfshTimer_2, QtCore.SIGNAL("timeout()"), lambda who=i: self.UpdateRate(i))
# to restart the ioc:
#caput IOC:MEC:LAS:GIGE02:SYSRESET 1
#caput IOC:MEC:LAS:GIGE03:SYSRESET 1
## -----------------------------------------------------------------------------





if DEBUG:
    print '''    
8888888b.         888                      
888  "Y88b        888                      
888    888        888                      
888    888 .d88b. 88888b. 888  888 .d88b.  
888    888d8P  Y8b888 "88b888  888d88P"88b 
888    88888888888888  888888  888888  888 
888  .d88PY8b.    888 d88PY88b 888Y88b 888 
8888888P"  "Y8888 88888P"  "Y88888 "Y88888 
                                       888 
                                  Y8b d88P 
                                   "Y88P"  
                                   
        8888888888                888     888             888 
        888                       888     888             888 
        888                       888     888             888 
        8888888   88888b.  8888b. 88888b. 888 .d88b.  .d88888 
        888       888 "88b    "88b888 "88b888d8P  Y8bd88" 888 
        888       888  888.d888888888  88888888888888888  888 
        888       888  888888  888888 d88P888Y8b.    Y88b 888 
        8888888888888  888"Y88888888888P" 888 "Y8888  "Y88888 
                                                          
'''
logger.debug( "running on host %s", socket.gethostname() )
logger.debug( "python version: %s", sys.version )

    



if __name__ == '__main__':
    #===========================================================================
    # Parsing options
    #===========================================================================
    cams = list()
    cwd = os.getcwd()
    #os.chdir("/tmp") # change the working dir to /tmp, so the core dump can be generated

    # Options( [mandatory list, optional list, switches list] )
    options = Options(['instrument'], ['pvlist', 'cfgdir'], ['syn'])
    try:
        options.parse()
    except Exception, msg:
        options.usage(str(msg))
        sys.exit()
    print 40*'-'
    print ' Starting %s Multiviewer Application' % options.instrument.upper()
    print 40*'-'
    
    if options.syn != None:
        print 'Using syn option'
    camLstFname = 'camera.lst' if (options.pvlist == None) else options.pvlist
    #===========================================================================
    # Configuration directory
    #===========================================================================
    if options.cfgdir == None:
        cfgdir = os.getenv("HOME")
        if cfgdir == None:
            cfgdir = ".mviewer/"
        else:
            cfgdir = cfgdir + "/.mviewer/"
    else:
        cfgdir = options.cfgdir
    try:
        os.mkdir(cfgdir)
    except:
        pass
    #===========================================================================
    # Main Application
    #===========================================================================
    app   = QtGui.QApplication([''])
    app.setStyle('Cleanlooks')
    app.setPalette(app.style().standardPalette())    

    gui = Viewer(app, cwd, options.instrument, camLstFname, cfgdir)#cwd, cams, cfgdir)
       
    sys.exit(app.exec_())


