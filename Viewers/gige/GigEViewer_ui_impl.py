#! /bin/env python

import sys
import time
import logging
from PycaImage import PycaImage
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QPainter
from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QWidget
from PyQt4.QtCore import QRect
from PyQt4.QtGui import QPen, QBrush
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from GigEViewer_ui import Ui_MainWindow
from pyca_widgets import *


class DisplayImage(QWidget):
    def __init__(self, parent, img, gui):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.image = img.img
        self._gui = gui
        self.scaled_image = img.img
        self.xoff = 0
        self.yoff = 0
        self.scale = 1.0
        self.painter = QPainter()
        img.set_new_image_callback(self.set_image)
        self.updates = 0
        self.last_updates = 0
        self.last_time = time.time()
        self.rateTimer = QTimer()
        self.connect(self.rateTimer, SIGNAL("timeout()"), self.calcDisplayRate)
        self.rateTimer.start(1000)

    def paintEvent(self, event):
        self.painter.begin(self)
        if self.scaled_image:
            self.painter.drawImage(self.xoff, self.yoff, self.scaled_image)
            self.drawCross(self.painter)
        self.painter.end()
        self.updates += 1

    def drawCross(self, qp):
        color = self._gui.cbCross1Color.currentIndex()
        # logging.debug("color = %d", color)
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
            try:
                x1 = int(self._gui.leCross1X.text())
            except:
                x1 = 0
            try:
                y1 = int(self._gui.leCross1Y.text())
            except:
                y1 = 0
            x1 *= self.scale
            y1 *= self.scale
            x1 += self.xoff
            y1 += self.yoff
            # logging.debug("x=%d  y=%d", x1, y1)
            qp.drawLine( x1-5, y1, x1+5, y1)
            qp.drawLine( x1, y1-5, x1, y1+5)

        color = self._gui.cbCross2Color.currentIndex()
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
            try:
                x2 = int(self._gui.leCross2X.text())
            except:
                x2 = 0
            try:
                y2 = int(self._gui.leCross2Y.text())
            except:
                y2 = 0
            x2 *= self.scale
            y2 *= self.scale
            x2 += self.xoff
            y2 += self.yoff
            # logging.debug("x2=%d  y2=%d", x2, y2)
            qp.drawLine( x2-5, y2, x2+5, y2)
            qp.drawLine( x2, y2-5, x2, y2+5)

    def resizeEvent(self, event):
        if self.image:
            # logging.debug("w=%d  h=%d", self.width(), self.height())
            self.scaled_image = self.image.scaled(self.width(), self.height(), aspectRatioMode = Qt.KeepAspectRatio)
            self.xoff = ( self.width() - self.scaled_image.width() ) / 2
            self.yoff = ( self.height() - self.scaled_image.height() ) / 2
            self.scale = float(self.scaled_image.width()) / self.image.width()
            # logging.debug("scale = %f", self.scale)

    def set_image(self, img):
        self.setGeometry(QRect(0, 0, self.parent.width(), self.parent.height()))
        self.image = img
        if self.image and not self.image.isNull():
            # logging.debug("w=%d  h=%d", self.width(), self.height())
            self.scaled_image = self.image.scaled(self.width(), self.height(), aspectRatioMode = Qt.KeepAspectRatio)
        self.update()

    def calcDisplayRate(self):
        now = time.time()
        updates = self.updates - self.last_updates
        delta = now - self.last_time
        rate = updates/delta
        self._gui.label_rate.setText('%.1f' % rate)
        self._gui.label_rate.repaint()
        self.last_time = now
        self.last_updates = self.updates


