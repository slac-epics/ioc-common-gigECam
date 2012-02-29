#! /bin/env python

import sys
import logging
import pyca
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QWidget
from Pv import Pv

class PycaWidget(QWidget):
    
    def __init__(self, pv_name, widget, timeout = 1.0):
        QWidget.__init__(self)
        self.pv = Pv(pv_name)
        self.widget = widget
        self.timeout = timeout
        self.val = None
        self.callback = None
        self.pv_connected = False
        self.widget.setEnabled(False)
        # logging.debug("PycaWidget: starting %s timer ...", pv_name)
        QTimer.singleShot(50, self.connect_pv)

    def __del__(self):
        # logging.debug("deleting %s", self.pv.name)
        if self.pv_connected:
            # logging.debug("disconnecting %s", self.pv.name)
            self.pv.disconnect()
            self.pv_connected = False

    def connect_pv(self):
        # logging.debug("connecting to %s", self.pv.name)
        try:
            self.pv.connect(self.timeout)
            self.pv_connected = True
            self.pv.monitor_cb = self._update_widget
            self.pv.connect_cb = self._disconnected
            evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM  
            self.pv.monitor(evtmask)    
            pyca.flush_io()
            self.widget.setEnabled(True)
        except Exception, e:
            # logging.warning("PycaWidget:  connect error: %s", str(e))
            self.pv.disconnect()
            self.pv_connected = False
            self.widget.setEnabled(False)
            QTimer.singleShot(1000, self.connect_pv)

    def disconnect_pv(self):
        # logging.debug("PycaWidget: %s" % self.pv.name)
        self.pv.unsubscribe()    
        if self.pv_connected:
            # logging.debug("disconnecting pv %s", self.pv.name)
            self.pv.disconnect()
        self.pv_connected = False

    def _update_widget(self, exception = None):
        if exception == None:
            try:
                self.val = self.pv.value
                self.widget.setText(str(self.val))
                self.pv_connected = True
                self.widget.setEnabled(True)
                if self.callback:
                    self.callback()
            except:
                self.widget.setEnabled(False)
        else:
            # logging.debug("error")
            self.widget.setEnabled(False)

    def _disconnected(self, exception = None):
        self.pv_connected = False
        self.widget.setEnabled(False)

    def _update_pv(self):
        if self.pv_connected:
            try:
                val = self.widget.text()
                if self.pv.type() == 'DBF_ENUM':
                    val = int(val)
                elif self.pv.type() == 'DBF_INT':
                    val = int(val)
                elif self.pv.type() == 'DBF_LONG':
                    val = long(val)
                elif self.pv.type() == 'DBF_FLOAT':
                    val = float(val)
                elif self.pv.type() == 'DBF_DOUBLE':
                    val = float(val)
                self.pv.put(val, self.timeout)
            except Exception, e:
                # logging.debug("failed:  %s", str(e))
                pass

    def setCallback(self, cb):
        self.callback = cb

class PycaLabel(PycaWidget):
    def __init__(self, pv_name, label, timeout = 1.0):
        PycaWidget.__init__(self, pv_name, label, timeout)


class PycaLineEdit(PycaWidget):
    
    def __init__(self, pv_name, line_edit, timeout = 1.0):
        PycaWidget.__init__(self, pv_name, line_edit, timeout)
        self.widget.editingFinished.connect(self._update_pv)


