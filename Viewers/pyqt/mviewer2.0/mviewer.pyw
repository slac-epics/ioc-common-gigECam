#! /bin/env python
import sys, os
import mantaGiGE 
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import QTimer, Qt, QPoint, QPointF, QSize, QRectF, QObject
from PyQt4.QtGui import qApp
from PyQt4.Qt import QColorDialog
from options import Options
import time
from time import strftime as date
import math
import pyca
from Pv import Pv
import Image
import signal
import socket # for getting hostname
#from splash import SplashScreen

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
DEBUG = False
DEBUG_LEVEL_0 = 0x00
DEBUG_LEVEL_0 = 0x01
DEBUG_LEVEL_0 = 0x02
DEBUG_LEVEL_0 = 0x04
#DEBUG = DEBUG_LEVEL_0
MAX_MOT = 7


if DEBUG:
    print "running on host", socket.gethostname()
    print '''
                                                  
 #####  ###### #####  #    #  ####                
 #    # #      #    # #    # #    #               
 #    # #####  #####  #    # #                    
 #    # #      #    # #    # #  ###               
 #    # #      #    # #    # #    #               
 #####  ###### #####   ####   ####                
                                                  
                                                  
 ###### #    #   ##   #####  #      ###### #####  
 #      ##   #  #  #  #    # #      #      #    # 
 #####  # #  # #    # #####  #      #####  #    # 
 #      #  # # ###### #    # #      #      #    # 
 #      #   ## #    # #    # #      #      #    # 
 ###### #    # #    # #####  ###### ###### #####  
                                                  '''

def signal_handler(signal, frame):
     print '\nShutdown application...'
     t = Viewer() # or the class that contains a clean close code
     t.shutdown()
     sys.exit(1)
    
def caput(pvname, value, timeout=1.0):
    try:
        pv = Pv(pvname)
        pv.connect(timeout)
        pv.get(ctrl=False, timeout=timeout)
        pv.put(value, timeout)
        pv.disconnect()
        #print 'caput', pvname, value
    except pyca.pyexc, e:
        print 'pyca exception: %s' %(e)
    except pyca.caexc, e:
        print 'channel access exception: %s' %(e)
        
def caget(pvname, timeout=1.0):
    try:
        pv = Pv(pvname)
        pv.connect(timeout)
        pv.get(ctrl=False, timeout=timeout)
        v = pv.value
        pv.disconnect()
        #print 'caget', pvname, v
        return v
    except pyca.pyexc, e:
        print 'pyca exception: %s' %(e)
        return []
    except pyca.caexc, e:
        print 'channel access exception: %s' %(e)
        return []
        
class cfginfo():
    def __init__(self):
      self.dict = {}
  
    def read(self, name):
        try:
            cfg = open(name).readlines()
            for line in cfg:
                line = line.lstrip()
                token = line.split()
                if len(token) == 2:
                    self.dict[token[0]] = token[1]
                else:
                    self.dict[token[0]] = token[1:]
            return True
        except:
            return False
  
    def add(self, attr, val):
        self.dict[attr] = val
  
    def __getattr__(self, name):
        if self.dict.has_key(name):
            return self.dict[name]
        else:
            raise AttributeError, name

class CAComm(QtCore.QThread):
    def __init__(self, lock, ctrlname, parent):
        super(CAComm, self).__init__(parent)
        self.lock      = lock
        self.mutex     = QtCore.QMutex()
        self.ctrlname  = ctrlname
        self.parent    = parent
        self.stopped   = False
        self.completed = False
        
    def isStopped(self):
        try:
            self.mutex.lock()
            return self.stopped
        finally:
            self.mutex.unlock()

    def stop(self):
        try:
            self.mutex.lock()
            self.stopped = True
        finally:
            self.mutex.unlock()
            
    def run(self):
        pyca.attach_context()
        self.send(self.pv, self.val)
        
    def set_cmd(self, pv, val):
        self.pv    = pv
        self.val   = val
        
    def send(self, pv, val):
        self.set_pv(pv, val) 
        if not 'SYSRESET' in pv:
            self.get_pv(pv+'_RBV')
    
    def set_pv(self, pv, val):
        '''Set camera parameter'''
        if 'SYSRESET' in pv:
            target = pv
            caput(target, int(val))
        else:
            target = self.ctrlname + ':' + pv
            caput(target, val)
        
        
    def get_pv(self, pv):
        '''Get camera parameter'''
        target = self.ctrlname + ':' + pv
        val = caget(target)
        return val
    
