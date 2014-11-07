import signal
import logging
import commands
import PyQt4.QtCore as QtCore
import pyca
from Pv import Pv

logger = logging.getLogger('mviewer.utils')

def signal_handler(signal, frame):
     logger.info( '\nShutdown application...')
     t = Viewer() # or the class that contains a clean close code
     t.shutdown()
     sys.exit(1)
    
def caput(pvname, value, timeout=2.0):
    try:
        pv = Pv(pvname)
        pv.connect(timeout)
        pv.get(ctrl=False, timeout=timeout)
        pv.put(value, timeout)
        pv.disconnect()
        #print 'caput', pvname, value
    except pyca.pyexc, e:
        logger.error( 'pyca exception: %s' %(e))
    except pyca.caexc, e:
        logger.error( 'channel access exception: %s' %(e))
        
def caget(pvname, timeout=2.0):
    try:
        pv = Pv(pvname)
        pv.connect(timeout)
        pv.get(ctrl=False, timeout=timeout)
        v = pv.value
        pv.disconnect()
        #print 'caget', pvname, v
        return v
    except pyca.pyexc, e:
        logger.error( 'pyca exception: %s' %(e))
        return []
    except pyca.caexc, e:
        logger.error( 'channel access exception: %s' %(e))
        return []
        


        
class cfginfo():
    def __init__(self):
      self.dict = {}
  
    def read(self, name):
        try:
            cfg = open(name).readlines()
            for line in cfg:
                line = line.lstrip()
                token = line.split()
                if len(token) == 2:
                    self.dict[token[0]] = token[1]
                else:
                    self.dict[token[0]] = token[1:]
            return True
        except:
            return False
  
    def add(self, attr, val):
        self.dict[attr] = val
  
    def __getattr__(self, name):
        if self.dict.has_key(name):
            return self.dict[name]
        else:
            raise AttributeError, name

class CAComm(QtCore.QThread):
    def __init__(self, lock, ctrlname, parent):
        super(CAComm, self).__init__(parent)
        self.lock      = lock
        self.mutex     = QtCore.QMutex()
        self.ctrlname  = ctrlname
        self.parent    = parent
        self.stopped   = False
        self.completed = False
        
    def isStopped(self):
        try:
            self.mutex.lock()
            return self.stopped
        finally:
            self.mutex.unlock()

    def stop(self):
        try:
            self.mutex.lock()
            self.stopped = True
        finally:
            self.mutex.unlock()
            
    def run(self):
        pyca.attach_context()
        self.send(self.pv, self.val)
        
    def set_cmd(self, pv, val):
        self.pv    = pv
        self.val   = val
        
    def send(self, pv, val):
        self.set_pv(pv, val) 
        if not 'SYSRESET' in pv:
            self.get_pv(pv+'_RBV')
    
    def set_pv(self, pv, val):
        '''Set camera parameter'''
        if 'SYSRESET' in pv:
            target = pv
            caput(target, int(val))
        else:
            target = self.ctrlname + ':' + pv
            caput(target, val)
        
        
    def get_pv(self, pv):
        '''Get camera parameter'''
        target = self.ctrlname + ':' + pv
        val = caget(target)
        return val
    
    # My dirty work until get fixed pyca:
    def get(pvname):
        status, output = commands.getstatusoutput("caget %s" % pvname)
        if status != 0:
            print 'ERROR:', output
            return None
        return ''.join(output.split()[1:])
    
    def put(pvname_value):
        status, output = commands.getstatusoutput("caput %s" % pvname_value)
        if status != 0:
            print 'ERROR:', output.split('found.')[0] + 'found.'
            return None
        return True    
