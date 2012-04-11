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
    """ When constructed, an object of this class tries to connect itself
    to a PV in an IOC over channel access. If it fails to connect,
    it will retry forever every second.  Once connected, the object emits
    a Qt signal every time the value of the PV changes. It also calls a
    user callback function if one is provided.
    """

    def __init__(self, name, callback = None):
        """ Constructor:  name is the name of the PV.
        When the value of the PV changes, the callback is called if any """
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
        """ Destructor:  disconnect if connected """
        # logging.debug("deleting %s", self.name)
        if self.connected:
            # logging.debug("disconecting %s", self.name)
            self.disconnect()

    def try_connect(self):
        """ Try to connected to the PV every second.
        When successful, start monitoring the PV and call self.changed() when it changes"""
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
        """ Disconnect from channel access if connected """
        # logging.debug("disconnect %s", self.name)
        if self.connected:
            # logging.debug("unsubscribing from %s", self.name)
            self.unsubscribe()

    def disconnected(self):
        """ Called when the PV disconnects at the remote end.
        Start a periodic sequence to attempt to reconnect every second """
        # logging.debug("disconnected %s", self.name)
        QTimer.singleShot(1000, self.try_connect)

    def changed(self):
        """ Called when the value of the PV changes.
        Emitting the signal will cause the callback to be invoked. """
        # logging.debug("%s value = %s", self.name, self.value)
        self.emmiter.emit(SIGNAL('valueChanged'))

    def set_processor(self, buf, size, width, height, bytesPerLine, format):
        """ This method registers a 'processor' function for an object of class Pv.
        Normally, when the value of a PV changes, the Pv class will fetch the value
        from channel access, convert it to a python value and return it.
        This conversion can be quite inefficient for large arrays like images.
        The array grows as data arrives and probably multiple realloc() take
        place under the hood.
        This automatic conversion does not take place if one registers a callback
        function as a processor with the object of class Pv
        """
        buf_hi = buf >> 32;      # kluge to pass 64-bit address to C using two 32-bit ints
        buf_lo = buf & ((1 << 32) - 1);
        # logging.debug("buf = 0x%08x", buf)
        # logging.debug("buf_hi = 0x%08x", buf_hi)
        # logging.debug("buf_lo = 0x%08x", buf_lo)

        support_code = """
            #line 98                      
            static unsigned char *img_buffer;
            static int            img_size;
            static int            img_width;
            static int            img_height;
            static int            img_bytes_per_line;
            static unsigned char *buf_end;
            static                int fmt;

            static void pydspl_qimage(const void* cadata, long count, size_t size, void* usr) 
            {
                const unsigned char *data = static_cast<const unsigned char*>(cadata);

                if (fmt == 3) {       // QImage.Format_Indexed8      
                    // printf("img_data=%p img_buffer=%p\\n", data, img_buffer);
                    unsigned char *dp = img_buffer;
                    for (int j=0; j<img_height; j++) {
                        // printf("copying %ld bytes from %p to %p\\n", img_width, data, dp);
                        memcpy(dp, data, img_width);
                        data += img_width;
                        dp += img_bytes_per_line;
                    }
                    // Save images to a file
                    // FILE *fp = fopen("/reg/neh/home/pstoffel/nimg.dat", "w");
                    // fwrite(cadata, 1, count, fp);
                    // fclose(fp);
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
            img_width = width;
            img_height = height;
            img_bytes_per_line = bytesPerLine;
            buf_end = img_buffer + (size << 2);   // used for RGB32 images only
            fmt = format;

            void *func = (void*)pydspl_qimage;
            PyObject* pyfunc =  PyCObject_FromVoidPtr(func, NULL);
            return_val = pyfunc;
        """

        rv = inline(code, ['buf_hi', 'buf_lo', 'size', 'width', 'height', 'bytesPerLine', 'format'],
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
