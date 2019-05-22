import sys, os, subprocess

if os.name == "nt":
	import _winreg
	
#------------------------------------------------------

def getRegistryValue(iPath, iKey):
	theValue = ""
	try:
		key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, iPath, 0, _winreg.KEY_READ)
		theValue = _winreg.QueryValueEx(key, iKey)[0]
		key.Close()
	except:
		pass
	return theValue

#------------------------------------------------------

def executeCommand(aCommand, aCommandLogName, afUseShell=False, afCloseFDS=False):

	print "*******************************************************************"
	print "Executing " + aCommandLogName + "..."
	print "Working Directory: " + os.getcwd()
	print "Command          : " + aCommand
	print "*******************************************************************"
	sys.stdout.flush()
	
	p = subprocess.Popen(aCommand, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=afUseShell, close_fds=afCloseFDS)
	for line in iter(p.stdout.readline, ''):
		line = line.replace('\r', '').replace('\n', '')
		print line
		sys.stdout.flush()
		
	p.wait()

	return p.returncode
