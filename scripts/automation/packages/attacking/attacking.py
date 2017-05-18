from packages.system.echoX import echoC
from packages.attacking import scan, dos, bruteForce
from subprocess import Popen
from datetime import datetime
from uuid import getnode
from ConfigParser import SafeConfigParser
import threading
import random
import datetime
import linecache
import sys
import time

attackList = 'packages/attacking/attackList.txt'

pathToLog = "/home/debian/log/"
logFile = pathToLog + str(getnode()) + ".log"

# Class which creates a thread for a given program call
class RunCmd(threading.Thread):

	# Constructor 
	def __init__(self, mode, startOfWorkday, endOfWorkday):
		threading.Thread.__init__(self)
		self.mode = mode
		self.endOfWorkday = endOfWorkday
		self.startOfWorkday = startOfWorkday
		self.goOn = True
	
	# Start Thread 
	# is called by start() 
	# asynchron!!!
	def run(self):
		
		while True:
				
			# Keep browsing until the end of the evening
			# Since the browsing itself gladly times hang up it is every 5 min restarted
			while datetime.datetime.now().hour < self.endOfWorkday:
				
				# Cancel if there are no more attacks
				if self.goOn == False:
					echoC(__name__, "Will not start another browsing process")
					return
			
				echoC(__name__, "Starting browsing process while attacking")
				self.p = Popen(["python", "-m", "packages.browsing.browsing", self.mode])
				time.sleep(300)
				
				# Regulatory exit of the virtual display and Firefox
				self.p.terminate()
				time.sleep(3)
				echoC(__name__, "Stopped browsing to check the clock")
			
			echoC(__name__, "End of workday. Taking a break from browsing")
			
			# If the next working day still the attack, the browsing is resumed
			while datetime.datetime.now().hour != self.startOfWorkday:
				time.sleep(300)
			
			echoC(__name__, "Start of workday. Continuing browsing")
			
			
	# Indirect start of the Thread 
	def Run(self):
	
		# Wait a moment before browsing is started
		time.sleep(5)

		# run method 
		self.start()
		

# Write the log for the dashboard
def writeLog(a_start, a_end, act, a_err):

	# Determine runtime 
	a_diff = str(a_end - a_start)
	
	# Add miliseconds 
	if "." not in a_diff:
		a_diff += ".000000"
		
	# Write the log on a network drive
	with open(logFile, "a") as myfile:
		myfile.write(str(a_start) + "," + str(a_end) + "," + a_diff + "," + act + "," + str(a_err) + "\n")
		
def createAttackList():
	try:
		with open(attackList) as f:
			content = [x.strip('\n') for x in f.readlines()]
	except Exception as e:
		echoC(__name__, "Error reading attackList: " + str(e))
		return -1
	return content

def main():
	
	echoC(__name__, "Doing some attacks")

	# View list of all pre-set attacks
	attacks = createAttackList()
	if attacks == -1:
		return -1
	
	b_start = datetime.datetime.now()
	
	# Determine end of workday 
	# Since the attacks can take quite a long time must be checked between whether or not is already evening
	parser = SafeConfigParser()
	parser.read("packages/system/config.ini")
	endOfWorkday = parser.getint("workinghours", "clock_out")
	startOfWorkday = parser.getint("workinghours", "clock_in")
	
	# By the way is still surfing the Internet
	# Browsing takes place in a thread
	browsingThread = RunCmd("e", startOfWorkday, endOfWorkday)
	browsingThread.Run()
	
	# Run different attacks differently often
	firstTime = True
	currentHour = datetime.datetime.now().hour
	while (random.randint(0, 3) != 0) or (firstTime == True):
		firstTime = False;
		
		# Do not start an attack if it is already after the end of the event
		if currentHour >= endOfWorkday:
			break
		
		a_start = datetime.datetime.now()
		a_error = 0
		
		# Select a random attack
		rand = random.randint(0, len(attacks)-1)
		attack = attacks[rand]

		# Start the script with the respective attack
		if attack == "dos":
			a_error = dos.main()
			
		if attack == "bruteForce":
			# Random number of passwords to try
			noOfPWs = random.randint(50, 150)
			a_error = bruteForce.main(noOfPWs)
			
		if attack == "scan":
			a_error = scan.main()
		
		# Write Logs 
		writeLog(a_start, datetime.datetime.now(), attack, a_error)
		
		waiting = random.randint(300, 600)
		echoC(__name__, "Waiting " + str(waiting/60) + " min")
		time.sleep(waiting)
		
		currentHour = datetime.datetime.now().hour
	
	# Stop browsing after the attacks
	browsingThread.goOn = False
	
	# Wait until the browsing thread is finished
	echoC(__name__, "Waiting for browsing thread to finish")
	browsingThread.join()
	
	writeLog(b_start, datetime.datetime.now(), "browsing", 0)
	
	echoC(__name__, "Done")
	
	return 0

if __name__ == "__main__":
    main()
