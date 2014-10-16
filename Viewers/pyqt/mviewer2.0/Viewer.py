import math
import time
import logging

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import QTimer, QObject #, Qt, QPoint, QPointF, QSize, QRectF, QObject
from PyQt4.Qt import QColorDialog

from utils import *
from SplashScreen import SplashScreen
from ViewerFrame import ViewerFrame

logger = logging.getLogger('mviewer.Viewer')

MAX_MOT = 7

form_class, base_class = uic.loadUiType('ui/mviewer2.8.ui')

class Viewer(QtGui.QMainWindow, form_class):    
    '''Display multiple gigE cameras in a single application'''
    def __init__(self, app, cwd, instrument, camLstFname, cfgdir, parent=None):
        super(Viewer, self).__init__(parent)
        #QtGui.QWidget.__init__(self)
        self.setupUi(self)
        
        self.splashScreen = SplashScreen()
#        self.setGeometry(QtCore.QRect(self.width()/2-10, self.height()/2-10,
#                                      self.width()/2+10, self.height()/2+10))
        self.splashScreen.showMsg("Starting Aplication...")
        #time.sleep(0.5)

        self.app        = app
        self.cwd        = cwd
        self.instrument = instrument
        self.camerListFilename  = camLstFname
        self.cfgdir     = cfgdir
        self.cfg        = None
        self.iScaleIndex= False
        self.ioc1       = None # server for cams 1-4
        self.ioc2       = None # server for cams 5-8
        
        #layout = 
        #layout = QtGui.QGridLayout(self)
        #self.setLayout(layout)
        
        self.ledoff     = QtGui.QPixmap('ui/led-off-22x22.png')
        self.ledon      = QtGui.QPixmap('ui/led-red-22x22.png')
        self.limitoff  = QtGui.QPixmap('ui/led-off-16x16.png')
        self.limiton   = QtGui.QPixmap('ui/led-red-16x16.png')
        self.viewer     = [None for i in range(8)]
        self.ca         = [None for i in range(8)]
        self.colormap   = [None for i in range(8)]
        self.camlabel   = [''   for i in range(8)]
        self.cam_n      = 0  # Default: controls starts by first camera
        self.mot_n      = 0  # motor index
        self.last_cam_n = 0    
        self.iocmod     = [True  for i in range(8)] # default: uses CA
        self.ipmod      = [False for i in range(8)]
        
        
        self.w_Img = [self.w_Img_1, self.w_Img_2, self.w_Img_3, self.w_Img_4,
                      self.w_Img_5, self.w_Img_6, self.w_Img_7, self.w_Img_8]
        
        self.idock = [self.dW_Img_1,self.dW_Img_2,self.dW_Img_3,self.dW_Img_4,
                       self.dW_Img_5,self.dW_Img_6,self.dW_Img_7,self.dW_Img_8]
        
        self.lb_limM = [self.lb_limM_1, self.lb_limM_2, self.lb_limM_3,
                        self.lb_limM_4, self.lb_limM_5, self.lb_limM_6,
                        self.lb_limM_7]

        self.lb_limP = [self.lb_limP_1, self.lb_limP_2, self.lb_limP_3,
                        self.lb_limP_4, self.lb_limP_5, self.lb_limP_6,
                        self.lb_limP_7]
        
        self.lE_mr = [self.lE_mr_1, self.lE_mr_2, self.lE_mr_3,
                        self.lE_mr_4, self.lE_mr_5, self.lE_mr_6,
                        self.lE_mr_7]

        self.tB_mminus = [self.tB_mminus_1, self.tB_mminus_2, self.tB_mminus_3,
                        self.tB_mminus_4, self.tB_mminus_5, self.tB_mminus_6,
                        self.tB_mminus_7]

        self.tB_mplus = [self.tB_mplus_1, self.tB_mplus_2, self.tB_mplus_3,
                        self.tB_mplus_4, self.tB_mplus_5, self.tB_mplus_6,
                        self.tB_mplus_7]  
              
        self.cB_onmot = [self.cB_onmot_1, self.cB_onmot_2, self.cB_onmot_3,
                        self.cB_onmot_4, self.cB_onmot_5, self.cB_onmot_6,
                        self.cB_onmot_7]

        self.xPos_val = [self.X1Position, self.X2Position, self.X3Position, self.X4Position]

        self.yPos_val = [self.Y1Position, self.Y2Position, self.Y3Position, self.Y4Position]

        self.rd_cross = [self.Cross1, self.Cross2, self.Cross3, self.Cross4]
        self.rd_line  = [self.rd_line1, self.rd_line2, self.rd_line3, self.rd_line4]

        self.dist_val = [self.Distance1, self.Distance2]

        self.from_val = [self.From1, self.From2]

        self.check_box = [
                self.checkBox11, self.checkBox12, self.checkBox13, self.checkBox14,
                self.checkBox21, self.checkBox22, self.checkBox23, self.checkBox24,
                self.checkBox31, self.checkBox32, self.checkBox33, self.checkBox34,
                self.checkBox41, self.checkBox42, self.checkBox43, self.checkBox44,
                ]
        
        #self.tB_reset = [self.tB_reset_1, self.tB_reset_2]

        self.lb_ImStats = [self.lb_minValdata, self.lb_maxValdata]

        self.timers = [self.Timer1, self.Timer2, self.Timer3, self.Timer4, 
                self.Timer5, self.Timer6, self.Timer7, self.Timer8 ]

        self.timerKeepers = 8 * [ QTimer(), ]

        self.timerlabels = [self.TimerLabel1, self.TimerLabel2, self.TimerLabel3, self.TimerLabel4,
                self.TimerLabel5, self.TimerLabel6, self.TimerLabel7, self.TimerLabel8 ]

        self.timerreset9 =  [self.ResetTimer9h1, self.ResetTimer9h2, self.ResetTimer9h3, self.ResetTimer9h4,
                self.ResetTimer9h5, self.ResetTimer9h6, self.ResetTimer9h7, self.ResetTimer9h8]

        self.timerclear = [self.TimerClear1, self.TimerClear2, self.TimerClear3, self.TimerClear4,
                self.TimerClear5, self.TimerClear6, self.TimerClear7,self.TimerClear8]

        self.timerreset1 = [self.ResetTimer1h1, self.ResetTimer1h2, self.ResetTimer1h3, self.ResetTimer1h4,
                self.ResetTimer1h5, self.ResetTimer1h6, self.ResetTimer1h7, self.ResetTimer1h8]

        self.timerReferenceTime = 8*[None, ]

        self.lb_ImStats[0].setText('n/a')
        self.lb_ImStats[1].setText('n/a')
        
        for iMotor in range(MAX_MOT): 
            self.lb_limM[iMotor].setPixmap(self.limitoff)
            self.lb_limP[iMotor].setPixmap(self.limitoff)

        self.splashScreen.showMsg("Reading Camera File...")            

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
        sig8   = QtCore.SIGNAL("setCameraCombo(int)")
        sig9   = QtCore.SIGNAL("topLevelChanged(bool)")
        sig10  = QtCore.SIGNAL("released()")
        sig11  = QtCore.SIGNAL("timeout()")

        self.objc  , self.qsig  , self.sig0  , self.sig1  , self.sig2  , self.sig3  , self.sig4  , self.sig5  , self.sig6  , self.sig7  , self.sig8  , self.sig9  , self.sig10 , self.sig11 , = objc  , qsig  , sig0  , sig1  , sig2  , sig3  , sig4  , sig5  , sig6  , sig7  , sig8  , sig9  , sig10 , sig11 ,

        
        # Colormap controls: --------------------------------------
        #self.connect(self.cB_camera,    sig3, self.onCameraCombo)
        self.connect(self.cB_camera,    sig3, self.updateCamCombo)
        self.connect(self.cBoxScale,    sig3, self.onComboBoxScaleIndexChanged)
        self.connect(self.rBColor_Cool, sig0, self.set_cool)
        self.connect(self.rBColor_Gray, sig0, self.set_gray)
        self.connect(self.rBColor_HSV,  sig0, self.set_hsv)
        self.connect(self.rBColor_Hot,  sig0, self.set_hot)
        self.connect(self.rBColor_Jet,  sig0, self.set_jet)
        self.connect(self.hSRngMin,     sig2, self.onSliderRangeMinChanged )
        self.connect(self.hSRngMax,     sig2, self.onSliderRangeMaxChanged)
        self.connect(self.lERngMin,     sig5, self.onRangeMinTextEnter )
        self.connect(self.lERngMax,     sig5, self.onRangeMaxTextEnter)
        # --------------------------------------------------------
        self.connect(self.lEBXY,        sig5, self.set_bin)
        self.connect(self.dS_expt,      sig1, self.set_expt)
        self.connect(self.iS_gain,      sig2, self.set_gain)
        #self.connect(self.cB_on,        sig0, self.onCameraButton)
        self.connect(self.pB_on,        sig0, self.onCameraCombo)
        self.connect(self.grayScale,    sig0, self.onCheckGrayScale)
        self.connect(self.pB_quit,      sig0, self.shutdown)
        self.connect(self.pB_resetioc,  sig0, self.resetIOC)
        self.connect(self.pB_save,      sig0, lambda: self.mytest('save'))
        self.connect(self.pB_elog,      sig0, lambda: self.mytest('elog'))
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
        self.connect(self.showHideCross,sig10, self.handleShowHide)
        self.connect(self.Cross1,       sig10, self.handleRadio)
        self.connect(self.Cross2,       sig10, self.handleRadio)
        self.connect(self.Cross3,       sig10, self.handleRadio)
        self.connect(self.Cross4,       sig10, self.handleRadio)
        self.connect(self.lockCross,    sig10, self.handleLockCross)

        self.connect(self.X1Position,   sig5, lambda: self.handleCrossText('X1'))
        self.connect(self.X2Position,   sig5, lambda: self.handleCrossText('X2'))
        self.connect(self.X3Position,   sig5, lambda: self.handleCrossText('X3'))
        self.connect(self.X4Position,   sig5, lambda: self.handleCrossText('X4'))
        self.connect(self.Y1Position,   sig5, lambda: self.handleCrossText('Y1'))
        self.connect(self.Y2Position,   sig5, lambda: self.handleCrossText('Y2'))
        self.connect(self.Y3Position,   sig5, lambda: self.handleCrossText('Y3'))
        self.connect(self.Y4Position,   sig5, lambda: self.handleCrossText('Y4'))
       #
        self.connect(self.timerreset9[0], sig10, lambda: self.handleTimerReset(0,9) )
        self.connect(self.timerreset1[0], sig10, lambda: self.handleTimerReset(0,1) )
        self.connect( self.timerclear[0], sig10, lambda: self.handleTimerReset(0,0) )
        self.connect(self.timerKeepers[0],sig11,      lambda: self.updateTimer(0) )

        self.connect(self.timerreset9[1], sig10, lambda: self.handleTimerReset(1,9) )
        self.connect(self.timerreset1[1], sig10, lambda: self.handleTimerReset(1,1) )
        self.connect( self.timerclear[1], sig10, lambda: self.handleTimerReset(1,0) )
        self.connect(self.timerKeepers[1],sig11,      lambda: self.updateTimer(1) )

        self.connect(self.timerreset9[2], sig10, lambda: self.handleTimerReset(2,9) )
        self.connect(self.timerreset1[2], sig10, lambda: self.handleTimerReset(2,1) )
        self.connect( self.timerclear[2], sig10, lambda: self.handleTimerReset(2,0) )
        self.connect(self.timerKeepers[2],sig11,      lambda: self.updateTimer(2) )

        self.connect(self.timerreset9[3], sig10, lambda: self.handleTimerReset(3,9) )
        self.connect(self.timerreset1[3], sig10, lambda: self.handleTimerReset(3,1) )
        self.connect( self.timerclear[3], sig10, lambda: self.handleTimerReset(3,0) )
        self.connect(self.timerKeepers[3],sig11,      lambda: self.updateTimer(3) )

        self.connect(self.timerreset9[4], sig10, lambda: self.handleTimerReset(4,9) )
        self.connect(self.timerreset1[4], sig10, lambda: self.handleTimerReset(4,1) )
        self.connect( self.timerclear[4], sig10, lambda: self.handleTimerReset(4,0) )
        self.connect(self.timerKeepers[4],sig11,      lambda: self.updateTimer(4) )

        self.connect(self.timerreset9[5], sig10, lambda: self.handleTimerReset(5,9) )
        self.connect(self.timerreset1[5], sig10, lambda: self.handleTimerReset(5,1) )
        self.connect( self.timerclear[5], sig10, lambda: self.handleTimerReset(5,0) )
        self.connect(self.timerKeepers[5],sig11,      lambda: self.updateTimer(5) )

        self.connect(self.timerreset9[6], sig10, lambda: self.handleTimerReset(6,9) )
        self.connect(self.timerreset1[6], sig10, lambda: self.handleTimerReset(6,1) )
        self.connect( self.timerclear[6], sig10, lambda: self.handleTimerReset(6,0) )
        self.connect(self.timerKeepers[6],sig11,      lambda: self.updateTimer(6) )

        self.connect(self.timerreset9[7], sig10, lambda: self.handleTimerReset(7,9) )
        self.connect(self.timerreset1[7], sig10, lambda: self.handleTimerReset(7,1) )
        self.connect( self.timerclear[7], sig10, lambda: self.handleTimerReset(7,0) )
        self.connect(self.timerKeepers[7],sig11,      lambda: self.updateTimer(7) )

        #print dir (self.w_Img_1)#.sizePolicy.setHeightForWidth(True)
        #print dir(self.dW_Img_1.sizePolicy.setHeightForWidth)
        for iwdg in self.idock:
            iwdg.setEnabled(False)
            iwdg.setWindowTitle('')
        self.lock = [QtCore.QReadWriteLock() for i in range(8)]
        self.splashScreen.showMsg("Loading Cameras...")            
        refTime = int(time.time()) # throw away variable
        for i in range(self.n_cams):
            self.cam_n = i # update current camera
            self.idock[i].setEnabled(True)
            self.w_Img[i].setEnabled(True)
            if self.iocmod[i]:
                self.ca[i] = CAComm(self.lock[i], self.ctrlname[i], self)
                self.getConfig(i)
                self.viewer[i] = ViewerFrame(self.w_Img[i], self)
                self.viewer[i].onCameraSelect(i) # set camera pv and start display
                self.onUpdateColorMap(i)
                self.connect(self.viewer[i], self.sig6, self.onUpdateRate)
                self.connect(self.viewer[i], self.sig8, self.setCameraCombo)
                self.connect(self.idock[i],  self.sig9, self.centerDock)
                self.splashScreen.showMsg("Loading... %s as Cam[%d]" %\
                                                (self.lCameraDesc[i], i))
                self.setupTimer(i,refTime=refTime)
                time.sleep(1)            
        self.cam_n = 0
        self.settoolTips()




        # Destroy Splash once all are loaded
        if self.splashScreen:
            self.splashScreen.finish(self)

        self.centerOnScreen()
        self.setCameraCombo(0) # to update the selection indicator *
        self.show()


    def setupTimer(self, i,refTime=None,duration=9):
        logger.debug( "setup timer called %i"% i )
        self.timerlabels[i].setEnabled(True)
        self.timers[i].setEnabled(True)
        self.timerreset9[i].setEnabled(True)
        self.timerreset1[i].setEnabled(True)
        self.timerclear[i].setEnabled(True)
        self.timerlabels[i].setText( self.lCameraDesc[i] )
        self.handleTimerReset(i,duration)
        if not refTime:
            refTime = time.time()
        self.timerReferenceTime[i] = (refTime,duration*3600.)
        self.timerKeepers[i].start(1000)

    def handleTimerReset(self,cam_n, t):
        logger.debug( "timer reset %g %g", cam_n, t )
        #self.updateCamCombo()
        self.timers[cam_n].setText("{:02.0f}:00:00".format(t))
        self.timerReferenceTime[cam_n] = (time.time(),float(t)*3600.)
        logger.debug( "handleTimerReset %g %g %s", t, cam_n, self.viewer[cam_n] )
        if t > 0 and self.viewer[cam_n].camera is None :
            print "reconnecting", cam_n
            self.setCameraCombo(cam_n)
            self.viewer[cam_n].onCameraSelect(cam_n)
            self.viewer[cam_n].connectCamera( self.viewer[cam_n].cameraBase )
            #self.onUpdateColorMap(cam_n)
            self.viewer[cam_n].setColorMap()
            self.connect(self.viewer[cam_n], self.sig6, self.onUpdateRate)
            self.connect(self.viewer[cam_n], self.sig8, self.setCameraCombo)
            self.updateCameraTitle(cam_n)
        elif t == 0 and self.viewer[cam_n].camera is not None : 
            print "clearing Cam", cam_n
            self.setCameraCombo(cam_n)
            self.viewer[cam_n].clear()

    def updateTimer(self,cam_n):
        if self.timers[cam_n].isEnabled() and self.timerReferenceTime[cam_n]:
            ref, totalseconds = self.timerReferenceTime[cam_n]
            endTime = ref+totalseconds
            delta = int(endTime - time.time())
            if delta > 0:
                hours = delta / 3600
                minutes = (delta % 3600) / 60
                seconds = (delta % 3600) % 60
                #if DEBUG:
                #    print cam_n, ref, totalseconds, endTime, delta, hours, minutes, seconds
                self.timers[cam_n].setText("{:02.0f}:{:02.0f}:{:02.0f}".format(hours,minutes,seconds))
            else :
                hours = 0
                minutes = 0
                seconds = 0
                self.timers[cam_n].setText("{:02.0f}:{:02.0f}:{:02.0f}".format(hours,minutes,seconds))
                if self.viewer[cam_n].camera is not None :
                    self.setCameraCombo(cam_n)
                    self.viewer[cam_n].clear()
                #if DEBUG:
                #    print "camera", cam_n, "should be disabled"

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
        logger.debug( "checked? %s", self.showHideCross.isChecked() )
        return self.showHideCross.isChecked()

    def getLockCross(self):
        logger.debug( "locked? %s", self.lockCross.isChecked() )
        return self.lockCross.isChecked()


    def handleShowHide(self):
        i = self.getSelectedCross()
        self.viewer[self.cam_n].showCross[i] = self.getShowCross()

    def handleLockCross(self):
        i = self.getSelectedCross()
        self.viewer[self.cam_n].lockCross[i] = self.getLockCross()


    def handleColorButton(self):
        i = self.getSelectedCross()
        newcolor = QColorDialog().getColor( self.viewer[self.cam_n].colors[i] )
        #print newcolor.getRgb(), newcolor.isValid()
        if newcolor.isValid():
            self.viewer[self.cam_n].colors[i]  = newcolor
            self.viewer[self.cam_n].updateRdColors()

    def handleRadio(self):
        i = self.getSelectedCross()
        self.showHideCross.setChecked( self.viewer[self.cam_n].showCross[i] )
        self.lockCross.setChecked( self.viewer[self.cam_n].lockCross[i] )

    def handleCrossText(self,XY):
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
#        self.dW_Img_1.
#        self.dW_Img_2.
#        self.dW_Img_3.
#        self.dW_Img_4.
#        self.dW_Img_5.
#        self.dW_Img_6.
#        self.dW_Img_7.
#        self.dW_Img_8.

    def updateCamCombo(self):
        #print "update cam combo called from main gui"
        cam_n = self.cB_camera.currentIndex()
        self.cam_n = cam_n
        #self.setCameraCombo( cam_n )
        self.updateCameraTitle(cam_n)
        
    def setCameraCombo(self, cam_n):
        self.cB_camera.setCurrentIndex(cam_n)
        
    def updateCameraTitle(self,cam_n):
        # first clear any *'s from the titles
        for i in xrange( self.cB_camera.count() ):
            thisTitle = self.idock[i].windowTitle()
            if len(thisTitle) > 0 and thisTitle[-1] == '*':
                self.idock[i].setWindowTitle( self.idock[i].windowTitle()[:-1] )
        # then put a * on the currently selected title
        if len(self.idock[cam_n].windowTitle()) > 0:
            self.idock[cam_n].setWindowTitle( self.idock[cam_n].windowTitle() + "*" )
        self.getConfig(cam_n)
        #self.onUpdateColorMap(cam_n)
        self.viewer[cam_n].updateMarkerXY()
        self.viewer[cam_n].updateCrossPanel()
        self.viewer[cam_n].updateLock()
        self.viewer[cam_n].updateRdColors()

    def set_bin(self):
        bindex = int(self.lEBXY.text())
        self.snd_cmd(self.cam_n, 'BinX', bindex)
        time.sleep(1)  
        self.snd_cmd(self.cam_n, 'BinY', bindex)
        if self.cfg == None: self.dumpConfig(self.cam_n)
        
    def set_expt(self):
        val = float(self.dS_expt.value())
        self.snd_cmd(self.cam_n, 'AcquireTime', val)
        if self.cfg == None: self.dumpConfig(self.cam_n)
    
    def set_gain(self):
        val = float(self.iS_gain.value())
        self.snd_cmd(self.cam_n, 'Gain', val)
        if self.cfg == None: self.dumpConfig(self.cam_n)
        
    def onComboBoxScaleIndexChanged(self, iNewIndex):
        #print 'onComboBoxScaleIndexChanged called'
        if self.viewer[self.cam_n]:
            self.viewer[self.cam_n].iScaleIndex = iNewIndex
            self.viewer[self.cam_n].setColorMap()
            if self.cfg == None: self.dumpConfig(self.cam_n)
        
    def set_cool(self):
        self.setImageColorMap(self.rBColor_Cool, 'cool')
    
    def set_gray(self):
        self.setImageColorMap(self.rBColor_Gray, 'gray')
        
    def set_hsv(self):
        self.setImageColorMap(self.rBColor_HSV, 'hsv')
    
    def set_hot(self):
        self.setImageColorMap(self.rBColor_Hot, 'hot')
    
    def set_jet(self):
        self.setImageColorMap(self.rBColor_Jet, 'jet')
        
    def setImageColorMap(self, radiobutton, colormap):
        #print 'setImageColorMap called'
        self.colormap[self.cam_n] = colormap
        if self.viewer[self.cam_n]:
            #print 'viewer[%s] gui[%s]' % (self.viewer[cam_n].colorMap, self.colormap[cam_n])
            if self.viewer[self.cam_n].colorMap != colormap:
                self.viewer[self.cam_n].colorMap = colormap
                if not radiobutton.isChecked():
                   radiobutton.setChecked(True)
                self.viewer[self.cam_n].setColorMap()
                if self.cfg == None: self.dumpConfig(self.cam_n)
        else:
            if not radiobutton.isChecked():
                radiobutton.setChecked(True)
                
    def onUpdateColorMap(self, cam_n):
        logger.debug( 'onUpdateColorMap called %g', cam_n )
        if self.viewer[cam_n].colorMap != self.colormap[cam_n]:
            self.viewer[cam_n].colorMap = self.colormap[cam_n]
            self.viewer[cam_n].setColorMap()
        if self.cfg == None: self.dumpConfig(cam_n)
        
    def onSliderRangeMinChanged(self, newSliderValue):
        if self.viewer[self.cam_n]:        
            self.lERngMin.setText(str(newSliderValue))
            self.viewer[self.cam_n].iRangeMin = newSliderValue
            if newSliderValue > self.viewer[self.cam_n].iRangeMax:
                self.hSRngMax.setValue(newSliderValue)
            if self.viewer[self.cam_n].colorMap != None:
                self.viewer[self.cam_n].setColorMap()
                if self.cfg == None: self.dumpConfig(self.cam_n)

    def onSliderRangeMaxChanged(self, newSliderValue):
        if self.viewer[self.cam_n]:
            self.lERngMax.setText(str(newSliderValue))
            self.viewer[self.cam_n].iRangeMax = newSliderValue
            if newSliderValue < self.viewer[self.cam_n].iRangeMin:
                self.hSRngMin.setValue(newSliderValue)
            if self.viewer[self.cam_n].colorMap != None:
                self.viewer[self.cam_n].setColorMap()
                if self.cfg == None: self.dumpConfig(self.cam_n)
    
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
        
