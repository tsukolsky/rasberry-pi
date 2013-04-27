#!/usr/bin/python

import os
import sys
import optparse
import subprocess

email=''

use="Usage: %prog [options] <arguments>. Email is input string."
parser=optparse.OptionParser(usage=use)
parser.add_option('-e',dest='emailIn',help='Email to add delete')

(options,args)=parser.parse_args()

if options.emailIn is None:
	exit(1)
else:
	email=options.emailIn

IF=open('/home/sukolsky/Documents/rasberry-pi/theWeather.system_files/emailList.txt','r')
emails=IF.readlines()
IF.close()
OF=open('/home/sukolsky/Documents/rasberry-pi/theWeather.system_files/emailList.txt','w')
hadToDelete=False
for anEmail in emails:
	if anEmail!=email+'\n':
		##Write the email back to the file
		OF.write(anEmail)
	else:
		hadToDelete=True

if hadToDelete is False:
	OF.write(email+'\n')
	OF.close()
	p=subprocess.Popen(['/home/sukolsky/Documents/CommAVR.py','-s','STATS.'],stdout=subprocess.PIPE)
	out,err=p.communicate()
	try:
		print "Output:"+out
	except:
		print "No output"
	try:
		print "Error:"+err
	except:
		print "No errors"

##Emails are now done
exit(0)
