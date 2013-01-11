#! /bin/env python
import sys
from PyQt4 import QtGui, QtCore, uic
from ConnectedPv import ConnectedPv
from PycaImage import PycaImage
from PycaSettings import PycaSettings
from collections import OrderedDict
import time
import math
import pyca
from Pv import Pv

N_CAMS = 8
class CamCA(QtCore.QObject):
    def __init__(self, parent=None):
        pass
    
    def put(self, pvname, value, timeout=1.0):
        try:
            pv = Pv(str(pvname))
            pv.connect(timeout)
            pv.get(ctrl=False, timeout=timeout)
            pv.put(value, timeout)
            pv.disconnect()
        except pyca.pyexc, e:
            print 'ERROR: pyca exception %s' %(e)
        except pyca.caexc, e:
            print 'ERROR: channel access exception %s' %(e)
            
    def get(self, pvname, pvshort=True, timeout=1.0):
        try:
            pv = Pv(str(pvname))
            pv.connect(timeout)
            pv.get(ctrl=pvshort, timeout=timeout)
            value = pv.value
            print 'value', value
            pv.disconnect()
        except pyca.pyexc, e:
            print 'ERROR: pyca exception %s' %(e)
            return None
        except pyca.caexc, e:
            print 'ERROR: channel access exception %s' %(e)
            return None
        return value
                
class DisplayImage(QtGui.QWidget):
    # A widget for displaying an image from a GigE camera
    def __init__(self, cam):
        QtGui.QWidget.__init__(self, cam['wdg']['w_Img'])
        self.cam = cam
        self.wImg = self.cam['wdg']['w_Img']
        self.image = self.cam['image'].img 
        self.scaled_image = self.cam['image'].img
        self.xoff = 0
        self.yoff = 0        
        self.scale = 1.0
        self.old_width = 0
        self.old_height = 0
        self.painter = QtGui.QPainter()
        self.cam['image'].set_new_image_callback(self.set_image)
        self.updates = 0
        self.last_updates = 0
        self.new_value = False
        self.pvname = self.cam['pv']['name']

        self.last_time = time.time()
        self.rateTimer = QtCore.QTimer()
        self.rateTimer.timeout.connect(self.calcdisplayrate)
        self.rateTimer.start(1000)        
            
#    def set_image_size(self):
#        if self.size0 != None and self.size1 != None and self.size2 != None:
#            #print "size0 = %d" % self.size0
#            #print "size1 = %d" % self.size1
#            #print "size2 = %d" % self.size2
#            # FIXME  - look at NDimensions_RBV
#            
#            if self.cam['ColorMode_RBV']['value'] == 'Mono':                    # b/w image
#                iformat = QtGui.QImage.Format_Indexed8
#                width = self.size0
#                height = self.size1
#                # logging.debug("format=b/w")
#            else: # self.size0 == 3:      # color image
#                iformat = QtGui.QImage.Format_RGB32
#                width = self.size1
#                height = self.size2
#                # logging.debug("format=color")                
#            # logging.debug("width=%d  height=%d", width, height)
#            self.img = QtGui.QImage(width, height, iformat)
#            if format == QtGui.QImage.Format_Indexed8:
#                # TODO: insert colortable routine ...
#                colorTable = [QtGui.QColor(i, i, i).rgb() for i in range(256)]
#                self.img.setColorTable(colorTable)
#            # TODO  - emit changed img object signal if we had a previous img object
#            try:
#                buf = int(self.img.bits())
#                size = width * height
#                # logging.debug("buf=0x%08x  size=%d", buf, size)
#                bytesPerLine = self.img.bytesPerLine()
#                self.data_pv.set_processor(buf, size, width, height, bytesPerLine, format)
#            except:
#                pass
#                 

    def paintEvent(self, event):
        self.painter.begin(self)
        if self.scaled_image:
            self.painter.drawImage(self.xoff, self.yoff, self.scaled_image)
        self.painter.end()
        self.updates += 1
                       
    def set_image(self, img):
        self.setGeometry(QtCore.QRect(0, 0, self.wImg.width(), self.wImg.height()))
        self.image = img
        if self.image and not self.image.isNull():
            self.scaled_image = self.image.scaled(self.width(), self.height(), aspectRatioMode = QtCore.Qt.KeepAspectRatio)
        self.update()        
        
    def calcdisplayrate(self):
        now = time.time() # FPS --------------------------------------
        updates = self.updates - self.last_updates
        delta = now - self.last_time
        rate = updates/delta
        self.last_updates = self.updates
        fps = '%.1f' % rate
        t = time.time() # TIMESTAMP ----------------------------------
        l = time.localtime(t)
        f = '.%02d' % int(100 * math.modf(t)[0] + 0.5)
        timestamp = ('%04d-%02d-%02d_%02d:%02d:%02d' % (l[:6])) + f
        title = '| C%s | %5s fps | %s  |' % (self.cam['cam_n'], fps, timestamp) 
        # ------------------------------------------------------------
        self.cam['wdg']['dockWidget'].setWindowTitle(title)
        self.last_time = now                 
        
