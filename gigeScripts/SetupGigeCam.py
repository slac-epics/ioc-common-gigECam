# New gigECam Setup Script that uses config parser
"""
SetupGigeCam.py

Usage:
  SetupGigeCam.py PV [--config=cfg_name] [-v|--verbose]
  SetupGigeCam.py [-h|--help]

Arguments:
  PV                  Camera PV. Must be inputted.

Options:
  -h|--help           Show this help message
  --config=cfg_name   Explicitly specify which cfg to use.
  -v|--verbose        Print more about active process

General quick setup for the gigECams. To create a new configuration just create
a new cfg file in the configurations folder and then run the 
"""

from psp.Pv import Pv
from ConfigParser import SafeConfigParser
from pprint import pprint
from docopt import docopt
from sys import exit


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

if __name__ == "__main__":
	# Parse docopt inputs
	arguments = docopt(__doc__)
	camName = arguments["PV"]
	if arguments["--config"]:
		config = "configurations/" + arguments["--config"]
	else:
		config = "configurations/gige_default.cfg"
	if arguments["--verbose"] or arguments["-v"]: verbose = True
	else: verbose = False
	
	if verbose: print "Creating parser object"
	# Create parser object and try to read from it
	try: parser = SafeConfigParser()
	except: exit("Failed to create parser object.")
	parser.optionxform=str                # Maintain case of key
	try: parser.read(config)
	except: exit("Failed to read from configuration file.")
	
	# Now loop through plugins
	for plugin in parser.sections():
		if plugin == "CAM": 
			for (FIELD, VAL) in parser.items(plugin):
				full_PV = camName + ":" + FIELD
				if verbose: print "Applying {0} to {1}".format(VAL, full_PV) 
				# caput(full_PV, VAL)
		else:
			for (FIELD, VAL) in parser.items(plugin):
				full_PV = camName + ":" + plugin + ":" + FIELD
				if verbose: print "Applying {0} to {1}".format(VAL, full_PV) 
				# caput(full_PV, VAL)
	
