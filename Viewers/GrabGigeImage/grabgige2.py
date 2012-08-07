#! /usr/bin/env python

# import sys
import time
from   scipy.weave import inline
from   scipy import misc
from   Pv import Pv
import pyca

import numpy as np


def caget(pvname):
    try:
        pv = Pv(pvname)
        pv.connect(1.)
        pv.get(False, 1.)
        pv.disconnect()
        return pv.value
    except pyca.pyexc, e:
        print 'pyca exception: %s' %(e)
        raise pyca.pyexc(e)
    except pyca.caexc, e:
        print 'channel access exception: %s' %(e)
        raise pyca.caexc(e)
    except Exception, e:
        print 'Exception: %s' % str(e)
        raise Exception(e)

  
class ConnectedPv(Pv):
    def __init__(self, name, adata=None):
        Pv.__init__(self, name)
        self._name = name
        if adata != None:
            self.set_processor(adata)
        self.val = ""
        self.connected = False
        self.connect()
        
    def __del__(self):
        if self.connected:
            self.disconnect()

    def connect(self):
        self.connected = False
        try:
            Pv.connect(self, timeout = 1.0)
            self.connected = True
            self.monitor_cb = self.changed
            evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM
            self.monitor(evtmask)
            pyca.flush_io()
        except:
            print "Could not connect to %s" % self._name
            raise

    def disconnect(self):
        if self.connected:
            self.unsubscribe()

    def set_processor(self, a):
        support_code = """
            #line 48
            static unsigned char *img_buffer;
            static int            buf_size;
            static unsigned char *buf_end;

            static void grab_image(const void* cadata, long count, size_t size, void* usr)
            {
                const unsigned char *data = static_cast<const unsigned char*>(cadata);

                if (count > buf_size)
                    count = buf_size;
                memcpy(img_buffer, data, count);
            }
        """
        code = """
            #line 62
            img_buffer = (unsigned char *)a;
            buf_size = nbytes;
            buf_end = img_buffer + nbytes;

            void *func = (void*)grab_image;
            PyObject* pyfunc =  PyCObject_FromVoidPtr(func, NULL);
            return_val = pyfunc;
        """

        nbytes = a.nbytes

        rv = inline(code, ['a', 'nbytes'],
                    support_code = support_code,
                    force = 0,
                    verbose = 0)
        self.processor = rv
        pyca.flush_io()

    def changed(self):
        # print "%s = %s" % (self._name, self.value)
        self.val = self.value

class GigEImage():
    def __init__(self, name):
        self._name = name
        print 'connecting to size0'
        self.size0 = caget(name+':ArraySize0_RBV')
        print 'connecting to size1'
        self.size1 = caget(name+':ArraySize1_RBV')
        print 'connecting to size2'
        self.size2 = caget(name+':ArraySize2_RBV')
        print 'connecting to counter'
        self.counter = ConnectedPv(name+':ArrayCounter_RBV')
        # print "Size:  %d x %d x %d" % self.size0, self.size1, self.size2
        # time.sleep(1)

    # def __del__(self):
        # self.counter.disconnect()

    def grab(self):
        if self.size0 == 3:
            # print "%d x %d x %d => %d" % (self.size0, self.size1, self.size2, self.size0 * self.size1 * self.size2)
            a = np.empty( ( self.size2, self.size1, self.size0 ), dtype=np.uint8, order='C' )
        else:
            a = np.empty( ( self.size1, self.size0 ), dtype=np.uint8, order='C' )
        imgPv = ConnectedPv(self._name+':ArrayData', adata=a)
        time.sleep(0.3)
        imgPv.disconnect()
        return a

    def save(self, data):
        print misc.imsave.__doc__
        misc.imsave('outfile.png', data)

def main():
    from matplotlib import pyplot as plt
    import matplotlib.cm as cm
    try:
        # img = GigEImage('TST:GIGE:IMAGE1')
        img = GigEImage('MEC:GIGE:IMAGE1')
        data = img.grab()
        print data.nbytes
        print data.shape
        if (data.ndim == 3):
            plt.imshow(data)    # color image
        else:
            plt.imshow(data, cmap=cm.Greys_r)    # b/w as grayscale
        plt.show()

    except Exception, e:
        print 'Exiting with exception: %s' %(e)
        pass

if __name__ == '__main__':
    main()
