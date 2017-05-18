from subprocess import Popen
from ConfigParser import SafeConfigParser
from datetime import datetime
import subprocess
import socket
import platform
import urllib
import sys


# Download recent ServerConfig
def getCurrentServerConfig():
	newConfigFile = urllib.URLopener()
	newConfigFile.retrieve("YOUR_SERVER_IP/scripts/automation/packages/system/serverconfig.ini", "/home/debian/serverconfig.ini")

# Configure backup server 
def configBackupServer(parser):
	
	# Read ips from backup servers 	
	backupIP = parser.get("backup", "ip")
			
	# Mount netstorage 
	try:
		cmd = "mount -t cifs -o username=nobody,password=nobody //" + backupIP + "/backup_fileserver /home/debian/backup"
		subprocess.check_call(cmd, shell=True)
	except Exception as e:
		with open("/home/debian/log.txt", "a") as file:
			file.write(datetime.now().strftime("%y%m%d-%H%M%S") + " | Fehler beim Mount des Backup-Servers | " + str(e) + "\n")

# Init 
def main():

	# Fetch recent server config file 
	getCurrentServerConfig()
	
	# Init parser 
	parser = SafeConfigParser()
	
	# Open ServerConfig file with parser 
	parser.read("/home/debian/serverconfig.ini")
	
	# Configure Backup strategy 
	configBackupServer(parser)

if __name__ == "__main__":
	main()
