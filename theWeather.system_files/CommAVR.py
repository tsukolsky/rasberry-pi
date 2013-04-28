#!/usr/bin/python
########################################################################
## CommAVR.py
## Author: Todd Sukolsky
## Copyright of Todd Sukolsky
## Date Created: 4/25/13
## Last Reviced: 4/25/13
########################################################################
## Description: This script communicates with the AVR on theWeather.system
## 	board. It communicates over USB<->UART using an FTDI chip on the board.
########################################################################
## Revisions:
##		4/25: Initial Build
########################################################################
## Notes: Commands to AVR are 'STATS.' currently, that's it
########################################################################

import random
import sys
import os
import time
import serial
import optparse
import subprocess
import smtplib
import socket
from email.mime.text import MIMEText
import datetime

##OPTPARSER INFO
inputString=''
askUser=False

use = "Usage: %prog [options] <arguments>. String entered must have '.' to terminate."
parser = optparse.OptionParser(usage=use)
parser.add_option('-s', dest='inString', help='String to be sent, real mode')
parser.add_option('-D',action="store_true", dest="debug",default=False,help='User String for debug mode')
parser.add_option('-e',dest='email',help='Which email to send to')
parser.add_option('-E',action="store_true",dest="noSend",default=False,help='Send an email, or just print?')
(options, args) = parser.parse_args()


if options.inString is None and options.debug is True:
	askUser=True
elif options.inString is not None and options.debug is False:
	inputString=options.inString
elif options.inString is not None and options.debug is True:
	askUser=True
	inputString=options.inString

##Declare send string routines.
def sendString(theString):
	#Loop through each character in the string and write it.
	for char in theString:
		serialPort.write(char)
		time.sleep(100.0/1000.0)

##getString() routine. Set to get UART strings fromt he AVR, terminated by X. Timeout=10 seconds.
def getString(waitingForAck):
	##Wait for an X that signifies the end of data.
	gotX=False
	timeout=time.time()+10
	captureString=''
	while gotX is False and ((time.time()-timeout) < 0):
		captureString+=serialPort.read(serialPort.inWaiting())
		if captureString.find('X')!=-1:							#If we found an X, we can kill it and return the string striped					
			gotX=True
		#	print captureString.strip().rstrip().replace('X','')
			return captureString.strip().rstrip().replace('X','')			#Strip of newline, while space, X
		elif captureString.find('ACK.')!=-1 and waitingForAck is True:
			gotX=True
			return captureString.strip().rstrip()
		else:
			time.sleep(20.0/1000.0)		#Wait for another 20 milliseonces
		#print captureString
	print captureString		
	return 'error'

	
##Main Program
#Open the serial port
portName='/dev/ttyUSB0'
baud=9600
serialPort = serial.Serial(
        port=portName,
        baudrate=baud,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
)

##Try and open the serial port, if it doesn't open exit
try:
	serialPort.open()
except:
	print "Error: Unable to open serial port "+portName
	exit(3)
	
#Variables
ackString=''				##What we get back when we initiate the connection
dataString=''				##What we get back when we ask for data
noAck=True					##If we have gotten an ack or not

#Setup the connection with the system
os.system('echo 1 > /sys/class/gpio/gpio25/value')
time.sleep(25.0/1000.0)
os.system('echo 0 > /sys/class/gpio/gpio25/value')

##We have 60 seconds to get an ack
ackTimeout=time.time()+60
while ((time.time()-ackTimeout)<0) and noAck:
	##Get the ACK
	ackString=getString(True)
	if ackString.find('error')==-1:			#Error wasn't returned, so we have a valid ack string. continue
		noAck=False
	else:
		time.sleep(100.0/1000.0)

##After we send the string asking what we want, we have 5 seconds to get the data string.
#If no ack was gotten in 60 seconds, exit
if noAck:
	print 'Timeout: Unable to get ACK, exiting'
	exit()