class GigEImageViewer(QMainWindow, Ui_MainWindow):
    myImgCounterLab = None
    myImgRateLab    = None
    myExpTimeLab    = None
    myExpPeriodLab  = None
    myGainLab       = None
    myExpTimeLE     = None
    myExpPeriodLE   = None
    myGainLE        = None
    myROIMinXLab    = None
    myROISizeXLab   = None
    myROIMinYLab    = None
    myROISizeYLab   = None
    myROIMinXLE     = None
    myROISizeXLE    = None
    myROIMinYLE     = None
    myROISizeYLE    = None
    myBinXLab       = None
    myBinXLE        = None
    myImgModeCB     = None
    myTriggerModeCB = None
    myCross1XLE     = None
    myCross1YLE     = None
    myCross2XLE     = None
    myCross2YLE     = None
    myCross1CB      = None
    myCross2CB      = None
    myStartB        = None
    myStopB         = None

    def __init__(self, pv_name):
        QMainWindow.__init__(self)
        self.setupUi(self)

        cam_pv = pv_name
        image_pv = pv_name.replace( 'cam', 'image' )
        image_pv = image_pv.replace( 'CAM', 'IMAGE' )

        self.img = PycaImage(image_pv)
        logging.debug("%s", cam_pv+':BinY')
        self.biny_pv = Pv(cam_pv+':BinY')
        try:
            self.biny_pv.connect(1.0)
        except:
            pass

        self.display_image = DisplayImage(self.wImage, self.img, self)

        self.lPV.setText(cam_pv)
        GigEImageViewer.myImgCounterLab = PycaLabel      (image_pv+':ArrayCounter_RBV', self.lImgCounter)
        GigEImageViewer.myImgRateLab    = PycaLabel      (image_pv+':ArrayRate_RBV',    self.lImgRate)
        GigEImageViewer.myExpTimeLab    = PycaLabel      (cam_pv+':AcquireTime_RBV',    self.lExpTime)
        GigEImageViewer.myExpPeriodLab  = PycaLabel      (cam_pv+':AcquirePeriod_RBV',  self.lExpPeriod)
        GigEImageViewer.myGainLab       = PycaLabel      (cam_pv+':Gain_RBV',           self.lGain)
        GigEImageViewer.myExpTimeLE     = PycaLineEdit   (cam_pv+':AcquireTime',        self.leExpTime)
        GigEImageViewer.myExpPeriodLE   = PycaLineEdit   (cam_pv+':AcquirePeriod',      self.leExpPeriod)
        GigEImageViewer.myGainLE        = PycaLineEdit   (cam_pv+':Gain',               self.leGain)
        GigEImageViewer.myROIMinXLab    = PycaLabel      (cam_pv+':MinX_RBV',           self.lRoiXStart)
        GigEImageViewer.myROISizeXLab   = PycaLabel      (cam_pv+':SizeX_RBV',          self.lRoiXSize)
        GigEImageViewer.myROIMinYLab    = PycaLabel      (cam_pv+':MinY_RBV',           self.lRoiYStart)
        GigEImageViewer.myROISizeYLab   = PycaLabel      (cam_pv+':SizeY_RBV',          self.lRoiYSize)
        GigEImageViewer.myROIMinXLE     = PycaLineEdit   (cam_pv+':MinX',               self.leRoiXStart)
        GigEImageViewer.myROISizeXLE    = PycaLineEdit   (cam_pv+':SizeX',              self.leRoiXSize)
        GigEImageViewer.myROIMinYLE     = PycaLineEdit   (cam_pv+':MinY',               self.leRoiYStart)
        GigEImageViewer.myROISizeYLE    = PycaLineEdit   (cam_pv+':SizeY',              self.leRoiYSize)
        GigEImageViewer.myBinXLE        = PycaLineEdit   (cam_pv+':BinX',               self.leBinX)
        GigEImageViewer.myBinXLab       = PycaLabel      (cam_pv+':BinX_RBV',           self.lBinX)
        self.leBinX.editingFinished.connect(self.setBinning)
        imageModes = ('Single', 'Multiple', 'Continuous')
        GigEImageViewer.myImgModeCB     = PycaComboBox   (cam_pv+':ImageMode',          self.cbImageMode, items = imageModes)
        triggerModes = ('Free Run', 'Sync In 1', 'Sync In 2', 'Sync In 3',
                        'Sync In 4', 'Fixed Rate', 'Software')
        GigEImageViewer.myTriggerModeCB = PycaComboBox   (cam_pv+':TriggerMode',        self.cbTriggerMode, items = triggerModes)
        GigEImageViewer.myCross1XLE     = PycaLineEdit   (cam_pv+':Cross1X',            self.leCross1X)
        GigEImageViewer.myCross1YLE     = PycaLineEdit   (cam_pv+':Cross1Y',            self.leCross1Y)
        GigEImageViewer.myCross2XLE     = PycaLineEdit   (cam_pv+':Cross2X',            self.leCross2X)
        GigEImageViewer.myCross2YLE     = PycaLineEdit   (cam_pv+':Cross2Y',            self.leCross2Y)
        colors          = ('None', 'Black', 'Red', 'Green', 'Blue', 'White')
        GigEImageViewer.myCross1CB      = PycaComboBox   (cam_pv+':Cross1Color',        self.cbCross1Color, items = colors)
        GigEImageViewer.myCross2CB      = PycaComboBox   (cam_pv+':Cross2Color',        self.cbCross2Color, items = colors)
        GigEImageViewer.myStartB        = PycaPushButton (cam_pv+':Acquire',            self.bStart,        value = 1)
        GigEImageViewer.myStopB         = PycaPushButton (cam_pv+':Acquire',            self.bStop,         value = 0)

    def setBinning(self):
        # Called when the user enters a number for binning
        try:
            val = int(self.leBinX.text())
            logging.debug("val = %d", val)
            # set the camera binnning value
            self.biny_pv.put(val, 1.0)
        except Exception, e:
            logging.debug("e = %s", e)
            pass

    def __del__(self):
        self.img.disconnect()
        GigEImageViewer.myImgCounterLab = None
        GigEImageViewer.myImgRateLab    = None
        GigEImageViewer.myExpTimeLab    = None
        GigEImageViewer.myExpPeriodLab  = None
        GigEImageViewer.myGainLab       = None
        GigEImageViewer.myExpTimeLE     = None
        GigEImageViewer.myExpPeriodLE   = None
        GigEImageViewer.myGainLE        = None
        GigEImageViewer.myROIMinXLab    = None
        GigEImageViewer.myROISizeXLab   = None
        GigEImageViewer.myROIMinYLab    = None
        GigEImageViewer.myROISizeYLab   = None
        GigEImageViewer.myROIMinXLE     = None
        GigEImageViewer.myROISizeXLE    = None
        GigEImageViewer.myROIMinYLE     = None
        GigEImageViewer.myROISizeYLE    = None
        GigEImageViewer.myBinXLab       = None
        GigEImageViewer.myBinXLE        = None
        GIGEImageViewer.myImgModeCB     = None
        GIGEImageViewer.myTriggerModeCB = None
        GigEImageViewer.myCross1XLE     = None
        GigEImageViewer.myCross1YLE     = None
        GigEImageViewer.myCross2XLE     = None
        GigEImageViewer.myCross2YLE     = None
        GigEImageViewer.myCross1CB      = None
        GigEImageViewer.myCross2CB      = None
        GigEImageViewer.myStartB        = None
        GigEImageViewer.myStopB         = None
        try:
            self.biny_pv.disconnect()
        except:
            pass


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
