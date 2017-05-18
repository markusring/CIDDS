from datetime import datetime
from ConfigParser import SafeConfigParser
import time
import sys

# Output of date and time, runtime, calling module, and text passed
# Since the module is passed with path and file transfer, these must be truncated (split)
def echoC(modul, text):

	# An forward and backward Slash splits 
	modulName = modul.split("/")[-1].split("\\")[-1]
	
	# Remove file ending 	
	modulName = modulName.split(".")[-1]

	# Log text: date and time, runtime, module name (field always 11 characters), text passed (without whitespaces)
	outputText = datetime.now().strftime("%y%m%d-%H%M%S") + " | " + str(getRuntime()) + " | " + "{0:15s}".format(modulName) + " | " + str(text).rstrip()
	print(outputText)
	
	# Save in Logfile 
	with open("packages/system/tracelog.txt", "a") as myFile:
		myFile.write(outputText + "\n")

# Determination of the running time using the stored start time
def getRuntime():
	
	# Read start time from configuration 
	parser = SafeConfigParser()
	parser.read("packages/system/config.ini")
	startTime = datetime.strptime(parser.get("starttime", "starttime"), "%y%m%d-%H%M%S%f")
	
	# Set runtime and return it
	runtime = datetime.now() - startTime
	return runtime
