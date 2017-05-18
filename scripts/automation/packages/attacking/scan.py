from packages.system.echoX import echoC
import sys
import random
import linecache
import platform

if platform.system() == "Linux":
	import nmap
else:
	return -1

iprange = 'packages/attacking/iprange.txt'
ipList = 'packages/attacking/ipList.txt'

def getIPRange():
	try:
		with open(iprange) as f:
			content = [x.strip('\n') for x in f.readlines()]
	except Exception as e:
		echoC(__name__, "Error reading IP ranges: " + str(e))
		content = -1
	return content

def main():

	echoC(__name__, "Starting a scan")
	
	# Determine subnets 
	ipRangeList = getIPRange()
	if ipRangeList == -1:
		return -1
	
	# Select a random subnet 
	rand = random.randint(0, len(ipRangeList)-1) 
	ipRange = ipRangeList[rand]
	
	# Define arguments 
	scanOptions = ["-sF", "-sA", "-sU", "-sS", "-n -sP -PE"]
	myArguments = random.choice(scanOptions) + " -T " + str(random.randint(1, 3))
	
	echoC(__name__, "Scanning " + str(ipRange) + " with arguments: " + myArguments)
	
	# Execute Scan 
	nm = nmap.PortScanner()
	nm.scan(hosts=ipRangeList[rand], arguments=myArguments)
	
	# Store the found IPs 
	# At first, delete old IPs 
	open(ipList, 'w').close()
	for i in nm.all_hosts():
		with open(ipList, 'a') as myfile:
			myfile.write(str(i) + '\n')
			
	echoC(__name__, "Done")
	
	returnval = "0,nmap args: " + myArguments
	return returnval

if __name__ == "__main__":
	main()