class ViewerFrame(QtGui.QWidget):
  def __init__(self, parent, gui):
    QtGui.QWidget.__init__(self, parent)
    self.gui    = gui
    self.parent = parent
    # ---------------------------------
    self.rfshTimer  = QTimer();
    self.x = 175
    self.y = 132
    
    self.isColor = False
    self.iRangeMin       = 0
    self.iRangeMax       = 255#1023
    self.cam_n           = self.gui.cam_n
    self.camera          = None
    self.rowPv           = None
    self.colPv           = None
    self.gainPv          = None
    self.exposurePv      = None
    self.binXPv          = None
    self.binYPv          = None
    self.display_image   = None
    self.autobin         = False
    self.lastUpdateTime  = time.time()
    self.displayRateMax  = 5
    self.dispUpdates     = 0
    self.lastDispUpdates = 0
    self.dataUpdates     = 0
    self.lastDataUpdates = 0
    self.connected       = False
    self.camera_on       = False
    self.cameraBase      = ""
    self.event           = QObject()
    self.iScaleIndex     = False
    self.someundocked    = False
    self.colorMap        = None
    self.lastImageUpdateDispTime = 0
    self.lastImageProcessingTime = 0
    self.callInterval            = 0    
    self.cpv = {} # current pv settings
    self.cpv['exposure'] = str(float(self.gui.dS_expt.value()))
    self.cpv['gain']     = str(int(self.gui.iS_gain.value()))
    self.cpv['bin_x']    = str(self.gui.lEBXY.text())
    self.cpv['bin_y']    = str(self.gui.lEBXY.text())

    self.colors = [ QtGui.QColor(255,0,0), QtGui.QColor(255,170,0), QtGui.QColor(0,170,0), QtGui.QColor(85,170,255) ]
    #                            red                    orange                   green                  light blue
    self.xpos = [None,None,None,None]
    self.ypos = [None,None,None,None]
    self.showCross = [True, True, True, True]
    self.lockCross = [False, False, False, False]
    self.win_W = None
    self.win_H = None
    #self.winsize = [self.parent.width(),self.parent.height()]
    self.markers = [None,None,None,None]
    self.check_stack= []
    
    self.connect(self.rfshTimer, QtCore.SIGNAL("timeout()"), self.UpdateRate)
    self.connect(self.event, QtCore.SIGNAL("onImageUpdate"), self.onImageUpdate)
    self.connectDisplay()

  def connectDisplay(self):
      if not self.camera_on:
        self.display_image = DisplayImage(self.parent, self)
        self.imageBuffer = mantaGiGE.pyCreateImageBuffer(self.display_image.image, 0) # For storing the image PV value
        self.parent.resizeEvent = self.setNewImageSize
        self.parent.installEventFilter(self)

  def setCross(self,event):
      # which radio button is selected
      i = self.gui.getSelectedCross()
      if self.lockCross[i]:
          if DEBUG:
              print "this cross is locked"
      else:
          self.win_W = self.display_image.scaled_image.width() 
          self.win_H = self.display_image.scaled_image.height() 
          cross_X = float(event.x())/self.win_W
          cross_Y = float(event.y())/self.win_H
          if DEBUG:
              print "cross",i,"is checked", event.x(), event.y()
              print "float",cross_X, cross_Y
              print "win", self.win_W, self.win_H
              print "show", self.showCross[i]
          self.gui.xPos_val[i].setText("{:0.0f}".format(cross_X*self.win_W))
          self.gui.yPos_val[i].setText("{:0.0f}".format(cross_Y*self.win_H))
          self.xpos[i] = float(cross_X)
          self.ypos[i] = float(cross_Y)

  def drawCrosses(self,painter):  # this is in the wrong place, me thinks.
      size = 10
      self.win_W = self.display_image.scaled_image.width() 
      self.win_H = self.display_image.scaled_image.height() 
      for i in xrange(4):
          if self.xpos[i] and self.ypos[i] and self.showCross[i]:
              painter.setPen( QtGui.QPen(self.colors[i],1,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin) )
              self.markers[i] = ( 
                      painter.drawLine( self.win_W*self.xpos[i]     , self.win_H*self.ypos[i]-size, self.win_W*self.xpos[i]     , self.win_H*self.ypos[i]+size),
                      painter.drawLine( self.win_W*self.xpos[i]-size, self.win_H*self.ypos[i]     , self.win_W*self.xpos[i]+size, self.win_H*self.ypos[i]     )
                      )

  def updateCrossPos(self,x,y):
      #print "rescaling cross positions",x,y,self.winsize[0],self.winsize[1], float(x)/self.winsize[0]
      #self.updateCrossSize(self.parent.width(),self.parent.height()) 
      #self.winsize = [ int(x), int(y) ]
      self.win_H = int(y)
      self.win_W = int(x)
      for i in xrange(4):
          if self.xpos[i]:
              self.gui.xPos_val[i].setText("{:0.0f}".format( self.xpos[i] * self.win_W)  )
              self.gui.yPos_val[i].setText("{:0.0f}".format( self.ypos[i] * self.win_H)  )
      self.gui.onCheckPress()

  def updateMarkerXY(self):
      '''restore cross positions on camera change
      '''
      for i in xrange(4):
          if self.xpos[i]:
              self.gui.xPos_val[i].setText("{:0.0f}".format(self.win_W*self.xpos[i]))
              self.gui.yPos_val[i].setText("{:0.0f}".format(self.win_H*self.ypos[i]))
          else:
              self.gui.xPos_val[i].setText("")
              self.gui.yPos_val[i].setText("")

  def updateCrossPanel(self):
      for i in xrange(16):
          self.gui.check_box[i].setCheckState(0)
      for i in self.check_stack:
          self.gui.check_box[i].setCheckState(1)
      self.gui.onCheckPress()


  def updateLock(self):
      i = self.gui.getSelectedCross()
      self.gui.lockCross.setChecked( self.lockCross[i] )

  def updateRdColors(self):
      for i in xrange(4):
          self.gui.rd_cross[i].setStyleSheet('background-color: rgb({0:0.0f},{1:0.0f},{2:0.0f})'.format( *self.colors[i].getRgb() ) )
          #print i, self.colors[i].getRgb()
          #if self.colors[i].lightnessF() < .2:
              #self.gui.rd_cross[i].setStyleSheet('color: white')
          #else:
              #self.gui.rd_cross[i].setStyleSheet('color: black')

  def eventFilter(self, target, event):
        '''Create an event filter to capture mouse press signal over 
           the selected image witdget
           Rigth button select new camera controls
           Left button select previous camera controls
        '''
        if(event.type()==QtCore.QEvent.MouseButtonPress):
            if event.buttons() & Qt.LeftButton:
                #print 40*'-'
                # here is where to put the cross putting code
                if self.gui.cam_n == self.cam_n:
                    if DEBUG:
                        print "this cam already selected", self.cam_n
                    self.setCross(event)
                    
                else:
                    self.gui.cam_n = self.cam_n
                    if DEBUG:
                        print "selecting cam", self.cam_n

                #self.gui.cB_camera.setCurrentIndex(self.cam_n)
                self.emit(QtCore.SIGNAL("setCameraCombo(int)"), self.cam_n)
                if not self.camera_on:
                    self.connectDisplay()
                    self.onCameraSelect(self.cam_n)
                    if not self.camera_on:
                        self.gui.lb_on.setPixmap(self.gui.ledoff)
                    else:
                        self.gui.lb_on.setPixmap(self.gui.ledon)
                    self.onExposureUpdate()
                    self.onGainUpdate()
                    self.onBinXYUpdate()
                    #self.gui.cB_on.setChecked(True)                    
                else:
                    self.gui.lb_on.setPixmap(self.gui.ledon)
                    #self.gui.cB_on.setChecked(False)
                self.updateall()
                #print 40*'-'
                return True
        return False
    
  def disconnectPv(self, pv):
    if pv != None:
      try:
        pv.disconnect();
        pyca.flush_io()
      except:
        pass
    return None

  def connectPv(self, name, timeout=1.0):
    try:
      pv = Pv(name)
      pv.connect(timeout)
      pv.get(False, timeout)
      return pv
    except:
        pass
