#! /bin/env python

import sys
import time
import logging
import math
from PycaImage import PycaImage
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QPainter
from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QWidget
from PyQt4.QtCore import QRect
from PyQt4.QtGui import QPen, QBrush
from PyQt4.QtCore import Qt
from GigEViewer_ui import Ui_MainWindow
from pyca_widgets import *


class DisplayImage(QWidget):
    # A widget for displaying an image from a GigE camera
    def __init__(self, parent, img, gui):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.image = img.img
        self.gui = gui
        self.scaled_image = img.img
        self.xoff = 0
        self.yoff = 0
        self.scale = 1.0
        self.old_width = 0
        self.old_height = 0
        self.roiXoff = 0
        self.roiYoff = 0
        self.binning = 0
        self.painter = QPainter()
        img.set_new_image_callback(self.set_image)
        self.updates = 0
        self.last_updates = 0
        self.last_time = time.time()
        self.rateTimer = QTimer()
        self.rateTimer.timeout.connect(self.calcDisplayRate)
        self.rateTimer.start(1000)
        self.ROIX = -1
        self.ROIY = 0
        self.ROIW = 0
        self.ROIH = 0

    def paintEvent(self, event):
        self.painter.begin(self)
        if self.scaled_image:
            self.painter.drawImage(self.xoff, self.yoff, self.scaled_image)
            try:
                color = self.gui.cbCross1Color.currentIndex()
                if color:
                    x = int(self.gui.leCross1X.text())
                    y = int(self.gui.leCross1Y.text())
                    self.drawCross(self.painter, x, y, color)
            except Exception, e:
                # logging.debug("%s", e)
                pass
            try:
                color = self.gui.cbCross2Color.currentIndex()
                if color:
                    x = int(self.gui.leCross2X.text())
                    y = int(self.gui.leCross2Y.text())
                    self.drawCross(self.painter, x, y, color)
            except Exception, e:
                # logging.debug("%s", e)
                pass
            if self.ROIX >= 0:
                x = self.ROIX
                y = self.ROIY
                w = self.ROIW
                h = self.ROIH
                self.drawRect(self.painter, x, y, w, h)
        self.painter.end()
        self.updates += 1

    def isPointOnROIImage(self, x, y):
        # logging.debug("ROI: x=%d y=%d w=%d h=%d", self.roiXoff, self.roiYoff, self.image.width(), self.image.height())
        # logging.debug("%s", self.roiXoff <= x and x <= self.roiXoff + self.image.width() and self.roiYoff <= y and y <= self.roiYoff + self.image.height())
        return self.roiXoff <= x and x <= self.roiXoff + self.image.width() * self.binning and \
               self.roiYoff <= y and y <= self.roiYoff + self.image.height() * self.binning

    def drawCross(self, qp, x, y, color):
        # logging.debug("x=%d y=%d color=%d", x, y, color)
        if (color == 0) or not self.isPointOnROIImage(x, y):
            return

        if color == 1:
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
        pen = QPen(QBrush(color), width, style = Qt.SolidLine)
        qp.setPen(pen)
        x -= self.roiXoff
        y -= self.roiYoff
        x /= self.binning
        y /= self.binning
        x *= self.scale
        y *= self.scale
        x += self.xoff
        y += self.yoff
        # logging.debug("x=%d  y=%d", x, y)
        qp.drawLine( x-5, y, x+5, y)
        qp.drawLine( x, y-5, x, y+5)

    def drawRect(self, qp, x, y, w, h):
        color = Qt.white
        # if (color == 0) or not self.isPointOnROIImage(x, y) or not self.isPointOnROIImage(x+w, y+h):
            # return

        logging.debug("x=%d y=%d w=%d h=%d", x, y, w, h)
        color = Qt.white
        width = 1
        pen = QPen(QBrush(color), width, style = Qt.DashLine)
        qp.setPen(pen)
        qp.drawRect( x, y, w, h )

    def resizeEvent(self, event):
        if self.image:
            # logging.debug("frame size: %d x %d", self.width(), self.height())
            self.scaled_image = self.image.scaled(self.width(), self.height(), aspectRatioMode = Qt.KeepAspectRatio)
            self.xoff = ( self.width() - self.scaled_image.width() ) / 2
            self.yoff = ( self.height() - self.scaled_image.height() ) / 2
            try:     # avoid a possible division by zero
                self.scale = float(self.scaled_image.width()) / self.image.width()
            except:
                self.scale = 1.0

    def mousePressEvent(self, ev):
        logging.debug("mousePressEvent:  x=%d  y=%d" % (ev.x(), ev.y()))
        if self.gui.bCross1.isChecked():
            x, y = self.screen2imgTransform(ev.x(), ev.y())
            if self.isPointOnROIImage(x, y):
                self.gui.leCross1X.setText("%.0f" % x)
                self.gui.leCross1Y.setText("%.0f" % y)
                self.gui.myCross1XLE.update_pv()
                self.gui.myCross1YLE.update_pv()
        if self.gui.bCross2.isChecked():
            x, y = self.screen2imgTransform(ev.x(), ev.y())
            if self.isPointOnROIImage(x, y):
                self.gui.leCross2X.setText("%.0f" % x)
                self.gui.leCross2Y.setText("%.0f" % y)
                self.gui.myCross2XLE.update_pv()
                self.gui.myCross2YLE.update_pv()
        if self.gui.bSelectROI.isChecked():
            x, y = self.screen2imgTransform(ev.x(), ev.y())
            if self.isPointOnROIImage(x, y):
                self.ROIX = ev.x()
                self.ROIY = ev.y()
                self.ROIW = 0
                self.ROIH = 0
            else:
                self.ROIX = -1

    def mouseMoveEvent(self, ev):
        # logging.debug("x=%d  y=%d" % (ev.x(), ev.y()))
        if self.gui.bSelectROI.isChecked():
            x, y = self.screen2imgTransform(ev.x(), ev.y())
            if self.isPointOnROIImage(x, y):
                self.ROIW = ev.x() - self.ROIX
                self.ROIH = ev.y() - self.ROIY

    def mouseReleaseEvent(self, ev):
        # logging.debug("x=%d  y=%d" % (ev.x(), ev.y()))
        if self.gui.bSelectROI.isChecked():
            x, y = self.screen2imgTransform(ev.x(), ev.y())
            if self.isPointOnROIImage(x, y):
                self.ROIW = ev.x() - self.ROIX
                self.ROIH = ev.y() - self.ROIY

                logging.debug("ROI: x=%d  y=%d  w=%d  h=%d" \
                              % (self.ROIX, self.ROIY, self.ROIW, self.ROIH))
                x1, y1 = self.screen2imgTransform(self.ROIX, self.ROIY)
                x2, y2 = self.screen2imgTransform(ev.x(), ev.y())
                w = x2 - x1
                h = y2 - y1
                logging.debug("ROI: x=%d  y=%d  w=%d  h=%d" \
                              % (x1, y1, w, h))

            self.ROIX = -1
            self.gui.bSelectROI.setChecked(False)

    def screen2imgTransform(self, x, y):
        x = x - self.xoff
        x /= self.scale
        x *= self.binning
        x += self.roiXoff
        y = y - self.yoff
        y /= self.scale
        y *= self.binning
        y += self.roiYoff
        # logging.debug("Image coordinates: x=%.0f  y=%.0f" % (x, y))
        return (x, y)

    def set_image(self, img):
        self.setGeometry(QRect(0, 0, self.parent.width(), self.parent.height()))
        self.image = img
        if self.image and not self.image.isNull():
            self.scaled_image = self.image.scaled(self.width(), self.height(), aspectRatioMode = Qt.KeepAspectRatio)
            if self.image.width() != self.old_width or self.image.height() != self.old_height:
                # logging.debug("img:  w=%d  h=%d", self.image.width(), self.image.height())
                self.old_width = self.image.width()
                self.old_height = self.image.height()
                # logging.debug("scaled img:  w=%d  h=%d", self.scaled_image.width(), self.scaled_image.height())
                self.xoff = ( self.width() - self.scaled_image.width() ) / 2
                self.yoff = ( self.height() - self.scaled_image.height() ) / 2
                self.scale = float(self.scaled_image.width()) / self.image.width()
        self.update()

    def calcDisplayRate(self):
        now = time.time()
        updates = self.updates - self.last_updates
        delta = now - self.last_time
        rate = updates/delta
        self.gui.label_rate.setText('%.1f' % rate)
        self.gui.label_rate.repaint()
        self.last_time = now
        self.last_updates = self.updates


