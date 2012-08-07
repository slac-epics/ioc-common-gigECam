#! /usr/bin/env python

import sys
import time
import logging
from PyQt4 import QtGui, QtCore, uic
from GigECamera import GigECamera


class DisplayImage(QtGui.QWidget):
    def __init__(self, parent, gui):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.image = None
        self.gui = gui
        self.img_width = 0
        self.img_height = 0
        self.data = None
        self.scaled_image = None
        self.painter = QtGui.QPainter()
        self.updates = 0
        self.last_updates = 0
        self.last_time = time.time()
        self.rateTimer = QtCore.QTimer()
        self.rateTimer.timeout.connect(self.calcDisplayRate)
        self.rateTimer.start(1000)

    def paintEvent(self, event):
        self.setGeometry(QtCore.QRect(0, 0, self.parent.width(), self.parent.height()))
        self.image = QtGui.QImage(self.data, self.img_width, self.img_height, QtGui.QImage.Format_RGB32);
        if self.image and not self.image.isNull():
            self.scaled_image = self.image.scaled(self.width(), self.height(), aspectRatioMode = QtCore.Qt.KeepAspectRatio)
            self.painter.begin(self)
            x = ( self.width() - self.scaled_image.width() ) / 2
            y = ( self.height() - self.scaled_image.height() ) / 2
            self.painter.drawImage(x, y, self.scaled_image)
            self.painter.end()
            self.updates += 1

    def setImage(self, img, width, height):
        self.data = img
        self.img_width = width
        self.img_height = height
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

class MyMainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.ui = uic.loadUi('GigEViewer.ui')
        self.ui.closeEvent = self.closeEvent

        self.c = GigECamera(self.imageCaptured)
        self.c.connect('192.168.100.221')

        expTime = self.c.expTime()
        self.ui.lExpTime.setText("%d" % expTime)
        gain = self.c.gain()
        self.ui.lGain.setText("%d" % gain)

        self.c.start()

        self.view = DisplayImage(self.ui.wImage, self.ui)

        self.ui.show()

    def closeEvent(self, event):
        self.c.stop()
        self.c.disconnect()

    def imageCaptured(self, img, count, width, height):
        logging.debug("%s", repr(img))
        self.ui.lImgCounter.setText("%d" % count)
        self.ui.lImgRate.setText("")
        self.view.setImage(img, width, height)

if __name__ == '__main__':
    logging.basicConfig(\
        format='%(filename)s:%(lineno)d:%(levelname)-8s %(funcName)s: %(message)s',
        level=logging.INFO)   # DEBUG, INFO, ERROR, CRITICAL

    app = QtGui.QApplication(sys.argv)
    win = MyMainWindow()
    sys.exit(app.exec_())

