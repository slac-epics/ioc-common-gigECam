#! /usr/bin/env python

from prosilica1350_ui import Ui_GigEImageViewer
from Pv import Pv
import pycaqt
import pyca
from pyca_widgets import PycaLabelConnection
from pyca_widgets import PycaLineEditConnection
from pyca_widgets import PycaComboBoxConnection
# from pyca_widgets import PycaPushButtonConnection

from PyQt4 import QtCore
from PyQt4.QtGui import QWidget, QImage, QPainter
from PyQt4.QtGui import QPen, QBrush, QMainWindow, QMessageBox
from PyQt4.QtCore import QTimer, Qt, QPoint, QSize

import time
import threading


# ----- the camera -----

class Camera():

    def __init__(self, name):
        self.name = name
        self.last_img_counter = -1

    # def setRoiXStart(self, val):
        # self.cam_put("MinX", int(val))

    # def setRoiXSize(self, val):
        # self.cam_put("SizeX", int(val))

    # def setRoiYStart(self, val):
        # self.cam_put("MinY", int(val))

    # def setRoiYSize(self, val):
        # self.cam_put("SizeY", int(val))

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
        # self.cam_put("BinX", int(val))
        # self.cam_put("BinY", int(val))

    # def binX(self):
        # stat, data = self.caget("BinX_RBV")
        # return stat, str(data)

    def start(self):
        # print "starting ..."
        self.cam_put("ArrayCallbacks", 1)
        self.cam_put("ColorMode", 2)
        self.cam_put("DataType", 0)
        self.cam_put("Acquire", 1)
        # FIXME: - caput 13PS1:image1:EnableCallbacks

    def stop(self):
        # print "stopping ..."
        self.cam_put("Acquire", 0)

    def cam_put(self, pvname, value, timeout=1.0):
        self.caput(pvname, value, timeout)

    def image_put(self, pvname, value, timeout=1.0):
        self.caput(pvname, value, timeout)

    def caput(self, pvname, value, timeout=1.0):
        try:
            ## print "caput: " + self.name + ":" + pvname
            pv = Pv(self.name + ":" + pvname)
            pv.connect(timeout)
            pv.get(ctrl=False, timeout=timeout)
            pv.put(value, timeout)
            pv.disconnect()
        except pyca.pyexc, e:
            # print 'pyca exception: %s' %(e)
            pass
        except pyca.caexc, e:
            # print 'channel access exception: %s' %(e)
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
      color = self.__gui.c1color.val
      if 0 <= color <= 5:
          color = (None, Qt.black, Qt.red, Qt.green, Qt.blue, Qt.white)[color]
      width = 1
      if color != None:
          style = Qt.SolidLine
          pen = QPen(QBrush(color), width, style)
          qp.setPen(pen)
          x1 = self.__gui.c1x.val
          y1 = self.__gui.c1y.val
          # print "Drawing cross1 @ %d %d" % (x1, y1)
          qp.drawLine( x1-5, y1, x1+5, y1)
          qp.drawLine( x1, y1-5, x1, y1+5)

      color = self.__gui.c2color.val
      if 0 <= color <= 5:
          color = (None, Qt.black, Qt.red, Qt.green, Qt.blue, Qt.white)[color]
      width = 1
      if color != None:
          style = Qt.SolidLine
          pen = QPen(color, width, style)
          qp.setPen(pen)
          x2 = self.__gui.c2x.val
          y2 = self.__gui.c2y.val
          x2 = int(x2); y2 = int(y2)
          # print "Drawing cross2 @ %d %d" % (x2, y2)
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

        cam_name = self.camera_pvs[0]
        PycaLabelConnection(cam_name + ':ArrayRate_RBV', self.lImgRate)
        PycaLabelConnection(cam_name + ':ArrayCounter_RBV', self.lImgCounter)
        PycaLabelConnection(cam_name + ':AcquireTime_RBV', self.lExpTime)
        PycaLineEditConnection(cam_name + ':AcquirePeriod', self.leExpPeriod)
        PycaLabelConnection(cam_name + ':AcquirePeriod_RBV', self.lExpPeriod)
        PycaLineEditConnection(cam_name + ':Gain', self.leGain)
        PycaLabelConnection(cam_name + ':Gain_RBV', self.lGain)
        self.c1x = PycaLineEditConnection(cam_name + ':Cross1X', self.leCross1X)
        # PycaLabelConnection(cam_name + ':Cross1X_RBV', self.lCross1X)
        self.c1y = PycaLineEditConnection(cam_name + ':Cross1Y', self.leCross1Y)
        # PycaLabelConnection(cam_name + ':Cross1Y_RBV', self.lCross1Y)
        self.c2x = PycaLineEditConnection(cam_name + ':Cross2X', self.leCross2X)
        # PycaLabelConnection(cam_name + ':Cross2X_RBV', self.lCross2X)
        self.c2y = PycaLineEditConnection(cam_name + ':Cross2Y', self.leCross2Y)
        # PycaLabelConnection(cam_name + ':Cross2Y_RBV', self.lCross2Y)

        colors = ('None', 'Black', 'Red', 'Green', 'Blue', 'White')
        self.c1color = PycaComboBoxConnection(cam_name + ':Cross1Color', \
                                              self.cbCross1Color, \
                                              items = colors)
        self.c2color = PycaComboBoxConnection(cam_name + ':Cross2Color', \
                                              self.cbCross2Color, \
                                              items = colors)

        image_modes = ('Single', 'Multiple', 'Continuous')
        PycaComboBoxConnection(cam_name + ':ImageMode', \
                               self.cbImageMode, \
                               items = image_modes)

        trigger_modes = ('Free Run', 'Sync In 1', 'Sync In 2', 'Sync In 3', \
                         'Sync In 4', 'Fixed Rate', 'Software')
        PycaComboBoxConnection(cam_name + ':TriggerMode', \
                               self.cbTriggerMode, \
                               items = trigger_modes)

        self.current_cam_num = 0
        self.cam = self.cameras[self.current_cam_num]


        # Connect up the buttons.
        self.connect(self.cbCamera, QtCore.SIGNAL("currentIndexChanged(int)"), self.go)
        # self.leRoiXStart.editingFinished.connect(self.roiXStart)
        # self.leRoiXSize.editingFinished.connect(self.roiXSize)
        # self.leRoiYStart.editingFinished.connect(self.roiYStart)
        # self.leRoiYSize.editingFinished.connect(self.roiYSize)
        # self.leBinX.editingFinished.connect(self.binX)
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
        # print "start clicked"
        try:
            self.cam.start()
        except:
            pass

    def stopClicked(self):
        # print "stop clicked"
        try:
            self.cam.stop()
        except:
            pass

    def selectCurrentCamera(self, val):
        self.current_cam_num = val
        self.cam = self.cameras[val]
        ## print "Selecting camera %d" % (val + 1)
        self.clearEntryFields()

    def clearEntryFields(self):
        ## print "Clearing data entry fields"
        self.leRoiXStart.setText('')
        self.leRoiXSize.setText('')
        self.leRoiYStart.setText('')
        self.leRoiYSize.setText('')
        self.leBinX.setText('')

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

        # TODO: initialize area detector module

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

    # update functions -- called when a pv changed value

    def UpdateImage(self, exception=None):
        try:
          if exception is None:
            self.updates += 1
            self.display_image.update()
          else:
#            print "%-30s " %(self.name), exception
             pass
        except Exception, e:
#          print e
           pass
           

    def UpdateTime(self):
        now = time.time()
        updates = self.updates - self.last_updates
        delta = now - self.last_time
        rate = updates/delta
        self.label_rate.setText('%.1f Hz' %rate)
        self.last_time = now
        self.last_updates = self.updates