#    def get_string(self, pvname):
#        #pv = Pv('MEC:LAS:GIGE:CAM1:ColorMode_RBV')
#        pv = Pv(pvname)
#        pv.set_string_enum(True)
#        pv.connect(timeout=2.0)
#        pv.get(ctrl=False, timeout=1.0)
#        print pv.value
#        pv.disconnect()         



class UpdateSettings(QtGui.QWidget):
    # A widget for update parameters from a GigE camera
    def __init__(self, cam):
        QtGui.QWidget.__init__(self, parent=None)
        self.cam = cam
        self.cam['params'].set_new_settings_callback(self.upd_settings)
        self.new_value = False
        self.ca = CamCA()
        self.val = 0
        
    def upd_settings(self):
        print 'upd_settings here'
        if self.new_value:
            self.ca.put(self.pvname, self.val)
            self.new_value = False
        
    def set_pv(self, pv, val):
        '''update camera setings'''
        self.pvname = self.cam['pv'][pv]['name']
        self.val = val
        print 'set_pv', self.new_value, self.pvname, self.val
        self.ca.put(self.pvname, self.val)

#form_class, base_class = uic.loadUiType('ui/viewer2x4.ui')
form_class, base_class = uic.loadUiType('ui/CamLaserApp.ui')
class Viewer(QtGui.QWidget, form_class):
    '''Display multiple gigE cameras in a single application'''
    def __init__(self, pv_names=[], parent=None):
        super(Viewer, self).__init__(parent)
        self.setupUi(self)
        self.pvnames = pv_names
        self._create_widgetdict()
        self._create_slots()
        self.show()

    def _create_slots(self):
        '''Create connections'''
        self.set_acqrs = [self.set_acqr for i in range(7)]
        self.set_expts = [self.set_expt for i in range(7)]
        self.set_gains = [self.set_gain for i in range(7)]
        self.set_bins  = [self.set_bin  for i in range(7)]
        
        self.set_jets  = [self.set_jet  for i in range(7)]
        self.set_hsvs  = [self.set_hsv  for i in range(7)]
        self.set_cools = [self.set_cool for i in range(7)]
        self.set_grays = [self.set_gray for i in range(7)]
        self.set_hots  = [self.set_hot  for i in range(7)]
        
        self.set_hSRngMins = [self.set_hSRngMin for i in range(7)]
        self.set_lERngMins = [self.set_lERngMin for i in range(7)]
        self.set_hSRngMaxs = [self.set_hSRngMax for i in range(7)]
        self.set_lERngMaxs = [self.set_lERngMax for i in range(7)]
                
        objc = QtCore.QObject.connect
        sig0 = QtCore.SIGNAL("clicked()")
        sig1 = QtCore.SIGNAL("valueChanged(double)")
        sig2 = QtCore.SIGNAL("valueChanged(int)")
        sig3 = QtCore.SIGNAL("currentIndexChanged(int)")
        sig4 = QtCore.SIGNAL("par_upd(int, QVariant, QVariant)")
        for i in range(1, N_CAMS+1):
            if self.cam[i]['pv']['name']:
                self.cam[i]['image'] = PycaImage(self.cam[i]['pv']['image'])
                self.cam[i]['params'] = PycaSettings(self.cam[i]['pv']['cam'], self.cam[i], self)
                self.cam[i]['display'] = DisplayImage(self.cam[i])
                self.cam[i]['settings'] = UpdateSettings(self.cam[i])                
                objc(self.cam[i]['settings'], sig4, self.par_upd) 
                objc(self.cam[i]['wdg']['cB_on'], sig0, self.set_acqrs[i-1])
                objc(self.cam[i]['wdg']['dS_expt'], sig1, self.set_expts[i-1])
                objc(self.cam[i]['wdg']['iS_gain'], sig2, self.set_gains[i-1])
                objc(self.cam[i]['wdg']['cmB_bin'], sig3, self.set_bins[i-1])
                self.cam[i]['wdg']['lEpvname'].setText(self.cam[i]['pv']['cam'])
            else:
