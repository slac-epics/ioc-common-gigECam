#! /usr/bin/env python

# ----- Camera UI -----
from prosilica1350_ui import Ui_GigEImageViewer

# ----- EPICS Channel Access and PV's -----
from Pv import Pv
import pycaqt
import pyca

from PyQt4 import QtCore
from PyQt4.QtGui import QWidget, QImage, QPainter
from PyQt4.QtGui import QPen, QBrush, QMainWindow, QMessageBox
from PyQt4.QtCore import QTimer, Qt, QPoint, QSize

import time
import threading
import logging


# TODO -- the code needs major cleanup


# ----- the camera -----

class Camera():

    def __init__(self, name):
        self.name = name
        self.last_img_counter = -1
        stat, data = self.caget('Cross1X_RBV')
        if stat > 0:
            self._cross1X = data
        else:
            self._cross1X = 0
        stat, data = self.caget('Cross1Y_RBV')
        if stat > 0:
            self._cross1Y = data
        else:
            self._cross1Y = 0
        stat, data = self.caget('Cross1Color_RBV')
        if stat > 0:
            self._cross1Color = data
        else:
            self._cross1Color = 0
        stat, data = self.caget('Cross2X_RBV')
        if stat > 0:
            self._cross2X = data
        else:
            self._cross2X = 0
        stat, data = self.caget('Cross2Y_RBV')
        if stat > 0:
            self._cross2Y = data
        else:
            self._cross2Y = 0
        stat, data = self.caget('Cross2Color_RBV')
        if stat > 0:
            self._cross2Color = data
        else:
            self._cross2Color = 0

    def setExpTime(self, val):
        self.caput("AcquireTime", float(val))

    def setExpPeriod(self, val):
        self.caput("AcquirePeriod", float(val))

    def setGain(self, val):
        self.caput("Gain", float(val))

    # def setRoiXStart(self, val):
        # self.caput("MinX", int(val))

    # def setRoiXSize(self, val):
        # self.caput("SizeX", int(val))

    # def setRoiYStart(self, val):
        # self.caput("MinY", int(val))

    # def setRoiYSize(self, val):
        # self.caput("SizeY", int(val))

    # def roiXStart(self):
        # stat, data = self.caget("MinX_RBV")
        # return stat, str(data)

    # def roiXSize(self):
        # stat, data = self.caget("SizeX_RBV")
        # return stat, str(data)

    # def roiYStart(self):
        # stat, data = self.caget("MinY_RBV")
        # return stat, str(data)

    # def roiYSize(self):
        # stat, data = self.caget("SizeY_RBV")
        # return stat, str(data)

    # def setBinX(self, val):
        # self.caput("BinX", int(val))
        # self.caput("BinY", int(val))

    def setCross1X(self, val):
        #logging.debug(  "Setting cross1 X = %d" % int(val) )
        self.caput("Cross1X", int(val))
        self._cross1X = int(val)

    def setCross1Y(self, val):
        self.caput("Cross1Y", int(val))
        self._cross1Y = int(val)

    def setCross2X(self, val):
        self.caput("Cross2X", int(val))
        self._cross2X = int(val)

    def setCross2Y(self, val):
        self.caput("Cross2Y", int(val))
        self._cross2Y = int(val)

    # def binX(self):
        # stat, data = self.caget("BinX_RBV")
        # return stat, str(data)

    def cross1X(self):
        #logging.debug(  "Getting cross1 X : %d" % self._cross1X )
        return 1, self._cross1X

    def cross1Y(self):
        return 1, self._cross1Y

    def cross2X(self):
        return 1, self._cross2X

    def cross2Y(self):
        return 1, self._cross2Y

    def selectCross1Color(self, val):
        self.caput("Cross1Color", int(val))
        self._cross1Color = int(val)

    def cross1Color(self):
        return 1, self._cross1Color

    def selectCross2Color(self, val):
        self.caput("Cross2Color", int(val))
        self._cross2Color = int(val)

    def cross2Color(self):
        return 1, self._cross2Color

    def imageMode(self):
        stat, data = self.caget("ImageMode_RBV")
        return stat, int(data)

    def selectImageMode(self, val):
        self.caput("ImageMode", int(val))

    def triggerMode(self):
        stat, data = self.caget("TriggerMode_RBV")
        return stat, int(data)

    def selectTriggerMode(self, val):
        self.caput("TriggerMode", int(val))

    def start(self):
        logging.debug(  "starting ..." )
        self.caput("ArrayCallbacks", 1)
        self.caput("ColorMode", 2)
        self.caput("DataType", 0)
        self.caput("Acquire", 1)

    def stop(self):
        logging.debug(  "stopping ..." )
        self.caput("Acquire", 0)

    def caget(self, pvname, timeout=1.0):
      try:
        pv = Pv(self.name + ":" + pvname)
        #logging.debug(  "caget: " + self.name + ":" + pvname )
        pv.connect(timeout)
        pv.get(ctrl=False, timeout=timeout)
        pv.disconnect()
        return (1, pv.value)
      # except pyca.pyexc, e:
        logging.debug(  'pyca exception: %s' %(e) )
      except pyca.pyexc:
        pass
      # except pyca.caexc, e:
        logging.debug(  'channel access exception: %s' %(e) )
      except pyca.caexc:
        pass
      return (-1, 0)

    def caput(self, pvname, value, timeout=1.0):
      try:
        #logging.debug(  "caput: " + self.name + ":" + pvname )
        pv = Pv(self.name + ":" + pvname)
        pv.connect(timeout)
        pv.get(ctrl=False, timeout=timeout)
        pv.put(value, timeout)
        pv.disconnect()
      except pyca.pyexc, e:
         logging.debug(  'pyca exception: %s' %(e) )
         pass
      except pyca.caexc, e:
         logging.debug(  'channel access exception: %s' %(e) )
         pass


