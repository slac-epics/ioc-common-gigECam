import math
import time
import logging
import sys, os

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import QTimer, QObject #, Qt, QPoint, QPointF, QSize, QRectF, QObject
from PyQt4.Qt import QColorDialog

from utils import *
from SplashScreen import SplashScreen
from ViewerFrame import ViewerFrame, Glob

logger = logging.getLogger('mviewer.Viewer')

'''
TODO: 
Add save as in SetupDialog
Explore possibility of use of mouseMoveEvent to draw continuously the cross

'''



form_class1, base_class1 = uic.loadUiType('ui/mvsetup1.0.ui')

class SetupDialog(QtGui.QDialog, form_class1):    
    '''Setup dialog to define PV names'''
    def __init__(self, parent=None):
        super(SetupDialog, self).__init__(parent)
        self.setupUi(self)

        self.camPvs = [self.le_camPv_1, self.le_camPv_2, self.le_camPv_3, self.le_camPv_4,
                       self.le_camPv_5, self.le_camPv_6, self.le_camPv_7, self.le_camPv_8 ]

        self.camDescs = [self.le_camDesc_1, self.le_camDesc_2, self.le_camDesc_3, self.le_camDesc_4,
                       self.le_camDesc_5, self.le_camDesc_6, self.le_camDesc_7, self.le_camDesc_8 ]

        self.iocPvs = [self.le_iocPv_1, self.le_iocPv_2, self.le_iocPv_3, self.le_iocPv_4,
                       self.le_iocPv_5, self.le_iocPv_6, self.le_iocPv_7, self.le_iocPv_8 ]
        
        self.cB_encams = [self.cB_en_c1, self.cB_en_c2, self.cB_en_c3, self.cB_en_c4,
                          self.cB_en_c5, self.cB_en_c6, self.cB_en_c7, self.cB_en_c8 ]
        
        self.mmsPvs = [self.le_mmsPv_1, self.le_mmsPv_2, self.le_mmsPv_3, self.le_mmsPv_4,
                       self.le_mmsPv_5, self.le_mmsPv_6, self.le_mmsPv_7, self.le_mmsPv_8 ]

        self.mmsDescs = [self.le_mmsDesc_1, self.le_mmsDesc_2, self.le_mmsDesc_3, self.le_mmsDesc_4,
                       self.le_mmsDesc_5, self.le_mmsDesc_6, self.le_mmsDesc_7, self.le_mmsDesc_8 ]

        self.cB_enmmss = [self.cB_en_m1, self.cB_en_m2, self.cB_en_m3, self.cB_en_m4,
                          self.cB_en_m5, self.cB_en_m6, self.cB_en_m7, self.cB_en_m8 ]
                
        self.setupvals = [self.camPvs, self.camDescs, self.iocPvs, self.cB_encams,\
                          self.mmsPvs, self.mmsDescs, self.cB_enmmss]
        self.filename = None
        self.connect(self.pB_saveas, QtCore.SIGNAL("clicked()"), self.saveas)
        self.connect(self.pB_load,   QtCore.SIGNAL("clicked()"), self.load)
        self.connect(self.pB_clear,  QtCore.SIGNAL("clicked()"), self.clearall)
        
    def getValues(self):
        # enumerated elements order
        cam, camdesc, ioc, cen, mms, mmsdesc, men = (0,1,2,3,4,5,6)
        return self.setupvals
        
    def load(self):
        '''Load values from file'''
        logger.debug("SetupDialog load called")
        self.filename = QtGui.QFileDialog.getOpenFileName(self, 'Open Camera Pvs File', os.getenv('HOME') + '/.mviewer', '*.lst')
        self.readCamList(self.filename)
        
    def saveas(self):
        '''Save values to specific file'''
        logger.debug("SetupDialog saveas called")
        self.filename = QtGui.QFileDialog.getSaveFileName(self, 'Save Camera Pvs File as', os.getenv('HOME') + '/.mviewer', '*.lst')
        if self.filename[-4:] != '.lst':
            self.filename += '.lst'
        self.setupvals = self.getValues()
        self.dumpCamList(self.filename) # write to camera.lst updated data.        
        #f.close()
        
    def clearall(self):
        '''Clear all fields'''
        self.all_le = self.camPvs + self.camDescs + self.iocPvs + self.mmsPvs + self.mmsDescs
        self.all_cB = self.cB_encams + self.cB_enmmss
        for w in self.all_le:
            w.clear()
        for c in self.all_cB:
            c.setChecked(False)
        self.filename = None
            
    def dumpCamList(self, filename):
        '''Writes camera Pvs parameters in user assigned filename'''
        if self.setupvals == []:
            return False
        # enumerate
        cam, camdesc, ioc, cen, mms, mmsdesc, men = (0,1,2,3,4,5,6)
        # shortcuts
        camPv = self.setupvals[cam]; camPvdesc = self.setupvals[camdesc]
        iocPv = self.setupvals[ioc]; cen       = self.setupvals[cen]
        mmsPv = self.setupvals[mms]; mmsPvdesc = self.setupvals[mmsdesc]
        men   = self.setupvals[men]
        
        # assign to additional shortcuts
        camPv1 = camPv[0].text(); camPvDesc1 = camPvdesc[0].text()
        camPv2 = camPv[1].text(); camPvDesc2 = camPvdesc[1].text()
        camPv3 = camPv[2].text(); camPvDesc3 = camPvdesc[2].text()
        camPv4 = camPv[3].text(); camPvDesc4 = camPvdesc[3].text()
        camPv5 = camPv[4].text(); camPvDesc5 = camPvdesc[4].text()
        camPv6 = camPv[5].text(); camPvDesc6 = camPvdesc[5].text()
        camPv7 = camPv[6].text(); camPvDesc7 = camPvdesc[6].text()
        camPv8 = camPv[7].text(); camPvDesc8 = camPvdesc[7].text()
        
        iocPv1 = iocPv[0].text(); camEn1 = '' if cen[0].isChecked() else '#'
        iocPv2 = iocPv[1].text(); camEn2 = '' if cen[1].isChecked() else '#'
        iocPv3 = iocPv[2].text(); camEn3 = '' if cen[2].isChecked() else '#'
        iocPv4 = iocPv[3].text(); camEn4 = '' if cen[3].isChecked() else '#'
        iocPv5 = iocPv[4].text(); camEn5 = '' if cen[4].isChecked() else '#'
        iocPv6 = iocPv[5].text(); camEn6 = '' if cen[5].isChecked() else '#'
        iocPv7 = iocPv[6].text(); camEn7 = '' if cen[6].isChecked() else '#'
        iocPv8 = iocPv[7].text(); camEn8 = '' if cen[7].isChecked() else '#'
        
        mmsPv1 = mmsPv[0].text(); mmsPvDesc1 = mmsPvdesc[0].text()
        mmsPv2 = mmsPv[1].text(); mmsPvDesc2 = mmsPvdesc[1].text()
        mmsPv3 = mmsPv[2].text(); mmsPvDesc3 = mmsPvdesc[2].text()
        mmsPv4 = mmsPv[3].text(); mmsPvDesc4 = mmsPvdesc[3].text()
        mmsPv5 = mmsPv[4].text(); mmsPvDesc5 = mmsPvdesc[4].text()
        mmsPv6 = mmsPv[5].text(); mmsPvDesc6 = mmsPvdesc[5].text()
        mmsPv7 = mmsPv[6].text(); mmsPvDesc7 = mmsPvdesc[6].text()
        mmsPv8 = mmsPv[7].text(); mmsPvDesc8 = mmsPvdesc[7].text()
        
        mmsEn1 = '' if men[0].isChecked() else '#'
        mmsEn2 = '' if men[1].isChecked() else '#'
        mmsEn3 = '' if men[2].isChecked() else '#'
        mmsEn4 = '' if men[3].isChecked() else '#'
        mmsEn5 = '' if men[4].isChecked() else '#'
        mmsEn6 = '' if men[5].isChecked() else '#'
        mmsEn7 = '' if men[6].isChecked() else '#'
        mmsEn8 = '' if men[7].isChecked() else '#'
        
        # Write to file cameras.lst
        f = open(filename, "w")
        f.write("\n")
        f.write(''
'# ---------------------------------------------------------------\n'
'# MultiViewer Description File (Generated by Setup Dialog)\n'
'# ---------------------------------------------------------------\n'
'# Syntax:\n'
'#   <TYPE>, <PVNAME|IOCNAME>, <DESC> # some_more_comments\n'
'# Where:\n'
'#   <Type>    : "GIG" -> GigE Cameras or\n'
'#               "IOC" -> Server name\n'
'#               "MMS" -> Motor or\n'
'#   <PVNAME>  : Camera PV Name to display in the display\n'
'#   <IOCNAME> : Server name associated to restart button\n'
'#   <DESC>    : User Camera or Server description\n'
'# Notes:\n'
'#   PVNAME or IOCNAME are not case sensitive.\n'
'#   Line can be commented out by starting with \'#\' character.\n'
'# ---------------------------------------------------------------\n\n')
        f.write('# CAMERA PV NAMES (located in the cfg file, \'CAM\' variable):\n')
        f.write('%sGIG, %s, %s \t #\n' % (camEn1, camPv1, camPvDesc1))
        f.write('%sGIG, %s, %s \t #\n' % (camEn2, camPv2, camPvDesc2))
        f.write('%sGIG, %s, %s \t #\n' % (camEn3, camPv3, camPvDesc3))
        f.write('%sGIG, %s, %s \t #\n' % (camEn4, camPv4, camPvDesc4))
        f.write('%sGIG, %s, %s \t #\n' % (camEn5, camPv5, camPvDesc5))
        f.write('%sGIG, %s, %s \t #\n' % (camEn6, camPv6, camPvDesc6))
        f.write('%sGIG, %s, %s \t #\n' % (camEn7, camPv7, camPvDesc7))
        f.write('%sGIG, %s, %s \t #\n' % (camEn8, camPv8, camPvDesc8))
        f.write('\n')
        f.write('# IOC PV NAMES (located in the cfg file, \'IOC_PV\' variable):)\n')
        f.write('%sIOC, %s, %s \t #\n' % (camEn1, iocPv1, camPvDesc1))
        f.write('%sIOC, %s, %s \t #\n' % (camEn2, iocPv2, camPvDesc2))
        f.write('%sIOC, %s, %s \t #\n' % (camEn3, iocPv3, camPvDesc3))
        f.write('%sIOC, %s, %s \t #\n' % (camEn4, iocPv4, camPvDesc4))
        f.write('%sIOC, %s, %s \t #\n' % (camEn5, iocPv5, camPvDesc5))
        f.write('%sIOC, %s, %s \t #\n' % (camEn6, iocPv6, camPvDesc6))
        f.write('%sIOC, %s, %s \t #\n' % (camEn7, iocPv7, camPvDesc7))
        f.write('%sIOC, %s, %s \t #\n' % (camEn8, iocPv8, camPvDesc8))
        f.write('\n')
        f.write('# MOTOR PV NAMES:\n')
        f.write('%sMMS, %s, %s \t #\n' % (mmsEn1, mmsPv1, mmsPvDesc1))
        f.write('%sMMS, %s, %s \t #\n' % (mmsEn2, mmsPv2, mmsPvDesc2))
        f.write('%sMMS, %s, %s \t #\n' % (mmsEn3, mmsPv3, mmsPvDesc3))
        f.write('%sMMS, %s, %s \t #\n' % (mmsEn4, mmsPv4, mmsPvDesc4))
        f.write('%sMMS, %s, %s \t #\n' % (mmsEn5, mmsPv5, mmsPvDesc5))
        f.write('%sMMS, %s, %s \t #\n' % (mmsEn6, mmsPv6, mmsPvDesc6))
        f.write('%sMMS, %s, %s \t #\n' % (mmsEn7, mmsPv7, mmsPvDesc7))
        f.write('%sMMS, %s, %s \t #\n' % (mmsEn8, mmsPv8, mmsPvDesc8))
        f.close()
        
        
    def readCamList(self, filename):
        '''Reads camera.lst file, update camera combo, etc...'''
        # shortcuts
        camPv = self.camPvs;    camPvDesc = self.camDescs
        iocPv = self.iocPvs;    camEn     = self.cB_encams
        mmsPv = self.mmsPvs;    mmsPvDesc = self.mmsDescs
        mmsEn = self.cB_enmmss;

        pvlist = open(filename,"r").readlines()
        
        camEnVal     = False
        camPvVal     = ''
        camPvDescVal = ''
        iocPvVal     = ''
        mmsEnVal     = False
        mmsPvVal     = ''
        mmsPvDescVal = ''
        
        i = 0; j = 0; k = 0
        
        for line in pvlist:
            line = line.lstrip()
            if not line:
                continue
            if 'GIG' in line[0:5] and ',' in line[0:5]:
                if i > 7: continue
                if line.startswith("#"): 
                    camEnVal = False
                else: 
                    camEnVal = True 
                camPvVal = line.split(",")[1].strip()
                camPvDescVal = line.split(",")[2].strip().split('#')[0].rstrip()
                camEn[i].setChecked(camEnVal); camPv[i].setText(camPvVal), camPvDesc[i].setText(camPvDescVal)
                i += 1
            elif 'IOC' in line[0:5] and ',' in line[0:5]:
                if j > 7: continue
                iocPvVal = line.split(",")[1].strip()
                iocPv[j].setText(iocPvVal)
                j += 1
            elif 'MMS' in line[0:5] and ',' in line[0:5]:
                if k > 7: continue
                if line.startswith("#"): 
                    mmsEnVal = False
                else: 
                    mmsEnVal = True
                mmsPvVal = line.split(",")[1].strip()
                mmsPvDescVal = line.split(",")[2].strip().split('#')[0].rstrip()
                mmsEn[k].setChecked(mmsEnVal); mmsPv[k].setText(mmsPvVal), mmsPvDesc[k].setText(mmsPvDescVal)
                k += 1 
        return True
    
