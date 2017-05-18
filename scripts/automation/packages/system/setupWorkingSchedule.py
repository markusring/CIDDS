from echoX import echoC
from ConfigParser import SafeConfigParser
from datetime import datetime
import random
import sys

# Parameters for working hours
START_WORK_EARLY = 6
START_WORK_LATE = 10
END_WORK_EARLY = 16
END_WORK_LATE = 20

# Parameters for the working days
SATURDAY_PROBABILITY = 10
SUNDAY_PROBABILITY = 5
WEEKDAY_PROBABILITY = 90

# Determien working days 
def setWorkdays(parser):

	# Read all weekdays from config (list with tuples)
	workdays = parser.items("workdays")

	# Iterate through weekdays and determine whether to work on this day
	for workdayTuple in workdays:
		workdayName = workdayTuple[0]
		
		# Find a random value between 1 and 100
		# This value is used to determine whether the respective day of the week has to be worked on
		isWorkdayProbability = random.randint(1, 100)
		
		# Probability to work on Saturday is 10%
		isWorkday = "0"
		if workdayName == "saturday":
			isWorkday = "1" if isWorkdayProbability < SATURDAY_PROBABILITY else "0"

		# Probability to work on Sonday is 5%
		elif workdayName == "sunday":
			isWorkday = "1" if isWorkdayProbability < SUNDAY_PROBABILITY else "0"

		# Probability to work under the week is 90%
		else:
			isWorkday = "1" if isWorkdayProbability < WEEKDAY_PROBABILITY else "0"
		
		# Write config 
		parser.set("workdays", workdayName, isWorkday)

		if isWorkday == "0":
			status = " is not a workday"
		else:
			status = " is a workday"

		echoC(__name__, workdayName + status)
	
# Determine working time 
def setWorkingHours(parser):
	
	clockIn = random.randint(START_WORK_EARLY, START_WORK_LATE)
	clockOut = random.randint(END_WORK_EARLY, END_WORK_LATE)

	parser.set("workinghours", "clock_in", str(clockIn))
	parser.set("workinghours", "clock_out", str(clockOut))

	echoC(__name__, "Working hours: " + str(clockIn) + " - " + str(clockOut) + " h")

def main(parser):

	# Determine working days 
	setWorkdays(parser)

	# Determine working hours 
	setWorkingHours(parser)
	
	# "flush" 
	with open("packages/system/config.ini", "w") as config:
		parser.write(config)

if __name__ == "__main__":
	main(parser)
