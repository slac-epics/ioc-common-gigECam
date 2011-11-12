#! /usr/bin/env python

from prosilica1350_ui_impl import GraphicUserInterface
from PyQt4.QtGui import QApplication

import sys
import logging

from options import Options

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG,
                        format='%(filename)s:%(lineno)d:%(levelname)-8s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S')

    options = Options(['camerapv'], [], [])
    try:
        options.parse()
    except Exception, msg:
        options.usage(str(msg))
        sys.exit()

    app = QApplication([''])
    gui = GraphicUserInterface(app, options.camerapv)
    try:
        sys.setcheckinterval(1000) # default is 100
        gui.show()
        retval = app.exec_()
    except KeyboardInterrupt:
        app.exit(1)
        retval = 1
    gui.shutdown()
    sys.exit(retval)
