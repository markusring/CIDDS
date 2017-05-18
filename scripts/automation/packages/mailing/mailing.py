from packages.system.echoX import echoC
from ConfigParser import SafeConfigParser
from email.mime.text import MIMEText
from email.MIMEBase import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import Encoders
from datetime import datetime
import smtplib
import random
import linecache
import sys
import time
import imaplib
import email
import getpass
import platform
import string

def readMails(mailuser, mailuserpw, mailserverIP):
	# Start SSL-Connection 
	mail = imaplib.IMAP4_SSL(mailserverIP)

	# Login
	mail.login(mailuser, mailuserpw)

	# Selecting a folder - returns the number of mails (as a string) in [1] [0]
	no_of_msg = mail.select("inbox")[1][0]
	echoC(__name__, "Messages in inbox: " + no_of_msg)
	
	# Read existing e-mails
	if no_of_msg != '0':
		# Search all emails in the Inbox folder
		result, data = mail.uid('search', None, "ALL")

		# Search for the unique ID of the most recent e-mail
		latest_email_uid = data[0].split()[-1]
	
		#  read last E-Mail 
		result, data = mail.uid('fetch', latest_email_uid, "(RFC822)")
	
		# Random number of e-mail read (so to say as "new" e-mails not yet available on client)
		while random.randint(0, 3) != 0:
			# Read most recent E-Mail 
			result, data = mail.uid('fetch', latest_email_uid, "(RFC822)")
	
		raw_email = data[0][1]

		#Create Email object 
		email_message = email.message_from_string(raw_email)
	
		# Iterate over all E-Mails, search and store notes 
		for part in email_message.walk():
			if part.get_content_maintype() == 'multipart':
				continue
			if part.get('Content-Disposition') is None:
				continue
			data = part.get_payload(decode=True)
			if not data:
				continue
			
			if platform.system() == "Linux":
				attachment = "/home/debian/localstorage/attachment"
			else:
				attachment = "C:\\localstorage\\attachment"
				
			with open(attachment, "w") as f:
				f.write(data)

		# Output of some information from the last e-mail
		echoC(__name__, "Latest mail of " + email_message['Subject'] + " from '" + email_message['From'].split('@')[0] + "'")	
		time.sleep(30)
		
	# If no e-mail is present, 0 is returned and an e-mail is sent
	return no_of_msg

# Find the number of lines of the transferred file
def file_len(myfile):
	with open(myfile) as f:
		for i, l in enumerate(f):
			pass
		return i+1

# Identify the recipient
def getRecipient():
	# Random subnet and host share
	subnet = str(random.randint(0, 255))
	host = str(random.randint(0, 255))
	
	# Configure user identification from subnet and host part
	user = "user." + subnet.zfill(3) + "." + host.zfill(3)
	domain = "@mailserver.example"
	
	return user + domain

# Connect to SMTP server
def getConnection(parser, mailuser, mailuserpw):
	# Read server names from Mailconfig
	smtp_server = parser.get('mailconfig', 'smtp')
	
	# Connect to host / port with user and PW
	try:
		smtpserver = smtplib.SMTP(smtp_server, 587)
		smtpserver.ehlo()
		smtpserver.starttls()
		smtpserver.ehlo()
		smtpserver.login(mailuser, mailuserpw)
	except Exception as e:
		echoC(__name__, "Error connecting to the STMP-Server")
		return -1
		
	echoC(__name__, "SMTP-Server: " + str(smtp_server) + " User: " + str(mailuser).split('@')[0])
	return smtpserver

# create E-Mail content 
def createMessage(mailuser, to):	
	# Header erzeugen
	msg = MIMEMultipart()
	msg['From'] = mailuser
	msg['To'] = ", ".join(to)
	msg['Subject'] = datetime.now().strftime("%y%m%d-%H%M%S")

	# Random content 
	noOfChars = random.randint(200, 5000)
	body = "".join([random.choice(string.letters) for i in xrange(noOfChars)])
	msg.attach(MIMEText(body))
	
	return msg

def addAttachments(msg):
	attachments = []
	lines = file_len("packages/mailing/attachments.txt")
	nb = random.randint(0, lines)
	for i in range(0, nb-1):
		rand = random.randint(1, lines)
		att = linecache.getline("packages/mailing/attachments.txt", rand).replace ("\n", "")
		attachments.append(att)
	if nb > 0:
		for f in attachments or []:
			with open(f, "rb") as fil:
				part = MIMEBase('application', "octet-stream")
				part.set_payload(fil.read())
				Encoders.encode_base64(part)
				part.add_header('Content-Disposition', 'attachment; filename="%s"' %f)
				msg.attach(part)
		echoC(__name__, "Attachments attached")
	else:
		echoC(__name__, "No attachments")
	return msg

def main():
	
	# Return value for error detection
	error = 0

	echoC(__name__, "Started mailing script...")
	
	# Init parser 
	parser = SafeConfigParser()
	parser.read('packages/mailing/mail.ini')

	# Read e-mail user and password
	mailuser = parser.get('mailconfig', 'user')
	mailuserpw = parser.get('mailconfig', 'pw')
	mailserverIP = parser.get('mailconfig', 'smtp')
	
	# Connect to SMTP server
	smtpserver = getConnection(parser, mailuser, mailuserpw)
	if smtpserver == -1:
		return -1
	
	# E-Mails check
	no_of_mails = readMails(mailuser, mailuserpw, mailserverIP)
	time.sleep(10)
	
	# Send multiple e-mails 
	firstTime = True
	while random.randint(0, 2) != 0 or firstTime == True:
		firstTime = False
		
		# Determine receiver 
		# If there are no e-mails in the inbox, an e-mail is sent to itself (sometimes just as well)
		if no_of_mails == '0' or random.randint(0, 1) == 1:
			to = mailuser
		else:
			# Identify random recipient
			to = getRecipient()

		# Generate E-Mail content 
		msg = createMessage(mailuser, to)
	
		# Add note to the E-Mail 
		addAttachments(msg)
	
		# Send E-Mail 
		try:
			time.sleep(10)
			smtpserver.sendmail(mailuser, to, msg.as_string())
			echoC(__name__, "Mail sent to '" + to.split('@')[0] + "'")
		except Exception as e:
			echoC(__name__, "sendmail() error: " + str(e))
			error = -1
	
	# Close connection to server 
	smtpserver.close()

	echoC(__name__, "Done")
	return error

if __name__ == "__main__":
	main()
