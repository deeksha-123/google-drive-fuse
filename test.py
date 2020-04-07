import subprocess
import os
cmd="fusermount"
args1="-u"
args2="/home/deeksha/mount_point"
temp = subprocess.Popen([cmd,args1,args2], stdout = subprocess.PIPE) 
cmd="rm"
args1="token.json"
temp = subprocess.Popen([cmd,args1], stdout = subprocess.PIPE)
cmd="rm"
args1="directory.txt"
temp = subprocess.Popen([cmd,args1], stdout = subprocess.PIPE)
cmd="rm"
args1="-rf"
args2="/home/deeksha/gdrive"
temp = subprocess.Popen([cmd,args1,args2], stdout = subprocess.PIPE)
cmd="rm"
args1="-rf"
args2="/home/deeksha/mount_point"
temp = subprocess.Popen([cmd,args1,args2], stdout = subprocess.PIPE)


