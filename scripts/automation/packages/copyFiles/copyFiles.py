from packages.system.echoX import echoC
from glob import glob
from random import randint
from shutil import copyfile
from uuid import getnode
from datetime import datetime
import sys
import platform
import os
import time
import random


# Names and paths of the files in the given location
def getNamesOfFiles(location):
	fileNames = glob(location + "*.dat")
	if len(fileNames) == 0:
		return -1
	return fileNames

# Select a file and copy it to the VM or the file server
def copyRandomFile(fileNames, destination):
	
	# Pick a random file 
	fileNameWithPath = fileNames[randint(0, len(fileNames)-1)]
	
	if platform.system() == "Linux":
		separator = "/"
	elif platform.system() == "Windows":
		separator = "\\"

	# If the file is copied to the VM, the MAC address (as an integer) is placed before the file names
	# -> Avoid deadlocks when copying to the server
	if "localstorage" in destination:
		localFileName = str(getnode()) + "-" + fileNameWithPath.split(separator)[-1]
	else:
		localFileName = fileNameWithPath.split(separator)[-1]

	# Path to the appropriate drive and filename
	dstWithFileName = destination + localFileName
	
	# Copy file 
	try:
		copyfile(fileNameWithPath, dstWithFileName)
		echoC(__name__, "Copied file " + localFileName + " to " + destination)
	except Exception as e:
		echoC(__name__, "copyfile() with destination " + destination + " error: " + str(e))
		return -1
	
	# copyfile() is not blocking 
	time.sleep(random.randint(15,120))
	return 0

def main():
	
	echoC(__name__, "Copying some netstorage files")
	
	# Return value for error detection
	error = 0
	
	if platform.system() == "Linux":
		pathToNetStorage_read = "/home/debian/netstorage/"
		pathToNetStorage_write = "/home/debian/netstorage/inbox/"
		pathToLocalStorage = "/home/debian/localstorage/"
	elif platform.system() == "Windows":
		pathToNetStorage_read = "N:\\"
		pathToNetStorage_write = "N:\\inbox\\"
		pathToLocalStorage = "C:\\localstorage\\"

	# Names and paths of the files in the Netstorage list
	netFileNames = getNamesOfFiles(pathToNetStorage_read)
	
	# Names and paths of the files in the local storage in list
	localFileNames = getNamesOfFiles(pathToLocalStorage)
	
	# Copy operation can be called multiple times
	firstTime = True
	while randint(0, 3) != 0 or firstTime == True:
		firstTime = False
		
		# Randomly switch between local and Netstorage files
		# Copying local files makes sense only if they exist
		if randint(0, 1) or localFileNames == -1:
			
			# Check if there are files in Netstorage
			if netFileNames == -1:
				echoC(__name__, "netFileNames() error")
				error = -1
			
			# Save files locally from Netstorage and refresh list of local files
			else:
				error = copyRandomFile(netFileNames, pathToLocalStorage)
				localFileNames = getNamesOfFiles(pathToLocalStorage)

		# Write files from the local directory to the Netstorage
		else:
			error = copyRandomFile(localFileNames, pathToNetStorage_write)
	
	echoC(__name__, "Done")
	return error
	
if __name__ == "__main__":
	main()
