import logging
import time
from time import strftime as date

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QTimer, QObject, Qt #, Qt, QPoint, QPointF, QSize, QRectF, QObject
import mantaGiGE 
import Image

from DisplayImage import DisplayImage
from utils import *

logger = logging.getLogger('mviewer.ViewerFrame')


class ViewerFrame(QtGui.QWidget):
    def __init__(self, parent, gui):
        QtGui.QWidget.__init__(self, parent)
        self.gui    = gui
        self.parent = parent
        # ---------------------------------
        self.rfshTimer   = QTimer()
        self.timerKeeper = QTimer()
        self.timerReferenceTime = None
        
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
        #self.colorMap        = None
        self.colorMap        = 'gray'
        self.lastImageUpdateDispTime = 0
        self.lastImageProcessingTime = 0
        self.callInterval            = 0    
        self.cpv = {} # current pv settings
        self.cpv['exposure'] = str(float(self.gui.dS_expt.value()))
        self.cpv['gain']     = str(int(self.gui.iS_gain.value()))
        self.cpv['bin_x']    = str(self.gui.lEBXY.text())
        self.cpv['bin_y']    = str(self.gui.lEBXY.text())
        
        #                            red                    orange                   green                  light blue
        self.colors = [ QtGui.QColor(255,0,0), QtGui.QColor(255,170,0), QtGui.QColor(0,170,0), QtGui.QColor(85,170,255) ]
        self.xpos = [None,None,None,None]
        self.ypos = [None,None,None,None]
        self.showCross = [True, True, True, True]
        self.lockCross = [False, False, False, False]
        self.win_W = None
        self.win_H = None
        #self.winsize = [self.parent.width(),self.parent.height()]
        self.markers = [None,None,None,None]
        self.check_stack= []

        self.connect(self.rfshTimer,          QtCore.SIGNAL("timeout()"),          self.UpdateRate)
        self.connect(self.event,              QtCore.SIGNAL("onImageUpdate"),      self.onImageUpdate)
        
#        self.connect(self.gui.ResetTimer9, QtCore.SIGNAL("released()"), lambda: self.handleTimerReset(9))
#        self.connect(self.gui.ResetTimer1h,QtCore.SIGNAL("released()"), lambda: self.handleTimerReset(1))
#        self.connect(self.gui.TimerClear,  QtCore.SIGNAL("released()"), lambda: self.handleTimerReset(0))
        
        self.connect(self.timerKeeper,        QtCore.SIGNAL("timeout()"),  lambda: self.updateTimer)
        
        self.connectDisplay()
        self.setupTimer()

    def setupTimer(self, refTime=None, duration=9):
        logger.debug( "setup timer called" )
        self.gui.TimerLabel.setEnabled(True)
        self.gui.Timer.setEnabled(True)
        self.gui.ResetTimer9h.setEnabled(True)
        self.gui.ResetTimer1h.setEnabled(True)
        self.gui.TimerClear.setEnabled(True)
        self.gui.TimerLabel.setText( str(self.gui.lCameraDesc[self.cam_n]) )
        self.handleTimerReset(duration)
        if not refTime:
            refTime = time.time()
        self.timerReferenceTime = (refTime, duration * 3600.)
        self.timerKeeper.start(1000)
        
    def handleTimerReset(self, t):
        logger.debug( "timer reset %g", t )
        #self.updateCamCombo()
        self.gui.Timer.setText("{:02.0f}:00:00".format(t))
        self.timerReferenceTime = (time.time(),float(t)*3600.)
        #logger.debug( "handleTimerReset %g %g %s", t, cam_n, self.viewer[cam_n] )
        if t > 0 and self.camera is None :
            print "reconnecting", self.cam_n
#            self.setCameraCombo(cam_n)
#            self.viewer[cam_n].onCameraSelect(cam_n)
#            self.viewer[cam_n].connectCamera( self.viewer[cam_n].cameraBase )
#            #self.onUpdateColorMap(cam_n)
#            self.viewer[cam_n].setColorMap()
#            self.connect(self.viewer[cam_n], self.sig6, self.onUpdateRate)
#            self.connect(self.viewer[cam_n], self.sig8, self.setCameraCombo)
#            self.updateCameraTitle(cam_n)
        elif t == 0 and self.camera is not None : 
            print "clearing Cam", self.cam_n
#            self.setCameraCombo(cam_n)
#            self.viewer[cam_n].clear()

    def updateTimer(self, cam_n):
        logger.debug( "updateTimer %s", cam_n )
        if self.gui.Timer.isEnabled() and self.timerReferenceTime:
            ref, totalseconds = self.timerReferenceTime
            endTime = ref + totalseconds
            delta = int(endTime - time.time())
            if delta > 0:
                hours = delta / 3600
                minutes = (delta % 3600) / 60
                seconds = (delta % 3600) % 60
                #if DEBUG:
                #    print cam_n, ref, totalseconds, endTime, delta, hours, minutes, seconds
                self.gui.Timer.setText("{:02.0f}:{:02.0f}:{:02.0f}".format(hours,minutes,seconds))
            else :
                hours = 0
                minutes = 0
                seconds = 0
                self.gui.Timer.setText("{:02.0f}:{:02.0f}:{:02.0f}".format(hours,minutes,seconds))
                self.clear()
