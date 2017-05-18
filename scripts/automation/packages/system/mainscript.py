from packages.system.echoX import echoC
from packages.mailing import mailing
from packages.browsing import browsing
from packages.copyFiles import copyFiles
from packages.copyFiles import copySea
from packages.printing import printing
from packages.ssh import sshConnections
from packages.attacking import attacking

from subprocess import Popen, check_output
from ConfigParser import SafeConfigParser
from datetime import datetime, date
from Queue import Queue
from uuid import getnode
import random
import threading
import time
import platform
import sys
import socket
import os

# Init atWork parameters
isTimeToWork = 0
isDayToWork = 0

# Initialize the lunch flag
# Is set to true at the start of the lunch break and reset at the start of each working day
hadLunchToday = False

# ID of the instance consisting of the host name and the int value of the MAC address
myID = "empty"

# Path which the log file is to be stored
pathForLog = "empty"

# Class which creates a thread for a given program call
class RunCmd(threading.Thread):

	# Constructor
	def __init__(self, arg, timeout, queue):
		threading.Thread.__init__(self)
		self.arg = arg
		self.timeout = timeout
		self.queue = queue
	
	# Start Thread 
	# is called with start() 
	# CONSIDER: asynchronous function! 
	def run(self):
		self.p = Popen(["python", "-m", "packages.browsing.browsing", self.arg])
		self.queue.put(self.p.wait())
	
	# Indirect start of the Thread 
	def Run(self):

		# call run method
		self.start()
		
		# Wait x seconds for thread timeout 
		self.join(self.timeout)
		
		# If the thread is still active after x seconds, it is terminated
		if self.is_alive():			
			
			# Stop the Firefox driver so that they do not block the RAM as zombies 
			# Only for linux 
			# Update: Does not always work, therefore first kill()
			self.p.kill()
			
			self.queue.put(-1)

			self.join()
			echoC(__name__, "Browsing timeout: killed the Thread")

# Write the log for the dashboard
def writeLog(a_start, a_end, act, a_err):

	# Determine runtime 
	a_diff = str(a_end - a_start)
	
	# Add milliseconds 
	if "." not in a_diff:
		a_diff += ".000000"
		
	# Write logs on the network drive 
	with open(pathForLog + myID + ".log", "a") as myfile:
		myfile.write(str(a_start) + "," + str(a_end) + "," + a_diff + "," + act + "," + str(a_err) + "\n")

def getSubnetHostAndHostname():
	# Determine IP of VM 
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("google.com", 80))
	ip = (s.getsockname()[0])
	s.close()
	echoC(__name__, "My IP is " + ip)
	
	# Determine Subnet using IP 
	subnet = ip.split('.')[2]
	
	# Determine host part of the IP 
	host = ip.split('.')[3]
	
	# Determine host name 
	hostname = socket.gethostname()
	
	return subnet, host, hostname

# According to the weekday, it is decided whether to work
def isWorkday(parser):
	
	# Read all weekdays from config (list with tuples)
	workdays = parser.items("workdays")

	# Current weekday as int (0 = Monday, ...)
	currWeekday = date.today().weekday()

	# Determine whether it is a working day
	if workdays[currWeekday][1] == "1":
		isDayToWorkNew = 1
	else:
		isDayToWorkNew = 0
	
	# If a status change takes place, a corresponding output is generated
	# as well as the global flag
	global isDayToWork	
	if isDayToWork != isDayToWorkNew:
		isDayToWork = isDayToWorkNew
		if isDayToWork == 1:
			echoC(__name__, "Today is a workday (" + workdays[currWeekday][0] + ")")
			echoC(__name__, "Working hours: " + parser.get("workinghours", "clock_in") + " - " + parser.get("workinghours", "clock_out") + " h")
		else:
			echoC(__name__, "Today is not a workday (" + workdays[currWeekday][0] + ")")
	
	return isDayToWork

# According to the time, work is done or the work resumes
def isWorkingHours(parser):
	
	# Read working times from config
	clockIn = parser.getint("workinghours", "clock_in")
	clockOut = parser.getint("workinghours", "clock_out")	
	
	# Determine cureent time 
	try:
		currHour = int(datetime.now().strftime("%H"))
	except Exception as e:
		echoC(__name__,  str(e))
		currHour = 8

	# Determine whether the working time has elapsed
	if clockIn <= currHour < clockOut:
 		isTimeToWorkNew = 1
	else:
		isTimeToWorkNew = 0

	# If a status change takes place, a corresponding output is generated
	# as well as the global flag
	global isTimeToWork	
	if isTimeToWork != isTimeToWorkNew:
		isTimeToWork = isTimeToWorkNew
		if isTimeToWork == 1:
			echoC(__name__, "Workday starts")

			# Status flag for showing whether already lunch break was made already today
			global hadLunchToday
			hadLunchToday = False
		else:
			echoC(__name__, "Workday ends")
			if platform.system() == "Linux":
			
				# Install updates
				echoC(__name__, "Updating system")
				update = Popen("sudo apt-get update -qy && sudo apt-get upgrade -qy", shell=True)
				update.wait()
				
			# Restart client at the end of each working day 
			echoC(__name__, "Restarting system")
			restartClient()

	return isTimeToWork	

