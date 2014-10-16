import time
from PyQt4 import QtGui, QtCore

class SplashScreen(QtGui.QSplashScreen):
    def __init__(self):
        self.loadImages()
        self.lblAlignment = QtCore.Qt.Alignment(QtCore.Qt.AlignBottom | 
                                                QtCore.Qt.AlignRight  |
                                               QtCore.Qt.AlignAbsolute)

        QtGui.QSplashScreen.__init__(self, self.splashLogo)

        self.centerOnScreen()
        self.msgdelay = 0
        self.show()
        QtCore.QCoreApplication.flush()

#		# Progress bar
#		self.progressBar = QProgressBar(self)
#		#self.progressBar.setGeometry(QRect(4, 207, 200, 18))
#		self.progressBar.setGeometry(self.width()/10, 8*self.height()/20,
#                        8*self.width()/10, self.height()/20)
#		self.progressBar.show()
#		self.barTimer = QTimer() # not implemented yet

    def showMsg(self, msg):
        '''Show message in lower part of splash screen'''
        QtGui.QSplashScreen.showMessage(self, msg, 
                                        self.lblAlignment, 
                                        QtGui.QColor(QtCore.Qt.black))
        time.sleep(self.msgdelay)		
        QtGui.qApp.processEvents()

    def clearMsg(self):
        '''Clear message in lower part of splash screen'''
        QtGui.QSplashScreen.clearMessage(self)
        QtGui.qApp.processEvents()		

    def loadImages(self):
        #self.splashLogo = QtGui.QPixmap('ui/LCLS_400.png')
        self.splashLogo = QtGui.QPixmap('ui/pcdsMultiviewer.png')

    def centerOnScreen(self):
        '''centerOnScreen() Centers the window on the screen.'''
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

    def setMsgTime(self, delay=0.5):
        self.msgdelay = delay
