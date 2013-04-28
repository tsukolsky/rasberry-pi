#!/usr/bin/python

import os
import sys
import serial
import subprocess
from time import localtime, strftime

eastern=strftime('%H%M%S.',localtime())
timeToSend='T'+eastern
print timeToSend

p=subprocess.Popen(['/home/sukolsky/Documents/CommAVR.py','-s',timeToSend,'-E','true'],stdout=subprocess.PIPE)
out,err=p.communicate()
try:
	print out
except:
	print "no output..."

exit()