# Determine whether it is time for the lunch break
def isTimeForLunch():
	# Determine recent time 
	try:
		currHour = int(datetime.now().strftime("%H"))
	except Exception as e:
		echoC(__name__,  str(e))
		currHour = 8
	
	# Check whether the current time is in the period of the lunch break
	if 11 <= currHour < 13:
		
		# Determine whether lunch break is to be carried out
		if random.randint(1, 10) >= 9:		
			return True
	return False

# Completed written work
def doSomething(activities):
	activity = activities[random.randint(0,  len(activities)-1)]
	
	a_error = 0
	a_start = datetime.now()

	if activity == "browsing":
		queue = Queue()
		# For browsing, a thread is started which ends after 10 minutes at the latest
		RunCmd("b", 600, queue).Run()
		a_error = queue.get()
	if activity == "copyFiles":
		a_error = copyFiles.main()
	if activity == "copySea":
		a_error = copySea.main()
	if activity == "mailing":
		a_error = mailing.main()
	if activity == "printing":
		a_error = printing.main()
	if activity == "ssh":
		a_error = sshConnections.main()
	if activity == "meeting":
		meetingDuration = random.randint(10*60,120*60)
		echoC(__name__, "Attending a meeting for " + str(meetingDuration/60) + " mins")	
		time.sleep(meetingDuration)
	if activity == "offline":
		offlinew = random.randint(1*60,50*60)	
		echoC(__name__, "Doing some offline work for " + str(offlinew/60) + " min")	
		time.sleep(offlinew)
	if activity == "private":
		queue = Queue()
		# For browsing, a thread is started which ends after 10 minutes at the latest
		RunCmd("p", 600, queue).Run()
		a_error = queue.get()
	if activity == "breaks":
		takeABreak()
	if activity == "attacking":
		a_error = attacking.main()
		
	writeLog(a_start, datetime.now(), activity, a_error)

# Do breaks 
def takeABreak():
	# Determine whether it is time for lunch break, otherwise short coffee break
	# MinDuration and maxDuration represent the lower and upper limit of the pause duration in minutes
	breakDuration = 1	
	if hadLunchToday == False and isTimeForLunch():
		minDuration = 15
		maxDuration = 60
		
		# Determine a random pause duration in seconds
		breakDuration = random.randint(minDuration * 60, maxDuration * 60)
		echoC(__name__, "Heading for lunch (" + str(breakDuration/60) + " min)")
		
		# Set the lunch flag so that lunch is made only once a day
		global hadLunchToday
		hadLunchToday = True
	else:
		minDuration = 1
		maxDuration = 5

		# Determine a random pause duration in seconds
		breakDuration = random.randint(minDuration * 60, maxDuration * 60)
		echoC(__name__, "I need coffee (" + str(breakDuration/60) + " min)")

	# Do break 
	time.sleep(breakDuration)
	return

# Restart instance 
def restartClient():
	if platform.system() == "Linux":
		os.system("shutdown -r now")
	if platform.system() == "Windows":
		# Works with Windows only sometimes (!?)
		# subprocess.call(["shutdown", "/r", "/f"])
		echoC(__name__, "Windows does not reboot properly...")
		return False

# Check which activity flags are set and create a list for the Python files accordingly
def createActivityList(browsing, mailing, printing, copyfiles, copysea, ssh, meeting, offline, private, breaks, attacking):

	l = []
	for i in range(0, browsing):
		l.append("browsing")
	for i in range(0, mailing):
		l.append("mailing")
	for i in range(0, printing):
		l.append("printing")
	for i in range(0, copyfiles):
		l.append("copyFiles")
	for i in range(0, copysea):
		l.append("copySea")
	for i in range(0, ssh):
		l.append("ssh")
	for i in range(0, meeting):
		l.append("meeting")
	for i in range(0, offline):
		l.append("offline")
	for i in range(0, private):
		l.append("private")
	for i in range(0, breaks):
		l.append("breaks")
	for i in range(0, attacking):
		l.append("attacking")
	if not l:
		echoC(__name__, "Nothing to do. Maybe you should check some activities...")
		sys.exit(0)
	return l

# Activiate work day 
def init(browsing, mailing, printing, copyfiles, copysea, ssh, meeting, offline, private, breaks, attacking, t):
	activities = createActivityList(browsing, mailing, printing, copyfiles, copysea, ssh, meeting, offline, private, breaks, attacking)
	
	time.sleep(2)

	parser = SafeConfigParser()
	parser.read("packages/system/config.ini")
	
	subnet, host, hostname = getSubnetHostAndHostname()
	global myID
	
	if platform.system() == "Linux":
		myID = str(getnode())
	else:
		# For Windows, something must be trickled, since getnode () returns an incorrect value
		hexMac = check_output(["getmac"])[162:180]
		hexMacNoDash = hexMac.replace("-", "")
		intMac = int(hexMacNoDash, 16)
		myID = str(intMac)
		
	global pathForLog
	if platform.system() == "Linux":
		pathForLog = "/home/debian/log/"
	else:
		pathForLog = "M:\\"
		
	# In endless loop perform different activities
	try:	
		while True:
			
			if isWorkday(parser) and isWorkingHours(parser):
					doSomething(activities)
			
			else:
				# Should be just the end of his work, he must wait until he has to work again
				time.sleep(random.randint(1, 15)*60 - random.randint(1, 55))

	except KeyboardInterrupt:
		echoC(__name__, "SCRIPT STOPPED: KEYBOARDINTERRUPT")	
		sys.exit(0)