#                if self.viewer[cam_n].camera is not None :
#                    self.setCameraCombo(cam_n)
#                    self.viewer[cam_n].clear()
#                #if DEBUG:
#                #    print "camera", cam_n, "should be disabled"

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
            logger.debug( "this cross is locked")
        else:
            self.win_W = self.display_image.scaled_image.width() 
            self.win_H = self.display_image.scaled_image.height() 
            cross_X = float(event.x())/self.win_W
            cross_Y = float(event.y())/self.win_H
            logger.debug( "cross %g is checked %g %g",i, event.x(), event.y() )
            logger.debug( "float %g %g",cross_X, cross_Y )
            logger.debug( "win %g %g", self.win_W, self.win_H )
            logger.debug( "show %g", self.showCross[i] )
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
                self.gui.xPos_val[i].setText("0")
                self.gui.yPos_val[i].setText("0")
    
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
            self.gui.rd_line[i].setStyleSheet('background-color: rgb({0:0.0f},{1:0.0f},{2:0.0f})'.format( *self.colors[i].getRgb() ) )
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
                  if self.gui.cam_n == self.cam_n and self.camera is not None:
                      logger.debug( "this cam already selected %g", self.cam_n )
                      if self.gui.showHideCross.isChecked():
                          self.setCross(event)
                  else:
                      self.gui.cam_n = self.cam_n
                      logger.debug( "selecting cam %g", self.cam_n )
                      self.emit(QtCore.SIGNAL("setCameraCombo(int)"), self.cam_n)
    
                  if not self.camera_on:
                      self.connectDisplay()
                      self.onCameraSelect(self.cam_n)
                      self.onExposureUpdate()
                      self.onGainUpdate()
                      self.onBinXYUpdate()
                  self.updateall()
                  self.gui.getConfig(self.cam_n)
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
      logger.debug( 'clearCamGUI called' )
      self.gui.idock[self.cam_n].setWindowTitle('')
      #self.gui.lb_on.setPixmap(self.gui.ledoff)
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
      #self.gui.lb_on.setPixmap(self.gui.ledon)
      #self.gui.cB_on.setChecked(True)
      
      self.rfshTimer.start(1000)      
      #self.onExposureUpdate()
      #self.onGainUpdate()
      #self.onBinXYUpdate()
      #self.onColorMapUpdate()
      #self.setColorMap()
      
    def connectCamera(self, sCAMPv):#, index):
      timeout = 5.0
      #sCAMPv  = sCameraPv.replace('IMAGE', 'CAM')
      sImagePv = sCAMPv + ':IMAGE1'
      self.camera     = self.disconnectPv(self.camera)
      self.rowPv      = self.disconnectPv(self.rowPv)
      self.colPv      = self.disconnectPv(self.colPv)
      self.gainPv     = self.disconnectPv(self.gainPv)
      self.exposurePv = self.disconnectPv(self.exposurePv)
      self.binXPv     = self.disconnectPv(self.binXPv)
      self.binYPv     = self.disconnectPv(self.binYPv)
      
      depth = caget(sImagePv + ":ArraySize0_RBV", timeout)
      
      if depth == []:
        logger.error( 'Connection ERROR: couldn\'t get depth')
        self.clearCamGUI()
        return False
      elif depth == 3: # It's a color camera!
        rowpvname = sImagePv + ":ArraySize2_RBV"
        colpvname = sImagePv + ":ArraySize1_RBV"
        self.isColor = True
        self.gui.setSliderRangeMax(10) # 10 bits camera
        self.gui.grayScale.setVisible(True)      
      else: # Just B/W!
        rowpvname = sImagePv + ":ArraySize1_RBV"
        colpvname = sImagePv + ":ArraySize0_RBV"
        self.isColor = False
        self.gui.setSliderRangeMax(8)  #  8 bits camera
        self.gui.grayScale.setEnabled(False)
      self.camera     = self.connectPv(sImagePv + ":ArrayData")
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
          self.camera_on = False
    
      if logger.getEffectiveLevel() <= 20:
          self.dumpVARS()
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
      ####### Check if its necessary ->>> self.clear()    
      if index < 0:
        return      
      if index >= len(self.gui.lCameraList):
        logger.error( "index %d out of range (max: %d)" % (index, len(self.gui.lCameraList) - 1) )
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
      if exception is None:
        self.onSizeUpdate()
      else:
        logger.error( "sizeCallback(): %-30s " % exception )
    
    # Note: this function is called by the CA library, from another thread
    def gainCallback(self, exception=None):
      if exception is None:
        self.onGainUpdate()
      else:
        logger.error("gainCallback(): %-30s " % exception )
         
    # Note: this function is called by the CA library, from another thread
    def exposureCallback(self, exception=None):
      if exception is None:
        self.onExposureUpdate()
      else:
        logger.error( "exposureCallback(): %-30s " % exception )
      
    # Note: this function is called by the CA library, from another thread
    def binXYCallback(self, exception=None):
      if exception is None:
        self.onBinXYUpdate()
      else:
        logger.error( "binXYCallback(): %-30s " % exception )
        
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
          logger.info( "Image update interval %.3f < Image Update Processing Time: %.3f" % 
            (callInterval, self.lastImageProcessingTime) )
          return      
        if self.callInterval < 1.0/self.displayRateMax:# throttle the display speed
          return        
        self.lastImageUpdateDispTime = currentTime    
        ### commented next 2 lines for performance test purposes
        # Send out the signal to notify windows update (in the GUI thread)
        self.event.emit(QtCore.SIGNAL("onImageUpdate")) 
      else:
        logger.error( "imagePvUpdateCallback(): %-30s " %(self.name), exception)
    
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
        logger.error( 'updateImage: %s', e )
    
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
      logger.debug( 'self.cam_n %s', self.cam_n)
      logger.debug( 'setColorMap called %s', self.colorMap)
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
      logger.debug( "new size %g %g", newx, newy )
    
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
      