class PycaComboBox(PycaWidget):
    
    def __init__(self, pv_name, combo_box, timeout = 1.0, items = (), value = 0):
        # logging.debug("PycaComboBox:  combo_box had %d items", combo_box.count())
        PycaWidget.__init__(self, pv_name, combo_box, timeout)
        self.val = value
        self.widget.clear()
        # logging.debug("PycaComboBox:  widget had %d items", self.widget.count())
        # logging.debug("PycaComboBox:  len of items is %d", len(items))
        self.widget.addItems(items)
        # logging.debug("PycaComboBox:  widget had %d items", self.widget.count())
        self.widget.setCurrentIndex(self.val)
        self.widget.connect(self.widget, SIGNAL("currentIndexChanged(int)"), self._update_pv)

    def _update_widget(self, exception = None):
        # logging.debug("PycaComboBox:  _update_widget")
        if exception == None:
            try:
                self.val = self.pv.value
                # logging.debug("PycaComboBox:  val = %d", int(self.val))
                self.widget.setCurrentIndex(int(self.val))
                self.pv_connected = True
                self.widget.setEnabled(True)
            except Exception, e:
                # logging.debug("PycaComboBox:  error:  %s", str(e))
                self.widget.setEnabled(False)
        else:
            # logging.debug("PycaComboBox:  error")
            pass

    def _update_pv(self):
        if self.pv_connected:
            try:
                # TODO: might want to map val using a dictionary
                val = self.widget.currentIndex()
                if self.pv.type() == 'DBF_ENUM':
                    val = int(val)
                elif self.pv.type() == 'DBF_INT':
                    val = int(val)
                elif self.pv.type() == 'DBF_LONG':
                    val = long(val)
                elif self.pv.type() == 'DBF_FLOAT':
                    val = float(val)
                elif self.pv.type() == 'DBF_DOUBLE':
                    val = float(val)
                self.pv.put(val, self.timeout)
            except Exception, e:
                # logging.debug("caput failed:  %s", str(e))
                pass


class PycaPushButton(PycaWidget):
    
    def __init__(self, pv_name, push_button, timeout = 1.0, value = 0):
        PycaWidget.__init__(self, pv_name, push_button, timeout)
        self.widget.clicked.connect(self._update_pv)
        self.val = value

    def _update_widget(self, exception = None):
        if exception == None:
            self.pv_connected = True
            self.widget.setEnabled(True)
        else:
            # logging.debug("PycaPushButton:  error")
            self.widget.setEnabled(False)

    def _update_pv(self):
        if self.pv_connected:
            try:
                self.pv.put(self.val, self.timeout)
            except Exception, e:
                # logging.debug("caput failed:  %s", str(e))
                pass


def main(args):
    from PyQt4.QtGui import QApplication
    from PyQt4.QtGui import QWidget
    from PyQt4.QtGui import QLabel
    from PyQt4.QtGui import QLineEdit
    from PyQt4.QtGui import QComboBox
    from PyQt4.QtGui import QPushButton
    from PyQt4.QtGui import QVBoxLayout

    app = QApplication(args)

    # the gui widgets
    lab = QLabel()
    le = QLineEdit()
    bStart = QPushButton('Start')
    bStop = QPushButton('Stop')
    lCount = QLabel()
    cb = QComboBox()
    # cb.addItems(('0', '1', '2', '3'))

    # the pyca connected widgets
    ioc = 'XCS:R42:IOC:38:UPTIME'
    cam = 'XCS:GIGE:CAM2:'
    myLab = PycaLabel(ioc, lab)
    myLe = PycaLineEdit(cam+'Gain', le)
    myStartButton = PycaPushButton(cam+'Acquire', bStart, value=1)
    myStopButton = PycaPushButton(cam+'Acquire', bStop, value=0)
    myLabCount = PycaLabel(cam+'ArrayCounter_RBV', lCount)
    myCB = PycaComboBox(cam+'Cross1Color', cb, items = ('0', '1', '2', '3', '4', '5'))

    # layout the widgets
    layout = QVBoxLayout()
    layout.addWidget(myLab)
    layout.addWidget(le)
    layout.addWidget(bStart)
    layout.addWidget(bStop)
    layout.addWidget(lCount)
    layout.addWidget(cb)

    # place them in a main window
    win = QWidget()
    win.resize(250, 50)
    win.setWindowTitle('Hello world!')
    win.setLayout(layout)
    win.show()

    # the application's event loop
    sys.exit(app.exec_())


if __name__ == '__main__':
    logging.basicConfig(format='%(filename)s:%(lineno)d:%(levelname)-8s %(funcName)s: %(message)s',
                        level=logging.DEBUG)
    main(sys.argv)
