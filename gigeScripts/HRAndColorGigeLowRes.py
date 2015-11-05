#This is used to set up the Hi-Res and color cameras at a lower resolution but increased frame rate
from caput import caput
import sys

length = len(sys.argv)
for j in range(1, length):
#The following lines connect and start the camera, and also enable the correct port	
	camName = str(sys.argv[j])
	caput(camName+":AsynIO.CNCT", 1)
	caput(camName+":Acquire", 1)
	caput(camName+":IMG_OVER2:NDArrayPort", "CAM")
	caput(camName+":IMG_OVER2:EnableCallbacks", 1)
	caput(camName+":Over2:EnableCallbacks", 0)
	caput(camName+":ROI6:EnableCallbacks", 0)
#The following lines set the Frame Rate and Resolution of the camera

	caput(camName+":AcquireTime",0.20)
	caput(camName+":AcquirePeriod",0.033)
	caput(camName+":BinX", 2)
	caput(camName+":BinY", 2)

