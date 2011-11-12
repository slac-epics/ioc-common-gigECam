#! /bin/env python

import sys
import logging
import pyca
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QTimer
from Pv import Pv

class PycaWidget:
    
    def __init__(self, pv_name, widget, timeout = 1.0):
        logging.debug("PycaWidget: %s", pv_name)
        self.pv = Pv(pv_name)
        self.widget = widget
        self.timeout = timeout
        self.val = None
        self.pv_connected = False
        self.widget.setEnabled(False)
        QTimer.singleShot(1000, self.connect_pv)

    def __del__(self):
        logging.debug("PycaWidget:  %s", self.pv.name)
        if self.pv_connected:
            logging.debug("disconnecting %s", self.pv.name)
            self.pv.disconnect()

    def connect_pv(self):
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
            logging.warning("PycaWidget:  connect error: %s", str(e))
            self.pv.disconnect()
            self.widget.setEnabled(False)
            QTimer.singleShot(1000, self.connect_pv)

    def disconnect_pv(self):
        logging.debug("PycaWidget: %s" % self.pv.name)
        self.pv.unsubscribe()    
        if self.pv_connected:
            logging.debug("disconnecting pv %s", self.pv.name)
            self.pv.disconnect()
        self.pv_connected = False

    def _update_widget(self, exception = None):
        if exception == None:
            try:
                self.val = self.pv.value
                self.widget.setText(str(self.val))
                self.pv_connected = True
                self.widget.setEnabled(True)
            except:
                self.widget.setEnabled(False)
        else:
            logging.debug("error")
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
                elif self.pv.type() == 'DBF_FLOAT':
                    val = float(val)
                elif self.pv.type() == 'DBF_DOUBLE':
                    val = float(val)
                self.pv.put(val, self.timeout)
            except Exception, e:
                logging.debug("failed:  %s", str(e))

class PycaLabel(PycaWidget):
    pass


class PycaLineEdit(PycaWidget):
    
    def __init__(self, pv_name, line_edit, timeout = 1.0):
        PycaWidget.__init__(self, pv_name, line_edit, timeout)
        self.widget.editingFinished.connect(self._update_pv)


class PycaComboBox(PycaWidget):
    
    def __init__(self, pv_name, combo_box, timeout = 1.0, items = (), value = 0):
        PycaWidget.__init__(self, pv_name, combo_box, timeout)
        self.val = value
        self.widget.clear()
        self.widget.addItems(items)
        self.widget.setCurrentIndex(self.val)
        self.widget.connect(self.widget, SIGNAL("currentIndexChanged(int)"), self._update_pv)

    def _update_widget(self, exception = None):
        if exception == None:
            try:
                self.val = self.pv.value
                self.widget.setCurrentIndex(int(self.val))
                self.pv_connected = True
                self.widget.setEnabled(True)
            except Exception, e:
                logging.debug("PycaComboBox:  error:  %s", str(e))
                self.widget.setEnabled(False)
        else:
            logging.debug("PycaComboBox:  error")

    def _update_pv(self):
        if self.pv_connected:
            try:
                # TODO: might want to map val using a dictionary
                val = self.widget.currentIndex()
                if self.pv.type() == 'DBF_ENUM':
                    val = int(val)
                elif self.pv.type() == 'DBF_INT':
                    val = int(val)
                elif self.pv.type() == 'DBF_FLOAT':
                    val = float(val)
                elif self.pv.type() == 'DBF_DOUBLE':
                    val = float(val)
                self.pv.put(val, self.timeout)
            except Exception, e:
                logging.debug("caput failed:  %s", str(e))


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
            logging.debug("PycaPushButton:  error")
            self.widget.setEnabled(False)

    def _update_pv(self):
        if self.pv_connected:
            try:
                self.pv.put(self.val, self.timeout)
            except Exception, e:
                logging.debug("caput failed:  %s", str(e))


def main():
    from PyQt4.QtGui import QApplication
    from PyQt4.QtGui import QWidget
    from PyQt4.QtGui import QLabel
    from PyQt4.QtGui import QLineEdit
    from PyQt4.QtGui import QComboBox
    from PyQt4.QtGui import QPushButton
    from PyQt4.QtGui import QVBoxLayout

    app = QApplication([''])

    # the gui widgets
    lab = QLabel()
    le = QLineEdit()
    b = QPushButton('Start')
    cb = QComboBox()
    cb.addItems(('0', '1', '2', '3'))

    # the pyca connected widgets
    myLab = PycaLabel('TST:R40:IOC:24:LAS:01:UPTIME', lab)
    myLe = PycaLineEdit('TST:LAS:MMN:01:MTRXPS_RESET', le)
    myButton = PycaPushButton('TST:LAS:MMN:01:MTRXPS_RESET', b, value=1)
    myCB = PycaComboBox('TST:LAS:MMN:01:MTRXPS_RESET', cb)

    # layout the widgets
    layout = QVBoxLayout()
    layout.addWidget(lab)
    layout.addWidget(le)
    layout.addWidget(cb)
    layout.addWidget(b)

    # place them in a main window
    win = QWidget()
    win.resize(250, 50)
    win.setWindowTitle('Hello world!')
    win.setLayout(layout)
    win.show()

    # the application's event loop
    ret = app.exec_()

    # disconnect the widgets (__del__ would do that also)
    # myLab.disconnect_pv()
    # myLe.disconnect_pv()
    # myButton.disconnect_pv()
    # myCB.disconnect_pv()

    sys.exit(ret)


if __name__ == '__main__':
    logging.basicConfig(format='%(filename)s:%(lineno)d:%(levelname)-8s %(funcName)s: %(message)s',
                        level=logging.DEBUG)
    main()
