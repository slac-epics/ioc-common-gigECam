#! /bin/env python

import sys
import logging
from ConnectedPv import ConnectedPv
from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QImage
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QWidget


class PycaImage():

    def __init__(self, pv_name):
        self.name = pv_name
        self.size0 = self.size1 = self.size2 = None
        self.img = None
        self.size0_pv = ConnectedPv(pv_name + ':ArraySize0_RBV', self.size0_changed)
        self.size1_pv = ConnectedPv(pv_name + ':ArraySize1_RBV', self.size1_changed)
        self.size2_pv = ConnectedPv(pv_name + ':ArraySize2_RBV', self.size2_changed)
        self.counter_pv = ConnectedPv(pv_name + ':ArrayCounter_RBV', self.counter_changed)
        self.data_pv = ConnectedPv(pv_name + ':ArrayData', self.image_changed)
        self.emitter = QObject()
        self.new_image_callback = None

    def disconnect(self):
        self.data_pv.disconnect()
        self.counter_pv.disconnect()
        self.size0_pv.disconnect()
        self.size1_pv.disconnect()
        self.size2_pv.disconnect()

    def size0_changed(self):
        self.size0 = int(self.size0_pv.value)
        self.set_image_size()

    def size1_changed(self):
        self.size1 = int(self.size1_pv.value)
        self.set_image_size()

    def size2_changed(self):
        self.size2 = int(self.size2_pv.value)
        self.set_image_size()

    def set_image_size(self):
        if self.size0 != None and self.size1 != None and self.size2 != None:
            # print "size0 = %d" % self.size0
            # print "size1 = %d" % self.size1
            # print "size2 = %d" % self.size2
            # FIXME  - look at ColorMode_RBV and NDimensions_RBV
            if self.size0 == 3:      # color image
                format = QImage.Format_RGB32
                w = self.size1
                h = self.size2
            else:                    # b/w image
                format = QImage.Format_Indexed8
                w = self.size0
                h = self.size1
            self.img = QImage(w, h, format)
            if format == QImage.Format_Indexed8:
                colorTable = [QColor(i, i, i).rgb() for i in range(256)]
                self.img.setColorTable(colorTable)
            # TODO  - emit changed img object signal if we had a previous img object
            # FIXME - check img for None / make this thread safe
            buf = int(self.img.bits())
            size = w * h
            self.data_pv.set_processor(buf, size, format)

    def counter_changed(self):
        # logging.debug("%d", int(self.counter_pv.value))
        pass

    def set_new_image_callback(self, fnct):
        QObject.connect(self.emitter, SIGNAL('image_changed'), fnct)

    def image_changed(self):
        # logging.debug("")
        self.emitter.emit(SIGNAL('image_changed'), self.img)


def main():
    from options import Options
    options = Options(['camerapv'], [], [])
    # e.g.  --camerapv XCS:GIGE:IMAGE2
    try:
        options.parse()
    except Exception, msg:
        options.usage(str(msg))
        sys.exit()

    app = QApplication(sys.argv)

    img = PycaImage(options.camerapv)

    win = QWidget()
    win.resize(170, 160)
    win.show()

    stat = app.exec_()

    img.disconnect()

    sys.exit(stat)

if __name__ == '__main__':
    logging.basicConfig(format='%(filename)s:%(lineno)d:%(levelname)-8s %(funcName)s: %(message)s',
                        level=logging.DEBUG)
    main()
