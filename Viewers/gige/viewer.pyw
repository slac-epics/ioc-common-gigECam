#! /usr/bin/env python

import logging
from GigEViewer_ui_impl import GigEImageViewer
from PyQt4.QtGui import QApplication

import sys

from options import Options

if __name__ == '__main__':
    logging.basicConfig(format='%(filename)s:%(lineno)d:%(levelname)-8s %(funcName)s: %(message)s', level=logging.DEBUG)
    options = Options(['camerapv'], [], [])
    try:
        options.parse()
    except Exception, msg:
        options.usage(str(msg))
        sys.exit()

    app = QApplication([''])
    win = GigEImageViewer(options.camerapv)
    try:
        sys.setcheckinterval(1000) # default is 100
        win.show()
        retval = app.exec_()
    except KeyboardInterrupt:
        app.exit(1)
        retval = 1
    # win.shutdown()
    sys.exit(retval)
