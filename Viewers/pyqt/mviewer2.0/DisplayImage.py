import logging

from PyQt4 import QtGui, QtCore 
from PyQt4.QtCore import Qt # , QObject #, Qt, QPoint, QPointF, QSize, QRectF, QObject


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
    #print 'paintEvent', event, self.gui.cam_n
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