#      QtGui.QMessageBox.critical(None,
#                           "Error", "Failed to connect to PV %s" % (name),
#                           QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
    return None

  def clearCamGUI(self):
    print 'clearCamGUI called'
    self.gui.idock[self.cam_n].setWindowTitle('')
    self.gui.lb_on.setPixmap(self.gui.ledoff)
    #self.gui.cB_on.setChecked(False)
    self.gui.lb_dispRate.setText("-") 
    self.rfshTimer.stop()
    self.camera_on = False 
    
  def setCamGUI(self):
    #print 'setCamGUI called'
    #camtitle = self.gui.lCameraDesc[self.gui.cam_n]
    self.camera_on = True
    #camtitle = 'CAM[%d] %s' % (self.cam_n, self.gui.lCameraList[self.cam_n].split(':')[-1])    
    camtitle = self.gui.lCameraDesc[self.cam_n]
    self.gui.idock[self.cam_n].setWindowTitle(camtitle)
    self.gui.lb_on.setPixmap(self.gui.ledon)
    #self.gui.cB_on.setChecked(True)
    
    self.rfshTimer.start(1000)      
    #self.onExposureUpdate()
    #self.onGainUpdate()
    #self.onBinXYUpdate()
    #self.onColorMapUpdate()
    #self.setColorMap()
    
  def connectCamera(self, sCameraPv):#, index):
    timeout = 5.0
    sCAMPv  = sCameraPv.replace('IMAGE', 'CAM')
    self.camera     = self.disconnectPv(self.camera)
    self.rowPv      = self.disconnectPv(self.rowPv)
    self.colPv      = self.disconnectPv(self.colPv)
    self.gainPv     = self.disconnectPv(self.gainPv)
    self.exposurePv = self.disconnectPv(self.exposurePv)
    self.binXPv     = self.disconnectPv(self.binXPv)
    self.binYPv     = self.disconnectPv(self.binYPv)
    
    depth = caget(sCameraPv + ":ArraySize0_RBV", timeout)
    
    if depth == []:
      print 'Connection ERROR: couldn\'t get depth'
      self.clearCamGUI()
      return False
    elif depth == 3: # It's a color camera!
      rowpvname = sCameraPv + ":ArraySize2_RBV"
      colpvname = sCameraPv + ":ArraySize1_RBV"
      self.isColor = True
      self.gui.setSliderRangeMax(10) # 10 bits camera
      self.gui.grayScale.setVisible(True)      
    else: # Just B/W!
      rowpvname = sCameraPv + ":ArraySize1_RBV"
      colpvname = sCameraPv + ":ArraySize0_RBV"
      self.isColor = False
      self.gui.setSliderRangeMax(8)  #  8 bits camera
      self.gui.grayScale.setVisible(False)
    
    self.camera     = self.connectPv(sCameraPv + ":ArrayData")
    self.rowPv      = self.connectPv(rowpvname)
    self.colPv      = self.connectPv(colpvname)
    
    self.gainPv     = self.connectPv(sCAMPv + ":Gain_RBV")
    self.exposurePv = self.connectPv(sCAMPv + ":AcquireTime_RBV")
    self.binXPv     = self.connectPv(sCAMPv + ":BinX_RBV")
    self.binYPv     = self.connectPv(sCAMPv + ":BinY_RBV")

    if self.camera != None and self.rowPv != None and self.colPv != None\
         and self.gainPv != None and self.exposurePv != None and\
         self.binXPv != None and self.binYPv != None:
      if self.isColor:
        self.camera.processor  = mantaGiGE.pyCreateColorImagePvCallbackFunc(self.imageBuffer)
      else:
        self.camera.processor  = mantaGiGE.pyCreateImagePvCallbackFunc(self.imageBuffer)
      self.camera.monitor_cb      = self.imagePvUpdateCallback
      self.rowPv.monitor_cb       = self.sizeCallback
      self.colPv.monitor_cb       = self.sizeCallback
      self.gainPv.monitor_cb      = self.gainCallback
      self.exposurePv.monitor_cb  = self.exposureCallback
      self.binXPv.monitor_cb      = self.binXYCallback
      self.binYPv.monitor_cb      = self.binXYCallback
      # Now, before we monitor, update the camera size!
      self.setImageSize(self.colPv.value, self.rowPv.value)
      self.setCamGUI()
      evtmask = pyca.DBE_VALUE
      self.camera.monitor(evtmask)
      self.rowPv.monitor(evtmask)
      self.colPv.monitor(evtmask)
      self.gainPv.monitor(evtmask)
      self.exposurePv.monitor(evtmask)
      self.binXPv.monitor(evtmask)
      self.binYPv.monitor(evtmask)
      
      pyca.flush_io()
    else:
        self.clearCamGUI()

    if (DEBUG): self.dumpVARS()
    return self.camera_on
  
  def dumpVARS(self):
    print 'PV Status                  : %s [CAM%d] -' % (str(self.gui.lCameraList[self.cam_n]), self.cam_n)
    print 'Date                       : %s' % date('%m/%d %H:%M:%S')
    print 'self.camera_on             :',  self.camera_on
    print 'self.camera                :',     self.camera
    print 'self.rowPv                 :',      self.rowPv
    print 'self.colPv                 :',      self.colPv
    print 'self.gainPv                :',     self.gainPv
    print 'self.exposurePv            :', self.exposurePv
    print 'self.binXPv                :',     self.binXPv
    print 'self.binYPv                :',     self.binYPv
    print 'self.colorMap              :',   self.colorMap
    print 'self.camera.monitor_cb     :',   self.imagePvUpdateCallback
    print 'self.rowPv.monitor_cb      :',   self.sizeCallback
    print 'self.colPv.monitor_cb      :',   self.sizeCallback
    print 'self.gainPv.monitor_cb     :',   self.gainCallback
    print 'self.exposurePv.monitor_cb :',   self.exposureCallback
    print 'self.binXPv.monitor_cb     :',   self.binXYCallback
    print 'self.binYPv.monitor_cb     :',   self.binXYCallback
    print '-----------------------------------------------------------'
          
  def onCameraSelect(self, index):
    self.clear()    
    if index < 0:
      return      
    if index >= len(self.gui.lCameraList):
      print "index %d out of range (max: %d)" % (index, len(self.gui.lCameraList) - 1)
      return            
    sCameraPv = str(self.gui.lCameraList[index])
    if sCameraPv == "":
      return
    self.cameraBase = sCameraPv
    self.connectCamera(sCameraPv)
    
  def clear(self):
    if self.camera is not None:
      try:
        #self.camera.disconnect()
        self.camera     = self.disconnectPv(self.camera)
        self.rowPv      = self.disconnectPv(self.rowPv)
        self.colPv      = self.disconnectPv(self.colPv)
        self.gainPv     = self.disconnectPv(self.gainPv)
        self.exposurePv = self.disconnectPv(self.exposurePv)
        self.binXPv     = self.disconnectPv(self.binXPv)
        self.binYPv     = self.disconnectPv(self.binYPv)
        self.clearCamGUI()
      except:
        pass
      self.camera = None

  # Note: this function is called by the CA library, from another thread
  def sizeCallback(self, exception=None):
    #print 'sizeCallback called', self.colPv.value, self.rowPv.value
    if exception is None:
      self.onSizeUpdate()
    else:
      print "sizeCallback(): %-30s " % exception
 
  # Note: this function is called by the CA library, from another thread
  def gainCallback(self, exception=None):
    #print 'gainCallback called', self.gainPv.value
    if exception is None:
      self.onGainUpdate()
    else:
      print "gainCallback(): %-30s " % exception
       
  # Note: this function is called by the CA library, from another thread
  def exposureCallback(self, exception=None):
    #print 'exposureCallback called', self.exposurePv.value
    if exception is None:
      self.onExposureUpdate()
    else:
      print "exposureCallback(): %-30s " % exception
    
  # Note: this function is called by the CA library, from another thread
  def binXYCallback(self, exception=None):
    #print 'binXYCallback called', self.binXPv.value
    if exception is None:
      self.onBinXYUpdate()
    else:
      print "binXYCallback(): %-30s " % exception
      
  def onSizeUpdate(self):
    #print 'onSizeUpdate called'
    try:
      newx = self.colPv.value
      newy = self.rowPv.value
      if newx != self.x or newy != self.y:
        self.setImageSize(newx, newy)
    except:
      pass
  
  def onGainUpdate(self):
    #print "onGainUpdate() called"
    try:
      self.gui.iS_gain.setValue(int(self.gainPv.value))