form_class, base_class = uic.loadUiType('ui/mviewer2.9.1.ui')

class Viewer(QtGui.QMainWindow, form_class):    
    '''Display multiple gigE cameras in a single application'''
    def __init__(self, app, cwd, instrument, camLstFname, cfgdir, parent=None):
        super(Viewer, self).__init__(parent)
        #QtGui.QWidget.__init__(self)
        self.setupUi(self)

        #self.splashScreen = SplashScreen()
#        self.setGeometry(QtCore.QRect(self.width()/2-10, self.height()/2-10,
#                                      self.width()/2+10, self.height()/2+10))
        #self.splashScreen.showMsg("Starting Aplication...")
        #time.sleep(0.5)

        self.app        = app
        self.cwd        = cwd
        self.instrument = instrument
        self.camerListFilename  = camLstFname
        self.cfgdir     = cfgdir
        self.cfg        = None
        self.EnableDumpConfig = False
        self.iScaleIndex= False
        
        
        #layout = 
        #layout = QtGui.QGridLayout(self)
        #self.setLayout(layout)
        self.iRangeMin = 0
        self.iRangeMax = 255
        self.ledoff     = QtGui.QPixmap('ui/led-off-22x22.png')
        self.ledon      = QtGui.QPixmap('ui/led-red-22x22.png')
        self.limitoff  = QtGui.QPixmap('ui/led-off-16x16.png')
        self.limiton   = QtGui.QPixmap('ui/led-red-16x16.png')
        self.viewer     = [None for i in range(8)]
        self.ca         = [None for i in range(8)]
        #self.colormap   = [None for i in range(8)]
        self.camlabel   = [''   for i in range(8)]
        self.cam_n      = 0  # Default: controls starts by first camera
        self.mot_n      = 0  # motor index
        self.last_cam_n = 0    
        self.iocmod     = [True  for i in range(8)] # default: uses CA
        self.ipmod      = [False for i in range(8)]
        
        self.ShowCross = [False, False, False, False]
        self.LockCross = [False, False, False, False]
        
        self.w_Img = [self.w_Img_1, self.w_Img_2, self.w_Img_3, self.w_Img_4,
                      self.w_Img_5, self.w_Img_6, self.w_Img_7, self.w_Img_8]
        
        self.idock = [self.dW_Img_1,self.dW_Img_2,self.dW_Img_3,self.dW_Img_4,
                       self.dW_Img_5,self.dW_Img_6,self.dW_Img_7,self.dW_Img_8]
        # Motors: --------------------------------------------------------------
        self.lb_limM   = [self.lb_limM_1, self.lb_limM_2, self.lb_limM_3, self.lb_limM_4, self.lb_limM_5, self.lb_limM_6, self.lb_limM_7, self.lb_limM_8]
        self.lb_limP   = [self.lb_limP_1, self.lb_limP_2, self.lb_limP_3, self.lb_limP_4, self.lb_limP_5, self.lb_limP_6, self.lb_limP_7, self.lb_limP_8]
        self.lE_mr     = [self.lE_mr_1, self.lE_mr_2, self.lE_mr_3, self.lE_mr_4, self.lE_mr_5, self.lE_mr_6, self.lE_mr_7, self.lE_mr_8]
        self.tB_mminus = [self.tB_mminus_1, self.tB_mminus_2, self.tB_mminus_3, self.tB_mminus_4, self.tB_mminus_5, self.tB_mminus_6, self.tB_mminus_7, self.tB_mminus_8]
        self.tB_mplus  = [self.tB_mplus_1, self.tB_mplus_2, self.tB_mplus_3, self.tB_mplus_4, self.tB_mplus_5, self.tB_mplus_6, self.tB_mplus_7, self.tB_mplus_8]  
        self.cB_onmot  = [self.cB_onmot_1, self.cB_onmot_2, self.cB_onmot_3, self.cB_onmot_4, self.cB_onmot_5, self.cB_onmot_6, self.cB_onmot_7, self.cB_onmot_8]
        # ----------------------------------------------------------------------
        self.xPos_val = [self.X1Position, self.X2Position, self.X3Position, self.X4Position]

        self.yPos_val = [self.Y1Position, self.Y2Position, self.Y3Position, self.Y4Position]

        self.rd_cross = [self.cBcross_1, self.cBcross_2, self.cBcross_3, self.cBcross_4]
        self.rd_line  = [self.rd_line1, self.rd_line2, self.rd_line3, self.rd_line4]

        self.dist_val = [self.Distance1, self.Distance2]

        self.from_val = [self.From1, self.From2]

        self.check_box = [
                self.checkBox11, self.checkBox12, self.checkBox13, self.checkBox14,
                self.checkBox21, self.checkBox22, self.checkBox23, self.checkBox24,
                self.checkBox31, self.checkBox32, self.checkBox33, self.checkBox34,
                self.checkBox41, self.checkBox42, self.checkBox43, self.checkBox44,
                ]
        self.colormapsrb = {'jet' : self.rBColor_Jet, 'hsv' : self.rBColor_HSV, 'cool': self.rBColor_Cool, 'gray': self.rBColor_Gray, 'hot' : self.rBColor_Hot}

        self.lb_ImStats = [self.lb_minValdata, self.lb_maxValdata]

        self.lb_ImStats[0].setText('n/a') ; self.lb_ImStats[1].setText('n/a')
        
        for iMotor in range(8): 
            self.lb_limM[iMotor].setPixmap(self.limitoff)
            self.lb_limP[iMotor].setPixmap(self.limitoff)

        #self.splashScreen.showMsg("Reading Camera File...")            

        self.n_cams = self.readPVListFile()


        if self.n_cams > len(self.w_Img):
            self.n_cams = len(self.w_Img)
        if not self.n_cams:
            print 'Not Cameras selected'
            sys.exit(1)

        objc   = QtCore.QObject.connect
        qsig   = QtCore.SIGNAL
        sig0   = QtCore.SIGNAL("clicked()")
        sig1   = QtCore.SIGNAL("valueChanged(double)")
        sig2   = QtCore.SIGNAL("valueChanged(int)")
        sig3   = QtCore.SIGNAL("currentIndexChanged(int)")
        sig4   = QtCore.SIGNAL("par_upd(int, QVariant, QVariant)")
        sig5   = QtCore.SIGNAL("returnPressed()")
        sig6   = QtCore.SIGNAL("onUpdateRate(int, float, float)")
        sig7   = QtCore.SIGNAL("stateChanged()")
        sig9   = QtCore.SIGNAL("topLevelChanged(bool)")
        sig10  = QtCore.SIGNAL("released()")
        sig11  = QtCore.SIGNAL("timeout()")
        sig12  = QtCore.SIGNAL("lostFocus()")
        sig13  = QtCore.SIGNAL("sliderReleased()")

        # Colormap controls: --------------------------------------
        self.connect(self.cBoxScale,    sig3, self.onComboBoxScaleIndexChanged)
        self.connect(self.rBColor_Cool, sig0, self.set_cool)
        self.connect(self.rBColor_Gray, sig0, self.set_gray)
        self.connect(self.rBColor_HSV,  sig0, self.set_hsv)
        self.connect(self.rBColor_Hot,  sig0, self.set_hot)
        self.connect(self.rBColor_Jet,  sig0, self.set_jet)
        self.connect(self.hSRngMin,     sig2, self.onSliderRangeMinChanged)
        self.connect(self.hSRngMax,     sig2, self.onSliderRangeMaxChanged)
        #self.connect(self.hSRngMin,     sig13, self.onSliderRangeMinChanged)
        #self.connect(self.hSRngMax,     sig13, self.onSliderRangeMaxChanged)

        self.connect(self.lERngMin,     sig5, self.onRangeMinTextEnter )
        self.connect(self.lERngMax,     sig5, self.onRangeMaxTextEnter)
        # --------------------------------------------------------
        # Control Pvs:
        self.connect(self.lEBXY,        sig5, self.set_bin)
        self.connect(self.dS_expt,      sig1, self.set_expt)
        self.connect(self.iS_gain,      sig2, self.set_gain)
        self.connect(self.pB_setExpGain,sig0, self.set_expgain)
        #self.connect(self.cB_on,        sig0, self.onCameraButton)
        self.connect(self.pB_on,        sig0, self.onCamera)
        self.connect(self.cBgrayScale,  sig0, self.onCheckGrayScale)
        self.connect(self.pB_quit,      sig0, self.shutdown)
        self.connect(self.pB_resetioc,  sig0, self.resetIOC)
        self.connect(self.pB_save,      sig0, lambda: self.mytest('save'))
        self.connect(self.pB_elog,      sig0, lambda: self.mytest('elog'))
        self.connect(self.pB_setup,     sig0, self.mvsetup)
        # --------------------------------------------------------
        self.connect(self.checkBox11,   sig0, self.onCheckPress)
        self.connect(self.checkBox12,   sig0, self.onCheckPress)
        self.connect(self.checkBox13,   sig0, self.onCheckPress)
        self.connect(self.checkBox14,   sig0, self.onCheckPress)
        self.connect(self.checkBox21,   sig0, self.onCheckPress)
        self.connect(self.checkBox22,   sig0, self.onCheckPress)
        self.connect(self.checkBox23,   sig0, self.onCheckPress)
        self.connect(self.checkBox24,   sig0, self.onCheckPress)
        self.connect(self.checkBox31,   sig0, self.onCheckPress)
        self.connect(self.checkBox32,   sig0, self.onCheckPress)
        self.connect(self.checkBox33,   sig0, self.onCheckPress)
        self.connect(self.checkBox34,   sig0, self.onCheckPress)
        self.connect(self.checkBox41,   sig0, self.onCheckPress)
        self.connect(self.checkBox42,   sig0, self.onCheckPress)
        self.connect(self.checkBox43,   sig0, self.onCheckPress)
        self.connect(self.checkBox44,   sig0, self.onCheckPress)
        # --------------------------------------------------------
        self.connect(self.colorButton,  sig10, self.handleColorButton)
        ###self.connect(self.showHideCross,sig10, self.handleShowHide)
        self.connect(self.cBcross_1,   sig10, self.handleCross_1)
        self.connect(self.cBcross_2,   sig10, self.handleCross_2)
        self.connect(self.cBcross_3,   sig10, self.handleCross_3)
        self.connect(self.cBcross_4,   sig10, self.handleCross_4)
        self.connect(self.cBlock_1,    sig10, self.handleLockCrosses)
        self.connect(self.cBlock_2,    sig10, self.handleLockCrosses)
        self.connect(self.cBlock_3,    sig10, self.handleLockCrosses)
        self.connect(self.cBlock_4,    sig10, self.handleLockCrosses)

        self.connect(self.X1Position,   sig5, lambda: self.handleCrossText('X1'))
        self.connect(self.X2Position,   sig5, lambda: self.handleCrossText('X2'))
        self.connect(self.X3Position,   sig5, lambda: self.handleCrossText('X3'))
        self.connect(self.X4Position,   sig5, lambda: self.handleCrossText('X4'))
        self.connect(self.Y1Position,   sig5, lambda: self.handleCrossText('Y1'))
        self.connect(self.Y2Position,   sig5, lambda: self.handleCrossText('Y2'))
        self.connect(self.Y3Position,   sig5, lambda: self.handleCrossText('Y3'))
        self.connect(self.Y4Position,   sig5, lambda: self.handleCrossText('Y4'))
        
        # Those need to be set to the ViewerFrame signal
        self.connect(self.ResetTimer9h, sig10, lambda: self.onhandleTimerReset(9))
        self.connect(self.ResetTimer1h, sig10, lambda: self.onhandleTimerReset(1))
        self.connect(self.TimerClear,   sig10, lambda: self.onhandleTimerReset(0))
        self.connect(self.Timer,        sig11, self.onupdateTimer)