class SaveImage():
    def __init__(self, parent, img, dir='.', file='img-', num=1, period=1.0):
        self.parent = parent
        self.img = img
        self.dir = dir
        self.file = file
        self.prefix = self.dir + '/' + self.file + '_'
        self.num_images = num
        self.timer = None
        self.period = 1000.0 * period
        if self.num_images > 0:
            self.saveImage()
        if self.num_images > 0:
            self.timer = QTimer()
            self.timer.timeout.connect(self.saveImage)
            self.timer.start(self.period)
                # logging.debug("%d ms timer started", self.period)

    def saveImage(self):
        ts = self.time_stamp()
        self.full_name = self.prefix + ts + '.png'
        logging.debug("%s", self.full_name)
        self.img.save(self.full_name)
        self.num_images -= 1
        # logging.debug("num_images = %d", self.num_images)
        if self.num_images <= 0:
            self.saveImageCancel()

    def time_stamp(self):
        t = time.time()
        l = time.localtime(t)
        f = '.%02d' % int(100 * math.modf(t)[0] + 0.5)
        datetime_stamp = ('%04d-%02d-%02d_%02d:%02d:%02d' % (l[:6])) + f
        return datetime_stamp

    def saveImageCancel(self):
        # logging.debug('')
        if self.timer != None and self.timer.isActive():
            self.timer.stop()

