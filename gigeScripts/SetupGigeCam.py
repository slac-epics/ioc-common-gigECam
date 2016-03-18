# New gigECam Setup Script that uses config parser
"""
SetupGigeCam.py

Usage:
  SetupGigeCam.py <PV>... [--config=cfg_name] [-v|--verbose] [-z|--zenity] [--HR | --LR]
  SetupGigeCam.py [-h|--help]

Arguments:
  <PV>                Camera PV. To do multiple cameras, input the full PV as 
                      the first argument, and then the numbers of the rest as 
                      single entries, or in a range using a hyphen. An example 
                      would be the following: 

                          python pmgrUtils.py save SXR:EXP:GIGE:01-03 05

                      This will set up gigecams 01, 02, 03, and 05

Options:
  -h|--help           Show this help message
  --config=cfg_name   Explicitly specify which cfg to use.
  -v|--verbose        Print more about active process
  -z|--zenity         Outputs messages via zenity
  --HR                Use high res mode for cfg
  --LR                Use low res mode for cfg

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

def SetupGigeCamera(camName, config, verbose, zenity):
	"""
	Function that loops through the config file and caputs the vals into the PVs
	"""

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
	parser = getParser(config, verbose, zenity)
	if not parser: return

	# Perform the caputs
	nFailedCaputs, failedCaputs = runCaputs(parser, camName, verbose, zenity)

	# Display any failures
	print "\nSetup complete for {0}".format(camName)
	if nFailedCaputs > 0:
		print "\nNumber of failed caputs: {0}".format(nFailedCaputs)
		print "PVs that failed:"
		pprint(failedCaputs)
	if zenity: system('zenity --info --text="Completed Setup"')

def runCaputs(parser, camName, verbose, zenity):
	""" 
	Performs caputs on all the fields specified in the cfg file using the val
	specified as well.
	"""
	# Error checking
	nFailedCaputs = 0
	failedCaputs = []

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

	return nFailedCaputs, failedCaputs

def getParser(config, verbose, zenity):
	""" 
	Returns a parser that has already read the config. Returns None if it fails
	in any way.
	"""
	if verbose: print "Creating parser object"
	try: parser = SafeConfigParser()
	except:
		if zenity: 
			system("zenity --error --text='Error: Failed to create parser'")
		print "Failed to create parser object."
		return None
	parser.optionxform=str				# Maintain case sensitivity
	try: parser.read(config)
	except:
		if zenity:
			system("zenity --error --text='Error: Failed to read config'")
		print "Failed to read from configuration file."
		return None
	
	return parser

def getConfig(PV, HR, LR):
	""" Returns a path to a config file based on the PV """
	hutch = PV[:3]
	if hutch.lower() == "sxr" or hutch.lower() == "amo":
		hutch = "SXD"
	
	if HR:
		config = "./gigeScripts/configurations/gige_"+hutch+"_HRMode.cfg"
	elif LR:
		config = "./gigeScripts/configurations/gige_"+hutch+"_LRMode.cfg"
	else:
		if ":col:" in PV.lower(): col = "_col"
		else: col = ""
		if ":hr:" in PV.lower() : hr = "_hr"
		else: hr = ""
	
		config = "./gigeScripts/configurations/gige_"+hutch+hr+col+".cfg"
	
	return config

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



if __name__ == "__main__":
	# Parse docopt inputs
	arguments = docopt(__doc__)
	print arguments
	PVArguments = arguments["<PV>"]
	camPVs = parsePVArguments(PVArguments)
	if arguments["--verbose"] or arguments["-v"]: verbose = True
	else: verbose = False
	if arguments["--zenity"] or arguments["-z"]: zenity = True
	else: zenity = False
	
	# Get a config
	if arguments["--config"]: 
		config = "./gigeScripts/configurations/" + arguments["--config"]
	else: config = getConfig(camPVs[0], arguments["--HR"], arguments["--LR"])
	if verbose: print "Using config file: {0}".format(config)
	
	# Set up each camera
	for camName in camPVs:
		print "Setting up {0}".format(camName)
		SetupGigeCamera(camName, config, verbose, zenity)