#      newGain = self.gainPv.value
#      #cam_n = 
#      if newGain != self.cpv['gain'] and \
#         self.cam_n == self.gui.cam_n:
#        self.gui.iS_gain.setValue(int(newGain))
        #print 'Gain updated'
    except:
      pass 
  
  def onExposureUpdate(self):
    #print "onExposureUpdate() called"
    try:
      newExposure = self.exposurePv.value
      if newExposure != self.cpv['exposure'] and \
         self.cam_n == self.gui.cam_n:
        self.gui.dS_expt.setValue(float(newExposure))
        #print 'ExposureTime updated'
    except:
      pass      
  
  def onBinXYUpdate(self):
    #print "onBinXYUpdate() called"
    try:
      newBinX = self.binXPv.value
      newBinY = self.binYPv.value
      if (newBinX != self.cpv['bin_x'] or \
         newBinY != self.cpv['bin_y']) and \
         self.cam_n == self.gui.cam_n:
        self.gui.lEBXY.setText(str(newBinX))
        #print 'BinXY updated'
    except:
      pass    
  
  def onColorMapUpdate(self):
    #print "onColorMapUpdate() called"
    try: #assume radiobuttons auto-exclusives
        if   self.colorMap == 'jet':
            self.gui.rBColor_Jet.setChecked(True)
        elif self.colorMap == 'hsv':
            self.gui.rBColor_HSV.setChecked(True)
        elif self.colorMap == 'cool':
            self.gui.rBColor_Cool.setChecked(True)
        elif self.colorMap == 'gray':
            self.gui.rBColor_Gray.setChecked(True)
        elif self.colorMap == 'hot':
            self.gui.rBColor_Hot.setChecked(True)
        else:
            pass
        #print 'ColorMap updated'
    except:
      pass  
  
  # Note: this function is called by the CA library, from another thread
  def imagePvUpdateCallback(self, exception=None):       
    #print 'imagePvUpdateCallback called', self.dataUpdates
    if exception is None:
      currentTime       =  time.time()
      self.dataUpdates  += 1
      self.callInterval =  currentTime - self.lastImageUpdateDispTime
      if self.callInterval < self.lastImageProcessingTime:
        print( "Image update interval %.3f < Image Update Processing Time: %.3f" % 
          (callInterval, self.lastImageProcessingTime) )
        return      
      if self.callInterval < 1.0/self.displayRateMax:# throttle the display speed
        return        
      self.lastImageUpdateDispTime = currentTime    
      ### commented next 2 lines for performance test purposes
      # Send out the signal to notify windows update (in the GUI thread)
      self.event.emit(QtCore.SIGNAL("onImageUpdate")) 
    else:
      print "imagePvUpdateCallback(): %-30s " %(self.name), exception
  
  def onImageUpdate(self):    
    #print 'onImageUpdate called', self.dataUpdates, self.dispUpdates
    imageProcessingStartTime = time.time()
    self.updateImage()
    self.lastImageProcessingTime = time.time() - imageProcessingStartTime    
    #print( "Image update interval %.3f , Image Update Processing Time: %.3f" % 
    #  (self.callInterval, self.lastImageProcessingTime) ) # for debug only
    
  def updateImage(self):
    #print 'updateImage called', self.dataUpdates, self.dispUpdates
    try:
      self.dispUpdates += 1
      self.updateall()
    except Exception, e:
      print e

  def UpdateRate(self):
    
    now                  = time.time()
    delta                = now - self.lastUpdateTime
    dispUpdates          = self.dispUpdates - self.lastDispUpdates
    dispRate             = (float)(dispUpdates)/delta
    dataUpdates          = self.dataUpdates - self.lastDataUpdates
    dataRate             = (float)(dataUpdates)/delta
    
    #self.event.emit(QtCore.SIGNAL("onImageUpdate")) # Send out the signal to notify windows update (in the GUI thread)
    #print 'UpdateRate[local, gui]', self.cam_n, self.gui.cam_n
    #print 'UpdateRate  [%d][%d]' % (self.gui.cam_n, self.cam_n), repr(self.rfshTimer), self.dispUpdates, dataRate
    self.emit(QtCore.SIGNAL("onUpdateRate(int, float, float)"), self.cam_n, dispRate, dataRate)

    self.lastUpdateTime  = now
    self.lastDispUpdates = self.dispUpdates
    self.lastDataUpdates = self.dataUpdates
    self.updateImage()
    
  def setColorMap(self):
    #print 'setColorMap called [CAM%d] %s' % (self.cam_n, self.colorMap)
    self.iScaleIndex = self.gui.iScaleIndex
    if self.colorMap != "gray":
      fnColorMap = self.gui.cwd + "/" + self.colorMap + ".txt"
      mantaGiGE.pydspl_setup_color_map(self.imageBuffer, fnColorMap, self.iRangeMin, self.iRangeMax, self.iScaleIndex)
    else:
      mantaGiGE.pydspl_setup_gray(self.imageBuffer, self.iRangeMin, self.iRangeMax, self.iScaleIndex)
    