#
#        self.connect(self.timerreset9[1], sig10, lambda: self.handleTimerReset(1,9) )
#        self.connect(self.timerreset1[1], sig10, lambda: self.handleTimerReset(1,1) )
#        self.connect( self.timerclear[1], sig10, lambda: self.handleTimerReset(1,0) )
#        self.connect(self.timerKeepers[1],sig11,      lambda: self.updateTimer(1) )
#
#        self.connect(self.timerreset9[2], sig10, lambda: self.handleTimerReset(2,9) )
#        self.connect(self.timerreset1[2], sig10, lambda: self.handleTimerReset(2,1) )
#        self.connect( self.timerclear[2], sig10, lambda: self.handleTimerReset(2,0) )
#        self.connect(self.timerKeepers[2],sig11,      lambda: self.updateTimer(2) )
#
#        self.connect(self.timerreset9[3], sig10, lambda: self.handleTimerReset(3,9) )
#        self.connect(self.timerreset1[3], sig10, lambda: self.handleTimerReset(3,1) )
#        self.connect( self.timerclear[3], sig10, lambda: self.handleTimerReset(3,0) )
#        self.connect(self.timerKeepers[3],sig11,      lambda: self.updateTimer(3) )
#
#        self.connect(self.timerreset9[4], sig10, lambda: self.handleTimerReset(4,9) )
#        self.connect(self.timerreset1[4], sig10, lambda: self.handleTimerReset(4,1) )
#        self.connect( self.timerclear[4], sig10, lambda: self.handleTimerReset(4,0) )
#        self.connect(self.timerKeepers[4],sig11,      lambda: self.updateTimer(4) )
#
#        self.connect(self.timerreset9[5], sig10, lambda: self.handleTimerReset(5,9) )
#        self.connect(self.timerreset1[5], sig10, lambda: self.handleTimerReset(5,1) )
#        self.connect( self.timerclear[5], sig10, lambda: self.handleTimerReset(5,0) )
#        self.connect(self.timerKeepers[5],sig11,      lambda: self.updateTimer(5) )
#
#        self.connect(self.timerreset9[6], sig10, lambda: self.handleTimerReset(6,9) )
#        self.connect(self.timerreset1[6], sig10, lambda: self.handleTimerReset(6,1) )
#        self.connect( self.timerclear[6], sig10, lambda: self.handleTimerReset(6,0) )
#        self.connect(self.timerKeepers[6],sig11,      lambda: self.updateTimer(6) )
#
#        self.connect(self.timerreset9[7], sig10, lambda: self.handleTimerReset(7,9) )
#        self.connect(self.timerreset1[7], sig10, lambda: self.handleTimerReset(7,1) )
#        self.connect( self.timerclear[7], sig10, lambda: self.handleTimerReset(7,0) )
#        self.connect(self.timerKeepers[7],sig11,      lambda: self.updateTimer(7) )


        #print dir (self.w_Img_1)#.sizePolicy.setHeightForWidth(True)
        #print dir(self.dW_Img_1.sizePolicy.setHeightForWidth)
        
