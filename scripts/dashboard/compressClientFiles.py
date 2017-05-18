from datetime import datetime, timedelta
from ConfigParser import SafeConfigParser
from glob import glob
import os

# Read the MAC addresses of the available clients (according to OpenStack)
def getMacAddressesFromOpenStack():
	
	# Read the list of MAC addresses
	with open("/media/logs/clientmacs", "r") as f:
		macAddressesLong = f.readlines()
	
	# Correct formatting and create list
	macAddresses = []
	for macAddressAsHex in macAddressesLong:
		macAddressAsInt = int(macAddressAsHex.replace(':', ''), 16)
		macAddresses.append(str(macAddressAsInt))
		
	return macAddresses
	
# Read the MAC addresses of the configured config files
def getMacAddressesFromConfigs(allConfigFiles):

	macAddresses = []
	for configFile in allConfigFiles:
		
		# Remove path before filenames
		fileNameWithoutPath = configFile.split('/')[-1]
		
		#  Remove ending from filename
		macAddresses.append(fileNameWithoutPath.split('.')[0])
		
	return macAddresses

# Compress the client's Config for Web View
def compressConfig(clientID):

	# Open original ini file with parser
	parser = SafeConfigParser()
	parser.read("/media/logs/" + clientID + ".conf")	
		
	# Read the relevant data and write it to a new file
	with open("/home/stack/skripte/dashboard/instances/" + clientID + ".conf", "w") as f:
		
		# Network
		f.write(parser.get("network", "hostname") + "<br/>(")
		f.write(parser.get("network", "subnet") + ".")
		f.write(parser.get("network", "host") + ");")
		
		# Working hours
		f.write(parser.get("workinghours", "clock_in") + "&nbsp-&nbsp")
		f.write(parser.get("workinghours", "clock_out") + ";")
		
		# Working days
		f.write("x;" if parser.get("workdays", "monday") == "1" else "-;")
		f.write("x;" if parser.get("workdays", "tuesday") == "1" else "-;")
		f.write("x;" if parser.get("workdays", "wednesday") == "1" else "-;")
		f.write("x;" if parser.get("workdays", "thursday") == "1" else "-;")
		f.write("x;" if parser.get("workdays", "friday") == "1" else "-;")
		f.write("x;" if parser.get("workdays", "saturday") == "1" else "-;")
		f.write("x" if parser.get("workdays", "sunday") == "1" else "-")
		
		# Level
		#f.write(parser.get("activities", "business_lvl") + ";")
		#f.write(parser.get("activities", "activity_lvl"))

