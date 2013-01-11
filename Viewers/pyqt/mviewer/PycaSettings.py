#! /bin/env python
from ConnectedPv import ConnectedPv
from PyQt4.QtCore import QObject, SIGNAL
#from PyQt4.QtGui import QApplication, QImage, QColor, QWidget

class PycaSettings():

    def __init__(self, pv_name, cam, parent=None):
        self.parent = parent
        self.name = pv_name
        self.cam = cam
        print 'PycaSettings pv_name', self.name
        self.acq_stat_pv = ConnectedPv(pv_name + ':Acquire_RBV'     , self.upd_acq_stat)
        self.exp_time_pv = ConnectedPv(pv_name + ':AcquireTime_RBV' , self.upd_exp_time)
        self.cam_gain_pv = ConnectedPv(pv_name + ':Gain_RBV'        , self.upd_cam_gain)
        
        self.emitter  = QObject()
        self.new_settings_callback = None

    def disconnect(self):
        self.acq_stat_pv.disconnect()
        self.exp_time_pv.disconnect()
        self.cam_gain_pv.disconnect()

    def upd_acq_stat(self):
        #print 'upd_acq_stat here' 
        #print self.cam['pv'][pvname]['name'], self.acq_stat_pv.value
        #self.cam['pv'][pvname]['value'] = int(self.acq_stat_pv.value)
        self.upd_parameter('Acquire_RBV', int(self.acq_stat_pv.value))        
        
    def upd_exp_time(self):
        #pvname = 'AcquireTime_RBV'
        #self.cam['pv'][pvname]['value'] = float(self.exp_time_pv.value)
        self.upd_parameter('AcquireTime_RBV', float(self.exp_time_pv.value))
         
    def upd_cam_gain(self):
        #pvname = 'Gain_RBV'        
        #self.cam['pv'][pvname]['value'] = float(self.cam_gain_pv.value)
        self.upd_parameter('Gain_RBV', float(self.cam_gain_pv.value))

    def upd_parameter(self, pv, value):
        '''Updates the indicators from camera setings'''
        if not self.cam['pv']['name']:
            return False
        #self.sig0 = SIGNAL("par_upd(int, Qstring, QVariant)")
        #self.emit(self.sig0, self.cam['id'], self.cam['pv'][pv]['name'], self.cam)
        self.parent.par_upd(self.cam['cam_n'], pv, value)
    
    def set_new_settings_callback(self, fnct):
        QObject.connect(self.emitter, SIGNAL('settings_changed'), fnct)

    def settings_changed(self):
        print 'settings_changed where'
        self.emitter.emit(SIGNAL('settings_changed'), self.cam)

if __name__ == '__main__':
    print 'Need to do example here'

