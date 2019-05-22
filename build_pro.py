###############################################################################################################################################
# Note: requires the following environment variables to be defined:
#	- QTDIR: corresponds to the path where qmake.exe can be found. Should end with trailing '\'
#			 Ensure that if you are compiling for msvc, the qmake.exe is from a msvc Qt build!!!
#	- VS140COMNTOOLS: this variable is created when you install visual studio (make sure you checked the tools component during installation)
###############################################################################################################################################

import sys, os, subprocess, build_utils, version, fnmatch
	
#------------------------------------------------------

def Usage():
	print( "Usage: ")
	print( "     " +sys.argv[0] + " <.pro full path> <Configuration>")
	print( "")
	print( "     Configuration:")
	print( "                    release|makespec")
	print( "                    debug|makespec")
	print( "")
	print( "i.e:")
	print( "      " + sys.argv[0] + " \"MyProject.pro release|win32-msvc2015")
	print( "      " + sys.argv[0] + " \"MyProject..pro release|win32-win32-g++")
	sys.exit(1)

#------------------------------------------------------	
def GetQmakePath():
	qmakePath = os.environ.get('QTDIR')
	if qmakePath == None:
		print( "ERROR: QTDIR environment variable is not defined")
		sys.exit(6)
	else:
		if not os.path.exists(qmakePath):
			print( "ERROR: QTDIR environment variable is not valid: " + qmakePath)
			sys.exit(7)
		else:
			return os.environ['QTDIR']

#------------------------------------------------------
def GetVsDevCmdBat():
	vsDevCmdBatPath = os.environ.get('VS140COMNTOOLS')
	if vsDevCmdBatPath == None:
		print( "ERROR: VS140COMNTOOLS environment variable is not defined")
		sys.exit(8)
	else:
		if not os.path.exists(vsDevCmdBatPath):
			print( "ERROR: VS140COMNTOOLS environment variable is not valid: " + vsDevCmdBatPath)
			sys.exit(9)
		else:
			return os.environ['VS140COMNTOOLS']

#------------------------------------------------------

def Build(iProjectRelativePath, iProjectBuildMode, iTarget):

	theProjectPath, theProjectFilename = os.path.split(iProjectRelativePath)
	
	splitBuildMode = iProjectBuildMode.split("|")
	if len(splitBuildMode) != 2:
		print( "ERROR: Configuration string invalid: " + iProjectBuildMode)
		Usage() 
		sys.exit(6)
	
	debugReleaseCmd = splitBuildMode[0]
	makeSpecs = splitBuildMode[1]

	#Change working dir
	print "Changing directory to project root path: " + os.path.abspath(theProjectPath)
	os.chdir(os.path.abspath(theProjectPath))

	theVsDevCmd = GetVsDevCmdBat() + "VsDevCmd.bat"
	theQmakeCmd = "\"" + GetQmakePath() + "qmake.exe\" \"" + iProjectRelativePath + "\" -r -spec " + makeSpecs + " CONFIG+=" + debugReleaseCmd + " -o Makefile"
	theNmakeCmd = "nmake.exe /A /f Makefile " + debugReleaseCmd

	#qmakeRes = build_utils.executeCommand(theQmakeCmd, "QMake step")
	qmakeRes = build_utils.executeCommand("\"" + theVsDevCmd + "\" & " + theQmakeCmd, "QMake step")
	if qmakeRes != 0 :
		return qmakeRes
		
	nmakeRes = build_utils.executeCommand("\"" + theVsDevCmd + "\" & " + theNmakeCmd, "NMake step")
	if nmakeRes != 0 :
		return nmakeRes
	
	return 0
	
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
	