#  def forceMinSize(self):
#    self.gui.app.sendPostedEvents()
#    self.gui.resize(100, 100)
#    self.gui.app.sendPostedEvents()
#    self.gui.resize(100, 100)
    
  def setNewImageSize(self, event):
      #print 'calling setNewImageSize', self.parent.width(), self.parent.height()
      if self.display_image:
        if self.autobin: # change automatic binning
            bintrg = [250, 350] # width thresholds
            if self.parent.width() < bintrg[1]:
                self.gui.lEBXY.setText('3')
            elif self.parent.width() > bintrg[1] and self.parent.width() < bintrg[0]:
                self.gui.lEBXY.setText('2')
            elif self.parent.width() > bintrg[0]:
                self.gui.lEBXY.setText('1')
            self.gui.set_bin()
        self.display_image.scaled_image = self.display_image.image.scaled(self.parent.width(), self.parent.height(), 
                   QtCore.Qt.KeepAspectRatio,
                   QtCore.Qt.SmoothTransformation)
        self.display_image.update()
        #this updates toooo fast, so the changes is only ever .9999 or 1.0001 sizes
        self.updateCrossPos(self.display_image.scaled_image.width(),self.display_image.scaled_image.height()) 
      
  def setImageSize(self, newx, newy):
    self.x = newx
    self.y = newy
    if DEBUG:
        print "new size", newx, newy

    self.display_image.setImageSize()
    self.imageBuffer = mantaGiGE.pyCreateImageBuffer(self.display_image.image, 0)
    if self.camera != None:
      if self.isColor:
        self.camera.processor  = mantaGiGE.pyCreateColorImagePvCallbackFunc(self.imageBuffer)
        self.gui.grayScale.setVisible(True)
      else:
        self.camera.processor  = mantaGiGE.pyCreateImagePvCallbackFunc(self.imageBuffer)
        self.gui.grayScale.setVisible(False)
      mantaGiGE.pySetImageBufferGray(self.imageBuffer, self.gui.grayScale.isChecked())

  def onCheckGrayUpdate(self, newval):
    mantaGiGE.pySetImageBufferGray(self.imageBuffer, newval)
    if self.gui.cfg == None: self.gui.dumpConfig()

  def updateall(self):
    #print 'updateall called', self.dataUpdates, self.dispUpdates
    self.display_image.setGeometry(QtCore.QRect(0, 0, self.parent.width(), self.parent.height()))
    self.display_image.scaled_image = self.display_image.image.scaled(self.parent.width(), self.parent.height(), 
                   QtCore.Qt.KeepAspectRatio,
                   QtCore.Qt.SmoothTransformation)   
    #self.display_image.updateGeometry()
    self.display_image.repaint()
    self.display_image.update()
 
