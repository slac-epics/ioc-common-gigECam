#! /bin/env python

import sys
import logging
from   scipy.weave import inline
import pyca
from Pv import Pv
from PyQt4.QtCore import QObject
from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QWidget
from PyQt4.QtCore import SIGNAL


class ConnectedPv(Pv):

    def __init__(self, name, callback = None):
        Pv.__init__(self, name)
        self.name = name
        self.callback = callback
        # logging.debug("creating ConnectedPv %s", self.name)
        # self.name = name
        self.connected = False
        QTimer.singleShot(1000, self.try_connect)
        self.emmiter = QObject()
        if self.callback:
            QObject.connect(self.emmiter, SIGNAL('valueChanged'), self.callback)

    def __del__(self):
        # logging.debug("deleting %s", self.name)
        if self.connected:
            # logging.debug("disconecting %s", self.name)
            self.disconnect()

    def try_connect(self):
        # logging.debug("connecting to %s ...", self.name)
        try:
            self.connect(timeout = 1.0)
            self.connected = True
            self.connect_cb = self.disconnected
            self.monitor_cb = self.changed
            evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM
            self.monitor(evtmask)
            pyca.flush_io()
            # logging.debug("connected to %s", self.name)
            # logging.debug("%s value = %s", self.name, self.value)
        except:
            self.disconnect()
            QTimer.singleShot(1000, self.try_connect)

    def disconnect(self):
        # logging.debug("disconnect %s", self.name)
        if self.connected:
            # logging.debug("unsubscribing from %s", self.name)
            self.unsubscribe()

    def disconnected(self):
        # logging.debug("disconnected %s", self.name)
        QTimer.singleShot(1000, self.try_connect)

    def changed(self):
        # logging.debug("%s value = %s", self.name, self.value)
        self.emmiter.emit(SIGNAL('valueChanged'))

    def set_processor(self, buf, size, format):
        buf_hi = buf >> 32;      # kluge to pass 64-bit address to C using two 32-bit ints
        buf_lo = buf & ((1 << 32) - 1);

        support_code = """
            #line 70                      
            static unsigned char *img_buffer;
            static int            img_size;
            static unsigned char *buf_end;
            static                int fmt;

            static void pydspl_qimage(const void* cadata, long count, size_t size, void* usr) 
            {
                const unsigned char *data = static_cast<const unsigned char*>(cadata);

                if (fmt == 3) {       // QImage.Format_Indexed8      
                    if (count > img_size)
                        count = img_size;
                    memcpy(img_buffer, cadata, count);
                } else {              // QImage.Format_RGB32         
                    // printf("copying %ld bytes from %p to %p\\n", count, cadata, img_buffer);
                    unsigned char *bp = img_buffer;
                    while (bp < buf_end) {
                        unsigned char r = *data++;     
                        unsigned char g = *data++;
                        unsigned char b = *data++;
                        *bp++ = b;
                        *bp++ = g;
                        *bp++ = r;
                        bp++;
                    }
                }
            }
        """
        code = """
            #line 59
            // the 64-bit address of the image buffer
            unsigned long buf = ((unsigned long)buf_hi << 32) | (buf_lo & ((1L << 32) - 1));
            // printf(">>> buf = 0x%0lx\\n", buf);
            img_buffer = reinterpret_cast<unsigned char*>(buf);
            img_size = size;
            buf_end = img_buffer + (size << 2);   // used for RGB32 images only
            fmt = format;

            void *func = (void*)pydspl_qimage;
            PyObject* pyfunc =  PyCObject_FromVoidPtr(func, NULL);
            return_val = pyfunc;
        """

        rv = inline(code, ['buf_hi', 'buf_lo', 'size', 'format'],
                    support_code = support_code,
                    force = 0,
                    verbose = 0)
        self.processor = rv
        pyca.flush_io()


def main():
    app = QApplication(sys.argv)

    img = ConnectedPv('XCS:GIGE:IMAGE2:ArrayCounter_RBV')

    w = QWidget()
    w.resize(170, 160)
    w.show()
    stat = app.exec_()

    img.disconnect()

    sys.exit(stat)

if __name__ == '__main__':
    logging.basicConfig(format='%(filename)s:%(lineno)d:%(levelname)-8s %(funcName)s: %(message)s',
                        level=logging.DEBUG)
    main()