# Compress the Client Activity Log for web view
def compressActLog(clientID, allActsRuntimes):

	# Create list for each activity
	# 0. Name of the activity
	# 1. Number of executions
	# 2. End time of the last execution
	# 3. Duration of the complete execution in sec
	# 4. rel. Percentage of activity on all activities
	# 5. Time of the last error
	browsing = ["browsing", 0, "", 0, 0, ""]
	copySea = ["copySea", 0, "", 0, 0, ""]
	copyFiles = ["copyFile", 0, "", 0, 0, ""]
	mailing = ["mailing", 0, "", 0, 0, ""]
	printing = ["printing", 0, "", 0, 0, ""]
	private = ["private", 0, "", 0, 0, ""]
	meeting = ["meeting", 0, "", 0, 0, ""]
	offline = ["offline", 0, "", 0, 0, ""]
	ssh = ["ssh", 0, "", 0, 0, ""]
	breaks = ["break", 0, "", 0, 0, ""]
	
	# Aggregate all activities in a list
	allActs = [browsing, mailing, printing, copyFiles, copySea, ssh, meeting, offline, private, breaks]
	
	# Read the original log
	try:
		with open("/media/logs/" + clientID + ".log", "r") as f:
			content = f.readlines()
	except Exception as e:
		# Create a pseudo-log if there is no real log
			content = ""
			
	# Create list with the individual lines of the log
	content = [x.strip() for x in content]
	
	# Total duration of all activities
	durationAll = 0
	
	# Go through each line of the log and compress data for each activity
	for line in content:
		lastTime = line.split(',')[1].split('.')[0]
		duration = line.split(',')[2]
		activity = line.split(',')[3]
		error = line.split(',')[4]

		lastDeltaAsDate = datetime.strptime(line.split(',')[2], "%H:%M:%S.%f")
		lastDeltaAsTimedelta = timedelta(days=lastDeltaAsDate.day - 1, hours=lastDeltaAsDate.hour, minutes=lastDeltaAsDate.minute, seconds=lastDeltaAsDate.second, microseconds=lastDeltaAsDate.microsecond)
		lastDeltaInSeconds = lastDeltaAsTimedelta.total_seconds()
		
		durationAll += lastDeltaInSeconds
		
		if activity == "browsing":
			browsing[1] += 1
			browsing[2] = lastTime
			browsing[3] += lastDeltaInSeconds
			if error != "0":
				browsing[5] = lastTime
		
		if activity == "copySea":
			copySea[1] += 1
			copySea[2] = lastTime
			copySea[3] += lastDeltaInSeconds
			if error != "0":
				copySea[5] = lastTime
		
		if activity == "copyFiles":
			copyFiles[1] += 1
			copyFiles[2] = lastTime
			copyFiles[3] += lastDeltaInSeconds
			if error != "0":
				copyFiles[5] = lastTime
				
		if activity == "mailing":
			mailing[1] += 1
			mailing[2] = lastTime
			mailing[3] += lastDeltaInSeconds
			if error != "0":
				mailing[5] = lastTime
		
		if activity == "printing":
			printing[1] += 1
			printing[2] = lastTime
			printing[3] += lastDeltaInSeconds
			if error != "0":
				printing[5] = lastTime
		
		if activity == "private":
			private[1] += 1
			private[2] = lastTime
			private[3] += lastDeltaInSeconds
			if error != "0":
				private[5] = lastTime
		
		if activity == "meeting":
			meeting[1] += 1
			meeting[2] = lastTime
			meeting[3] += lastDeltaInSeconds
			if error != "0":
				meeting[5] = lastTime
		
		if activity == "offline":
			offline[1] += 1
			offline[2] = lastTime
			offline[3] += lastDeltaInSeconds
			if error != "0":
				offline[5] = lastTime
		
		if activity == "ssh":
			ssh[1] += 1
			ssh[2] = lastTime
			ssh[3] += lastDeltaInSeconds
			if error != "0":
				ssh[5] = lastTime
		
		# Newly installed clients set the activity "breaks"
		# There were still old clients installed which "break" used
		if activity == "break" or activity == "breaks":
			breaks[1] += 1
			breaks[2] = lastTime
			breaks[3] += lastDeltaInSeconds
			if error != "0":
				breaks[5] = lastTime
	
	# Calculate the relative proportions of the activities
	# Goes only if the total time is greater than 0 (Div0)
	if durationAll != 0:
		browsing[4] = browsing[3] * 100 / durationAll
		copySea[4] = copySea[3] * 100 / durationAll
		copyFiles[4] = copyFiles[3] * 100 / durationAll
		mailing[4] = mailing[3] * 100 / durationAll
		printing[4] = printing[3] * 100 / durationAll
		private[4] = private[3] * 100 / durationAll
		meeting[4] = meeting[3] * 100 / durationAll
		offline[4] = offline[3] * 100 / durationAll
		ssh[4] = ssh[3] * 100 / durationAll
		breaks[4] = breaks[3] * 100 / durationAll
	
	# Write the compressed values ​​into a new file
	with open("/home/stack/skripte/dashboard/instances/" + clientID + ".log", "w") as f:

		for activity in allActs:
			for item in activity:
				f.write(str(item) + ",")
			
			# Replace the last comma with a semicolon at the end of each activity
			f.seek(-1, os.SEEK_END)
			f.truncate()
			f.write(";")
		
		# Remove the last semicolon at the end of the file
		f.seek(-1, os.SEEK_END)
		f.truncate()
	
	# Add run times of all instances
	allActsRuntimes[0] += browsing[3]
	allActsRuntimes[1] += mailing[3]
	allActsRuntimes[2] += printing[3]
	allActsRuntimes[3] += copyFiles[3]
	allActsRuntimes[4] += copySea[3]
	allActsRuntimes[5] += ssh[3]
	allActsRuntimes[6] += meeting[3]
	allActsRuntimes[7] += offline[3]
	allActsRuntimes[8] += private[3]
	allActsRuntimes[9] += breaks[3]
	
	return allActsRuntimes;

def myPrint(title, msg):
	print str(datetime.now()) + ": " + str(title)
	print str(msg)

def main():
	# List of all MAC addresses that are known to OpenStack
	macAddressesFromOpenStack = getMacAddressesFromOpenStack()
	if not macAddressesFromOpenStack:
		myPrint("macAddressesFromOpenStack", macAddressesFromOpenStack)
	
	# Get list with all MAC addresses in the config files
	macAddressesFromConfigs = getMacAddressesFromConfigs(glob("/media/logs/*.conf"))

	open("/home/stack/skripte/dashboard/listOfInstances", "w").close()
	
	# Array to store the totals of all run times of all activities
	allActsRuntimes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	
	# Iterate through MAC addresses and only compress the logs of the actual running instances
	for macOS in macAddressesFromOpenStack:
		for macConf in macAddressesFromConfigs:
			if macOS == macConf:
			
				# Write the MAC address of the active instances
				with open("/home/stack/skripte/dashboard/listOfInstances", "a") as f:
					f.write(macOS + ";")
			
				# Compress the client's config
				compressConfig(macOS)
	
				# Compress the client activity log
				# The total running time of all activities is always added
				try:
					allActsRuntimes = compressActLog(macOS, allActsRuntimes)
				except Exception as e:
					print "Fehler bei Erzeugung des komprimierten Logs fuer Client " + macOS + ": " + str(e)
	
	# Write all run times of all activities of all instances
	# Consists of absolute and relative run times
	sumRuntime = 1
	sumRuntime += sum(allActsRuntimes)
	with open("/home/stack/skripte/dashboard/allActsRuntimes", "w") as f:
		for runtime in allActsRuntimes:
			try:
				f.write(str(runtime) + "," + str(runtime * 100 / sumRuntime) + ";")
			except Exception as e:
				f.write(str(runtime) + "," + "0" + ";")
			
		# Remove last semicolon
		f.seek(-1, os.SEEK_END)
		f.truncate()
if __name__ == "__main__":
	main()
