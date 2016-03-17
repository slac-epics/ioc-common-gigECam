# Sets up gige camera PVs to values that have been shown to produce images after
# running. Only the PCDS plugins are modified, while the common plugins are left
# untouched.



# TO DO: Turn this into a paramterized version of what it already is. Use a
# config file that loops through all the paramters

from psp.Pv import Pv
import sys

# caput is defined identically but with a timeout value of 10.0 instead of 2.0
# The default setting of 2.0 seconds was too short, causing the script to fail
# before completion. Try & excepts were also placed just to confirm that 10.0
# was a long enough wait time.
def caput(PVName, val):
    """ Same definition of caput but with a connect timeout of 10.0 """
    pv = Pv(PVName)

    try:
        pv.connect(timeout=10.0)
    except pyca.caexc, e:
        print "Channel access exception:", e
        print PVName
    except pyca.pyexc, e:
        print "Pyca exception:", e
        print PVName
    
    try:        
        pv.put(value=val, timeout=10.0)
    except pyca.caexc, e:
        print "Channel access exception:", e
        print PVName
    except pyca.pyexc, e:
        print "Pyca exception:", e
        print PVName

    pv.disconnect()

if sys.argv[1]:
    camName = sys.argv[1]
else:
    camName = raw_input("Enter the name of the gige cam: ")

    # Paramterize the image sizes
    # Frame rate can stay
    # Parameterize image_mode, trigger mode.

image_size_X = 1388             # Num Pixels in X
image_size_Y = 1038             # Num Pixels in Y
image_frame_rate = .20          # Framerate fr/sec
thumbnail_frame_rate = 1.00     # Thumbnail frame rate fr/sec
image_mode = 2                  # 0 = single, 1 = multiple, 2 = continuous
trigger_mode = 5                # 5 - fixed rate
image_callback = 0              # 0 = disabled, 1 = enabled

def setupPlugin(name, port, callback, minCallback = 0.00, blocking = 0,  
              arrayCounter = 0, droppedArrays = 0):
    '''
    Sets the default parameters for a plugin
    '''
    caput(camName+":"+name+":NDArrayPort", port)
    caput(camName+":"+name+":EnableCallbacks", callback)
    caput(camName+":"+name+":BlockingCallbacks", blocking)
    caput(camName+":"+name+":MinCallbackTime", minCallback)
    caput(camName+":"+name+":ArrayCounter", arrayCounter)
    caput(camName+":"+name+":DroppedArrays", droppedArrays)

    # Sets Additional Parameters for an ROI Plugin
    if name[:-1] == "ROI":
        # caput(camName+":"+name+":Name", "")
        caput(camName+":"+name+":DataTypeOut", 8)
        caput(camName+":"+name+":EnableScale", 0)
        caput(camName+":"+name+":Scale", 1)

        caput(camName+":"+name+":EnableX", 0)
        caput(camName+":"+name+":EnableY", 0)
        caput(camName+":"+name+":EnableZ", 0)

        caput(camName+":"+name+":BinX", 1)
        caput(camName+":"+name+":BinY", 1)
        caput(camName+":"+name+":BinZ", 1)

        caput(camName+":"+name+":MinX", 0)
        caput(camName+":"+name+":MinY", 0)
        caput(camName+":"+name+":MinZ", 0)

        caput(camName+":"+name+":SizeX", image_size_X)
        caput(camName+":"+name+":SizeY", image_size_Y)
        caput(camName+":"+name+":SizeZ", 0)

        caput(camName+":"+name+":ReverseX", 0)
        caput(camName+":"+name+":ReverseY", 0)
        caput(camName+":"+name+":ReverseZ", 0)

        caput(camName+":"+name+":AutoSizeX", 0)
        caput(camName+":"+name+":AutoSizeY", 0)
        caput(camName+":"+name+":AutoSizeZ", 0)

# GigECam Setup

caput(camName+":AsynIO.CNCT", 1)
caput(camName+":Acquire", 1)
caput(camName+":AcquireTime", image_frame_rate)
caput(camName+":AcquirePeriod", image_frame_rate)
caput(camName+":MinX", 0)       
caput(camName+":MinY", 0)       
caput(camName+":BinX", 1)       
caput(camName+":BinY", 1)       
 
caput(camName+":SizeX", image_size_X)
caput(camName+":SizeY", image_size_Y)
caput(camName+":ImageMode", image_mode)
caput(camName+":TriggerMode", trigger_mode)
caput(camName+":DataType", 0)
caput(camName+":ColorMode", 0)
caput(camName+":BayerConvert", 0)

# Plugins

## IMAGE1
setupPlugin("IMAGE1", "ROI5", 1)

## IMAGE2
setupPlugin("IMAGE2", "CAM", image_callback)

## IMAGE3
setupPlugin("IMAGE3", "CAM", image_callback)

## ROI5
setupPlugin("ROI5", "CAM", 1)

## IMG_OVER2
setupPlugin("IMG_OVER2", "CAM", 1)

## Over2
setupPlugin("Over2", "ROI6", 0)

## ROI6
setupPlugin("ROI6", "CAM", 0)

## THUMBNAIL
setupPlugin("THUMBNAIL", "ROI7", 1)

## ROI7
setupPlugin("ROI7", "CAM", 1, thumbnail_frame_rate)

# Setup Color settings if it is a color cam
if "COL" in camName:
	setupPlugin("CC1", "CAM", 1)	
	setupPlugin("CC2", "CAM", 1)
	setupPlugin("IMAGE1", "CC1", 1)
	setupPlugin("IMG_OVER2", "CC2", 1)
	

print "Reset complete"
