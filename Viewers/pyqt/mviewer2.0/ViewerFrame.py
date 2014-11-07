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

class Glob():
    pv, name = [0, 1]
    
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
        
        self.iRangeMin       = 0
        self.iRangeMax       = 255#1023
        self.cam_n           = self.gui.cam_n

        self.display_image   = None
        self.autobin         = False
        self.lastUpdateTime  = time.time()
        self.displayRateMax  = 5
        self.dispUpdates     = 0
        self.lastDispUpdates = 0
        self.dataUpdates     = 0
        self.lastDataUpdates = 0
        self.camera_on       = False
        self.event           = QObject()
        self.iScaleIndex     = False
        self.colormapfile    = None
        self.colorMap        = 'gray'
        self.lastImageUpdateDispTime = 0
        self.lastImageProcessingTime = 0
        self.callInterval            = 0
        self.controlling     = False
        # Monitor Pvs: ---------------------------------------------------------
        self.rowPv             = None ; self.colPv             = None
        self.sPv_CAM           = str(self.gui.lCameraList[self.cam_n])
        self.sPv_IMAGE1        = self.sPv_CAM + ':IMAGE1'
        self.Pv_Gain_RBV       = [None, self.sPv_CAM + ':Gain_RBV']
        self.Pv_Exposure_RBV   = [None, self.sPv_CAM + ':AcquireTime_RBV']
        self.Pv_BinX_RBV       = [None, self.sPv_CAM + ':BinX_RBV']
        self.Pv_BinY_RBV       = [None, self.sPv_CAM + ':BinY_RBV']
        self.Pv_ArraySize0_RBV = [None, self.sPv_IMAGE1 + ':ArraySize0_RBV']
        self.Pv_ArraySize1_RBV = [None, self.sPv_IMAGE1 + ':ArraySize1_RBV']
        self.Pv_ArraySize2_RBV = [None, self.sPv_IMAGE1 + ':ArraySize2_RBV']
        self.Pv_ArrayData      = [None, self.sPv_IMAGE1 + ':ArrayData']
        # Control Pvs: ---------------------------------------------------------
        self.Pv_Gain           = [None, self.sPv_CAM + ':Gain']
        self.Pv_Exposure       = [None, self.sPv_CAM + ':AcquireTime']
        self.Pv_BinX           = [None, self.sPv_CAM + ':BinX']
        self.Pv_BinY           = [None, self.sPv_CAM + ':BinY']
        self.connectedPvs      = list() # needed later for disconnect all on exit
        # ----------------------------------------------------------------------

        #                            red                    orange                   green                  light blue
        self.colors = [ QtGui.QColor(255,0,0), QtGui.QColor(255,170,0), QtGui.QColor(0,170,0), QtGui.QColor(85,170,255) ]
        self.xpos = [0, 0, 0, 0]
        self.ypos = [0, 0, 0, 0]

        
        self.showCross = [False, False, False, False]
        self.lockCross = [False, False, False, False]
        self.win_W = None
        self.win_H = None

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
        if t > 0 and self.Pv_ArrayData[Glob.pv] is None :
            print "reconnecting", self.cam_n
#            self.viewer[cam_n].onCameraSelect(cam_n)
#            #self.onUpdateColorMap(cam_n)
#            self.viewer[cam_n].setColorMap()
#            self.connect(self.viewer[cam_n], self.sig6, self.onUpdateRate)
#            self.updateCameraTitle(cam_n)
        elif t == 0 and self.Pv_ArrayData[Glob.pv] is not None : 
            print "clearing Cam", self.cam_n
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

    def connectDisplay(self):
        if not self.camera_on:
          self.display_image = DisplayImage(self.parent, self)
          self.imageBuffer = mantaGiGE.pyCreateImageBuffer(self.display_image.image, 0) # For storing the image PV value
          self.parent.resizeEvent = self.setNewImageSize
          self.parent.installEventFilter(self)
          
    def disconnectDisplay(self):
          self.parent.removeEventFilter(self)
          self.disconnectCamera()

    def mouseMoveEvent(self, event):
        print 'to be used to draw a cross while moving...'