class DisplayImage(QtGui.QWidget):
  def __init__(self, parent, gui):
    QtGui.QWidget.__init__(self, parent)
    #print 'DisplayImage called'
    self.gui          = gui
    self.parent       = parent
    size              = QtCore.QSize(self.pWidth(), self.pHeight())
    self.image        = QtGui.QImage(size, QtGui.QImage.Format_RGB32)
    self.scaled_image = self.image
    self.image.fill(0)
    self.paintevents  = 0
    
  def pWidth(self):
    return self.parent.width()

  def pHeight(self):
    return self.parent.height()

  def setImageSize(self):
    size              = QtCore.QSize(self.gui.x, self.gui.y)
    #size              = QtCore.QSize(self.pWidth(), self.pHeight())
    self.image        = QtGui.QImage(size, QtGui.QImage.Format_RGB32)
    self.image.fill(0)
    
  def paintEvent(self, event):
    #print 'paintEvent', event
    if self.gui.dispUpdates == 0:
      return
    painter  = QtGui.QPainter(self)
    #painter.drawImage(0, 0, self.scaled_image)

    # new stuff for putting the crosses on
    painter.setPen( QtGui.QPen(Qt.red,1,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin) )
    #self.display_image.scaled_image = self.display_image.image.scaled(self.parent.width(), self.parent.height(), 
                   #QtCore.Qt.KeepAspectRatio,
                   #QtCore.Qt.SmoothTransformation)   
    self.rectImage = QtCore.QRectF( 0,0,self.scaled_image.width(),self.scaled_image.height())
    painter.drawImage( self.rectImage, self.scaled_image)
    #print self.scaled_image.rect(), self.scaled_image.width(), self.scaled_image.height()
    self.gui.drawCrosses(painter)
    painter.setOpacity(1)


    self.paintevents += 1

    
form_class, base_class = uic.loadUiType('ui/mviewer2.6.ui')
#form_class, base_class = uic.loadUiType('ui/mviewer.ui')