class DisplayImage(QWidget):
  xres = 1360;
  yres = 1024;
  def __init__(self, parent, gui):
    QWidget.__init__(self, parent)
    self.__gui = gui
    size = QSize(DisplayImage.xres, DisplayImage.yres)
    self.image = QImage(size, QImage.Format_RGB32)
    self.painter = QPainter()
    self.where = QPoint(0,0)
    self.paintevents = 0

  def paintEvent(self, event):
    if self.__gui.updates > 0:
      self.paintevents += 1
      self.painter.begin(self)
      self.painter.drawImage(self.where, self.image)
      self.drawCross(self.painter)
      self.painter.end()

  def drawCross(self, qp):
      cur_cam = self.__gui.current_cam_num
      self.cam = self.__gui.cameras[ cur_cam ]
      stat, color = self.cam.cross1Color()
      if color == 0:
          color = None
      elif color == 1:
          color = Qt.black
      elif color == 2:
          color = Qt.red
      elif color == 3:
          color = Qt.green
      elif color == 4:
          color = Qt.blue
      elif color == 5:
          color = Qt.white
      width = 1
      if color != None:
          style = Qt.SolidLine
          pen = QPen(QBrush(color), width, style)
          qp.setPen(pen)
          stat, x1 = self.cam.cross1X()
          stat, y1 = self.cam.cross1Y()
          #logging.debug(  "Drawing cross1 @ %d %d" % (x1, y1) )
          qp.drawLine( x1-5, y1, x1+5, y1)
          qp.drawLine( x1, y1-5, x1, y1+5)

      stat, color = self.cam.cross2Color()
      if color == 0:
          color = None
      elif color == 1:
          color = Qt.black
      elif color == 2:
          color = Qt.red
      elif color == 3:
          color = Qt.green
      elif color == 4:
          color = Qt.blue
      elif color == 5:
          color = Qt.white
      width = 1
      if color != None:
          style = Qt.SolidLine
          pen = QPen(color, width, style)
          qp.setPen(pen)
          stat, x2 = self.cam.cross2X()
          stat, y2 = self.cam.cross2Y()
          x2 = int(x2); y2 = int(y2)
          qp.drawLine( x2-5, y2, x2+5, y2)
          qp.drawLine( x2, y2-5, x2, y2+5)


