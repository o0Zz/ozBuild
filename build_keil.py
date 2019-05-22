import sys, os, subprocess, build_utils

#------------------------------------------------------
	
def getKeilBuildPath():
	kDefaultPaths = []
	kDefaultPaths.append( build_utils.getRegistryValue("HKEY_LOCAL_MACHINE\\SOFTWARE\\Wow6432Node\\Keil\\Products\\MDK", "Path") )
	kDefaultPaths.append( build_utils.getRegistryValue("HKEY_LOCAL_MACHINE\\SOFTWARE\\Keil\\Products\\MDK", "Path") )
	kDefaultPaths.append( "C:\\Keil_v5\\ARM" )
	
	for thePath in kDefaultPaths:
		if os.path.isdir(thePath):
			theFullPath = os.path.join(thePath, "..\\UV4\\UV4.exe")
			if os.path.exists(theFullPath):
				return theFullPath

	return ""
	
#------------------------------------------------------

def Usage():
	print "Usage: "
	print "     " +sys.argv[0] + " <Keil project full path> <Debug|Release>"
	print ""
	print "i.e:"
	print "      " + sys.argv[0] + " \"MyKeilProject.uvprojx\" Debug"
	sys.exit(1)
	
#------------------------------------------------------

def Build(iProjectRelativePath, iProjectBuildMode, iTarget):
	theKeilFullPath = getKeilBuildPath()
	if len(theKeilFullPath) == 0:
		print "ERROR: Unable to determine Keil Path !"
		sys.exit(1)
		
	theProjectPath, theProjectFilename = os.path.split(iProjectRelativePath)
	
		#Change working dir
	os.chdir(os.path.abspath(theProjectPath))

	theCmd = theKeilFullPath + " -c -b " + theProjectFilename + " -t\"" + iProjectBuildMode + "\" -o build.log"
	
	theRetCode = 0
	
	for i in xrange(3): #Try to build 3 times (Because of L6002U issue, see below)
	
		theRetCode = build_utils.executeCommand(theCmd, "Keil")
		
		theLogs = ""
		if os.path.exists("build.log"):
			theBuildLog = open("build.log", "rb")
			theLogs = theBuildLog.read()
			theBuildLog.close()
		
		print theLogs
		
		#Keil return code:
		#	0	No Errors or Warnings
		#	1	Warnings Only
		#	2	Errors
		#	3	Fatal Errors
		#	11	Cannot open project file for writing
		#	12	Device with given name in not found in database
		#	13	Error writing project file
		#	15	Error reading import XML file

		if theRetCode == 1: #On warning, return success
			theRetCode = 0
		
		if theRetCode == 0:
			break
		
		#Try to fix Keil issue
		#http://www.keil.com/forum/23341/l6002u-compile-error-with-certain-disk-drives/
		#http://www.keil.com/forum/22241/l6002u-error/
		if theLogs.find("L6002U") == -1: 
			break
		
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
	
	