else:
	#If the inputString is null, ask the user what we should be sending.
	if inputString is None or askUser is True:
		inputString=raw_input(">>")
	#Send the string, wait 50 ms for a response before activating timeout
	sendString(inputString)
	time.sleep(200.0/1000.0)
	dataString=getString(False)
	#If error is not in the string, split the string into it's parts and display them
	if dataString.find('error')==-1:
		if dataString.find('/')!=-1:
			##We got the right data, print it out.
			print 'Got data...parsing'
		else:
			print dataString
			exit(0)
	else:
		##Didn't get valid date
		print 'Timeout: Unable to receive data. Exiting.'
		exit(2)

##Turn the data string into something interesting
from time import localtime,strftime
message='@%s Local Time:\n' % strftime('%I:%M:%S%p',localtime())

#print dataString

if dataString.find('AD')!=-1:
	##This is called when we asked for STATS. Print only the current weather readings
	message+='Your current weather readings, brought to you by Todd Sukolsky and Michael Gurr:\n\nCurrent Stats:\n---------------------------------------------\n'
	fields=dataString.split('/')
	for field in fields:
		if field.find('AD')!=-1:
			message+='Analog Devices On-Board Temp: '+field[2:]+' F\n'
		elif field.find('TI')!=-1:
			message+='Texas Instruments On-Board Temp: '+field[2:]+' F\n'
		elif field.find('TH')!=-1:
			message+='Thermistor Ambient Room Temp: '+field[2:]+' F\n'
		else:	
			message+='Humidity: '+field[2:]+'%\n'
else:
	##This is called when we asked for WEEK. Print out the week past weather data.
	message+='Ahh, a new week begins. Miles to go!\nHere are your weekly weather readings, brought to you by Todd Sukolsky and Michael Gurr:\n\nLast Weeks Stats:\n---------------------------\n'
	fields=dataString.split('/')
	for field in fields:
		if field.find('WH')!=-1:
			message+='Average High: '+field[2:]+' F\n'
		elif field.find('WL')!=-1:
			message+='Average Low: '+field[2:]+' F\n'
		elif field.find('WT')!=-1:
			message+='Average Temp: '+field[2:]+' F\n'
		else:
			message+='Average Humidity: '+field[2:]+'%\n'
##Add signature
message+='\n\n--theWeather.system'
random=random.randint(0,4)
creepers=['Oh, and btw, you forgot to call me','Look to the Northeast for a meteor show...Im a Virgo, you?','Dannggg, did you see her. Shes got some sizzle','Forgot to ask, but do you have a boyfriend?','Quick Question. When do I get to meet the parents??']
message+='\n\n\n'+creepers[random]

if options.noSend is True:
	print message
	exit(0)

##Get who to email.
emailList=[]
##If we didn't get an email here, then this was spawned by a new email into the server. Send only to that user (else statement)
##-otherwise, send to everyone on the list..
if options.email is None:
	IF=open('/home/sukolsky/Documents/emailList.txt','r')	
	emails=IF.readlines()
	IF.close()
	for address in emails:
		if address.rstrip()!='':
			emailList.append(address.rstrip().strip())
else:
	emailList.append(options.email)
	message='Thanks for subscribing to theWeather.system!\n\n'+message

print emailList

##Formulate the email
gmail_user=''
gmail_password=''
smtpserver=smtplib.SMTP('smtp.gmail.com',587)
smtpserver.ehlo()
smtpserver.starttls()
smtpserver.ehlo
smtpserver.login(gmail_user,gmail_password)
today=datetime.date.today()

#Create actual email
msg=MIMEText(message)
msg['Subject']='theWeather.system data on %s' % today.strftime('%b %d %Y')
msg['From']=gmail_user
try:
	smtpserver.sendmail(gmail_user,emailList,msg.as_string())
except:
	print 'Unable to send email. Most likely no recipients'

smtpserver.quit()

exit(0)