#                self.cam[i]['wdg']['dockWidget'].setVisible(False)
#                self.cam[i]['wdg']['dockWidget_1'].setVisible(False)
                self.cam[i]['wdg']['dockWidget'].setEnabled(False)
                self.cam[i]['wdg']['dockWidget_1'].setEnabled(False)
                       
    def set_expt(self):
        cam_n = self.lExpT[self.sender()]
        val = float(self.cam[cam_n]['wdg']['dS_expt'].value())
        self.snd_cmd(cam_n, 'AcquireTime', val)
    
    def set_gain(self):
        cam_n = self.lGain[self.sender()]
        val = float(self.cam[cam_n]['wdg']['iS_gain'].value())
        self.snd_cmd(cam_n, 'Gain', val)  

    def set_bin(self):
        cam_n = self.cmBBin[self.sender()]
        bindex = self.cam[cam_n]['wdg']['cmB_bin'].currentIndex()
        self.snd_cmd(cam_n, 'BinX', bindex + 1)  
        self.snd_cmd(cam_n, 'BinY', bindex + 1)
        self.cam[cam_n]['display'].update()  
        
    def set_acqr(self):
        cam_n = self.cB_on[self.sender()]
        if self.cam[cam_n]['wdg']['cB_on'].isChecked(): val = 1
        else:                                    val = 0
        self.snd_cmd(cam_n, 'Acquire', val)

    def set_hsv(self):
        print  'TODO later needs mod in gui combo'
        return False
        cam_n = self.set_hsvs[self.sender()]
        self.colorMap = "hsv"
        self.setColorMap(cam_n, 'hsv')
    
    def set_hot(self):
        print  'TODO later needs mod in gui combo'
        return False
        cam_n = self.hots[self.sender()]
        self.colorMap = "hot"
        self.setColorMap(cam_n, 'hot')
    
    def set_jet(self):
        print  'TODO later needs mod in gui combo'
        return False
        cam_n = self.lExpT[self.sender()]
        self.colorMap = "jet"
        self.setColorMap(cam_n, 'jet')
    
    def set_cool(self):
        print  'TODO later needs mod in gui combo'
        return False
        cam_n = self.lExpT[self.sender()]
        self.colorMap = "cool"
        self.setColorMap(cam_n, 'cool')
    
    def set_gray(self):
        print  'TODO later needs mod in gui combo'
        return False
        cam_n = self.lExpT[self.sender()]
        self.colorMap = "gray"    
        self.setColorMap(cam_n, 'gray')

    def set_hSRngMin(self):
        print  'TODO later needs mod in gui combo'
        return False
        cam_n = self.lExpT[self.sender()]
        self.colorMap = "gray"    
        self.setColorMap()
   
    def set_lERngMin(self):
        print  'TODO later needs mod in gui combo'
        return False
        cam_n = self.lExpT[self.sender()]
        self.colorMap = "gray"    
        self.setColorMap()
    
    def set_hSRngMax(self):
        print  'TODO later needs mod in gui combo'
        return False
        cam_n = self.lExpT[self.sender()]
        self.colorMap = "gray"    
        self.setColorMap()
    
    def set_lERngMax(self):
        print  'TODO later needs mod in gui combo'
        return False
        cam_n = self.lExpT[self.sender()]
        self.colorMap = "gray"    
        self.setColorMap()
         
    def setColorMap(self, cam_n, cmode):
        print 'TODO self.colorMap', self.colorMap
        return 
        
    def snd_cmd(self, cam_n, par, val):
        self.cam[cam_n]['settings'].set_pv(par, val) 
                            
    def par_upd(self, cam_n, par, value):
        '''Signal from DisplayImage to update values'''
        if   par == 'AcquireTime_RBV' or par == 'Gain_RBV':
            self.cam[cam_n]['wdg'][par].setValue(value)
            self.cam[cam_n]['pv'][par]['value'] = value
        elif par == 'Acquire_RBV':
            self.cam[cam_n]['wdg'][par].setChecked(value)
            self.cam[cam_n]['pv'][par]['value'] = value
        elif par == None:
            print 'Bad parameter from Thread'
        else:
            pass        
        
    def wdg_init(self):
        self.dockWidget = {1: self.dockWidget_1,
                           2: self.dockWidget_2,
                           3: self.dockWidget_3,
                           4: self.dockWidget_4,
                           5: self.dockWidget_5,
                           6: self.dockWidget_6,
                           7: self.dockWidget_7,
                           8: self.dockWidget_8}
        
        self.w_Img = {1: self.w_Img_1,
                           2: self.w_Img_2,
                           3: self.w_Img_3,
                           4: self.w_Img_4,
                           5: self.w_Img_5,
                           6: self.w_Img_6,
                           7: self.w_Img_7,
                           8: self.w_Img_8}

        self.dockWidget_1 = {1: self.dockWidget_1_1,
                           2: self.dockWidget_1_2,
                           3: self.dockWidget_1_3,
                           4: self.dockWidget_1_4,
                           5: self.dockWidget_1_5,
                           6: self.dockWidget_1_6,
                           7: self.dockWidget_1_7,
                           8: self.dockWidget_1_8}
          
        self.lEpvname = {1: self.lEpvname_1,
                           2: self.lEpvname_2,
                           3: self.lEpvname_3,
                           4: self.lEpvname_4,
                           5: self.lEpvname_5,
                           6: self.lEpvname_6,
                           7: self.lEpvname_7,
                           8: self.lEpvname_8}   
        
        self.cmB_bin = {1: self.cmB_bin_1,
                           2: self.cmB_bin_2,
                           3: self.cmB_bin_3,
                           4: self.cmB_bin_4,
                           5: self.cmB_bin_5,
                           6: self.cmB_bin_6,
                           7: self.cmB_bin_7,
                           8: self.cmB_bin_8}   

        self.dS_expt = {1: self.dS_expt_1,
                           2: self.dS_expt_2,
                           3: self.dS_expt_3,
                           4: self.dS_expt_4,
                           5: self.dS_expt_5,
                           6: self.dS_expt_6,
                           7: self.dS_expt_7,
                           8: self.dS_expt_8}   

        self.iS_gain = {1: self.iS_gain_1,
                           2: self.iS_gain_2,
                           3: self.iS_gain_3,
                           4: self.iS_gain_4,
                           5: self.iS_gain_5,
                           6: self.iS_gain_6,
                           7: self.iS_gain_7,
                           8: self.iS_gain_8}   
                          
        self.hSRngMin = {1: self.hSRngMin_1,
                           2: self.hSRngMin_2,
                           3: self.hSRngMin_3,
                           4: self.hSRngMin_4,
                           5: self.hSRngMin_5,
                           6: self.hSRngMin_6,
                           7: self.hSRngMin_7,
                           8: self.hSRngMin_8}                             
                          
        self.lERngMin = {1: self.lERngMin_1,
                           2: self.lERngMin_2,
                           3: self.lERngMin_3,
                           4: self.lERngMin_4,
                           5: self.lERngMin_5,
                           6: self.lERngMin_6,
                           7: self.lERngMin_7,
                           8: self.lERngMin_8}                             
                                                    
        self.hSRngMax = {1: self.hSRngMax_1,
                           2: self.hSRngMax_2,
                           3: self.hSRngMax_3,
                           4: self.hSRngMax_4,
                           5: self.hSRngMax_5,
                           6: self.hSRngMax_6,
                           7: self.hSRngMax_7,
                           8: self.hSRngMax_8}  

        self.lERngMax = {1: self.lERngMax_1,
                           2: self.lERngMax_2,
                           3: self.lERngMax_3,
                           4: self.lERngMax_4,
                           5: self.lERngMax_5,
                           6: self.lERngMax_6,
                           7: self.lERngMax_7,
                           8: self.lERngMax_8}
        
        self.rBColor_Jet = {1: self.rBColor_Jet_1,
                           2: self.rBColor_Jet_2,
                           3: self.rBColor_Jet_3,
                           4: self.rBColor_Jet_4,
                           5: self.rBColor_Jet_5,
                           6: self.rBColor_Jet_6,
                           7: self.rBColor_Jet_7,
                           8: self.rBColor_Jet_8}
        
        self.rBColor_HSV = {1: self.rBColor_HSV_1,
                           2: self.rBColor_HSV_2,
                           3: self.rBColor_HSV_3,
                           4: self.rBColor_HSV_4,
                           5: self.rBColor_HSV_5,
                           6: self.rBColor_HSV_6,
                           7: self.rBColor_HSV_7,
                           8: self.rBColor_HSV_8}
        
        self.rBColor_Cool = {1: self.rBColor_Cool_1,
                           2: self.rBColor_Cool_2,
                           3: self.rBColor_Cool_3,
                           4: self.rBColor_Cool_4,
                           5: self.rBColor_Cool_5,
                           6: self.rBColor_Cool_6,
                           7: self.rBColor_Cool_7,
                           8: self.rBColor_Cool_8}
                                              
        self.rBColor_Gray = {1: self.rBColor_Gray_1,
                           2: self.rBColor_Gray_2,
                           3: self.rBColor_Gray_3,
                           4: self.rBColor_Gray_4,
                           5: self.rBColor_Gray_5,
                           6: self.rBColor_Gray_6,
                           7: self.rBColor_Gray_7,
                           8: self.rBColor_Gray_8}
        
        self.rBColor_Hot = {1: self.rBColor_Hot_1,
                           2: self.rBColor_Hot_2,
                           3: self.rBColor_Hot_3,
                           4: self.rBColor_Hot_4,
                           5: self.rBColor_Hot_5,
                           6: self.rBColor_Hot_6,
                           7: self.rBColor_Hot_7,
                           8: self.rBColor_Hot_8}
              
        self.cBoxScale = {1: self.cBoxScale_1,
                           2: self.cBoxScale_2,
                           3: self.cBoxScale_3,
                           4: self.cBoxScale_4,
                           5: self.cBoxScale_5,
                           6: self.cBoxScale_6,
                           7: self.cBoxScale_7,
                           8: self.cBoxScale_8}      
        
        self.cB_on = {1: self.cB_on_1,
                           2: self.cB_on_2,
                           3: self.cB_on_3,
                           4: self.cB_on_4,
                           5: self.cB_on_5,
                           6: self.cB_on_6,
                           7: self.cB_on_7,
                           8: self.cB_on_8}      
                
        self.rB_iocmod = {1: self.rB_iocmod_1,
                           2: self.rB_iocmod_2,
                           3: self.rB_iocmod_3,
                           4: self.rB_iocmod_4,
                           5: self.rB_iocmod_5,
                           6: self.rB_iocmod_6,
                           7: self.rB_iocmod_7,
                           8: self.rB_iocmod_8}
              
        self.pB_save = {1: self.pB_save_1,
                           2: self.pB_save_2,
                           3: self.pB_save_3,
                           4: self.pB_save_4,
                           5: self.pB_save_5,
                           6: self.pB_save_6,
                           7: self.pB_save_7,
                           8: self.pB_save_8}   

        self.wdg = {'dockWidget': self.dockWidget,
                        'w_Img': self.w_Img,
                        'dockWidget_1': self.dockWidget_1,
                        'lEpvname': self.lEpvname,
                        'cmB_bin': self.cmB_bin,
                        'dS_expt': self.dS_expt,
                        'AcquireTime_RBV': self.dS_expt,
                        'AcquireTime': self.dS_expt,
                        'iS_gain': self.iS_gain,
                        'Gain_RBV': self.iS_gain,
                        'Gain': self.iS_gain,
                        'BinXY': self.cmB_bin,
                        'hSRngMin': self.hSRngMin,
                        'lERngMin': self.lERngMin,
                        'hSRngMax': self.hSRngMax,
                        'lERngMax': self.lERngMax,
                        'rBColor_Jet': self.rBColor_Jet,
                        'rBColor_HSV': self.rBColor_HSV,
                        'rBColor_Cool': self.rBColor_Cool,
                        'rBColor_Gray': self.rBColor_Gray,
                        'rBColor_Hot': self.rBColor_Hot,
                        'cBoxScale': self.cBoxScale,
                        'cB_on': self.cB_on,
                        'Acquire_RBV': self.cB_on,
                        'Acquire': self.cB_on,
                        'rB_iocmod': self.rB_iocmod,
                        'pB_save': self.pB_save}
                
    def _create_widgetdict(self):
        '''Creates widget dictionary'''
        ''' Equivalent calls:
            print '-----------'
            print  self.w_Img_7
            print self.cam[self.cam[7]['cam_n']]['wdg']['w_Img']
            print self.cam[7]['wdg']['w_Img']
            print '-----------'
        '''        
        
        self.wdg_init()
        self.cam = {}
        self.cam['n_cameras'] = len(self.pvnames)
        n_cameras = self.cam['n_cameras']

        # widgets ordered dict:
        self.lGain    = OrderedDict()
        self.cmBBin   = OrderedDict()
        self.cB_on    = OrderedDict()
        self.lExpT    = OrderedDict()
        self.hSRngMin = OrderedDict()
        self.lERngMin = OrderedDict()
        self.hSRngMax = OrderedDict()
        self.lERngMax = OrderedDict()
        
        # populating cam dictionary
        #TODO: to cleanup
        for i in range(1, N_CAMS+1):
            self.cam[i] = {}
            self.cam[i]['pv'] = {}
            self.cam[i]['wdg'] = {}
            self.cam[i]['display'] = None
            self.cam[i]['cam_n'] = i  # Camera index
            self.cam[i]['fps'] = ''   # frames per second value
            self.cam[i]['tstp'] = ''  # timestamp value
            self.cam[i]['img'] = None # img
            self.cam[i]['display'] = None
            self.cam[i]['image'] = None
            self.cam[i]['cam'] = None
            self.cam[i]['settings'] = None
                        
            for wdgname, wdg in self.wdg.iteritems():
                self.cam[i]['wdg'][wdgname] = wdg[i]
                            
            # assign cam number to widgets:
            self.cB_on[self.cam[i]['wdg']['cB_on']] = i
            self.lExpT[self.cam[i]['wdg']['dS_expt']] = i
            self.lGain[self.cam[i]['wdg']['iS_gain']] = i
            self.cmBBin[self.cam[i]['wdg']['cmB_bin']] = i
            self.hSRngMin[self.cam[i]['wdg']['hSRngMin']] = i
            self.lERngMin[self.cam[i]['wdg']['lERngMin']] = i
            self.hSRngMax[self.cam[i]['wdg']['hSRngMax']] = i
            self.lERngMax[self.cam[i]['wdg']['lERngMax']] = i
            
            if n_cameras:  
                self.cam[i]['pv']['cam'] = self.pvnames[i-1]
                
                self.cam[i]['pv']['Acquire_RBV'] = {}
                self.cam[i]['pv']['Acquire_RBV']['name'] = self.cam[i]['pv']['cam'] + ':' + 'Acquire_RBV'
                self.cam[i]['pv']['Acquire_RBV']['value'] = None
                
                self.cam[i]['pv']['Gain_RBV'] = {}
                self.cam[i]['pv']['Gain_RBV']['name'] = self.cam[i]['pv']['cam'] + ':' + 'Gain_RBV'
                self.cam[i]['pv']['Gain_RBV']['value'] = None
                
                self.cam[i]['pv']['AcquireTime_RBV'] = {}
                self.cam[i]['pv']['AcquireTime_RBV']['name'] = self.cam[i]['pv']['cam'] + ':' + 'AcquireTime_RBV'
                self.cam[i]['pv']['AcquireTime_RBV']['value'] = None

                self.cam[i]['pv']['Acquire'] = {}
                self.cam[i]['pv']['Acquire']['name'] = self.cam[i]['pv']['cam'] + ':' + 'Acquire'
                self.cam[i]['pv']['Acquire']['value'] = None
                
                self.cam[i]['pv']['Gain'] = {}
                self.cam[i]['pv']['Gain']['name'] = self.cam[i]['pv']['cam'] + ':' + 'Gain'
                self.cam[i]['pv']['Gain']['value'] = None
                
                self.cam[i]['pv']['AcquireTime'] = {}
                self.cam[i]['pv']['AcquireTime']['name'] = self.cam[i]['pv']['cam'] + ':' + 'AcquireTime'
                self.cam[i]['pv']['AcquireTime']['value'] = None

                self.cam[i]['pv']['BinX_RBV'] = {}
                self.cam[i]['pv']['BinX_RBV']['name'] = self.cam[i]['pv']['cam'] + ':' + 'BinX_RBV'
                self.cam[i]['pv']['BinX_RBV']['value'] = None
                
                self.cam[i]['pv']['BinY_RBV'] = {}
                self.cam[i]['pv']['BinY_RBV']['name'] = self.cam[i]['pv']['cam'] + ':' + 'BinY_RBV'
                self.cam[i]['pv']['BinY_RBV']['value'] = None

                self.cam[i]['pv']['BinX'] = {}
                self.cam[i]['pv']['BinX']['name'] = self.cam[i]['pv']['cam'] + ':' + 'BinX'
                self.cam[i]['pv']['BinX']['value'] = None
                
                self.cam[i]['pv']['BinY'] = {}
                self.cam[i]['pv']['BinY']['name'] = self.cam[i]['pv']['cam'] + ':' + 'BinY'
                self.cam[i]['pv']['BinY']['value'] = None

                         
                self.cam[i]['pv']['name'] = ':'.join(self.pvnames[i-1].split(':')[:-1])
                pvimage = self.pvnames[i-1].replace('CAM','IMAGE')                
                self.cam[i]['pv']['image'] = pvimage
                self.cam[i]['wdg']['dockWidget'].setWindowTitle('| CAM %s | Initializing ... |' % i)
                n_cameras -= 1
            else:
                self.cam[i]['pv']['name'] = None
                self.cam[i]['wdg']['dockWidget'].setWindowTitle('| CAM %s | Not Connected    |' % i)
                
                
            
            
            
def viewerMxN():
    #cams = ['MEC:LAS:GIGE:CAM2','MEC:LAS:GIGE:CAM4']
    cams = ['MEC:LAS:GIGE:CAM1','MEC:LAS:GIGE:CAM2',
            'MEC:LAS:GIGE:CAM3','MEC:LAS:GIGE:CAM4',
            'MEC:LAS:GIGE:CAM5','MEC:LAS:GIGE:CAM6']#,
#            #'MEC:LAS:GIGE:CAM7']
#    cams = ['MEC:LAS:GIGE:CAM6','MEC:LAS:GIGE:CAM4']
    
#    cams = ['MEC:LAS:GIGE:CAM1','MEC:LAS:GIGE:CAM2',
#            'MEC:LAS:GIGE:CAM3','MEC:LAS:GIGE:CAM4']    
        
    app   = QtGui.QApplication(sys.argv)
    app.setStyle('Cleanlooks')
    app.setPalette(app.style().standardPalette())    
    win = Viewer(cams)
    win.show()   
    sys.exit(app.exec_())
       
if __name__ == '__main__':
    viewerMxN()