class GraphicUserInterface(QMainWindow, Ui_GigEImageViewer):
    def __init__(self, app, pv):
        QMainWindow.__init__(self)
        self.__app = app
        self.rfshTimer = QTimer()
        self.setupUi(self)
        self.image_frame.setFixedSize(DisplayImage.xres, DisplayImage.yres)

        # local modifications

        self.pvbase = pv
        self.camera_pvs = []
        self.image_pvs = []
        self.cameras = []
        for n in range( 2):
            cam_name = pv + ":cam" + str( n + 1 )
            img_name = pv + ":image" + str( n + 1 ) + ":ArrayData"
            self.camera_pvs.append( cam_name )
            self.image_pvs.append( img_name )
            self.cameras.append( Camera(cam_name) )

        self.cbCamera.addItems( self.camera_pvs )
        self.cbCamera.setCurrentIndex(0)

        self.current_cam_num = 0
        self.cam = self.cameras[self.current_cam_num]

        colors = ('None', 'Black', 'Red', 'Green', 'Blue', 'White')
        self.cbCross1Color.addItems( colors )
        stat, mode = self.cam.cross1Color()
        if stat > 0:
            self.cbCross1Color.setCurrentIndex(mode)
        else:
            pass

        self.cbCross2Color.addItems( colors )
        stat, mode = self.cam.cross2Color()
        if stat > 0:
            self.cbCross2Color.setCurrentIndex(mode)
        else:
            pass

        self.cbImageMode.addItems( ('Single', 'Multiple', 'Continuous') )
        stat, mode = self.cam.imageMode()
        if stat > 0:
            self.cbImageMode.setCurrentIndex(mode)
        else:
            pass

        modes = ('Free Run', 'Sync In 1', 'Sync In 2', 'Sync In 3',
                 'Sync In 4', 'Fixed Rate', 'Software')
        self.cbTriggerMode.addItems( modes )
        stat, mode = self.cam.triggerMode()
        if stat > 0:
            self.cbTriggerMode.setCurrentIndex(mode)
        else:
            pass

        # Connect up the buttons.
        self.connect(self.cbCamera, QtCore.SIGNAL("currentIndexChanged(int)"), self.go)
        self.leExpTime.editingFinished.connect(self.expTime)
        self.leExpPeriod.editingFinished.connect(self.expPeriod)
        self.leGain.editingFinished.connect(self.gain)
        # self.leRoiXStart.editingFinished.connect(self.roiXStart)
        # self.leRoiXSize.editingFinished.connect(self.roiXSize)
        # self.leRoiYStart.editingFinished.connect(self.roiYStart)
        # self.leRoiYSize.editingFinished.connect(self.roiYSize)
        # self.leBinX.editingFinished.connect(self.binX)
        self.leCross1X.editingFinished.connect(self.cross1X)
        self.leCross1Y.editingFinished.connect(self.cross1Y)
        self.leCross2X.editingFinished.connect(self.cross2X)
        self.leCross2Y.editingFinished.connect(self.cross2Y)
        self.connect(self.cbCross1Color, QtCore.SIGNAL("currentIndexChanged(int)"), self.selectCross1Color)
        self.connect(self.cbCross2Color, QtCore.SIGNAL("currentIndexChanged(int)"), self.selectCross2Color)
        self.connect(self.cbImageMode, QtCore.SIGNAL("currentIndexChanged(int)"), self.selectImageMode)
        self.connect(self.cbTriggerMode, QtCore.SIGNAL("currentIndexChanged(int)"), self.selectTriggerMode)
        self.bStart.clicked.connect(self.startClicked)
        self.bStop.clicked.connect(self.stopClicked)

        self.last_time = time.time()
        self.updates = 0
        self.last_updates = 0
        self.display_image = DisplayImage(self.image_frame, self)
        self.display_image.setFixedSize(DisplayImage.xres, DisplayImage.yres)
        self.__connection_sem = threading.Event()
        self.__connected = False
        self.image = None

        self.connect(self.rfshTimer, QtCore.SIGNAL("timeout()"), self.UpdateTime)
        self.rfshTimer.start(1000)

        self.go( 0 )

    # ----- action routines -----

    def startClicked(self):
        logging.debug(  "start clicked" )
        try:
            self.cam.start()
        except:
            pass

    def stopClicked(self):
        logging.debug(  "stop clicked" )
        try:
            self.cam.stop()
        except:
            pass

    def selectCurrentCamera(self, val):
        self.current_cam_num = val
        self.cam = self.cameras[val]
        #logging.debug(  "Selecting camera %d" % (val + 1) )
        self.clearEntryFields()

    def clearEntryFields(self):
        #logging.debug(  "Clearing data entry fields" )
        self.leExpTime.setText('')
        self.leExpPeriod.setText('')
        self.leGain.setText('')
        self.leRoiXStart.setText('')
        self.leRoiXSize.setText('')
        self.leRoiYStart.setText('')
        self.leRoiYSize.setText('')
        self.leBinX.setText('')
        self.leCross1X.setText('')
        self.leCross1Y.setText('')
        self.leCross2X.setText('')
        self.leCross2Y.setText('')

    def expTime(self):
        self.cam.setExpTime(self.leExpTime.text())

    def expPeriod(self):
        self.cam.setExpPeriod(self.leExpPeriod.text())

    def gain(self):
        self.cam.setGain(self.leGain.text())

    # def roiXStart(self):
        # self.cam.setRoiXStart(self.leRoiXStart.text())

    # def roiXSize(self):
        # self.cam.setRoiXSize(self.leRoiXSize.text())

    # def roiYStart(self):
        # self.cam.setRoiYStart(self.leRoiYStart.text())

    # def roiYSize(self):
        # self.cam.setRoiYSize(self.leRoiYSize.text())

    # def binX(self):
        # self.cam.setBinX(self.leBinX.text())

    def cross1X(self):
        self.cam.setCross1X(self.leCross1X.text())

    def cross1Y(self):
        self.cam.setCross1Y(self.leCross1Y.text())

    def cross2X(self):
        self.cam.setCross2X(self.leCross2X.text())

    def cross2Y(self):
        self.cam.setCross2Y(self.leCross2Y.text())

    def selectCross1Color(self, val):
        self.cam.selectCross1Color(val)

    def selectCross2Color(self, val):
        self.cam.selectCross2Color(val)

    def selectImageMode(self, val):
        self.cam.selectImageMode(val)

    def selectTriggerMode(self, val):
        self.cam.selectTriggerMode(val)

    def __clear(self):
        self.clearEntryFields()
        self.label_rate.setText("-")
        self.label_connected.setText("NO")
        if self.image is not None:
          try:
            self.image.disconnect()
          except:
            pass
          self.image = None

    def shutdown(self):
        self.__clear()
        self.rfshTimer.stop()

    def go(self, val):
        self.__clear()
        self.current_cam_num = val
        cam_pv = self.camera_pvs[ self.current_cam_num ]
        self.cam = self.cameras[self.current_cam_num]
        self.image_pv = self.image_pvs[ self.current_cam_num ]
        logging.debug(  cam_pv )
        print self.image_pv )

        self.pvs = {}
        self.pvs['ImageRate'] = Pv(cam_pv + ':ArrayRate_RBV')
        self.pvs['ImageCounter'] = Pv(cam_pv + ':ArrayCounter_RBV')
        self.pvs['ExpTime'] = Pv(cam_pv + ':AcquireTime_RBV')
        self.pvs['ExpPeriod'] = Pv(cam_pv + ':AcquirePeriod_RBV')
        self.pvs['Gain'] = Pv(cam_pv + ':Gain_RBV')
        self.pvs['Cross1X'] = Pv(cam_pv + ':Cross1X_RBV')
        self.pvs['Cross1Y'] = Pv(cam_pv + ':Cross1Y_RBV')
        self.pvs['Cross1Color'] = Pv(cam_pv + ':Cross1Color_RBV')
        self.pvs['Cross2X'] = Pv(cam_pv + ':Cross2X_RBV')
        self.pvs['Cross2Y'] = Pv(cam_pv + ':Cross2Y_RBV')
        self.pvs['Cross2Color'] = Pv(cam_pv + ':Cross2Color_RBV')

        # setup pv monitor callbacks

        self.image = Pv(self.image_pv)
        timeout = 1.0
        try:
          self.image.connect(timeout)
          self.label_connected.setText("YES")
          self.image.processor = \
                                pycaqt.pydspl_qimage_func(self.display_image.image)
          self.image.monitor_cb = self.UpdateImage
          evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM 
          self.image.monitor(evtmask)
          pyca.flush_io()
        except:
          self.label_connected.setText("NO")
          QMessageBox.critical(None,
                               "Error", "Failed to connect to camera %s" % cam_pv,
                               QMessageBox.Ok, QMessageBox.Ok)

        self.imageRate = self.pvs['ImageRate']
        timeout = 1.0
        try:
          self.imageRate.connect(timeout)
          self.imageRate.monitor_cb = self.updateImageRate
          evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM 
          self.imageRate.monitor(evtmask)
          pyca.flush_io()
        except:
          pass

        self.imageCounter = self.pvs['ImageCounter']
        timeout = 1.0
        try:
          self.imageCounter.connect(timeout)
          self.imageCounter.monitor_cb = self.updateImageCounter
          evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM 
          self.imageCounter.monitor(evtmask)
          pyca.flush_io()
        except:
          pass

        self.expTime = self.pvs['ExpTime']
        timeout = 1.0
        try:
          self.expTime.connect(timeout)
          self.expTime.monitor_cb = self.updateExpTime
          evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM 
          self.expTime.monitor(evtmask)
          pyca.flush_io()
        except:
          pass

        self.expPeriod = self.pvs['ExpPeriod']
        timeout = 1.0
        try:
          self.expPeriod.connect(timeout)
          self.expPeriod.monitor_cb = self.updateExpPeriod
          evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM 
          self.expPeriod.monitor(evtmask)
          pyca.flush_io()
        except:
          pass

        self.gain = self.pvs['Gain']
        timeout = 1.0
        try:
          self.gain.connect(timeout)
          self.gain.monitor_cb = self.updateGain
          evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM 
          self.gain.monitor(evtmask)
          pyca.flush_io()
        except:
          pass

        self.cross1X = self.pvs['Cross1X']
        timeout = 1.0
        try:
          self.cross1X.connect(timeout)
          self.cross1X.monitor_cb = self.updateCross1X
          evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM 
          self.cross1X.monitor(evtmask)
          pyca.flush_io()
        except:
          pass

        self.cross1Y = self.pvs['Cross1Y']
        timeout = 1.0
        try:
          self.cross1Y.connect(timeout)
          self.cross1Y.monitor_cb = self.updateCross1Y
          evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM 
          self.cross1Y.monitor(evtmask)
          pyca.flush_io()
        except:
          pass

        self.cross1Color = self.pvs['Cross1Color']
        timeout = 1.0
        try:
          self.cross1Color.connect(timeout)
          self.cross1Color.monitor_cb = self.updateCross1Color
          evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM 
          self.cross1Color.monitor(evtmask)
          pyca.flush_io()
        except:
          pass

        self.cross2X = self.pvs['Cross2X']
        timeout = 1.0
        try:
          self.cross2X.connect(timeout)
          self.cross2X.monitor_cb = self.updateCross2X
          evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM 
          self.cross2X.monitor(evtmask)
          pyca.flush_io()
        except:
          pass

        self.cross2Y = self.pvs['Cross2Y']
        timeout = 1.0
        try:
          self.cross2Y.connect(timeout)
          self.cross2Y.monitor_cb = self.updateCross2Y
          evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM 
          self.cross2Y.monitor(evtmask)
          pyca.flush_io()
        except:
          pass

        self.cross2Color = self.pvs['Cross2Color']
        timeout = 1.0
        try:
          self.cross2Color.connect(timeout)
          self.cross2Color.monitor_cb = self.updateCross2Color
          evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM 
          self.cross2Color.monitor(evtmask)
          pyca.flush_io()
        except:
          pass

    # update functions -- called when a pv changed value

    def UpdateImage(self, exception=None):
        try:
          if exception is None:
            self.updates += 1
            self.display_image.update()
          else:
             logging.debug(  "%-30s " %(self.name), exception )
             pass
        except Exception, e:
           logging.debug( "%s", exception )
           pass
           

    def updateImageRate(self, exception=None):
        logging.debug(  "In updateImageRate" )
        try:
          if exception is None:
               pv = self.pvs['ImageRate']
               data = pv.value
               self.disp_val(self.lImgRate, 1, data)
          else:
                     logging.debug(  "%-30s " %(self.name), exception )
               self.disp_val(self.lImgRate, -1, None)
        except Exception, e:
                logging.debug( "%s", exception )
                self.disp_val(self.lImgRate, -1, None)


    def updateImageCounter(self, exception=None):
        logging.debug(  "In updateImageCounter" )
        try:
          if exception is None:
            pv = self.pvs['ImageCounter']
            data = pv.value
            logging.debug(  "ImageCounter = " + data )
            self.disp_val(self.lImgCounter, 1, data)
          else:
            print "%-30s " %(self.name), exception )
            self.disp_val(self.lImgCounter, -1, None)
        except Exception, e:
          print "ImageCounter exception: " + e )
          self.disp_val(self.lImgCounter, -1, None)


    def updateExpTime(self, exception=None):
        logging.debug(  "In updateExpTime" )
        try:
          if exception is None:
               pv = self.pvs['ExpTime']
               data = pv.value
               self.disp_val(self.lExpTime, 1, data)
          else:
      logging.debug(  "%-30s " %(self.name), exception )
               self.disp_val(self.lExpTime, -1, None)
        except Exception, e:
    logging.debug( "%s", exception )
          self.disp_val(self.lExpTime, -1, None)


    def updateExpPeriod(self, exception=None):
        logging.debug(  "In updateExpPeriod" )
        try:
          if exception is None:
               pv = self.pvs['ExpPeriod']
               data = pv.value
               self.disp_val(self.lExpPeriod, 1, data)
          else:
             logging.debug(  "%-30s " %(self.name), exception )
             self.disp_val(self.lExpPeriod, -1, None)
        except Exception, e:
          logging.debug( "%s", exception )
          self.disp_val(self.lExpPeriod, -1, None)


    def updateGain(self, exception=None):
        logging.debug(  "In updateGain" )
        try:
          if exception is None:
                        pv = self.pvs['Gain']
                        data = pv.value
                        self.disp_val(self.lGain, 1, data)
          else:
                        logging.debug(  "%-30s " %(self.name), exception )
                     self.disp_val(self.lGain, -1, None)
        except Exception, e:
                logging.debug( "%s", exception )
                self.disp_val(self.lGain, -1, None)


    def updateCross1X(self, exception=None):
        #logging.debug(  "In updateCross1X" )
        try:
          if exception is None:
                        pv = self.pvs['Cross1X']
                        data = pv.value
                        self.disp_val(self.leCross1X, 1, data)
          else:
      logging.debug(  "%-30s " %(self.name), exception )
               self.disp_val(self.lGain, -1, None)
        except Exception, e:
    logging.debug( "%s", exception )
          self.disp_val(self.lGain, -1, None)

    def updateCross1Y(self, exception=None):
        logging.debug(  "In updateCross1Y" )
        try:
          if exception is None:
                        pv = self.pvs['Cross1Y']
                        data = pv.value
                        self.disp_val(self.leCross1Y, 1, data)
          else:
         logging.debug(  "%-30s " %(self.name), exception )
               self.disp_val(self.lGain, -1, None)
        except Exception, e:
    logging.debug( "%s", exception )
          self.disp_val(self.lGain, -1, None)

    def updateCross1Color(self, exception=None):
        logging.debug(  "In updateCross1Color" )
        try:
          if exception is None:
                        pv = self.pvs['Cross1Color']
                        data = pv.value
                        self.cbCross1Color.setCurrentIndex(data)
          else:
         logging.debug(  "%-30s " %(self.name), exception )
               self.disp_val(self.lGain, -1, None)
        except Exception, e:
    logging.debug( "%s", exception )
          self.disp_val(self.lGain, -1, None)

    def updateCross2X(self, exception=None):
        logging.debug(  "In updateCross2X" )
        try:
          if exception is None:
               pv = self.pvs['Cross2X']
               data = pv.value
               self.disp_val(self.leCross2X, 1, data)
          else:
      logging.debug(  "%-30s " %(self.name), exception )
               self.disp_val(self.lGain, -1, None)
        except Exception, e:
          logging.debug( "%s", exception )
          self.disp_val(self.lGain, -1, None)

    def updateCross2Y(self, exception=None):
        logging.debug(  "In updateCross2Y" )
        try:
          if exception is None:
            pv = self.pvs['Cross2Y']
            data = pv.value
            self.disp_val(self.leCross2Y, 1, data)
          else:
            logging.debug(  "%-30s " %(self.name), exception )
            self.disp_val(self.lGain, -1, None)
        except Exception, e:
          logging.debug( "%s", exception )
          self.disp_val(self.lGain, -1, None)

    def updateCross2Color(self, exception=None):
        logging.debug(  "In updateCross2Color" )
        try:
          if exception is None:
            pv = self.pvs['Cross2Color']
            data = pv.value
            self.cbCross1Color.setCurrentIndex(data)
          else:
            logging.debug(  "%-30s " %(self.name), exception )
            self.disp_val(self.lGain, -1, None)
        except Exception, e:
    logging.debug( "%s", exception )
          self.disp_val(self.lGain, -1, None)


    def UpdateTime(self):
        now = time.time()
        updates = self.updates - self.last_updates
        delta = now - self.last_time
        rate = updates/delta
        self.label_rate.setText('%.1f Hz' %rate)
        self.last_time = now
        self.last_updates = self.updates


    def disp_val(self, widget, stat, data):
        if stat > 0:
            widget.setText(str(data))
            widget.enabled = True
            widget.setEnabled(True)
        else:
            widget.setText('0')
            widget.setEnabled(False)
