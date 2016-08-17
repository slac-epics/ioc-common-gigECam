"""
SetupGigeCam.py

Usage:
  SetupGigeCam.py <PV>... [--config=config] [-v|--verbose] [-z|--zenity]
  SetupGigeCam.py <PV>... [--hutch=hutch] [-v|--verbose] [-z|--zenity] [--HR|--LR] [--extra=extra] 
  SetupGigeCam.py [-h|--help]

Arguments:
  <PV>                Camera PV. To do multiple cameras, input the full PV as 
                      the first argument, and then the numbers of the rest as 
                      single entries, or in a range using a hyphen. Ex:

                          python SetupGigeCam.py SXR:EXP:GIGE:01-03 05

                      This will set up gigecams 01, 02, 03, and 05

Options:
  -h,--help           Show this help message
  --config=cfg_name   Explicitly specify which cfg to use.
  --hutch             Explicitly specify which hutch to use
  --extra=extra       Extra string to pad end of config path
  -v,--verbose        Print more about active process
  -z,--zenity         Outputs messages via zenity
  --HR                Use high res mode for cfg
  --LR                Use low res mode for cfg

General quick setup for the gigECams. To create a new configuration just create
a new cfg file in the configurations folder and then run the script specifying
the config name to use it.
"""

import os
import sys
from psp.Pv import Pv
from ConfigParser import SafeConfigParser
from optparse import OptionParser
from pprint import pprint

# caput is defined identically but with a timeout value of 10.0 instead of 2.0
# The default setting of 2.0 seconds was too short, causing the script to fail
# before completion.
def caput(PVName, val):
	"""Same definition of caput but with a connect timeout of 10.0"""
	pv = Pv(PVName)
	pv.connect(timeout=10.0)
	pv.put(value=val, timeout=10.0)
	pv.disconnect()

def SetupGigeCamera(camName, config, verbose, zenity):
	"""
	Function that loops through the config file and caputs the vals into the PVs
	"""
	# Create parser object and try to read from it	
	parser = getParser(config, verbose, zenity)
	if not parser: return
	# Perform the caputs
	nFailedCaputs, failedCaputs, nCaputs = runCaputs(parser, camName, verbose, zenity)
	# Display any failures
	print "Setup complete for {0}".format(camName)
	if nFailedCaputs > 0:
		print "\nNumber of failed caputs: {0} / {1}".format(nFailedCaputs, nCaputs)
		print "PVs that failed:"
		pprint(failedCaputs)
	if zenity: os.system('zenity --info --text="Completed Setup"')

def runCaputs(parser, camName, verbose, zenity):
	""" 
	Performs caputs on all the fields specified in the cfg file using the val
	specified as well.
	"""
	# Error checking
	nFailedCaputs = 0
	failedCaputs = []
	nCaputs = 0
	for plugin in parser.sections():
		if verbose: print "\nPlugin: {0}".format(plugin)
		if plugin == "CAM": base_PV = camName
		else: base_PV = camName + ":" + plugin
		for (FIELD, VAL) in parser.items(plugin):
			nCaputs += 1
			full_PV = base_PV + ":" + FIELD
			# Try to cast as a float or int first
			if "." in VAL:
				try: VAL = float(VAL)
				except: pass
			else:
				try: VAL = int(VAL)
				except: pass
			if verbose: print "Applying {0} to {1}".format(VAL, full_PV) 
			try: caput(full_PV, VAL)
			except Exception, e:
				print "\nFailed to apply {0} to {1}".format(VAL, full_PV)
				print "Error: {0}".format(str(e))
				print "Skipping {0}".format(full_PV)
				nFailedCaputs += 1
				failedCaputs.append([full_PV, VAL, type(VAL)])
				continue
	return nFailedCaputs, failedCaputs, nCaputs

def getParser(config, verbose, zenity):
	""" 
	Returns a parser that has already read the config. Returns None if it fails
	in any way.
	"""
	if verbose: print "Creating parser object"
	try: parser = SafeConfigParser()
	except:
		if zenity: 
			os.system("zenity --error --text='Error: Failed to create parser'")
		print "Failed to create parser object."
		return None
	parser.optionxform=str				# Maintain case sensitivity
	try: parser.read(config)
	except:
		if zenity:
			os.system("zenity --error --text='Error: Failed to read config'")
		print "Failed to read from configuration file."
		return None	
	return parser