##        self.splashScreen.showMsg("Reading Camera File...")
##        for iwdg in self.idock:
##            iwdg.setEnabled(False)
##            iwdg.setWindowTitle('')
##        self.lock = [QtCore.QReadWriteLock() for i in range(8)]
##        self.splashScreen.showMsg("Loading Cameras...")            
##        refTime = int(time.time()) # throw away variable
##        for i in range(self.n_cams):
##            self.cam_n = i # update current camera
##            self.idock[i].setEnabled(True)
##            self.w_Img[i].setEnabled(True)
##            if self.iocmod[i]:
##                self.getConfig(i)
##                self.ca[i] = CAComm(self.lock[i], self.basename[i], self)
##                self.viewer[i] = ViewerFrame(self.w_Img[i], self)
##                self.viewer[i].showCross = self.ShowCross
##                self.forceRefreshColorMap(i)
##                self.connect(self.viewer[i], sig6, self.onUpdateRate)
##                self.connect(self.idock[i],  sig9, self.centerDock)
##                self.splashScreen.showMsg("Loading... %s as Cam[%d]" % (self.lCameraDesc[i], i))
###                self.setupTimer(i,refTime=refTime)
##                #time.sleep(1)
##        self.cam_n = 0
        
        self.loadEverything()
        self.settoolTips()

##        # Destroy Splash once all are loaded
##        if self.splashScreen:
##            self.splashScreen.finish(self)

##        self.getConfig(0)
#        self.onComboBoxScaleIndexChanged()
#        self.viewer[0].setColorMap(self.getColorMapRadioButton())
#        self.updateCamCombo()
        
        #time.sleep(1)
        self.centerOnScreen()
        self.show()
        self.EnableDumpConfig = True
        
    def unloadEverything(self):
        logger.debug("unloadEverything called")
        for iwdg in self.idock:
            iwdg.setEnabled(False)
            iwdg.setWindowTitle('')
        self.lock = [None for i in range(8)]
        refTime = None
        for i in range(self.n_cams):
            self.cam_n = i # update current camera
            self.idock[i].setEnabled(False)
            self.w_Img[i].setEnabled(False)
            self.w_Img[i].setStyleSheet('background-image: ./ui/blue.png')
            if self.iocmod[i]:
                self.dumpConfig(i)
                self.disconnect(self.idock[i],  QtCore.SIGNAL("topLevelChanged(bool)"), self.centerDock)
                self.disconnect(self.viewer[i], QtCore.SIGNAL("onUpdateRate(int, float, float)"), self.onUpdateRate)
                self.viewer[i].disconnectDisplay()
                self.ca[i] = None
                self.viewer[i] = None
        self.cam_n = 0
        #self.w_Img_2.
        self.repaint()
        
    def loadEverything(self):
        logger.debug("loadEverything called")
        splashScreen = SplashScreen()
        splashScreen.showMsg("Reading Camera File..."); time.sleep(0.5)
        for iwdg in self.idock:
            iwdg.setEnabled(False)
            iwdg.setWindowTitle('')
        self.lock = [QtCore.QReadWriteLock() for i in range(8)]
        splashScreen.showMsg("Loading Cameras...")            
        refTime = int(time.time()) # throw away variable
        #for i in range(8):
        #    self.w_Img[i].setStyleSheet("QWidget { background: 'blue' }")
        for i in range(self.n_cams):
            self.cam_n = i # update current camera
            self.idock[i].setEnabled(True)
            self.w_Img[i].setEnabled(True)
            if self.iocmod[i]:
                self.getConfig(i)
                self.ca[i] = CAComm(self.lock[i], self.basename[i], self)
                self.viewer[i] = ViewerFrame(self.w_Img[i], self)
                self.viewer[i].connectCamera()
                self.viewer[i].showCross = self.ShowCross
                self.connect(self.viewer[i], QtCore.SIGNAL("onUpdateRate(int, float, float)"), self.onUpdateRate)
                self.connect(self.idock[i],  QtCore.SIGNAL("topLevelChanged(bool)"), self.centerDock)
                splashScreen.showMsg("Loading... %s as Cam[%d]" % (self.lCameraDesc[i], i))
                time.sleep(0.5)
                self.forceRefreshColorMap(i)
        self.cam_n = 0
        # Destroy Splash once all are loaded
        if splashScreen:
            splashScreen.finish(self)
        self.getConfig(0)

    def forceRefreshColorMap(self, cam_n):
        '''Workaround to force refreshing image with new colormap.'''
        if self.viewer[cam_n]:
            file1, file2 = self.getColorMapRadioButton(2)
            self.viewer[cam_n].setColorMap(file1)
            self.viewer[cam_n].setColorMap(file2)
        
    def mvsetup(self):
        '''Opens a Dialog with list of Pvs that can be assigned by the user,
           then save this list to camera.lst file.
           TODO: maybe implement a set of setup list files to be recalled
           by the user in the Setup Dialog.
        '''
        dlg = SetupDialog()
        # enumerate the setupvals elements, according to Setup Dialog class 
        # getValues method.
        cam, camdesc, ioc, cen, mms, mmsdesc, men = (0,1,2,3,4,5,6)
        if dlg.exec_():
            self.unloadEverything()
            filename  = dlg.filename
            if filename != None:
                self.n_cams = self.readPVListFile(filename)
            if self.n_cams > len(self.w_Img):
                self.n_cams = len(self.w_Img)
            if not self.n_cams:
                print 'Not Cameras selected'
                sys.exit(1)
                
            print '>>>>>>>>>>>>>>>> need to connect monitors for image....'
            self.loadEverything()
            print "Loaded loadEverything!"
            
            
            #self.setupvals = dlg.getValues()
            #self.dumpCamList() # write to camera.lst updated data.

#    def setupTimer(self, i,refTime=None,duration=9):
#        logger.debug( "setup timer called %i"% i )
#        self.timerlabels[i].setEnabled(True)
#        self.timers[i].setEnabled(True)
#        self.timerreset9[i].setEnabled(True)
#        self.timerreset1[i].setEnabled(True)
#        self.timerclear[i].setEnabled(True)
#        self.timerlabels[i].setText( self.lCameraDesc[i] )
#        self.handleTimerReset(i,duration)
#        if not refTime:
#            refTime = time.time()
#        self.timerReferenceTime[i] = (refTime,duration*3600.)
#        self.timerKeepers[i].start(1000)
#
    def onhandleTimerReset(self, t):
        logger.debug("onhandleTimerReset %g", t)
        pass
        # send signal to ViewerFrame ??
        
#        logger.debug( "timer reset %g %g", cam_n, t )
#        #self.updateCamCombo()
#        self.timers[cam_n].setText("{:02.0f}:00:00".format(t))
#        self.timerReferenceTime[cam_n] = (time.time(),float(t)*3600.)
#        logger.debug( "handleTimerReset %g %g %s", t, cam_n, self.viewer[cam_n] )
#        if t > 0 and self.viewer[cam_n].camera is None :
#            print "reconnecting", cam_n
#            self.viewer[cam_n].connectCamera( self.viewer[cam_n].cameraBase )
#            #self.onUpdateColorMap(cam_n)
#            self.viewer[cam_n].setColorMap()
#            self.connect(self.viewer[cam_n], self.sig6, self.onUpdateRate)
#            self.updateCameraTitle(cam_n)
#        elif t == 0 and self.viewer[cam_n].camera is not None : 
#            print "clearing Cam", cam_n
#            self.viewer[cam_n].clear()
#
    def onupdateTimer(self):
        logger.debug("onupdateTimer called")
        pass
        # send signal to ViewerFrame ??
        
        
#        if self.timers[cam_n].isEnabled() and self.timerReferenceTime[cam_n]:
#            ref, totalseconds = self.timerReferenceTime[cam_n]
#            endTime = ref+totalseconds
#            delta = int(endTime - time.time())
#            if delta > 0:
#                hours = delta / 3600
#                minutes = (delta % 3600) / 60
#                seconds = (delta % 3600) % 60
#                #if DEBUG:
#                #    print cam_n, ref, totalseconds, endTime, delta, hours, minutes, seconds
#                self.timers[cam_n].setText("{:02.0f}:{:02.0f}:{:02.0f}".format(hours,minutes,seconds))
#            else :
#                hours = 0
#                minutes = 0
#                seconds = 0
#                self.timers[cam_n].setText("{:02.0f}:{:02.0f}:{:02.0f}".format(hours,minutes,seconds))
#                if self.viewer[cam_n].camera is not None :
#                    self.viewer[cam_n].clear()
#                #if DEBUG:
#                #    print "camera", cam_n, "should be disabled"

    def centerOnScreen(self):
        '''centerOnScreen() Centers the window on the screen.'''
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

    def getSelectedCross(self):
      for i, cx in enumerate(self.rd_cross):
          if cx.isChecked():
              break
      return i

    def getShowCross(self):
        logger.debug( "getShowCross" )
        return [self.cBcross_1.isChecked(), self.cBcross_2.isChecked(), self.cBcross_3.isChecked(), self.cBcross_4.isChecked(), ]

    def getLockCross(self):
        logger.debug( "getLockCross" )
        return [self.cBlock_1.isChecked(), self.cBlock_2.isChecked(), self.cBlock_3.isChecked(), self.cBlock_4.isChecked(), ]
    
    def getSpecificCrossValue(self):
        logger.debug( "checked? %s", self.showHideCross.isChecked() )
        if self.showHideCross.isChecked():
            if   self.Cross1.isChecked():
                X = 'X1' ; Y = 'Y1'
            elif self.Cross2.isChecked():
                X = 'X2' ; Y = 'Y2'
            elif self.Cross3.isChecked():
                X = 'X3' ; Y = 'Y3'
            elif self.Cross4.isChecked():
                X = 'X4' ; Y = 'Y4'
            else:
                X = False ; Y = False
            return X, Y
        return False, False

    def getColorMapRadioButton(self, two=None):
        '''Returns the filename associated to the color map radio button'''
        logger.debug( "getColorMapRadioButton")
        if   self.rBColor_Jet.isChecked():
            colorfile = 'jet.txt'; otherfile = 'hot.txt'
        elif self.rBColor_Hot.isChecked():
            colorfile = 'hot.txt'; otherfile = 'hsv.txt'
        elif self.rBColor_HSV.isChecked():
            colorfile = 'hsv.txt'; otherfile = 'cool.txt'
        elif self.rBColor_Cool.isChecked():
            colorfile = 'cool.txt'; otherfile = 'jet.txt'
        else: # gray is checked
            colorfile =  None; otherfile = 'hot.txt'
        if two:
            return colorfile, otherfile
        return colorfile
    