#    def onCameraButton(self):
#        if self.cB_on.isChecked():
#            self.onCameraCombo()
#        else:
#            if self.viewer[self.cam_n]:
#                self.viewer[self.cam_n].clear()
    
    def onCheckGrayScale(self):
        status = int(self.grayScale.isChecked())
        self.viewer[self.cam_n].onCheckGrayUpdate(status)
                
    def onCameraCombo(self):
        if self.iocmod[self.cam_n] and self.viewer[self.cam_n]:
            self.viewer[self.cam_n].onCameraSelect(self.cam_n)
            self.onSliderRangeMaxChanged(int(self.lERngMax.text())) #self.cfg.colormax
            
    def onUpdateRate(self, cam_n, dispRate, dataRate): 
        if self.cam_n == cam_n:
            #print 'onUpdateRate[%d][%d]' % (self.cam_n, cam_n), dispRate, dataRate
            self.lb_dispRate.setText('%.1f Hz' % dispRate)
            self.lb_dataRate.setText('%.1f Hz' % dataRate)

    def onCheckPress(self):
        # implement a stack to ensure that only 2 checkboxes are checked.
        # dump the oldest (first) one, and append the new one to the end of the stack
        # could be changed from 2 if more calculation boxes are added
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


        return

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
        
    def readPVListFile(self):
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
        self.ctrlname    = list()
        self.camtypes    = list()
        self.mottypes    = list()
        iCamera = -1
        iMotor  = -1
        iIOC    = -1
        try:
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
            
                #self.cB_camera.addItem(sCameraDesc)
                comboLable = 'CAM[%d] %s' % (self.cam_n, sCameraPv)#.split(':')[-1])
                self.cB_camera.addItem(comboLable)
                
                self.camtypes.append(lsLine[0].strip())
    
                print 'Cam[%d] %s ' % (iCamera, sCameraDesc),
                '''
                if 'IMAGE' in sCameraPv:
                    self.ctrlname.append(sCameraPv.replace('IMAGE','CAM'))
                    self.basename.append(sCameraPv)
                    print 'Pv ',
                elif 'CAM' in sCameraPv:
                    self.ctrlname.append(sCameraPv)
                    self.basename.append(sCameraPv.replace('CAM','IMAGE'))
                    print 'Pv ',
                else:
                    print 'IP ',
                    print 'Using Vendor Libraries (not implemented yet)'
                '''    
                self.ctrlname.append(sCameraPv)
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
                #print sMotorPv, sMotorDesc        
                self.cB_onmot[iMotor].setText(sMotorPv)
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
                    
    def dumpConfig(self, cam_n):
        #print 'dumpConfig called [CAM%d]' % self.cam_n
        cameraBase = str(self.lCameraList[cam_n])
        if cameraBase == "":
          return
        if self.viewer[cam_n].camera != None:
          f = open(self.cfgdir + cameraBase, "w")
          display_image = self.viewer[cam_n].display_image
          
          f.write("exposure      " + str(float(self.dS_expt.value())) + "\n")
          f.write("gain          " + str(int(self.iS_gain.value())) + "\n")
          f.write("bin_x         " + str(self.lEBXY.text()) + "\n")
          f.write("bin_y         " + str(self.lEBXY.text()) + "\n")
          f.write("grayscale     " + str(int(self.grayScale.isChecked())) + "\n")
          f.write("colorscale    " + str(self.cBoxScale.currentText()) + "\n")
          f.write("colormin      " + self.lERngMin.text() + "\n")
          f.write("colormax      " + self.lERngMax.text() + "\n")
          f.write("colormap_jet  " + str(int(self.rBColor_Jet.isChecked())) + "\n")
          f.write("colormap_hsv  " + str(int(self.rBColor_HSV.isChecked())) + "\n")
          f.write("colormap_cool " + str(int(self.rBColor_Cool.isChecked())) + "\n")
          f.write("colormap_gray " + str(int(self.rBColor_Gray.isChecked())) + "\n")
          f.write("colormap_hot  " + str(int(self.rBColor_Hot.isChecked())) + "\n")
          f.close()

    def getConfig(self, cam_n):
        logger.debug( 'getConfig called [CAM%d]' , self.cam_n )
        cameraBase = str(self.lCameraList[cam_n])
        colormapsrb = {'jet' : self.rBColor_Jet,
                       'hsv' : self.rBColor_HSV,
                       'cool': self.rBColor_Cool,
                       'gray': self.rBColor_Gray,
                       'hot' : self.rBColor_Hot}
        if cameraBase == "":
          return
        self.cfg = cfginfo()
        if self.cfg.read(self.cfgdir + cameraBase):
            # functions that uses caput/caget:
            if self.dS_expt.value() != float(self.cfg.exposure):
                self.dS_expt.setValue(float(self.cfg.exposure))
            if self.iS_gain.value() != int(self.cfg.gain):
                self.iS_gain.setValue(int(self.cfg.gain))
            # ---------------------------
            self.lEBXY.setText(self.cfg.bin_x)
            self.lEBXY.setText(self.cfg.bin_y)
            self.iScaleIndex = self.cBoxScale.findText(self.cfg.colorscale)
            self.cBoxScale.setCurrentIndex(self.iScaleIndex)
            self.lERngMin.setText(self.cfg.colormin)
            self.onRangeMinTextEnter()
            self.lERngMax.setText(self.cfg.colormax)
            self.onRangeMaxTextEnter()
            
            if   int(self.cfg.colormap_jet):
                self.colormap[cam_n] = 'jet'
            elif int(self.cfg.colormap_hsv):
                self.colormap[cam_n] = 'hsv'
            elif int(self.cfg.colormap_cool):
                self.colormap[cam_n] = 'cool'
            elif int(self.cfg.colormap_gray):
                self.colormap[cam_n] = 'gray'
            elif int(self.cfg.colormap_hot):
                self.colormap[cam_n] = 'hot'
            else:
                pass
            
            # set radiobuttons:
            cB_colormap = colormapsrb[self.colormap[cam_n]]
            if not cB_colormap.isChecked():
#                   self.setImageColorMap(self.cam_n, 
#                                         cB_colormap, self.colormap[cam_n])
                   self.setImageColorMap(cB_colormap, self.colormap[cam_n])
                   cB_colormap.setChecked(True)
                   
            self.grayScale.setChecked(int(self.cfg.grayscale))
            #self.viewer[cam_n].updateall()
        else:
          pass
          #self.dumpConfig(cam_n)
        self.cfg = None
        
    def shutdown(self):
        for i in range(8):
            if self.viewer[i]:
                self.viewer[i].clear()
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