def getConfig(PV, verbose, **kwargs):
	"""Returns a path to a config file based on the PV"""
	if 'hutch' in kwargs and kwargs['hutch']:
		hutch = kwargs['hutch']
	else:
		hutch = PV[:3]
		if hutch.lower() == "sxr" or hutch.lower() == "amo":
			hutch = "sxd"
	col, hr, mode = "", "", ""
	if 'HR' in kwargs and kwargs['HR']: mode = "_hr_mode"
	elif 'LR' in kwargs and kwargs['LR']: mode = "_lr_mode"
	else:
		if ":col:" in PV.lower(): col = "_col"
		else: col = ""
		if ":hr:" in PV.lower() : hr = "_hr"
		else: hr = ""
	cfgName = hutch + hr + col + mode
	## Add new parameters below
	##
	extra = ""
	if 'extra' in kwargs and kwargs['extra']:
		extra = "_{0}".format(kwargs['extra'])
	cfgName += extra
	config = "./gigeScripts/configurations/gige_{0}.cfg".format(cfgName)
	##
	# Make sure the file exists
	if verbose: print "Checking config file"
	if not os.path.isfile(config):
		if not os.path.isfile(config[0:2] + config[14:]):
			print "Configuration file {0} does not exist!".format(config)
			config = None
		else: config = config[0:2] + config[14:]
	return config

def getBasePV(PVArguments):
	"""Returns the first base PV found in the list of PVArguments"""
	for arg in PVArguments:
		if ':' not in arg: continue
		for i, char in enumerate(arg[::-1]):
			if char == ':':
				return arg[:-i]
	return None

def parsePVArguments(PVArguments):
	"""Parses PV input arguments and returns a set of cam PVs"""
	camPVs = set()
	if len(PVArguments) == 0: return None
	basePV = getBasePV(PVArguments)
	if not basePV: return None
	for arg in PVArguments:
		try:
			if '-' in arg:
				splitArgs = arg.split('-')
				if getBasePV(splitArgs[0]) == basePV: camPVs.add(splitArgs[0])
				start = int(splitArgs[0][-2:])
				end = int(splitArgs[1])
				while start <= end:
					camPVs.add(basePV + "{:02}".format(start))
					start += 1
			elif len(arg) > 3:
				if getBasePV([arg]) == basePV: camPVs.add(arg)
			elif len(arg) < 3:
				camPVs.add(basePV + "{:02}".format(int(arg)))
			else: pass
		except: pass
	camPVs = list(camPVs)
	camPVs.sort()
	return camPVs


if __name__ == "__main__":
	parser = OptionParser(add_help_option=False)   #Disable help to use docstring
	parser.add_option('--config', action='store', type='string', dest='config')
	parser.add_option('--hutch', action='store', type='string', dest='hutch', default=None)
	parser.add_option('--extra', action='store', type='string', dest='extra', default=None)
	parser.add_option('--verbose', '-v', action='store_true', dest='verbose', default=False)
	parser.add_option('--zenity', '-z', action='store_true', dest='zenity', default=False)
	parser.add_option('--HR', action='store_true', dest='HR', default=False)
	parser.add_option('--LR', action='store_true', dest='LR', default=False)
	parser.add_option('-h', '--help', dest='help', action='store_true',
					  help='show this help message and exit')
	options, PVargs = parser.parse_args()
	if options.help:
		print __doc__
		sys.exit()
	camPVs = parsePVArguments(PVargs)
	if not camPVs or len(camPVs) == 0:
		exit("Error: Incorrect inputted arguments: {0}.".format(PVArgs))
	verbose = options.verbose
	zenity = options.zenity
	HRes = options.HR
	LRes = options.LR
	configPath = "./gigeScripts/configurations/"
	cfgExt = ".cfg"
	if options.config: 
		if os.path.isfile(options.config):
			config = options.config
		elif os.path.isfile(options.config + cfgExt):
			config = options.config + cfgExt
		elif os.path.isfile(configPath + options.config):
			config = configPath + options.config
		elif os.path.isfile(configPath + options.config + cfgExt):
			config = configPath + options.config + cfgExt
		else:
			print "Configuration file {0} does not exist!".format(options.config)
			config = None
	else: config = getConfig(camPVs[0], verbose, HR=HRes, LR=LRes,
							 hutch=options.hutch, extra=options.extra)
	if config:
		if verbose: print "Using config file: {0}".format(config)
		for camName in camPVs:
			print "\nSetting up {0}".format(camName)
			SetupGigeCamera(camName, config, verbose, zenity)	