#class Viewer(QtGui.QWidget, form_class):
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

        self.dist_val = [self.Distance1, self.Distance2]

        self.from_val = [self.From1, self.From2]

        self.check_box = [
                self.checkBox11, self.checkBox12, self.checkBox13, self.checkBox14,
                self.checkBox21, self.checkBox22, self.checkBox23, self.checkBox24,
                self.checkBox31, self.checkBox32, self.checkBox33, self.checkBox34,
                self.checkBox41, self.checkBox42, self.checkBox43, self.checkBox44,
                ]
        
        self.tB_reset = [self.tB_reset_1, self.tB_reset_2]

        self.lb_ImStats = [self.lb_minValdata, self.lb_maxValdata]

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
        
        # Colormap controls: --------------------------------------
        #self.connect(self.cB_camera,    sig3, self.onCameraCombo)
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
        self.connect(self.cB_on,        sig0, self.onCameraButton)
        self.connect(self.grayScale,    sig0, self.onCheckGrayScale)
        self.connect(self.pB_quit,      sig0, self.shutdown)
        self.connect(self.tB_reset_1,   sig0, self.resetIOC)
        self.connect(self.tB_reset_2,   sig0, self.resetIOC)
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
        
        #print dir (self.w_Img_1)#.sizePolicy.setHeightForWidth(True)
        #print dir(self.dW_Img_1.sizePolicy.setHeightForWidth)
        for iwdg in self.idock:
            iwdg.setEnabled(False)
            iwdg.setWindowTitle('')
        self.lock = [QtCore.QReadWriteLock() for i in range(8)]
        self.splashScreen.showMsg("Loading Cameras...")            
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
                self.connect(self.viewer[i], sig6, self.onUpdateRate)
                self.connect(self.viewer[i], sig8, self.setCameraCombo)
                self.connect(self.idock[i],  sig9, self.centerDock)
                self.splashScreen.showMsg("Loading... %s as Cam[%d]" %\
                                                (self.lCameraDesc[i], i))
                time.sleep(1)            
        self.cam_n = 0
        self.settoolTips()

        # Destroy Splash once all are loaded
        if self.splashScreen:
            self.splashScreen.finish(self)

        self.centerOnScreen()
        self.setCameraCombo(0) # to update the selection indicator *
        self.show()

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
        if DEBUG:
            print "checked?", self.showHideCross.isChecked()
        return self.showHideCross.isChecked()

    def getLockCross(self):
        if DEBUG:
            print "locked?", self.lockCross.isChecked()
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

        if DEBUG:
            print "handling it!", XY, ":", int(translate[XY].text())

        if self.viewer[self.cam_n].lockCross[i]:
            if DEBUG:
                print "it's locked"
            if XY[0] == 'X':
                translate[XY].setText("{:0.0f}".format( self.viewer[self.cam_n].xpos[i] * self.viewer[self.cam_n].win_W ) )
            else:
                translate[XY].setText("{:0.0f}".format( self.viewer[self.cam_n].ypos[i] * self.viewer[self.cam_n].win_W ) )
        else:
            if XY[0] == 'X':
                self.viewer[self.cam_n].xpos[ i ] = float(translate[XY].text()) / self.viewer[self.cam_n].win_W
            else:
                self.viewer[self.cam_n].ypos[ i ] = float(translate[XY].text()) / self.viewer[self.cam_n].win_H

        if DEBUG:
            print self.viewer[self.cam_n].xpos
            print self.viewer[self.cam_n].ypos

    def settoolTips(self):
        self.cB_on.setToolTip('Reconnect Camera')
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

        
    def setCameraCombo(self, cam_n):
# clear previous focus indication, if present
        if self.idock[self.cB_camera.currentIndex()].windowTitle()[-1] == '*':
            self.idock[self.cB_camera.currentIndex()].setWindowTitle( 
                    self.idock[self.cB_camera.currentIndex()].windowTitle()[:-1] )
        self.cB_camera.setCurrentIndex(cam_n)
        self.getConfig(cam_n)
        self.onUpdateColorMap(cam_n)
# set asterisk indication of window focus
        self.idock[cam_n].setWindowTitle( self.idock[cam_n].windowTitle() + "*" )
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
        #print 'onUpdateColorMap called'
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
        
    def onCameraButton(self):
        if self.cB_on.isChecked():
            self.onCameraCombo()
        else:
            if self.viewer[self.cam_n]:
                self.viewer[self.cam_n].clear()
    
    def onCheckGrayScale(self):
        status = int(self.grayScale.isChecked())
        self.viewer[self.cam_n].onCheckGrayUpdate(status)
                
    def onCameraCombo(self):
        if self.iocmod[self.cam_n] and self.viewer[self.cam_n]:
            self.viewer[self.cam_n].onCameraSelect(self.cam_n)
            
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
                if DEBUG:
                    print "no measuring of distance to self."
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
                sIOC = sIOC.replace(':','-').lower()
                
                if len(lsLine) >= 3:
                  sIOCDesc = lsLine[2].strip().split('#')[0]
                else:
                  sIOCDesc = sIOC
                
                self.lIOCList.append(sIOC)
                self.lIOCDesc.append(sIOCDesc)
                self.tB_reset[iIOC].setToolTip(sIOCDesc)
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

