import sys, os, subprocess, time, build_utils, shutil

#------------------------------------------------------
	
def getIARBuildPath():
	kIARDefaultPaths = []
	kIARDefaultPaths.append( build_utils.getRegistryValue("SOFTWARE\\Wow6432Node\\IAR Systems\\Embedded Workbench\\5.0\EW430\\5.60.1", "InstallPath") )
	kIARDefaultPaths.append( build_utils.getRegistryValue("SOFTWARE\\IAR Systems\\Embedded Workbench\\5.0\EW430\\5.60.1", "InstallPath") )
	kIARDefaultPaths.append( "C:\\Program Files (x86)\\IAR Systems\\Embedded Workbench 6.5" )
	kIARDefaultPaths.append( "C:\\Program Files\\IAR Systems\\Embedded Workbench 6.5" )
	
	for theIARPath in kIARDefaultPaths:
		if os.path.isdir(theIARPath):
			theIARFullPath = os.path.join(theIARPath, "common\\bin\\IarBuild.exe")
			if os.path.exists(theIARFullPath):
				return theIARFullPath

	return ""
	
#------------------------------------------------------

def Usage():
	print "Usage: "
	print "     " +sys.argv[0] + " <iar project full path> <Debug|Release>"
	print ""
	print "i.e:"
	print "      " + sys.argv[0] + " \"MyIARProject.eww\" Debug"
	sys.exit(1)
	
#------------------------------------------------------

def ConnectToDongle():
	theDongleIDs = ["1-1"]
	theDongleLicenses = ["DongleXXX.package"]
	theIarLicenseFile = "C:\\ProgramData\\IARSystems\\LicenseManagement\\LicensePackages\\430\\EW\\1\\Selected.package"
	
	for i in xrange(len(theDongleIDs)):
		print "Connecting dongle " + theDongleIDs[i] + "..."
		theRet = os.system("\"C:\\Program Files\\USB Redirector Client\\usbrdrltsh.exe\" -connect " + theDongleIDs[i])
		if theRet == 0:
			print "Copying license " + theDongleLicenses[i] + "..."
			shutil.copyfile(os.path.dirname(os.path.abspath(__file__)) + "/iar/" + theDongleLicenses[i], theIarLicenseFile);
			return theDongleIDs[i]
	
	print "ERROR: Dongle connection FAILED !"
	return ""
	
#------------------------------------------------------

def DisconnectFromDongle(aDongleID):
	print "Disconnecting dongle ..."
	os.system("\"C:\\Program Files\\USB Redirector Client\\usbrdrltsh.exe\" -disconnect " + aDongleID)
	time.sleep(2)
	
#------------------------------------------------------

def Build(iProjectRelativePath, iProjectBuildMode, iTarget):
	theContainsNoError = False
	theIARFullPath = getIARBuildPath()
	if len(theIARFullPath) == 0:
		print "ERROR: Unable to determine IAR Path !"
		sys.exit(1)
		
	theProjectPath, theProjectFilename = os.path.split(iProjectRelativePath)

		#Change working dir
	os.chdir(os.path.abspath(theProjectPath))

	theCmd = theIARFullPath + " " + theProjectFilename + " -build " + iProjectBuildMode + " -log all"
	
	theDongleID = ConnectToDongle()
	if len(theDongleID) == 0:
		print "BUILD ABORTED! Unable to connect the dongle !"
		return 999
		
	print "*******************************************************************"
	print "Executing IAR ..."
	print "Working Directory: " + os.getcwd()
	print "Command          : " + theCmd
	print "*******************************************************************"
	sys.stdout.flush()
	
	p = subprocess.Popen(theCmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	for line in iter(p.stdout.readline, ''):
		line = line.replace('\r', '').replace('\n', '')
		print line
		
		if line.find("Total number of errors: 0") != -1:
			theContainsNoError = True #Hack for IAR known issue: EW24771

		sys.stdout.flush()
		
	p.wait()
	
	DisconnectFromDongle(theDongleID)

	theRetCode = p.returncode
	if theRetCode == 1 and theContainsNoError == True:
		#Hack for IAR known issue
		#EW24771 / IDE-2207
		#In rare cases IarBuild.exe might return failure status (1) even when the build actions were successful. 
		theRetCode = 0
	
		#Forward error code for build machine
	return theRetCode
	
#------------------------------------------------------

if __name__ == '__main__':
	if len(sys.argv) < 3:
		Usage() 
		
	theProjectRelativePath 		= os.path.expandvars(sys.argv[1])
	theProjectBuildMode 		= sys.argv[2]
		
	theTarget 					= None
	if len(sys.argv) > 3:
		theTarget 				= sys.argv[3]
		
	theRet = Build(theProjectRelativePath, theProjectBuildMode, theTarget)
	sys.exit( theRet )
	