#        if not self.barrelPressed:
#            return
#        pos = event.pos()
#        if pos.x() <= 0:
#            pos.setX(1)
#        if pos.y() >= self.height():
#            pos.setY(self.height() - 1)
#        rad = math.atan((float(self.rect().bottom()) - pos.y()) / pos.x())
#        self.setAngle(QtCore.qRound(rad * 180 / 3.14159265))    
    
    
    def setCross(self, event):
        # which radio button is selected
        i = self.gui.getSelectedCross()
        if self.lockCross[i]:
            logger.debug( "this cross is locked")
        else:
            logger.debug( 'setCross called ViewerFrame prima %s %s', self.gui.X1Position.text(), self.gui.Y1Position.text() )
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
            #self.gui.dumpConfig(self.cam_n)
            logger.debug( 'setCross called ViewerFrame dopo %s %s', self.gui.X1Position.text(), self.gui.Y1Position.text() )
    
    def drawCrosses(self, painter):  # this is in the wrong place, me thinks.
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
        
        #logger.debug( 'onCheckPress called ViewerFrame %s %s', self.gui.X1Position.text(), self.gui.Y1Position.text() )
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
    
    
#    def updateLock(self):
#        i = self.gui.getSelectedCross()
#        print 'THIS NEED TO BE FIXED!!!'
#        #self.gui.cBlock_1.setChecked( self.lockCross[i] )
    
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
             the selected image widget
             Right button select new camera controls
             Left button select previous camera controls
          '''
          if(event.type()==QtCore.QEvent.MouseButtonPress):
              if event.buttons() & Qt.LeftButton:
                  self.gui.dumpConfig(self.gui.cam_n) # save last camera params
                  self.gui.cam_n = self.cam_n
                  self.gui.getConfig(self.cam_n)      # get new camera params
                  self.gui.updateCameraTitle(self.cam_n)
                  if self.showHideCrosses():
                      self.setCross(event)
                  self.updateall()
                  return True
          return False
      
    def showHideCrosses(self):
        return self.showCross[0] | self.showCross[1] | self.showCross[2] | self.showCross[3]

    def connectCamera(self):
        logger.debug( "connectCamera called")
        self.disconnectPvs()
        if self.connectPvs():
            # Setup the callbacks:
            self.Pv_ArrayData[Glob.pv].monitor_cb      = self.imagePvUpdateCallback
            self.rowPv.monitor_cb       = self.sizeCallback
            self.colPv.monitor_cb       = self.sizeCallback
            self.Pv_Gain_RBV[Glob.pv].monitor_cb      = self.gainCallback
            self.Pv_Exposure_RBV[Glob.pv].monitor_cb  = self.exposureCallback
            self.Pv_BinX_RBV[Glob.pv].monitor_cb      = self.binXYCallback
            self.Pv_BinY_RBV[Glob.pv].monitor_cb      = self.binXYCallback
            # Now, before we monitor, update the camera size!
            self.setImageSize(self.colPv.value, self.rowPv.value)
            evtmask = pyca.DBE_VALUE
            self.Pv_ArrayData[Glob.pv].monitor(evtmask)
            self.rowPv.monitor(evtmask)
            self.colPv.monitor(evtmask)
            self.Pv_Gain_RBV[Glob.pv].monitor(evtmask)
            self.Pv_Exposure_RBV[Glob.pv].monitor(evtmask)
            self.Pv_BinX_RBV[Glob.pv].monitor(evtmask)
            self.Pv_BinY_RBV[Glob.pv].monitor(evtmask)
            pyca.flush_io()
            # After everythin OK:
            self.gui.idock[self.cam_n].setWindowTitle(self.gui.lCameraDesc[self.cam_n])
            self.onExposureUpdate()
            self.onGainUpdate()
            self.onBinXYUpdate()
            #self.onColorMapUpdate()
            #self.setColorMap()            
            self.camera_on = True
            self.rfshTimer.start(1000)
            logger.debug("Camera connection succeded. Camera is %s", 'ON' if self.camera_on else 'OFF')
        else:
            logger.error("Camera connection failed. Camera is %s", 'ON' if self.camera_on else 'OFF')
            self.camera_on = False
        return self.camera_on

    def disconnectCamera(self):
        logger.debug( "disconnectCamera called")
        self.disconnectPvs()
        self.gui.idock[self.cam_n].setWindowTitle('')
        self.gui.lb_dispRate.setText("-") 
        self.rfshTimer.stop()
        self.camera_on = False 


#    def onColorMapUpdate(self):
#      #print "onColorMapUpdate() called"
#      try: #assume radiobuttons auto-exclusives
#          if   self.colorMap == 'jet':
#              self.gui.rBColor_Jet.setChecked(True)
#          elif self.colorMap == 'hsv':
#              self.gui.rBColor_HSV.setChecked(True)
#          elif self.colorMap == 'cool':
#              self.gui.rBColor_Cool.setChecked(True)
#          elif self.colorMap == 'gray':
#              self.gui.rBColor_Gray.setChecked(True)
#          elif self.colorMap == 'hot':
#              self.gui.rBColor_Hot.setChecked(True)
#          else:
#              pass
#          #print 'ColorMap updated'
#      except:
#        pass  
    
    # Note: this function is called by the CA library, from another thread
    def imagePvUpdateCallback(self, exception=None):
        if exception is None:
            currentTime       =  time.time()
            self.dataUpdates  += 1
            self.callInterval =  currentTime - self.lastImageUpdateDispTime
            if self.callInterval < self.lastImageProcessingTime:
                #logger.info( "Image update interval %.3f < Image Update Processing Time: %.3f" % (callInterval, self.lastImageProcessingTime) )
                return
            if self.callInterval < 1.0/self.displayRateMax:# throttle the display speed
                return
            self.lastImageUpdateDispTime = currentTime    
            ### commented next 2 lines for performance test purposes
            # Send out the signal to notify windows update (in the GUI thread)
            ###self.event.emit(QtCore.SIGNAL("onImageUpdate")) 
        else:
            logger.error( "imagePvUpdateCallback(): %-30s " %(self.name), exception)
            pass
    
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
      dispRate             = (float)(dispUpdates) / delta
      dataUpdates          = self.dataUpdates - self.lastDataUpdates
      dataRate             = (float)(dataUpdates) / delta
      #print 'UpdateRate[local, gui]', self.cam_n, self.gui.cam_n
      #print 'UpdateRate  [%d][%d]' % (self.gui.cam_n, self.cam_n), repr(self.rfshTimer), self.dispUpdates, dataRate
      self.emit(QtCore.SIGNAL("onUpdateRate(int, float, float)"), self.cam_n, dispRate, dataRate)
    
      self.lastUpdateTime  = now
      self.lastDispUpdates = self.dispUpdates
      self.lastDataUpdates = self.dataUpdates
      self.updateImage()
      
    def setColorMap(self, colormapfile=None):
      #print 'setColorMap called [CAM%d] %s' % (self.cam_n, self.colorMap)
      #logger.debug( 'self.cam_n %s', self.cam_n)
      #logger.debug( 'ViewerFrame setColorMap called, new      %s', colormapfile)
      #logger.debug( 'ViewerFrame setColorMap called, current: %s', self.colormapfile)
      ####self.iScaleIndex = self.gui.iScaleIndex
      #logger.debug('setColorMap self.gui.cwd %s', self.gui.cwd)
      #logger.debug('setColorMap self.colorMap %s', self.colorMap)
      if self.colormapfile == colormapfile:
          return False
      
      if colormapfile:
          fnColorMap = self.gui.cwd + "/" + colormapfile
          mantaGiGE.pydspl_setup_color_map(self.imageBuffer, fnColorMap, self.iRangeMin, self.iRangeMax, self.iScaleIndex)
      else:
          mantaGiGE.pydspl_setup_gray(self.imageBuffer, self.iRangeMin, self.iRangeMax, self.iScaleIndex)
      self.colormapfile = colormapfile
#      if self.colorMap != "gray":
#        fnColorMap = self.gui.cwd + "/" + self.colorMap + ".txt"
#        mantaGiGE.pydspl_setup_color_map(self.imageBuffer, fnColorMap, self.iRangeMin, self.iRangeMax, self.iScaleIndex)
#      else:
#        mantaGiGE.pydspl_setup_gray(self.imageBuffer, self.iRangeMin, self.iRangeMax, self.iScaleIndex)
      
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
      if self.Pv_ArrayData[Glob.pv] != None:
        if self.Pv_ArraySize0_RBV[Glob.pv].value == 3: # It's a color camera!
          self.Pv_ArrayData[Glob.pv].processor  = mantaGiGE.pyCreateColorImagePvCallbackFunc(self.imageBuffer)
          self.gui.cBgrayScale.setEnabled(True)
        else:
          self.Pv_ArrayData[Glob.pv].processor  = mantaGiGE.pyCreateImagePvCallbackFunc(self.imageBuffer)
          self.gui.cBgrayScale.setEnabled(False)
        mantaGiGE.pySetImageBufferGray(self.imageBuffer, self.gui.cBgrayScale.isChecked())
    
    def onCheckGrayUpdate(self, newval):
      mantaGiGE.pySetImageBufferGray(self.imageBuffer, newval)
      #if self.gui.cfg == None: self.gui.dumpConfig()
    
    def updateall(self):
      #logger.debug( "updateall called")
      self.display_image.setGeometry(QtCore.QRect(0, 0, self.parent.width(), self.parent.height()))
      self.display_image.scaled_image = self.display_image.image.scaled(self.parent.width(), self.parent.height(), 
                     QtCore.Qt.KeepAspectRatio,
                     QtCore.Qt.SmoothTransformation)   
      #self.display_image.updateGeometry()
      self.display_image.repaint()
      self.display_image.update()
      
      
      
      
      
    # FROM CALL BACK FUNCTIONS: ------------------------------------------------
    # Note: this function is called by the CA library, from another thread
    def sizeCallback(self, exception=None):
      if exception is None: self.onSizeUpdate()
      else: logger.error( "sizeCallback(): %-30s " % exception )

    def onSizeUpdate(self):
        logger.debug('onSizeUpdate called')
        newx = self.colPv.value ; newy = self.rowPv.value
        if newx != self.x or newy != self.y:
            self.setImageSize(newx, newy)

    # Note: this function is called by the CA library, from another thread
    def gainCallback(self, exception=None):
        if not self.controlling:
            if exception is None: self.onGainUpdate()
            else: logger.error("gainCallback(): %-30s " % exception )

    def onGainUpdate(self):
        logger.debug("onGainUpdate() called")
        if self.gui.iS_gain.value() != int(self.Pv_Gain_RBV[Glob.pv].value) and self.cam_n == self.gui.cam_n:
            self.gui.iS_gain.setValue(int(self.Pv_Gain_RBV[Glob.pv].value))

    # Note: this function is called by the CA library, from another thread
    def exposureCallback(self, exception=None):
        if not self.controlling:
           if exception is None: self.onExposureUpdate()
           else: logger.error( "exposureCallback(): %-30s " % exception )

    def onExposureUpdate(self):
        logger.debug("onExposureUpdate() called")
        if self.gui.dS_expt.value() != float(self.Pv_Exposure_RBV[Glob.pv].value) and self.cam_n == self.gui.cam_n:
            self.gui.dS_expt.setValue(float(self.Pv_Exposure_RBV[Glob.pv].value))

    # Note: this function is called by the CA library, from another thread
    def binXYCallback(self, exception=None):
        if not self.controlling:
            if exception is None: self.onBinXYUpdate()
            else: logger.error( "binXYCallback(): %-30s " % exception )

    def onBinXYUpdate(self):
        logger.debug("onBinXYUpdate() called")
        if self.gui.lEBXY.text() != str(self.Pv_BinX_RBV[Glob.pv].value) and self.cam_n == self.gui.cam_n:
            self.gui.lEBXY.setText(str(self.Pv_BinX_RBV[Glob.pv].value))
    # --------------------------------------------------------------------------
    
    def connectPvs(self):
        logger.debug( "connectPvs called")
        # Monitor Pvs:
        if not self.connectPv(self.Pv_Gain_RBV):
            return False
        if not self.connectPv(self.Pv_Exposure_RBV):
            return False
        if not self.connectPv(self.Pv_BinX_RBV):
            return False
        if not self.connectPv(self.Pv_BinY_RBV):
            return False
        if not self.connectPv(self.Pv_ArraySize0_RBV):
            return False
        if not self.connectPv(self.Pv_ArraySize1_RBV):
            return False
        if not self.connectPv(self.Pv_ArraySize2_RBV):
            return False
        if not self.connectPv(self.Pv_ArrayData):
            return False
        # Control Pvs (need to know the data type):
        if not self.connectPv(self.Pv_Gain):     # int
            return False
        if not self.connectPv(self.Pv_Exposure): # float
            return False
        if not self.connectPv(self.Pv_BinX):     # int
            return False
        if not self.connectPv(self.Pv_BinY):     # int
            return False
        
        if self.Pv_ArraySize0_RBV[Glob.pv].value == 3: # It's a color camera!
            logger.debug( "It's a Color Camera")
            self.gui.setSliderRangeMax(10) # 10 bits camera
            self.gui.cBgrayScale.setEnabled(True)
            self.rowPv = self.Pv_ArraySize2_RBV[Glob.pv] ; self.colPv = self.Pv_ArraySize1_RBV[Glob.pv]
            self.Pv_ArrayData[Glob.pv].processor = mantaGiGE.pyCreateColorImagePvCallbackFunc(self.imageBuffer)
        else: # Just B/W!
            logger.debug( "It's a Black&White Camera")
            self.gui.setSliderRangeMax(8) # 8 bits camera
            self.gui.cBgrayScale.setEnabled(False)
            self.rowPv = self.Pv_ArraySize1_RBV[Glob.pv] ; self.colPv = self.Pv_ArraySize0_RBV[Glob.pv]
            self.Pv_ArrayData[Glob.pv].processor = mantaGiGE.pyCreateImagePvCallbackFunc(self.imageBuffer)
        return True

    def connectPv(self, pvobj,timeout=1.0, nretries=2):
        ''' Try <nretries> to connect to pvobj[Glob.name] with <timeout>. 
            If success then it returns True else False.'''
        if pvobj[Glob.pv] != None:
            pvobj[Glob.pv].disconnect()
            pyca.flush_io()
        pvobj[Glob.pv] = None
        for i in range(nretries):
            try:
                pvobj[Glob.pv] = Pv(pvobj[Glob.name])
                pvobj[Glob.pv].connect(timeout)
                pvobj[Glob.pv].get(False, timeout)
                self.connectedPvs.append(pvobj) # needed later for disconnect all on exit
                logger.debug('[  OK  ] %s %s' % (pvobj[Glob.name], pvobj[Glob.pv]))
                return True
            except:
                logger.debug('[ FAIL ] %s %s' % (pvobj[Glob.name], pvobj[Glob.pv]))
                logger.error('ERROR: Couldn\'t get %s . Retrying %s/%s...',  (pvobj[Glob.name], i, nretries))
        pvobj[Glob.pv] = None
        return False

    def disconnectPv(self, pv):
        '''Disconnects Pv <pv> individually (not used here...)'''
        if pv != None:
            pv.disconnect();
            pyca.flush_io()
        return None

    def disconnectPvs(self):
        '''Disconnects all pvs that are in the connectedPvs list'''
        logger.debug('disconnectPvs called')
        for pv_item in self.connectedPvs:
            oldpv = pv_item[Glob.pv]
#            logger.debug('Pv %s was    %s' % (pv_item[Glob.name], str(pv_item[Glob.pv])))
            if pv_item[Glob.pv]:
                pv_item[Glob.pv].disconnect()
                pv_item[Glob.pv] = None
            if not pv_item[Glob.pv]:
                logger.debug('[  OK  ] Pv %s is disconnected was %s, now %s'% (pv_item[Glob.name], oldpv, str(pv_item[Glob.pv])))
                pass
        pyca.flush_io()

    def pvget(self, pvobj, timeout=1.0):
        try:
            pvobj[Glob.pv].get(ctrl=False, timeout=timeout)
            return pvobj[Glob.pv].value
        except pyca.pyexc, e:
            logger.error('pyca exception: %s' % (e))
            return []
        except pyca.caexc, e:
            logger.error('channel access exception: %s' % (e))
            return []

    def pvput(self, pvobj, val, timeout=1.0):
        try:
            pvobj[Glob.pv].put(val, timeout=timeout)
            return True
        except pyca.pyexc, e:
            logger.error('pyca exception: %s' % (e))
            return []
        except pyca.caexc, e:
            logger.error('channel access exception: %s' % (e))
            return []