#    def getLockCross(self):
#        logger.debug( "locked? %s", self.lockCross.isChecked() )
#        return self.lockCross.isChecked()

    def handleShowHide(self):
        logger.debug( "handleShowHide called %s %s", self.X1Position.text(), self.Y1Position.text() )
        i = self.getSelectedCross()
        if self.getShowCross():
            X, Y = self.getSpecificCrossValue()
            if X and Y:
                self.handleCrossText(X); self.handleCrossText(Y)
        self.viewer[self.cam_n].showCross[i] = self.getShowCross()
        logger.debug( "handleShowHide called %s %s", self.getShowCross() )

    def handleColorButton(self):
        i = self.getSelectedCross()
        newcolor = QColorDialog().getColor( self.viewer[self.cam_n].colors[i] )
        #print newcolor.getRgb(), newcolor.isValid()
        if newcolor.isValid():
            self.viewer[self.cam_n].colors[i]  = newcolor
            self.viewer[self.cam_n].updateRdColors()

    def handleCrosses(self):
        ''' Handle crosses sends to ViewerFrame[cam_n] the current status 
            of cross check boxes.''' 
        logger.debug( "handleCrosses %s", self.cam_n)
        
        self.viewer[self.cam_n].showCross = self.getShowCross()
    
    def handleCross_1(self):
        '''Mutual exclusive checkboxes'''
        logger.debug( "handleCross_1 %s", self.cam_n)
        self.cBcross_2.setChecked(False)
        self.cBcross_3.setChecked(False)
        self.cBcross_4.setChecked(False)
        self.handleCrosses()
        
    def handleCross_2(self):
        '''Mutual exclusive checkboxes'''
        logger.debug( "handleCross_2 %s", self.cam_n)
        self.cBcross_1.setChecked(False)
        self.cBcross_3.setChecked(False)
        self.cBcross_4.setChecked(False)
        self.handleCrosses()
        
    def handleCross_3(self):
        '''Mutual exclusive checkboxes'''
        logger.debug( "handleCross_3 %s", self.cam_n)
        self.cBcross_1.setChecked(False)
        self.cBcross_2.setChecked(False)
        self.cBcross_4.setChecked(False)
        self.handleCrosses()
        
    def handleCross_4(self):
        '''Mutual exclusive checkboxes'''
        logger.debug( "handleCross_4 %s", self.cam_n)
        self.cBcross_1.setChecked(False)
        self.cBcross_2.setChecked(False)
        self.cBcross_3.setChecked(False)
        self.handleCrosses()
    
    def handleLockCrosses(self):
        ''' Handle crosses sends to ViewerFrame[cam_n] the current status 
            of lock cross check boxes.''' 
        logger.debug( "handleLockCrosses %s", self.cam_n)
        self.viewer[self.cam_n].lockCross = self.getLockCross()

    def handleCrosses(self):
        ''' Handle crosses sends to ViewerFrame[cam_n] the current status 
            of crosses check boxes.''' 
        logger.debug( "handleCrosses %s", self.cam_n)
        self.viewer[self.cam_n].showCross = self.getShowCross()

    def handleCrossText(self,XY):
        logger.debug(' handleCrossText %s', XY )
        i = int(XY[1])-1
        translate = {
                'X1': self.X1Position, 'X2': self.X2Position, 'X3': self.X3Position, 'X4': self.X4Position,
                'Y1': self.Y1Position, 'Y2': self.Y2Position, 'Y3': self.Y3Position, 'Y4': self.Y4Position,}

        logger.debug( "handling it! %s : %g", XY,int(translate[XY].text()))

        if self.viewer[self.cam_n].lockCross[i]:
            logger.debug( "it's locked %g", i )
            if XY[0] == 'X':
                translate[XY].setText("{:0.0f}".format( self.viewer[self.cam_n].xpos[i] * self.viewer[self.cam_n].win_W ) )
            else:
                translate[XY].setText("{:0.0f}".format( self.viewer[self.cam_n].ypos[i] * self.viewer[self.cam_n].win_W ) )
        else:            
            if XY[0] == 'X':
                self.viewer[self.cam_n].xpos[ i ] = float(translate[XY].text()) / self.viewer[self.cam_n].win_W
            else:
                self.viewer[self.cam_n].ypos[ i ] = float(translate[XY].text()) / self.viewer[self.cam_n].win_H

        logger.debug( self.viewer[self.cam_n].xpos )
        logger.debug( self.viewer[self.cam_n].ypos )

    def settoolTips(self):
        self.pB_on.setToolTip('Reconnect Camera')
        #self.pB_save.setToolTip('Not implemented yet')
        self.pB_elog.setToolTip('Save Images to E-Log\nNot implemented yet')
        self.tB_mminus_1.setToolTip('Neg Lim\nNot implemented yet')
        self.tB_mminus_2.setToolTip('Neg Lim\nNot implemented yet')
        self.tB_mminus_3.setToolTip('Neg Lim\nNot implemented yet')
        self.tB_mminus_4.setToolTip('Neg Lim\nNot implemented yet')
        self.tB_mminus_5.setToolTip('Neg Lim\nNot implemented yet')
        self.tB_mminus_6.setToolTip('Neg Lim\nNot implemented yet')
        self.tB_mminus_7.setToolTip('Neg Lim\nNot implemented yet')
        self.tB_mplus_1.setToolTip('Pos Lim\nNot implemented yet')
        self.tB_mplus_2.setToolTip('Pos Lim\nNot implemented yet')
        self.tB_mplus_3.setToolTip('Pos Lim\nNot implemented yet')
        self.tB_mplus_4.setToolTip('Pos Lim\nNot implemented yet')
        self.tB_mplus_5.setToolTip('Pos Lim\nNot implemented yet')
        self.tB_mplus_6.setToolTip('Pos Lim\nNot implemented yet')
        self.tB_mplus_7.setToolTip('Pos Lim\nNot implemented yet')
        self.lE_mr_1.setToolTip('Relative Positon\nNot implemented yet')
        self.lE_mr_2.setToolTip('Relative Positon\nNot implemented yet')
        self.lE_mr_3.setToolTip('Relative Positon\nNot implemented yet')
        self.lE_mr_4.setToolTip('Relative Positon\nNot implemented yet')
        self.lE_mr_5.setToolTip('Relative Positon\nNot implemented yet')
        self.lE_mr_6.setToolTip('Relative Positon\nNot implemented yet')
        self.lE_mr_7.setToolTip('Relative Positon\nNot implemented yet')
        self.dW_Img_1.setToolTip('hold ALT to move this window')
        self.dW_Img_2.setToolTip('hold ALT to move this window')
        self.dW_Img_3.setToolTip('hold ALT to move this window')
        self.dW_Img_4.setToolTip('hold ALT to move this window')
        self.dW_Img_5.setToolTip('hold ALT to move this window')
        self.dW_Img_6.setToolTip('hold ALT to move this window')
        self.dW_Img_7.setToolTip('hold ALT to move this window')
        self.dW_Img_8.setToolTip('hold ALT to move this window')
        
    def updateCameraTitle(self,cam_n):
        '''Clear and set current camera selected with "*" character'''
        # first clear any *'s from the titles
        for i in range(self.n_cams):
            thisTitle = self.idock[i].windowTitle()
            if len(thisTitle) > 0 and thisTitle[-1] == '*':
                self.idock[i].setWindowTitle( self.idock[i].windowTitle()[:-1] )
        # then put a * on the currently selected title
        if len(self.idock[cam_n].windowTitle()) > 0:
            self.idock[cam_n].setWindowTitle( self.idock[cam_n].windowTitle() + "*" )

    def set_bin(self):
        if self.viewer[self.cam_n]:
            self.viewer[self.cam_n].controlling = True # gives the widget control to user
            self.viewer[self.cam_n].pvput(self.viewer[self.cam_n].Pv_BinX, int(self.lEBXY.text()))
            self.viewer[self.cam_n].pvput(self.viewer[self.cam_n].Pv_BinY, int(self.lEBXY.text()))
            self.viewer[self.cam_n].controlling = False # release the control
            
    def set_expt(self):
        return False
        if self.viewer[self.cam_n]:
            self.viewer[self.cam_n].controlling = True # gives the widget control to user
            self.viewer[self.cam_n].pvput(self.viewer[self.cam_n].Pv_Exposure, float(self.dS_expt.value()))
            self.viewer[self.cam_n].controlling = False # release the control
    
    def set_gain(self):
        return False
        if self.viewer[self.cam_n]:
            self.viewer[self.cam_n].controlling = True # gives the widget control to user
            self.viewer[self.cam_n].pvput(self.viewer[self.cam_n].Pv_Gain, int(self.iS_gain.value()))
            self.viewer[self.cam_n].controlling = False # release the control
             
    def set_expgain(self):
        if self.viewer[self.cam_n]:
            self.viewer[self.cam_n].controlling = True # gives the widget control to user
            self.viewer[self.cam_n].pvput(self.viewer[self.cam_n].Pv_Exposure, float(self.dS_expt.value()))
            self.viewer[self.cam_n].pvput(self.viewer[self.cam_n].Pv_Gain, int(self.iS_gain.value()))
            self.viewer[self.cam_n].controlling = False # release the control

    def onComboBoxScaleIndexChanged(self):
        logger.debug('onComboBoxScaleIndexChanged called')
        if self.viewer[self.cam_n]:
            self.viewer[self.cam_n].iScaleIndex = int(self.cBoxScale.currentIndex())
            self.viewer[self.cam_n].setColorMap(self.getColorMapRadioButton())
        
    def set_cool(self):
        self.setImageColorMap()
    
    def set_gray(self):
        self.setImageColorMap()
        
    def set_hsv(self):
        self.setImageColorMap()
    
    def set_hot(self):
        self.setImageColorMap()
    
    def set_jet(self):
        self.setImageColorMap()
        
    def setImageColorMap(self):
        if self.viewer[self.cam_n]:
            self.viewer[self.cam_n].setColorMap(self.getColorMapRadioButton())
                
    def onUpdateColorMap(self, cam_n):
        print 'WORKING ON THIS TOO...'
        return False
        
        if self.cfg == None:
            return False
        logger.debug( 'onUpdateColorMap called %g', cam_n )
        if self.viewer[cam_n].colorMap != self.colormap[cam_n]:
            self.viewer[cam_n].colorMap = self.colormap[cam_n]
            self.viewer[cam_n].setColorMap(self.getColorMapRadioButton())
        
    def onSliderRangeMinChanged(self, newSliderValue):
        if self.viewer[self.cam_n]:        
            self.iRangeMin = newSliderValue
            self.lERngMin.setText(str(self.iRangeMin))
            if self.iRangeMin > self.iRangeMax:
                self.hSRngMax.setValue(self.iRangeMin)
            if self.viewer[self.cam_n].colorMap != None:
                self.viewer[self.cam_n].setColorMap(self.getColorMapRadioButton())

    def onSliderRangeMaxChanged(self, newSliderValue):
        if self.viewer[self.cam_n]:
            self.iRangeMax = newSliderValue
            self.lERngMax.setText(str(self.iRangeMax))
            if self.iRangeMax < self.iRangeMin:
                self.hSRngMin.setValue(self.iRangeMax)
            if self.viewer[self.cam_n].colorMap != None:
                self.viewer[self.cam_n].setColorMap(self.getColorMapRadioButton())

    def onRangeMinTextEnter(self):
        try:    value = int(self.lERngMin.text())
        except: value = 0
        if value <    0 : value =    0
        if value > 1023 : value = 1023
        self.hSRngMin.setValue(value)

    def onRangeMaxTextEnter(self):
        try:    value = int(self.lERngMax.text())
        except: value = 0
        if value <    0 : value =    0
        if value > 1023 : value = 1023
        self.hSRngMax.setValue(value)
        
    def setSliderRangeMax(self, maxbits):
        self.hSRngMin.setMaximum((     1 << maxbits) - 1)
        self.hSRngMin.setTickInterval((1 << maxbits) / 4)
        self.hSRngMax.setMaximum((     1 << maxbits) - 1)
        self.hSRngMax.setTickInterval((1 << maxbits) / 4)
        
    def onCheckGrayScale(self):
        status = int(self.cBgrayScale.isChecked())
        self.viewer[self.cam_n].onCheckGrayUpdate(status)
                
    def onCamera(self):
        if self.iocmod[self.cam_n] and self.viewer[self.cam_n]:
            #self.viewer[self.cam_n].connectCamera() # FIXME: not working yet
            pass
            

    def onUpdateRate(self, cam_n, dispRate, dataRate): 
        if self.cam_n == cam_n:
            #print 'onUpdateRate[%d][%d]' % (self.cam_n, cam_n), dispRate, dataRate
            self.lb_dispRate.setText('%.1f Hz' % dispRate)
            self.lb_dataRate.setText('%.1f Hz' % dataRate)

    def onCheckPress(self):
        # implement a stack to ensure that only 2 checkboxes are checked.
        # dump the oldest (first) one, and append the new one to the end of the stack
        # could be changed from 2 if more calculation boxes are added
        #logger.debug( 'onCheckPress called prima %s %s', self.X1Position.text(), self.Y1Position.text() )
        newchecked = [ i for i,x in enumerate(self.check_box) if x.isChecked() ]
        # now check if diagonal boxes are checked, and if so uncheck them
        toremove = []
        check_stack = list(self.viewer[self.cam_n].check_stack)
        for s in newchecked:
            if s in [0,5,10,15]:
                toremove.append(s)
                self.check_box[s].setCheckState(0)
                logger.debug( "no measuring of distance to self." )
        for t in toremove:
            newchecked.remove(t)
        if set(newchecked) > set(check_stack):
            # user has added another check
            for s in newchecked:
                if s not in check_stack:
                    check_stack.append(s)
            if len(check_stack) > 2:
                self.check_box[check_stack[0]].setCheckState(0)
                check_stack = check_stack[1:]
        else:
            # the user has unchecked a box, we have to remove it from the stack
            for sc in check_stack:
                if sc not in newchecked:
                    check_stack.remove(sc)
        self.viewer[self.cam_n].check_stack = list(check_stack)
        
        #if DEBUG:
            #print "checkbox pressed" , repr( check_stack )

        # do calculation of distances
        for i, sc in enumerate(check_stack):
            #if DEBUG:
                #print "begin calculation", sc
            D, rel = self.calcMarkerDist(sc)
            if D != None :
                self.dist_val[i].setText("{:0.1f}".format( D ) )
                self.from_val[i].setText("{:0.0f},{:0.0f}".format( rel[0]+1, rel[1]+1 ))
            else:
                self.dist_val[i].setText("")
                self.from_val[i].setText("")
                
        if len(check_stack) < 2:
            self.dist_val[1].setText("")
            self.from_val[1].setText("")
        if len(check_stack) < 1:
            self.dist_val[0].setText("")
            self.from_val[0].setText("")
            
        return True

    def calcMarkerDist(self,sc):
        translate = {
             0:(0,0),    4:(0,1),    8:(0,2),   12:(0,3),
             1:(1,0),    5:(1,1),    9:(1,2),   13:(1,3),
             2:(2,0),    6:(2,1),   10:(2,2),   14:(2,3),
             3:(3,0),    7:(3,1),   11:(3,2),   15:(3,3), }
        x1 = self.xPos_val[ translate[ sc ][0] ].text()
        x2 = self.xPos_val[ translate[ sc ][1] ].text()
        y1 = self.yPos_val[ translate[ sc ][0] ].text()
        y2 = self.yPos_val[ translate[ sc ][1] ].text()
        D = None
        if not '' in [x1,x2,y1,y2]:
            D = math.sqrt( (float(x2)-float(x1))**2 + (float(y2)-float(y1))**2 )
        return D, translate[sc]
    
    def onUpdateCamPv(self, position):
        '''Update camera position settings with the new cam Pvs'''
        # here should enter the new settings
        print 'Updating CAM %d settings'% position
        self.onEnableCam(position)

    def onUpdateIocPv(self, position):
        '''Update camera position settings with the new ioc Pvs'''
        # here should enter the new settings
        print 'Updating IOC_PV %d settings'% position
        self.onEnableCam(position)
        
    def onUpdateMMSPv(self, position):
        '''Update motor position settings with the new mms Pvs'''
        # here should enter the new settings
        print 'Updating MMS_PV %d settings'% position
        print 'To be implemented...'

    def onEnableCam(self, position):
        '''Enable camera connection monitors and single viewer'''
        if self.cB_oncams[position].isChecked():
            print 'Connect CAM %d and monitors to specific location' % position
        else:
            print 'Disconnect CAM %d and monitors to specific location' % position
        
                
    def readPVListFile(self, filename=None):
        ''' Reads camera.lst file, update camera combo, etc...
        # ---------------------------------------------------------------
        # MultiViewer Description File
        # ---------------------------------------------------------------
        # Syntax:
        #   <TYPE>, <PVNAME|IOCNAME>, <DESC> # some_more_comments
        # Where:
        #   <Type>    : "GIG" -> GigE Cameras or
        #               "MMS" -> Motor or
        #               "IOC" -> Server name
        #   <PVNAME>  : Camera PV Name to display in the display
        #   <IOCNAME> : Server name associated to restart button
        #   <DESC>    : User Camera or Server description
        # Notes:
        #   PVNAME or IOCNAME are not case sensitive.
        #   Line can be commented out by starting with '#' character.
        # ---------------------------------------------------------------
        '''
        self.lCameraList = []
        self.lCameraDesc = []
        self.lMotorList  = []
        self.lMotorDesc  = []
        self.lIOCList    = []
        self.lIOCDesc    = []
        self.basename    = list()
        self.camtypes    = list()
        self.mottypes    = list()
        iCamera = -1
        iMotor  = -1
        iIOC    = -1
        try:
          if filename != None:
              fnCameraList = filename
          else:
            if (self.camerListFilename[0] == '/'):
              fnCameraList = self.camerListFilename
            else:
              fnCameraList = self.cwd + "/" + self.camerListFilename
          lCameraListLine = open( fnCameraList,"r").readlines()      
          self.lCameraList = []
          
          for line in lCameraListLine:
            line = line.lstrip()
            if not line:
                continue
            if line.startswith("#"):
              continue
            if line.startswith("GIG"):
                iCamera += 1
                self.cam_n = iCamera
    
                lsLine = line.split(",")
                if len(lsLine) < 2:
                    print throw("")
                
                sCameraPv = lsLine[1].strip()
                if len(lsLine) >= 3:
                  sCameraDesc = lsLine[2].strip().split('#')[0].rstrip()
                else:
                  sCameraDesc = sCameraPv
                  
                self.lCameraList.append(sCameraPv)
                self.lCameraDesc.append(sCameraDesc)
                self.camtypes.append(lsLine[0].strip())
    
                print 'Cam[%d] %s ' % (iCamera, sCameraDesc),
                self.basename.append(sCameraPv)
                print 'Pv ',
    
                print sCameraPv                
                
            elif line.startswith("MM"):
                iMotor += 1
                self.mot_n = iMotor
                
                lsLine = line.split(",")
                if len(lsLine) < 2:
                    print throw("")
                
                sMotorPv = lsLine[1].strip()
                if len(lsLine) >= 3:
                  sMotorDesc = lsLine[2].strip().split('#')[0]
                else:
                  sMotorDesc = sMotorPv
                  
                self.lMotorList.append(sMotorPv)
                self.lMotorDesc.append(sMotorDesc)
                #logger.debug( 'Motor PV>> %s Description>> %s', sMotorPv, sMotorDesc )
                        
                self.cB_onmot[iMotor].setText(sMotorPv)
                self.cB_onmot[iMotor].setChecked(True)
                self.mottypes.append(lsLine[0].strip())
                print 'Mot[%d] %s ' % (iMotor, sMotorDesc), sMotorPv
            elif line.startswith("IOC"):
                iIOC += 1
                lsLine = line.split(",")
                if len(lsLine) < 2:
                    print throw("")
                
                sIOC = lsLine[1].strip()
                #sIOC = sIOC.replace(':','-').lower()
                
                if len(lsLine) >= 3:
                  sIOCDesc = lsLine[2].strip().split('#')[0]
                else:
                  sIOCDesc = sIOC
                
                self.lIOCList.append(sIOC)
                self.lIOCDesc.append(sIOCDesc)
                
                #self.tB_reset[iIOC].setToolTip(sIOC)
                
                print 'IOC[%d] %s ' % (iIOC, sIOCDesc), sIOC
                
            else:
                continue
        except:
            #import traceback
            #traceback.print_exc(file=sys.stdout)
            print '!! Failed to read motor pv list from \"%s\"' % fnCameraList
            return 0
        return iCamera + 1

            
    def snd_cmd(self, cam_n, pv, val):
        self.ca[cam_n].set_cmd(pv, val)
        self._cathreadstart(cam_n)
    
    def _cathreadstart(self, cam_n):
        if self.ca[cam_n].isRunning():
            self.ca[cam_n].stop()
        self.ca[cam_n].wait()
        self.ca[cam_n].start()
        
    def _cathreadstop(self):
        if self.ca[cam_n].isRunning():
            self.ca[cam_n].stop()
    
