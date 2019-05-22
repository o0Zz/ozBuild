import sys, os, subprocess, version, fnmatch, build_utils

#------------------------------------------------------
	
def getRSVARSPath(iVSVersionStr):
	theRSVARSPaths = []
	theRSVARSPaths.append( build_utils.getRegistryValue("SOFTWARE\\Wow6432Node\\Embarcadero\\BDS\\" + iVSVersionStr + ".0", "RootDir") + "\\bin" )
	theRSVARSPaths.append( build_utils.getRegistryValue("SOFTWARE\\Embarcadero\\BDS\\" + iVSVersionStr + ".0", "RootDir") + "\\bin" )
	
	for theRSVARSPath in theRSVARSPaths:
		if os.path.isdir(theRSVARSPath):
			theRSVARSFullPath = os.path.join(theRSVARSPath, "rsvars.bat")
			if os.path.exists(theRSVARSFullPath):
				return theRSVARSFullPath

	return ""
	
#------------------------------------------------------

def Usage():
	print "Usage: "
	print "     " +sys.argv[0] + " <sln project full path> <Debug Win32|Release Win64>"
	print ""
	print "i.e:"
	print "      " + sys.argv[0] + " \"MyEmbarcaderoProject.sln\" \"Release Win64\""
	sys.exit(1)

#------------------------------------------------------

def GetEmbarcaderoVersionFromDPROJ(iProjectFilename):
	theProj = open(iProjectFilename, 'rb')
	theProjBuffer = theProj.read()
	theProj.close()
	
	theVersionIdx = theProjBuffer.find("<ProjectVersion>")
	if theVersionIdx == -1:
		print "ERROR: Unable to find ProjectVersion key in DPROJ"
		return ""
	
	theEOLIdx = theProjBuffer[theVersionIdx:].find("</ProjectVersion>")
	if theEOLIdx == -1:
		print "ERROR: Unable to find end of line in SLN"
		return ""
	
	theFullVersionStr = theProjBuffer[theVersionIdx + 16:theVersionIdx + theEOLIdx].strip()
		
	theMajorVersion = theFullVersionStr.split('.')[0]
	
	print "Proj Version found: " + theMajorVersion
	
	return theMajorVersion
	
#------------------------------------------------------

def Build(iProjectRelativePath, iProjectBuildMode, iTarget):
	
	theProjectPath, theProjectFilename = os.path.split(iProjectRelativePath)
	
		#Change working dir
	os.chdir(os.path.abspath(theProjectPath))

	theVersionStr = GetEmbarcaderoVersionFromDPROJ(theProjectFilename)
	if len(theVersionStr) == 0:
		print "ERROR: Unable to determine embarcadero version from dproj !"
		sys.exit(2)
	
	theVersionRSVars = str(int(theVersionStr) - 1)
	theRSVARSFullPath = getRSVARSPath(theVersionRSVars)
	if len(theRSVARSFullPath) == 0:
		print "ERROR: Unable to determine RSVARS Path for version: " + theVersionRSVars + "!"
		sys.exit(1)
	
	theBuildModeSplit = iProjectBuildMode.split(' ')
	theProjectConfig = theBuildModeSplit[0]
	
	theProjectPlatform = "Win32"
	if len(theBuildModeSplit) > 1:
		theProjectPlatform = theBuildModeSplit[1]
	
	theCmd = "cmd /C \"" + theRSVARSFullPath + "\" & msbuild.exe /v:Normal /t:Build /p:Config=" + theProjectConfig + " /p:Platform=" + theProjectPlatform +  " " + theProjectFilename
	
	return build_utils.executeCommand(theCmd, "MSBuild")
	
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
	