#    def readPVListFile(self):
##          self.lCameraList = []
##          self.lCameraDesc = []
##          self.lMotorList  = []
##          self.lMotorDesc  = []
##          self.basename    = list()
##          self.ctrlname    = list()
##          self.camtypes    = list()
##          self.mottypes    = list()
##          iCamera = -1
##          iMotor  = -1        
#        ''' Reads camera.lst file, update camera combo, etc...'''
#        self.lCameraList = []
#        self.lCameraDesc = []
#        self.lMotorList  = []
#        self.lMotorDesc  = []
#        self.basename    = list()
#        self.ctrlname    = list()
#        self.camtypes    = list()
#        self.mottypes    = list()
#        iCamera = -1
#        iMotor  = -1
#        try:
#          if (self.camerListFilename[0] == '/'):
#            fnCameraList = self.camerListFilename
#          else:
#            fnCameraList = self.cwd + "/" + self.camerListFilename
#          lCameraListLine = open( fnCameraList,"r").readlines()      
#          self.lCameraList = []
#          
#          for line in lCameraListLine:
#            line = line.lstrip()
#            if not line:
#                continue
#            if line.startswith("#"):
#              continue
#            if not line.startswith("MM"):
#                iCamera += 1
#                self.cam_n = iCamera
#    
#                lsLine = line.split(",")
#                if len(lsLine) < 2:
#                    print throw("")
#                
#                sCameraPv = lsLine[1].strip()
#                if len(lsLine) >= 4:
#                  sCameraDesc = lsLine[3].strip().split('#')[0]
#                else:
#                  sCameraDesc = sCameraPv
#                  
#                self.lCameraList.append(sCameraPv)
#                self.lCameraDesc.append(sCameraDesc)
#            
#                #self.cB_camera.addItem(sCameraDesc)
#                comboLable = 'CAM[%d] %s' % (self.cam_n, sCameraPv)#.split(':')[-1])
#                self.cB_camera.addItem(comboLable)
#                
#                self.camtypes.append(lsLine[0].strip())
#    
#                print 'Cam[%d] %s ' % (iCamera, sCameraDesc),
#                if 'IMAGE' in sCameraPv:
#                    self.ctrlname.append(sCameraPv.replace('IMAGE','CAM'))
#                    self.basename.append(sCameraPv)
#                    print 'Pv ',
#                elif 'CAM' in sCameraPv:
#                    self.ctrlname.append(sCameraPv)
#                    self.basename.append(sCameraPv.replace('CAM','IMAGE'))
#                    print 'Pv ',
#                else:
#                    print 'IP ',
#                    print 'Using Vendor Libraries (not implemented yet)'
#    
#                print sCameraPv
#            else: # now the motors in the lst file:
#                iMotor += 1
#                self.mot_n = iMotor
#                
#                lsLine = line.split(",")
#                if len(lsLine) < 2:
#                    print throw("")
#                
#                sMotorPv = lsLine[1].strip()
#                if len(lsLine) >= 4:
#                  sMotorDesc = lsLine[3].strip().split('#')[0]
#                else:
#                  sMotorDesc = sMotorPv
#                  
#                self.lMotorList.append(sMotorPv)
#                self.lMotorDesc.append(sMotorDesc)
#                #print sMotorPv, sMotorDesc        
#                self.cB_onmot[iMotor].setText(sMotorPv)
#                self.mottypes.append(lsLine[0].strip())
#                
#                print 'Mot[%d] %s ' % (iMotor, sMotorDesc), sMotorPv
#        except:
#            #import traceback
#            #traceback.print_exc(file=sys.stdout)
#            print '!! Failed to read motor pv list from \"%s\"' % fnCameraList
#            return 0
#        return iCamera + 1
            
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
        #print 'getConfig called [CAM%d]' % self.cam_n
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
        if self.sender() == self.tB_reset_1:
            reset = '%s:SYSRESET 1' % self.lIOCList[0]
        elif self.sender() == self.tB_reset_2:
            reset = '%s:SYSRESET 1' % self.lIOCList[1]
        else:
            return False
        print reset
        #self.snd_cmd(0, reset)
        return True
        
    def mytest(self, word):
        print "{:s} does nothing".format(word)
        pass


class SplashScreen(QtGui.QSplashScreen):
	def __init__(self):
		self.loadImages()
		self.lblAlignment = QtCore.Qt.Alignment(QtCore.Qt.AlignBottom | 
											   QtCore.Qt.AlignRight  |
                                               QtCore.Qt.AlignAbsolute)

		QtGui.QSplashScreen.__init__(self, self.splashLogo)

		self.centerOnScreen()
		self.msgdelay = 0
		self.show()
		QtCore.QCoreApplication.flush()

#		# Progress bar
#		self.progressBar = QProgressBar(self)
#		#self.progressBar.setGeometry(QRect(4, 207, 200, 18))
#		self.progressBar.setGeometry(self.width()/10, 8*self.height()/20,
#                        8*self.width()/10, self.height()/20)
#		self.progressBar.show()
#		self.barTimer = QTimer() # not implemented yet

	def showMsg(self, msg):
		'''Show message in lower part of splash screen'''
		QtGui.QSplashScreen.showMessage(self, msg, 
                                        self.lblAlignment, 
                                        QtGui.QColor(QtCore.Qt.black))
		time.sleep(self.msgdelay)		
		QtGui.qApp.processEvents()

	def clearMsg(self):
		'''Clear message in lower part of splash screen'''
		QtGui.QSplashScreen.clearMessage(self)
		QtGui.qApp.processEvents()		
	
	def loadImages(self):
		self.splashLogo = QtGui.QPixmap('ui/LCLS_400.png')

	def centerOnScreen(self):
		'''centerOnScreen() Centers the window on the screen.'''
		resolution = QtGui.QDesktopWidget().screenGeometry()
		self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

	def setMsgTime(self, delay=0.5):
		self.msgdelay = delay

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

#    sp = splashScreen()
#    sp.showSplashMsg('Complains to ...')
#    time.sleep(5)
    gui = Viewer(app, cwd, options.instrument, camLstFname, cfgdir)#cwd, cams, cfgdir)
       
    sys.exit(app.exec_())

