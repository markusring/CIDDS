from packages.system.echoX import echoC
from glob import glob
import os
import platform
import sys
import random
import time

def main():
	echoC(__name__, "Start Printing...")
	
	# Return value for error detection
	error = 0
	
	if platform.system() == "Linux":
		
		try:
			# Determine Default printer	
			import cups
			conn = cups.Connection()
			printers = conn.getPrinters()
			printer = printers.keys()[0]
			echoC(__name__, "Found " + printer + " as default printer.")
			time.sleep(5)
		
			# Create print command and call (multiple)
			firstTime = True
			while random.randint(0, 1) != 0 or firstTime == True: # Is not yet quite clean: If the first attempt is directly 0 "rolled" no document is printed
				firstTime = False
				
				# Number of copies to be printed				
				numberOfCopies = random.randint(1, 10)
				
				# Find a random file from the browsing directory (there are a lot of files)
				randFile = random.choice(os.listdir("packages/system/"))
				randFile = "packages/system/" + randFile
		
				# Print file
				cmd = "lpr -P " + printer + " -#" + str(numberOfCopies) + " " + randFile
				try:
					os.system(cmd)
					echoC(__name__, "Print job sent: " + randFile)
					error = 0
					time.sleep(10)
				except Exception as e:
					echoC(__name__, "Print job error: " + str(e))
					error = -1
					
		except Exception as e:
			echoC(__name__, "Printing error: " + str(e))
			error = -1


	elif platform.system() == "Windows":
		
		try:
			# Check if a default printer is configured
			import win32api
			import win32print
			printer = win32print.GetDefaultPrinter()
			if not "XPS" in printer and not "PDF" in printer:
				echoC(__name__, "Found " + printer + " as default printer.")
			
				# Create print order 
				firstTime = True
				while random.randint(0, 1) != 0 or firstTime == True: # Is not yet quite clean: If the first attempt is directly 0 "rolled" no document is printed
					firstTime = False
					
					# Select a file to print from a directory
					randFile = random.choice(glob("M:\\*.log"))
					
					# print
					try:
						os.startfile(randFile, "print")
						echoC(__name__, "Print job sent: " + randFile)
						error = 0
						time.sleep(10)
					except Exception as e:
						echoC(__name__, "Print job error: " + str(e))
						error = -1
			else:
				echoC(__name__, "Error. Maybe wrong default printer.")
				error = -1

		except Exception as e:
			echoC(__name__, "Printing error: " + str(e))
			error = -1
	else:
		echoC(__name__, "Could not determine OS.")
		error = -1
	
	echoC(__name__, "Done")
	return error

if __name__ == "__main__":
	main()