class GigEImageViewer(QMainWindow, Ui_MainWindow):

    def __init__(self, pv_name):
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.cam_pv = pv_name
        image_pv = pv_name.replace( 'cam', 'image' )
        image_pv = image_pv.replace( 'CAM', 'IMAGE' )
        image_pv = image_pv.replace( 'CVV', 'IMAGE' )

        self.setWindowTitle(self.cam_pv)

        self.img = PycaImage(image_pv)

        self.display_image = DisplayImage(self.wImage, self.img, self)

        # NOTE:  there is also a bug in the ROI plugin--the _RBV values could be wrong if out of range
        self.display_image.roiXoff = self.pv_get(self.cam_pv+':MinX_RBV')
        self.display_image.roiYoff = self.pv_get(self.cam_pv+':MinY_RBV')
        self.display_image.binning = self.pv_get(self.cam_pv+':BinX_RBV')

        self.lPV.setText(self.cam_pv)
        self.myImgCounterLab = PycaLabel      (image_pv+':ArrayCounter_RBV', self.lImgCounter)
        self.myImgRateLab    = PycaLabel      (image_pv+':ArrayRate_RBV',    self.lImgRate)
        self.myExpTimeLab    = PycaLabel      (self.cam_pv+':AcquireTime_RBV',    self.lExpTime)
        self.myExpPeriodLab  = PycaLabel      (self.cam_pv+':AcquirePeriod_RBV',  self.lExpPeriod)
        self.myGainLab       = PycaLabel      (self.cam_pv+':Gain_RBV',           self.lGain)
        self.myExpTimeLE     = PycaLineEdit   (self.cam_pv+':AcquireTime',        self.leExpTime)
        self.myExpPeriodLE   = PycaLineEdit   (self.cam_pv+':AcquirePeriod',      self.leExpPeriod)
        self.myGainLE        = PycaLineEdit   (self.cam_pv+':Gain',               self.leGain)
        self.myROIMinXLab    = PycaLabel      (self.cam_pv+':MinX_RBV',           self.lRoiXStart)
        self.myROIMinXLab.setCallback(self.roiXStartChanged)
        self.myROISizeXLab   = PycaLabel      (self.cam_pv+':SizeX_RBV',          self.lRoiXSize)
        self.myROIMinYLab    = PycaLabel      (self.cam_pv+':MinY_RBV',           self.lRoiYStart)
        self.myROIMinYLab.setCallback(self.roiYStartChanged)
        self.myROISizeYLab   = PycaLabel      (self.cam_pv+':SizeY_RBV',          self.lRoiYSize)
        self.myROIMinXLE     = PycaLineEdit   (self.cam_pv+':MinX',               self.leRoiXStart)
        self.myROISizeXLE    = PycaLineEdit   (self.cam_pv+':SizeX',              self.leRoiXSize)
        self.myROIMinYLE     = PycaLineEdit   (self.cam_pv+':MinY',               self.leRoiYStart)
        self.myROISizeYLE    = PycaLineEdit   (self.cam_pv+':SizeY',              self.leRoiYSize)
        self.myBinXLab       = PycaLabel      (self.cam_pv+':BinX_RBV',           self.lBinX)
        self.myBinXLab.setCallback(self.binningChanged)
        self.myBinXLE        = PycaLineEdit   (self.cam_pv+':BinX',               self.leBinX)
        self.leBinX.editingFinished.connect(self.setBinning)
        imageModes = ('Single', 'Multiple', 'Continuous')
        self.myImgModeCB     = PycaComboBox   (self.cam_pv+':ImageMode',          self.cbImageMode, items = imageModes)
        triggerModes = ('Free Run', 'Sync In 1', 'Sync In 2', 'Sync In 3',
                        'Sync In 4', 'Fixed Rate', 'Software')
        self.myTriggerModeCB = PycaComboBox   (self.cam_pv+':TriggerMode',        self.cbTriggerMode, items = triggerModes)
        self.myCross1XLE     = PycaLineEdit   (self.cam_pv+':Cross1X',            self.leCross1X)
        self.myCross1YLE     = PycaLineEdit   (self.cam_pv+':Cross1Y',            self.leCross1Y)
        self.myCross2XLE     = PycaLineEdit   (self.cam_pv+':Cross2X',            self.leCross2X)
        self.myCross2YLE     = PycaLineEdit   (self.cam_pv+':Cross2Y',            self.leCross2Y)
        colors          = ('None', 'Black', 'Red', 'Green', 'Blue', 'White')
        self.myCross1CB      = PycaComboBox   (self.cam_pv+':Cross1Color',        self.cbCross1Color, items = colors)
        self.myCross2CB      = PycaComboBox   (self.cam_pv+':Cross2Color',        self.cbCross2Color, items = colors)
        self.myStartB        = PycaPushButton (self.cam_pv+':Acquire',            self.bStart,        value = 1)
        self.myStopB         = PycaPushButton (self.cam_pv+':Acquire',            self.bStop,         value = 0)

        self.bCross1.toggled.connect(self.bCross1Toggled)
        self.bCross2.toggled.connect(self.bCross2Toggled)
        self.bSelectROI.toggled.connect(self.bSelectROIToggled)
        self.bClearROI.clicked.connect(self.clearROI)

        self.dir = '.'
        self.file = 'img'
        self.num_images = 1
        self.savePeriod = 1.0

        self.imageSaver = None

        self.lePath.editingFinished.connect(self.saveDirectoryChanged)
        self.leFile.editingFinished.connect(self.saveFileChanged)
        self.leNumber.editingFinished.connect(self.saveNumberChanged)
        self.lePeriod.editingFinished.connect(self.savePeriodChanged)
        self.bSave.clicked.connect(self.saveStart)
        self.bStopSave.clicked.connect(self.saveStop)

    def pv_get(self, pv_name):
        # logging.debug(pv_name)
        pv = Pv(pv_name)
        try:
            pv.connect(timeout=1.0)
            # logging.debug("connected")
            pv.get(False, 0.1)
            # logging.debug("value = %d", pv.value)
            return pv.value
        except Exception, e:
            # logging.debug("exception %s", e)
            return 0

    def pv_put(self, pv_name, val):
        # logging.debug("%s, %d", pv_name, val)
        pv = Pv(pv_name)
        try:
            pv.connect(timeout=1.0)
            # logging.debug("connected")
            pv.put(val)
        except Exception, e:
            # logging.debug("exception %s", e)
            pass

    def setBinning(self):
        # Called when the user enters a number for binning
        try:
            val = int(self.leBinX.text())
            self.pv_put(self.cam_pv+':BinY', val)
        except Exception, e:
            # logging.debug("e = %s", e)
            pass

    def roiXStartChanged(self):
        # called when the PV  XXX:MinX_RBV  changed
        try:
            self.display_image.roiXoff = int(self.lRoiXStart.text())
        except Exception, e:
            # logging.debug("e = %s", e)
            pass

    def roiYStartChanged(self):
        # called when the PV  XXX:MinY_RBV  changed
        try:
            self.display_image.roiYoff = int(self.lRoiYStart.text())
        except Exception, e:
            # logging.debug("e = %s", e)
            pass

    def binningChanged(self):
        # called when the PV  XXX:BinY_RBV  changed
        try:
            self.display_image.binning = int(self.lBinX.text())
        except Exception, e:
            # logging.debug("e = %s", e)
            pass

    def saveDirectoryChanged(self):
        # logging.debug("")
        self.dir = self.lePath.text()

    def saveFileChanged(self):
        # logging.debug("")
        self.file = self.leFile.text()

    def saveNumberChanged(self):
        # logging.debug("")
        try:
            self.num_images = int(self.leNumber.text())
        except:
            pass

    def savePeriodChanged(self):
        # logging.debug("")
        try:
            self.savePeriod = float(self.lePeriod.text())
        except:
            pass

    def saveStart(self):
        # logging.debug("")
        # self.img.img.save('./img-00001.png')
        self.imageSaver = SaveImage(self, self.img.img, dir=self.dir, file=self.file, num=self.num_images, period=self.savePeriod)

    def saveStop(self):
        # logging.debug("")
        if self.imageSaver != None:
            self.imageSaver.saveImageCancel()

    def __del__(self):
        self.img.disconnect()

    def bCross1Toggled(self):
        logging.debug("bCross1Toggled: isChecked = %d" % self.bCross1.isChecked())
        if self.bCross1.isChecked():
            self.bCross2.setChecked(False)
            self.bSelectROI.setChecked(False)

    def bCross2Toggled(self):
        logging.debug("bCross2Toggled: isChecked = %d" % self.bCross2.isChecked())
        if self.bCross2.isChecked():
            self.bCross1.setChecked(False)
            self.bSelectROI.setChecked(False)

    def bSelectROIToggled(self):
        logging.debug("bSelectROIToggled: isChecked = %d" % self.bSelectROI.isChecked())
        if self.bSelectROI.isChecked():
            self.bCross1.setChecked(False)
            self.bCross2.setChecked(False)

    def clearROI(self):
        self.bCross1.setChecked(False)
        self.bCross2.setChecked(False)
        self.bSelectROI.setChecked(False)


def main():
    from options import Options
    options = Options(['camerapv'], [], [])
    try:
        options.parse()
    except Exception, msg:
        options.usage(str(msg))
        sys.exit()

    app = QApplication(sys.argv)

    win = GigEImageViewer(options.camerapv)
    win.resize(1080, 687)

    sys.setcheckinterval(1000) # default is 100
    win.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    logging.basicConfig(format='%(filename)s:%(lineno)d:%(levelname)-8s %(funcName)s: %(message)s',
                        level=logging.DEBUG)
    main()
