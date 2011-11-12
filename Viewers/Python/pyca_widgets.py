#! /bin/env python

import pyca
from PyQt4.QtCore import SIGNAL
from Pv import Pv

class PycaWidgetConnection:
    
    def __init__(self, pv_name, widget, timeout = 1.0):
        self.pv = Pv(pv_name)
        self.widget = widget
        self.timeout = timeout
        self.val = None
        self.pv_connected = False
        self.connect_pv()

    def __del__(self):
        self.pv.disconnect()

    def connect_pv(self):
        try:
            self.pv.connect(self.timeout)
            self.pv_connected = True
            self.val = self.pv.get()
            self.pv.monitor_cb = self._update_widget
            evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM  
            self.pv.monitor(evtmask)    
            pyca.flush_io()
            self.widget.setEnabled(True)
        except:
            pass

    def disconnect_pv(self):
        self.pv.unsubscribe()    
        if self.pv_connected:
            self.pv.disconnect()
        self.pv_connected = False

    def _update_widget(self, exception = None):
        if exception == None:
            try:
                self.val = self.pv.value
                if not self.widget.hasFocus():
                    self.widget.setText(str(self.val))
                self.widget.setEnabled(True)
            except:
                1/0
                self.widget.setEnabled(False)
        else:
            1/0
            self.widget.setEnabled(False)

    def _update_pv(self):
        if self.pv_connected:
            # print self.pv.name + "(type=%s) => " \
                  # % self.pv.type() + self.widget.text()
            try:
                val = self.widget.text()
                if self.pv.type() == 'DBF_ENUM':
                    val = int(val)
                elif self.pv.type() == 'DBF_INT':
                    val = int(val)
                elif self.pv.type() == 'DBF_LONG':
                    val = int(val)
                elif self.pv.type() == 'DBF_FLOAT':
                    val = float(val)
                elif self.pv.type() == 'DBF_DOUBLE':
                    val = float(val)
                self.pv.put(val, self.timeout)
            except Exception, e:
                # FIXME - remove print; use log
                print self.pv.name + "(type=%s) put failed: val = " \
                      % self.pv.type() + str(val) + '  ' + str(e)


class PycaLabelConnection(PycaWidgetConnection):

    def connect_pv(self):
        try:
            self.pv.connect(self.timeout)
            self.pv_connected = True
            self.val = self.pv.get()
            self.pv.monitor_cb = self._update_widget
            evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM  
            self.pv.monitor(evtmask)    
            pyca.flush_io()
            self.widget.setText(str(self.val))
            self.widget.setEnabled(True)
        except:
            self.widget.setEnabled(False)



class PycaLineEditConnection(PycaWidgetConnection):
    
    def __init__(self, pv_name, line_edit, timeout = 1.0):
        PycaWidgetConnection.__init__(self, pv_name, line_edit, timeout)
        self.widget.editingFinished.connect(self._update_pv)


class PycaComboBoxConnection(PycaWidgetConnection):
    
    def __init__(self, pv_name, combo_box, timeout = 1.0, items = ()):
        PycaWidgetConnection.__init__(self, pv_name, combo_box, timeout)
        self.widget.clear()
        self.widget.addItems(items)
        if self.val == None: self.val = 0
        self.widget.setCurrentIndex(self.val)
        self.widget.connect(self.widget, SIGNAL("currentIndexChanged(int)"), self._update_pv)

    def connect_pv(self):
        try:
            self.pv.connect(self.timeout)
            self.pv_connected = True
            self.val = self.pv.get()
            self.pv.monitor_cb = self._update_widget
            evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM  
            self.pv.monitor(evtmask)    
            pyca.flush_io()
            self.widget.setEnabled(True)
        except:
            pass

    def _update_widget(self, exception = None):
        if exception == None:
            try:
                self.val = self.pv.value
                if not self.widget.hasFocus():
                    self.widget.setCurrentIndex(self.val)
            except:
                pass
        else:
            pass

    def _update_pv(self):
        if self.pv_connected:
            try:
                val = self.widget.currentIndex()
                if self.pv.type() == 'DBF_ENUM':
                    val = int(val)
                if self.pv.type() == 'DBF_INT':
                    val = int(val)
                elif self.pv.type() == 'DBF_FLOAT':
                    val = float(val)
                self.pv.put(val, self.timeout)
            except Exception, e:
                # FIXME - remove print; use log
                print self.pv.name + "(type=%s) put failed: val = " \
                      % self.pv.type() + str(val) + '  ' + str(e)


class PycaPushButton(PycaWidgetConnection):
    
    def __init__(self, pv_name, push_button, timeout = 1.0, value = 0):
        PycaWidgetConnection.__init__(self, pv_name, push_button, timeout)
        self.widget.clicked.connect(self._update_pv)
        self.val = value

    def connect_pv(self):
        try:
            self.pv.connect(self.timeout)
            self.pv_connected = True
            self.val = self.pv.get()
            self.pv.monitor_cb = self._update_widget
            pyca.flush_io()
            self.widget.setEnabled(True)
        except:
            pass

    def disconnect_pv(self):
        if self.pv_connected:
            self.pv.disconnect()
        self.pv_connected = False

    def _update_widget(self, exception = None):
        pass

    def _update_pv(self):
        if self.pv_connected:
            try:
                self.pv.put(self.val, self.timeout)
            except Exception, e:
                # FIXME - remove print; use log
                print self.pv.name + "(type=%s) put failed: val = " \
                      % self.pv.type() + str(self.val) + '  ' + str(e)


if __name__ == '__main__':
    import sys
    from options import Options
    from PyQt4.QtGui import QApplication
    from PyQt4.QtGui import QWidget
    from PyQt4.QtGui import QLabel
    from PyQt4.QtGui import QLineEdit
    from PyQt4.QtGui import QComboBox
    from PyQt4.QtGui import QPushButton
    from PyQt4.QtGui import QVBoxLayout

    options = Options([], ['pv'], [])
    try:
        options.parse()
    except Exception, msg:
        options.usage(str(msg))
        sys.exit()

    app = QApplication([''])

    # pv = Pv(options.pv)
    pv = 'TST:R40:IOC:20:UPTIME'
    lab = QLabel()
    PycaLabelConnection(pv, lab)
    pv = 'TST:EXP:CVV:02:AutoGain'
    le = QLineEdit()
    PycaLineEditConnection(pv, le)
    b = QPushButton('Start')
    PycaPushButton(pv, b, value=1)
    pv = 'TST:EXP:CVV:03:AutoGain'
    cb = QComboBox()
    PycaComboBoxConnection(pv, cb, items=('Disabled', 'Enabled'))

    layout = QVBoxLayout()
    layout.addWidget(lab)
    layout.addWidget(le)
    layout.addWidget(cb)
    layout.addWidget(b)

    win = QWidget()
    win.resize(250, 50)
    win.setWindowTitle('Hello world!')
    win.setLayout(layout)
    win.show()

    sys.exit(app.exec_())
