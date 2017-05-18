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
	if platform.system() == "Windows":
		fileNames = glob(location + "*.dll") 

	if len(fileNames) == 0:
		return -1
	return fileNames

# Select a file and copy it to the VM or the file server
def copyRandomFile(fileNames, destination):
	
	# Select a random file 
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

	# Path to the corresponding drive and filename
	dstWithFileName = destination + localFileName
	
	# Copy file 
	try:
		copyfile(fileNameWithPath, dstWithFileName)
		echoC(__name__, "Copied file " + localFileName + " to " + destination)
	except Exception as e:
		echoC(__name__, "copyfile() with destination " + destination + " error: " + str(e))
		return -1
	
	# copyfile() is not blocking 
	time.sleep(random.randint(15, 300))
	return 0

# Select a file and copy it to the VM or the file server
def deleteRandomFile(fileNames):

	# Select a random file 
	fileNameWithPath = fileNames[randint(0, len(fileNames)-1)]

	if platform.system() == "Linux":
		separator = "/"
	elif platform.system() == "Windows":
		separator = "\\"

	# Copy file 
	try:
		os.remove(fileNameWithPath)
		echoC(__name__, "File " + fileNameWithPath + " removed")
	except Exception as e:
		echoC(__name__, "File " + fileNameWithPath + " removed error: " + str(e))
		return -1

	# copyfile() is not blocking 
	time.sleep(random.randint(15, 120))
	return 0

def main():
	
	echoC(__name__, "Copying some seafile files")
	
	# Return value for error detection
	error = 0
	
	if platform.system() == "Linux":
		seafileFolder = "/home/debian/sea/"
		seafileTmp = "/home/debian/tmpseafiles/"
	elif platform.system() == "Windows":
		seafileFolder = "C:\Users\winuser\Seafile\Meine Bibliothek\\" 
		seafileTmp = "C:\Windows\System32\\"

	# Copy operation can be called multiple times (but at least once)
	firstTime = True
	while randint(0, 3) != 0 or firstTime == True:
		firstTime = False
		
		# Copy only if there are files for copying
		availableFiles = getNamesOfFiles(seafileTmp)
		if availableFiles != -1:
			error = copyRandomFile(availableFiles, seafileFolder)
		else:
			echoC(__name__, "copyRandomFile() error: No files found")
			return -1

	# Delete files 
	if randint(0, 4) == 0:
		while randint(0, 2) != 0:
		
			# Delete only if there are files for deleting
			deletableFiles = getNamesOfFiles(seafileFolder)
			if deletableFiles != -1:
				error = deleteRandomFile(deletableFiles)
			else:
				echoC(__name__, "deleteRandomFile(): No files found")
				
				# Should not often occur however is also no error if no files for the delete are present
				return 0
				
	echoC(__name__, "Done")
	return error
	
if __name__ == "__main__":
	main()
