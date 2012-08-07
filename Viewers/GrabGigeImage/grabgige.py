#! /usr/bin/env python

import threading
from   scipy.weave import inline
from   scipy import misc
from   Pv import Pv
import pyca

import numpy as np


def caget(pvname):
    pv = Pv(pvname)
    pv.connect(1.)
    pv.get(False, 1.)
    pv.disconnect()
    return pv.value

def caput(pvname, value):
    pv = Pv(pvname)
    pv.connect(1.)
    pv.put(value, timeout=1.)
    pv.disconnect()

  
class ConnectedPv(Pv):
    def __init__(self, name, adata=None):
        Pv.__init__(self, name)
        self.connected = False
        self._name = name
        self.evt = threading.Event()
        if adata != None:
            self.set_processor(adata)
        self.connect()
        
    def __del__(self):
        if self.connected:
            self.disconnect()

    def connect(self):
        Pv.connect(self, timeout = 1.0)
        self.connected = True
        # self.monitor_cb = self.changed
        evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM
        self.monitor(evtmask)
        pyca.flush_io()

    def disconnect(self):
        if self.connected:
            self.unsubscribe()

    def grabbed(self):
        self.evt.set()

    def wait(self):
        return self.evt.wait(1.0)

    def set_processor(self, a):
        support_code = """
            #line 55
            static unsigned char *img_buffer;
            static int            buf_size;
            static unsigned char *buf_end;
            static py::object     grab_cb;

            static void grab_image(const void* cadata, long count, size_t size, void* usr)
            {
                const unsigned char *data = static_cast<const unsigned char*>(cadata);

                if (count > buf_size)
                    count = buf_size;
                memcpy(img_buffer, data, count);
                grab_cb.call();
            }
        """
        code = """
            #line 72
            img_buffer = (unsigned char *)a;
            buf_size = nbytes;
            buf_end = img_buffer + nbytes;
            grab_cb = grabbed;

            void *func = (void*)grab_image;
            PyObject* pyfunc =  PyCObject_FromVoidPtr(func, NULL);
            return_val = pyfunc;
        """

        nbytes = a.nbytes
        grabbed = self.grabbed

        rv = inline(code, ['a', 'nbytes', 'grabbed'],
                    support_code = support_code,
                    force = 0,
                    verbose = 0)
        self.processor = rv
        pyca.flush_io()


class GigEImage():
    def __init__(self, name):
        self._name = name
        self.size0 = caget(name+':ArraySize0_RBV')
        self.size1 = caget(name+':ArraySize1_RBV')
        self.size2 = caget(name+':ArraySize2_RBV')
        # print "Size:  %d x %d x %d" % self.size0, self.size1, self.size2

    def grab(self):
        if self.size0 == 3:
            a = np.empty( ( self.size2, self.size1, self.size0 ), dtype=np.uint8, order='C' )
        else:
            a = np.empty( ( self.size1, self.size0 ), dtype=np.uint8, order='C' )
        imgPv = ConnectedPv(self._name+':ArrayData', adata=a)
        imgPv.wait()     # wait for the image to be grabbed
        imgPv.disconnect()
        return a

    def save(self, data):
        misc.imsave('outfile.png', data)

class GigECamera():
    def __init__(self, name):
        self.name = name

    def manufacturer(self):
        return caget(self.name+':Manufacturer_RBV')

    def model(self):
        return caget(self.name+':Model_RBV')

    def maxSizeX(self):
        return caget(self.name+':MaxSizeX_RBV')

    def maxSizeY(self):
        return caget(self.name+':MaxSizeY_RBV')

    def arraySizeX(self):
        return caget(self.name+':ArraySizeX_RBV')

    def arraySizeY(self):
        return caget(self.name+':ArraySizeY_RBV')

    def arraySizeZ(self):
        return caget(self.name+':ArraySizeZ_RBV')

    def setAcquireTime(self, value):
        return caput(self.name+':AcquireTime', value)

    def setAcquirePeriod(self, value):
        return caput(self.name+':AcquirePeriod', value)

    def setGain(self, value):
        return caput(self.name+':Gain', value)

    def setMinX(self, value):
        return caput(self.name+':MinX', value)

    def setMinY(self, value):
        return caput(self.name+':MinY', value)

    def setSizeX(self, value):
        return caput(self.name+':SizeX', value)

    def setSizeY(self, value):
        return caput(self.name+':SizeY', value)

    def setBinX(self, value):
        return caput(self.name+':BinX', value)

    def setBinY(self, value):
        return caput(self.name+':BinY', value)

    def setImageMode(self, value):
        return caput(self.name+':ImageMode', value)

    def setTriggerMode(self, value):
        return caput(self.name+':TriggerMode', value)

    def setAcquire(self, value):
        return caput(self.name+':Acquire', value)


def main():
    from matplotlib import pyplot as plt
    import matplotlib.cm as cm

    # The PV names for the camera and for the image
    camPv = 'MEC:GIGE:CAM1'
    #
    imagePv = camPv.replace('CAM', 'IMAGE')

    try:
        # Setup the camera
        cam = GigECamera(camPv)
        print 'Manufacturer: ' + cam.manufacturer()
        print 'Model: ' +  cam.model()
        print 'MaxSizeX: %d' %  cam.maxSizeX()
        print 'MaxSizeY: %d' %  cam.maxSizeY()
        print 'ArraySizeX: %d' %  cam.arraySizeX()
        print 'ArraySizeY: %d' %  cam.arraySizeY()
        print 'ArraySizeZ: %d' %  cam.arraySizeZ()
        # Exposure
        cam.setAcquireTime(0.05)
        cam.setAcquirePeriod(1)
        cam.setGain(10)
        # Region of Interest
        cam.setMinX(0)
        cam.setMinY(0)
        MaxSizeX = cam.maxSizeX() & -4  # for word alignment
        MaxSizeY = cam.maxSizeY()
        cam.setSizeX(MaxSizeX)
        cam.setSizeY(MaxSizeY)
        # Binning
        cam.setBinX(1)
        cam.setBinY(1)
        # Image Mode: Continuous
        cam.setImageMode(2)
        # Trigger Mode:  Fixed Rate
        cam.setImageMode(5)
        # Start
        cam.setAcquire(1)

        # Grab the image
        img = GigEImage(imagePv)
        data = img.grab()

        # Stop the camera
        cam.setAcquire(0)

        # Display the image
        if (data.ndim == 3):
            plt.imshow(data)                     # color image
        else:
            plt.imshow(data, cmap=cm.Greys_r)    # b/w as grayscale
        plt.show()

    except Exception, e:
        print 'Exception: %s' %(e)


if __name__ == '__main__':
    main()
