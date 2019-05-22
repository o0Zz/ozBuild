import sys, os, subprocess, build_utils

#------------------------------------------------------
	
def getMSBuildPath(iVSVersionStr):
	theMSBuildPaths = []
	theMSBuildPaths.append( build_utils.getRegistryValue("SOFTWARE\\Wow6432Node\\Microsoft\\MSBuild\\" + iVSVersionStr + ".0", "MSBuildOverrideTasksPath") )
	theMSBuildPaths.append( build_utils.getRegistryValue("SOFTWARE\\Microsoft\\MSBuild\\" + iVSVersionStr + ".0", "MSBuildOverrideTasksPath") )

	for theMSBuildPath in theMSBuildPaths:
		if os.path.isdir(theMSBuildPath):
			theMSBuildFullPath = os.path.join(theMSBuildPath, "MSBuild.exe")
			if os.path.exists(theMSBuildFullPath):
				return theMSBuildFullPath

	return ""
	
#------------------------------------------------------

def Usage():
	print "Usage: "
	print "     " +sys.argv[0] + " <sln project full path> <Configuration>"
	print ""
	print "     Configuration:"
	print "                    Release"
	print "                    Debug"
	print "                    Debug|Win32"
	print "                    Release|Win32"
	print "                    Debug|Any"
	print "                    Release|Any"
	print "                    ..."
	print ""
	print "i.e:"
	print "      " + sys.argv[0] + " \"MyProject.sln\" Release"
	sys.exit(1)

#------------------------------------------------------

def GetVisualStudioVersionFromSLN(iProjectFilename):
	theSLN = open(iProjectFilename, 'rb')
	theSLNBuffer = theSLN.read()
	theSLN.close()
	
	theVersionIdx = theSLNBuffer.find("VisualStudioVersion")
	if theVersionIdx == -1:
		print "ERROR: Unable to find VisualStudioVersion key in SLN"
		return ""
	
	theEOLIdx = theSLNBuffer[theVersionIdx:].find("\n")
	if theEOLIdx == -1:
		print "ERROR: Unable to find end of line in SLN"
		return ""
	
	theFullVersionLine = theSLNBuffer[theVersionIdx:theVersionIdx + theEOLIdx]
	
	theBeginVersionIdx = theFullVersionLine.find("=")
	if theBeginVersionIdx == -1:
		print "ERROR: Unable to find '=' in SLN"
		return ""
		
	theFullVersionStr = theFullVersionLine[theBeginVersionIdx + 1:].strip()
	
	theMajorVersion = theFullVersionStr.split('.')[0]
	
	#print "SLN Version found: " + theMajorVersion
	
	return theMajorVersion
	
#------------------------------------------------------

def Build(iProjectRelativePath, iProjectBuildMode, iTarget):

	theProjectPath, theProjectFilename = os.path.split(iProjectRelativePath)
	
		#Change working dir
	os.chdir(os.path.abspath(theProjectPath))
	
	theVSVersionStr = GetVisualStudioVersionFromSLN(theProjectFilename)
	if len(theVSVersionStr) == 0:
		print "ERROR: Unable to determine visual studio version from SLN !"
		sys.exit(2)
	
	theMSBuildFullPath = getMSBuildPath(theVSVersionStr)
	if len(theMSBuildFullPath) == 0:
		print "ERROR: Unable to determine MSBuild path for version: " + theVSVersionStr
		sys.exit(3)

	if iTarget == None:
		iTarget = "Rebuild"
		
	theConfiguration = "Configuration=" + iProjectBuildMode
	theConfigurationPlatform = iProjectBuildMode.split('|')
	if len(theConfigurationPlatform) > 1:
		theConfiguration = "Platform=\"" + theConfigurationPlatform[1] + "\";Configuration=\"" + theConfigurationPlatform[0] + "\""

	theCmd = theMSBuildFullPath + " " + theProjectFilename + " /t:" + iTarget + " /p:" + theConfiguration
	
	return build_utils.executeCommand(theCmd, "MSBuild v" + theVSVersionStr )
	
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
	