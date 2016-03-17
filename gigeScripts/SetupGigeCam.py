# New gigECam Setup Script that uses config parser
"""
SetupGigeCam.py

Usage:
  SetupGigeCam.py PV... [--config=cfg_name] [-v|--verbose] [-z|--zenity]
  SetupGigeCam.py [-h|--help]

Arguments:
  PV                Camera PV. Must be inputted.

Options:
  -h|--help           Show this help message
  --config=cfg_name   Explicitly specify which cfg to use.
  -v|--verbose        Print more about active process
  -z|--zenity         Outputs messages via zenity

General quick setup for the gigECams. To create a new configuration just create
a new cfg file in the configurations folder and then run the 
"""

import os.path
from psp.Pv import Pv
from ConfigParser import SafeConfigParser
from pprint import pprint
from docopt import docopt
from sys import exit
from os import system

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

def parsePVArguments(PVArguments):
	""" Parses PV input arguments and returns a set of cam PVs """
	camPVs = set()
	if '-' in PVArguments[0]:
	    basePV = PVArguments[0].split('-')[0][:-2]
	else:
		basePV = PVArguments[0][:-2]

	for arg in PVArguments:
		try:

			if '-' in arg:
				splitArgs = arg.split('-')

				if splitArgs[0][:-2] == basePV: camPVs.add(splitArgs[0])

				start = int(splitArgs[0][-2:])
				end = int(splitArgs[1])

				while start <= end:
					camPVs.add(basePV + "%02d"%start)
					start += 1
 
			elif len(arg) > 3:
				if arg[:-2] == basePV: camPVs.add(arg)
			
			elif len(arg) < 3:
				camPVs.add(basePV + "%02d"%int(arg))
			
			else: pass
				
		except: pass
			
	camPVs = list(camPVs)
	camPVs.sort()
	return camPVs

def SetupGigeCamera(camName, config, verbose, zenity):
	"""
	Function that loops through the config file and caputs the vals into the PVs
	"""
	# Error checking
	nFailedCaputs = 0
	failedCaputs = []

	# Make sure the file exists
	if verbose: print "Checking config file"
	if not os.path.isfile(config):
		config = config[0:2] + config[14:]
		if not os.path.isfile(config):
			if zenity:
				system("zenity --error --text='Error: Failed to read config'")
			print "Failed to read from configuration file."
			return

	# Create parser object and try to read from it	
	if verbose: print "Creating parser object"
	try: parser = SafeConfigParser()
	except:
		if zenity: 
			system("zenity --error --text='Error: Failed to create parser'")
		print "Failed to create parser object."
		return
	parser.optionxform=str				# Maintain case sensitivity
	try: parser.read(config)
	except:
		if zenity:
			system("zenity --error --text='Error: Failed to read config'")
		print "Failed to read from configuration file."
		return
		
	# Now loop through plugins
	for plugin in parser.sections():
		if verbose: print "\nPlugin: {0}".format(plugin)

		if plugin == "CAM": 
			for (FIELD, VAL) in parser.items(plugin):
				full_PV = camName + ":" + FIELD
				if verbose: print "Applying {0} to {1}".format(VAL, full_PV) 
				try: caput(full_PV, VAL)
				except:
					print "Failed to apply {0} to {1}".format(VAL, full_PV)
					print "Skipping {0}".format(full_PV)
					nFailedCaputs += 1
					failedCaputs.append(full_PV)
					continue

		else:
			for (FIELD, VAL) in parser.items(plugin):
				full_PV = camName + ":" + plugin + ":" + FIELD
				if verbose: print "Applying {0} to {1}".format(VAL, full_PV) 
				try: caput(full_PV, VAL)
				except:
					print "Failed to apply {0} to {1}".format(VAL, full_PV)
					print "Skipping {0}".format(full_PV)
					nFailedCaputs += 1
					failedCaputs.append(full_PV)
					continue

	print "\nSetup complete for {0}".format(camName)
	if nFailedCaputs > 0:
		print "\nNumber of failed caputs: {0}".format(nFailedCaputs)
		print "PVs that failed:"
		pprint(failedCaputs)
	if zenity:
		system('zenity --info --text="Completed Setup"')



if __name__ == "__main__":
	# Parse docopt inputs
	arguments = docopt(__doc__)
	PVArguments = arguments["PV"]
	print
	camPVs = parsePVArguments(PVArguments)
	print camPVs
	if arguments["--config"]:
		config = "./gigeScripts/configurations/" + arguments["--config"]
	else:
		config = "./gigeScripts/configurations/gige_default.cfg"
	if arguments["--verbose"] or arguments["-v"]: verbose = True
	else: verbose = False
	if verbose: print "Using config file: {0}".format(config)
	if arguments["--zenity"] or arguments["-z"]: zenity = True
	else: zenity = False
	
	for camName in camPVs:
		print "Setting up {0}".format(camName)
		SetupGigeCamera(camName, config, verbose, zenity)