#    def dumpCamList(self):
#        if self.setupvals == []:
#            return False
#        # enumerate
#        cam, camdesc, ioc, cen, mms, mmsdesc, men = (0,1,2,3,4,5,6)
#        # shortcuts
#        camPv = self.setupvals[cam]; camPvdesc = self.setupvals[camdesc]
#        iocPv = self.setupvals[ioc]; cen       = self.setupvals[cen]
#        mmsPv = self.setupvals[mms]; mmsPvdesc = self.setupvals[mmsdesc]
#        men   = self.setupvals[men]
#        
#        # assign to additional shortcuts
#        camPv1 = camPv[0].text(); camPvDesc1 = camPvdesc[0].text()
#        camPv2 = camPv[1].text(); camPvDesc2 = camPvdesc[1].text()
#        camPv3 = camPv[2].text(); camPvDesc3 = camPvdesc[2].text()
#        camPv4 = camPv[3].text(); camPvDesc4 = camPvdesc[3].text()
#        camPv5 = camPv[4].text(); camPvDesc5 = camPvdesc[4].text()
#        camPv6 = camPv[5].text(); camPvDesc6 = camPvdesc[5].text()
#        camPv7 = camPv[6].text(); camPvDesc7 = camPvdesc[6].text()
#        camPv8 = camPv[7].text(); camPvDesc8 = camPvdesc[7].text()
#        
#        iocPv1 = iocPv[0].text(); camEn1 = '' if cen[0].isChecked() else '#'
#        iocPv2 = iocPv[1].text(); camEn2 = '' if cen[1].isChecked() else '#'
#        iocPv3 = iocPv[2].text(); camEn3 = '' if cen[2].isChecked() else '#'
#        iocPv4 = iocPv[3].text(); camEn4 = '' if cen[3].isChecked() else '#'
#        iocPv5 = iocPv[4].text(); camEn5 = '' if cen[4].isChecked() else '#'
#        iocPv6 = iocPv[5].text(); camEn6 = '' if cen[5].isChecked() else '#'
#        iocPv7 = iocPv[6].text(); camEn7 = '' if cen[6].isChecked() else '#'
#        iocPv8 = iocPv[7].text(); camEn8 = '' if cen[7].isChecked() else '#'
#        
#        mmsPv1 = mmsPv[0].text(); mmsPvDesc1 = mmsPvdesc[0].text()
#        mmsPv2 = mmsPv[1].text(); mmsPvDesc2 = mmsPvdesc[1].text()
#        mmsPv3 = mmsPv[2].text(); mmsPvDesc3 = mmsPvdesc[2].text()
#        mmsPv4 = mmsPv[3].text(); mmsPvDesc4 = mmsPvdesc[3].text()
#        mmsPv5 = mmsPv[4].text(); mmsPvDesc5 = mmsPvdesc[4].text()
#        mmsPv6 = mmsPv[5].text(); mmsPvDesc6 = mmsPvdesc[5].text()
#        mmsPv7 = mmsPv[6].text(); mmsPvDesc7 = mmsPvdesc[6].text()
#        mmsPv8 = mmsPv[7].text(); mmsPvDesc8 = mmsPvdesc[7].text()
#        
#        mmsEn1 = '' if men[0].isChecked() else '#'
#        mmsEn2 = '' if men[1].isChecked() else '#'
#        mmsEn3 = '' if men[2].isChecked() else '#'
#        mmsEn4 = '' if men[3].isChecked() else '#'
#        mmsEn5 = '' if men[4].isChecked() else '#'
#        mmsEn6 = '' if men[5].isChecked() else '#'
#        mmsEn7 = '' if men[6].isChecked() else '#'
#        mmsEn8 = '' if men[7].isChecked() else '#'
#        
#        # Write to file cameras.lst
#        f = open(self.cfgdir + 'cameras.lst', "w")
#        f.write("\n")
#        f.write(''
#'# ---------------------------------------------------------------\n'
#'# MultiViewer Description File (Generated by Setup Dialog)\n'
#'# ---------------------------------------------------------------\n'
#'# Syntax:\n'
#'#   <TYPE>, <PVNAME|IOCNAME>, <DESC> # some_more_comments\n'
#'# Where:\n'
#'#   <Type>    : "GIG" -> GigE Cameras or\n'
#'#               "IOC" -> Server name\n'
#'#               "MMS" -> Motor or\n'
#'#   <PVNAME>  : Camera PV Name to display in the display\n'
#'#   <IOCNAME> : Server name associated to restart button\n'
#'#   <DESC>    : User Camera or Server description\n'
#'# Notes:\n'
#'#   PVNAME or IOCNAME are not case sensitive.\n'
#'#   Line can be commented out by starting with \'#\' character.\n'
#'# ---------------------------------------------------------------\n\n')
#        f.write('# CAMERA PV NAMES (located in the cfg file, \'CAM\' variable):\n')
#        f.write('%sGIG, %s, %s \t #\n' % (camEn1, camPv1, camPvDesc1))
#        f.write('%sGIG, %s, %s \t #\n' % (camEn2, camPv2, camPvDesc2))
#        f.write('%sGIG, %s, %s \t #\n' % (camEn3, camPv3, camPvDesc3))
#        f.write('%sGIG, %s, %s \t #\n' % (camEn4, camPv4, camPvDesc4))
#        f.write('%sGIG, %s, %s \t #\n' % (camEn5, camPv5, camPvDesc5))
#        f.write('%sGIG, %s, %s \t #\n' % (camEn6, camPv6, camPvDesc6))
#        f.write('%sGIG, %s, %s \t #\n' % (camEn7, camPv7, camPvDesc7))
#        f.write('%sGIG, %s, %s \t #\n' % (camEn8, camPv8, camPvDesc8))
#        f.write('\n')
#        f.write('# IOC PV NAMES (located in the cfg file, \'IOC_PV\' variable):)\n')
#        f.write('%sIOC, %s, %s \t #\n' % (camEn1, iocPv1, camPvDesc1))
#        f.write('%sIOC, %s, %s \t #\n' % (camEn2, iocPv2, camPvDesc2))
#        f.write('%sIOC, %s, %s \t #\n' % (camEn3, iocPv3, camPvDesc3))
#        f.write('%sIOC, %s, %s \t #\n' % (camEn4, iocPv4, camPvDesc4))
#        f.write('%sIOC, %s, %s \t #\n' % (camEn5, iocPv5, camPvDesc5))
#        f.write('%sIOC, %s, %s \t #\n' % (camEn6, iocPv6, camPvDesc6))
#        f.write('%sIOC, %s, %s \t #\n' % (camEn7, iocPv7, camPvDesc7))
#        f.write('%sIOC, %s, %s \t #\n' % (camEn8, iocPv8, camPvDesc8))
#        f.write('\n')
#        f.write('# MOTOR PV NAMES:\n')
#        f.write('%sMMS, %s, %s \t #\n' % (mmsEn1, mmsPv1, mmsPvDesc1))
#        f.write('%sMMS, %s, %s \t #\n' % (mmsEn2, mmsPv2, mmsPvDesc2))
#        f.write('%sMMS, %s, %s \t #\n' % (mmsEn3, mmsPv3, mmsPvDesc3))
#        f.write('%sMMS, %s, %s \t #\n' % (mmsEn4, mmsPv4, mmsPvDesc4))
#        f.write('%sMMS, %s, %s \t #\n' % (mmsEn5, mmsPv5, mmsPvDesc5))
#        f.write('%sMMS, %s, %s \t #\n' % (mmsEn6, mmsPv6, mmsPvDesc6))
#        f.write('%sMMS, %s, %s \t #\n' % (mmsEn7, mmsPv7, mmsPvDesc7))
#        f.write('%sMMS, %s, %s \t #\n' % (mmsEn8, mmsPv8, mmsPvDesc8))
#        f.close()
        
    def dumpConfig(self, cam_n):
        '''Dump the current camera gui settings in a config file located in the
           ~/.mviewer directory under cameraPv filename.
           Should be called when: 
           1/ Change current camera settings (like click on the image)
           2/ Change any setting (may not...necessary)
           3/ Exit the program (by the quit button or closing the window)
        '''

        if self.cfg != None or not self.EnableDumpConfig:
            return False
        cameraBase = str(self.lCameraList[cam_n])
        if cameraBase == "":
            return
        if self.viewer[cam_n] != None:
            if self.viewer[cam_n].Pv_ArrayData[Glob.pv] != None:
                #logger.debug('dumpConfig called')
                f = open(self.cfgdir + cameraBase.lower().replace(':','_'), "w")
                # Radio Buttons:
                f.write("rBColor_Jet        " + str(int(self.rBColor_Jet.isChecked()))    + "\n")
                f.write("rBColor_Hot        " + str(int(self.rBColor_Hot.isChecked()))    + "\n")
                f.write("rBColor_HSV        " + str(int(self.rBColor_HSV.isChecked()))    + "\n")
                f.write("rBColor_Gray       " + str(int(self.rBColor_Gray.isChecked()))   + "\n")
                f.write("rBColor_Cool       " + str(int(self.rBColor_Cool.isChecked()))   + "\n")
                # Combo Boxes:
                f.write("cBoxScale          " + str(int(self.cBoxScale.currentIndex()))+ "\n")
                # Check Boxes:
                f.write("cBgrayScale        " + str(int(self.cBgrayScale.isChecked())) + "\n")
                f.write("cBcross_1          " + str(int(self.cBcross_1.isChecked()))   + "\n")
                f.write("cBcross_2          " + str(int(self.cBcross_2.isChecked()))   + "\n")
                f.write("cBcross_3          " + str(int(self.cBcross_3.isChecked()))   + "\n")
                f.write("cBcross_4          " + str(int(self.cBcross_4.isChecked()))   + "\n")
                f.write("cBlock_1           " + str(int(self.cBlock_1.isChecked()))    + "\n")
                f.write("cBlock_2           " + str(int(self.cBlock_2.isChecked()))    + "\n")
                f.write("cBlock_3           " + str(int(self.cBlock_3.isChecked()))    + "\n")
                f.write("cBlock_4           " + str(int(self.cBlock_4.isChecked()))    + "\n")
                f.write("checkBox21         " + str(int(self.checkBox21.isChecked()))  + "\n")
                f.write("checkBox23         " + str(int(self.checkBox23.isChecked()))  + "\n")
                f.write("checkBox24         " + str(int(self.checkBox24.isChecked()))  + "\n")
                f.write("checkBox31         " + str(int(self.checkBox31.isChecked()))  + "\n")
                f.write("checkBox32         " + str(int(self.checkBox32.isChecked()))  + "\n")
                f.write("checkBox34         " + str(int(self.checkBox34.isChecked()))  + "\n")
                f.write("checkBox41         " + str(int(self.checkBox41.isChecked()))  + "\n")
                f.write("checkBox42         " + str(int(self.checkBox42.isChecked()))  + "\n")
                f.write("checkBox43         " + str(int(self.checkBox43.isChecked()))  + "\n")
                # Line Edits:
                f.write("lERngMin           " + self.lERngMin.text()                   + "\n")
                f.write("lERngMax           " + self.lERngMax.text()                   + "\n")
                f.write("TimerLabel         " + self.lCameraDesc[cam_n]                + "\n")
                f.write("X1Position         " + self.X1Position.text()                 + "\n")
                f.write("Y1Position         " + self.Y1Position.text()                 + "\n")
                f.write("X2Position         " + self.X2Position.text()                 + "\n")
                f.write("Y2Position         " + self.Y2Position.text()                 + "\n")
                f.write("X3Position         " + self.X3Position.text()                 + "\n")
                f.write("Y3Position         " + self.Y3Position.text()                 + "\n")
                f.write("X4Position         " + self.X4Position.text()                 + "\n")
                f.write("Y4Position         " + self.Y4Position.text()                 + "\n")
                f.close()
          

    def getConfig(self, cam_n):
        '''Retrieves the non EPICS variables and camera settings from the last
            time the user call the program.
            Should be called at the first time the camera is selected after 
            program started.
        '''
        #logger.debug( 'getConfig called [CAM%d]' , self.cam_n )
        cameraBase = str(self.lCameraList[cam_n])
        if cameraBase == "":
          return
        self.cfg = cfginfo()
        if self.cfg.read(self.cfgdir + cameraBase.lower().replace(':','_')):
            # Persistent Gui Widgets:
            # Radio Buttons:
            self.rBColor_Jet.setChecked(int(self.cfg.rBColor_Jet))
            self.rBColor_Hot.setChecked(int(self.cfg.rBColor_Hot))
            self.rBColor_HSV.setChecked(int(self.cfg.rBColor_HSV))
            self.rBColor_Gray.setChecked(int(self.cfg.rBColor_Gray))
            self.rBColor_Cool.setChecked(int(self.cfg.rBColor_Cool))
            # Combo Boxes:
            self.cBoxScale.setCurrentIndex(int(self.cfg.cBoxScale))
            # Check Boxes:
            self.cBgrayScale.setChecked(bool(self.cfg.cBgrayScale))
            self.cBcross_1.setChecked(int(self.cfg.cBcross_1))
            self.cBcross_2.setChecked(int(self.cfg.cBcross_2))
            self.cBcross_3.setChecked(int(self.cfg.cBcross_3))
            self.cBcross_4.setChecked(int(self.cfg.cBcross_4))
            self.cBlock_1.setChecked(int(self.cfg.cBlock_1))
            self.cBlock_2.setChecked(int(self.cfg.cBlock_2))
            self.cBlock_3.setChecked(int(self.cfg.cBlock_3))
            self.cBlock_4.setChecked(int(self.cfg.cBlock_4))
            self.checkBox21.setChecked(int(self.cfg.checkBox21))
            self.checkBox23.setChecked(int(self.cfg.checkBox23))
            self.checkBox24.setChecked(int(self.cfg.checkBox24))
            self.checkBox31.setChecked(int(self.cfg.checkBox31))
            self.checkBox32.setChecked(int(self.cfg.checkBox32))
            self.checkBox34.setChecked(int(self.cfg.checkBox34))
            self.checkBox41.setChecked(int(self.cfg.checkBox41))
            self.checkBox42.setChecked(int(self.cfg.checkBox42))
            self.checkBox43.setChecked(int(self.cfg.checkBox43))
            # Line Edits:
            self.lERngMin.setText(str(self.cfg.lERngMin))
            self.lERngMax.setText(str(self.cfg.lERngMax))
            self.TimerLabel.setText(str(' '.join(self.cfg.TimerLabel)))
            self.X1Position.setText(str(self.cfg.X1Position))
            self.Y1Position.setText(str(self.cfg.Y1Position))
            self.X2Position.setText(str(self.cfg.X2Position))
            self.Y2Position.setText(str(self.cfg.Y2Position))
            self.X3Position.setText(str(self.cfg.X3Position))
            self.Y3Position.setText(str(self.cfg.Y3Position))
            self.X4Position.setText(str(self.cfg.X4Position))
            self.Y4Position.setText(str(self.cfg.Y4Position))
            
            self.onRangeMinTextEnter()
            self.onRangeMaxTextEnter()

        else:
          pass
        self.cfg = None
        
    def shutdown(self):
        print 'len(self.viewer)', len(self.viewer)
        for i in range(len(self.viewer)):
            if self.viewer[i]:
                self.viewer[i].disconnectCamera()
        #time.sleep(5)
        # FIXME: make sure that all thread are finished before close the app
        self.close()
        
    def centerDock(self, floating=False):
        if floating:
            half_width  = self.sender().width()  / 2
            half_height = self.sender().height() / 2
            dockcenter = QtCore.QPoint(half_width, half_height)
            self.sender().move(self.geometry().center() - dockcenter)
        self.repaint()
        
    def resetIOC(self):
        if self.sender() == self.pB_resetioc:
            try:
                if self.lIOCList[self.cam_n]:
                    reset = '%s:SYSRESET 1' % self.lIOCList[self.cam_n]
            except:
                reset = 'ERROR: IOC Pv name not defined in lst file'
        print reset
        #self.snd_cmd(0, reset)
        return True
        
    def mytest(self, word):
        print "{:s} does nothing".format(word)
        pass

