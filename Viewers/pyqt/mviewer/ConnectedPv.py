#! /bin/env python
import sys
from scipy.weave import inline
import pyca
from Pv import Pv
from PyQt4.QtCore import QObject, QTimer, SIGNAL
from PyQt4.QtGui import QApplication, QWidget

class ConnectedPv(Pv):
    """ When constructed, an object of this class tries to connect itself
    to a PV in an IOC over channel access. If it fails to connect,
    it will retry forever every second.  Once connected, the object emits
    a Qt signal every time the value of the PV changes. It also calls a
    user callback function if one is provided.
    """

    def __init__(self, name, callback=None):
        """ Constructor:  name is the name of the PV.
        When the value of the PV changes, the callback is called if any """
        Pv.__init__(self, name)
        self.name = name
        self.callback = callback
        self.connected = False
        QTimer.singleShot(1000, self.try_connect)
        self.emitter = QObject()
        if self.callback:
            QObject.connect(self.emitter, SIGNAL('valueChanged'), self.callback)

    def __del__(self):
        """ Destructor:  disconnect if connected """
        if self.connected:
            self.disconnect()

    def try_connect(self):
        """ Try to connected to the PV every second.
        When successful, start monitoring the PV and call self.changed() when it changes"""
        try:
            self.connect(timeout = 1.0)
            self.connected = True
            self.connect_cb = self.disconnected
            self.monitor_cb = self.changed
            evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM
            self.monitor(evtmask)
            pyca.flush_io()
        except:
            self.disconnect()
            QTimer.singleShot(1000, self.try_connect)

    def disconnect(self):
        """ Disconnect from channel access if connected """
        if self.connected:
            self.unsubscribe()

    def disconnected(self):
        """ Called when the PV disconnects at the remote end.
        Start a periodic sequence to attempt to reconnect every second """
        QTimer.singleShot(1000, self.try_connect)

    def changed(self):
        """ Called when the value of the PV changes.
        Emitting the signal will cause the callback to be invoked. """
        self.emitter.emit(SIGNAL('valueChanged'))

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

        support_code = """
            #line 99
            //static unsigned char *img_buffer;
            //static int            img_size;
            //static int            img_width;
            //static int            img_height;
            //static int            img_bytes_per_line;
            //static unsigned char *buf_end;
            //static                int fmt;
            struct pydspl_qimage_data {
                 unsigned char *img_buffer;
                 int            img_size;
                 int            img_width;
                 int            img_height;
                 int            img_bytes_per_line;
                 unsigned char *buf_end;
                 int            fmt;
            };
            static void pydspl_qimage(const void* cadata, long count, size_t size, void* u) 
            {
                const unsigned char *data = static_cast<const unsigned char*>(cadata);
                struct pydspl_qimage_data *usr = static_cast<struct pydspl_qimage_data *>(u);
                //printf("\\nConnectedPv::pydspl_qimage\\n");
                if (usr->fmt == 3) {       // QImage.Format_Indexed8      
                    // printf("img_data=%p img_buffer=%p\\n", data, img_buffer);
                    unsigned char *dp = usr->img_buffer;
                    for (int j=0; j < usr->img_height; j++) {
                        // printf("copying %ld bytes from %p to %p\\n", img_width, data, dp);
                        memcpy(dp, data, usr->img_width);
                        data += usr->img_width;
                        dp += usr->img_bytes_per_line;
                    }
                    // Save images to a file
                    // FILE *fp = fopen("/reg/neh/home/pstoffel/nimg.dat", "w");
                    // fwrite(cadata, 1, count, fp);
                    // fclose(fp);
                } else {              // QImage.Format_RGB32         
                    // printf("copying %ld bytes from %p to %p\\n", count, cadata, img_buffer);
                    unsigned char *bp = usr->img_buffer;
                    while (bp < usr->buf_end) {
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
            // Frees the memory when python object is destroyed
            static void pydspl_qimage_destr(void *cobj, void *u)
            {
                struct pydspl_qimage_data *usr = static_cast<struct pydspl_qimage_data *>(u);
                delete usr;
            }
        """
        code = """
            #line 141
            //printf("\\nConnectedPv::code\\n");
            // the 64-bit address of the image buffer
            struct pydspl_qimage_data *tdata = new struct pydspl_qimage_data;            
            unsigned long buf = ((unsigned long)buf_hi << 32) | (buf_lo & ((1L << 32) - 1));
            // printf(">>> buf = 0x%0lx\\n", buf);
            tdata->img_buffer = reinterpret_cast<unsigned char*>(buf);
            tdata->img_size = size;
            tdata->img_width = width;
            tdata->img_height = height;
            tdata->img_bytes_per_line = bytesPerLine;
            tdata->buf_end = tdata->img_buffer + (size << 2);   // used for RGB32 images only
            tdata->fmt = format;

            void *func = (void*)pydspl_qimage;
            PyObject* pyfunc =  PyCObject_FromVoidPtrAndDesc(func, (void *)tdata, pydspl_qimage_destr);
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

    img = ConnectedPv('MEC:LAS:GIGE:IMAGE4:ArrayCounter_RBV')

    w = QWidget()
    w.resize(170, 160)
    w.show()
    stat = app.exec_()

    img.disconnect()

    sys.exit(stat)

if __name__ == '__main__':
    import logging
    logging.basicConfig(format='%(filename)s:%(lineno)d:%(levelname)-8s %(funcName)s: %(message)s',
                        level=logging.DEBUG)
    main()
