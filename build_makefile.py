import sys, os, subprocess, build_utils

#------------------------------------------------------

def Usage():
	print "Usage: "
	print "     " +sys.argv[0] + " <Makefile full path> [Target]"
	print ""
	print "i.e:"
	print "      " + sys.argv[0] + " \"MyMakefileProject/Makefile\""
	sys.exit(1)
	
#------------------------------------------------------

def Build(iProjectRelativePath, iProjectBuildMode, iTarget):
	theProjectPath, theProjectFilename = os.path.split(iProjectRelativePath)
	
		#Change working dir
	os.chdir(os.path.abspath(theProjectPath))

		#Force to rebuild project (Clean project first)
	build_utils.executeCommand("make -f " + theProjectFilename + " clean", "Makefile", True, True)
	
		#Build project
	theCmd = "make -f " + theProjectFilename
	if iProjectBuildMode != None:
		theCmd = theCmd + " " + iProjectBuildMode
	
	return build_utils.executeCommand(theCmd, "Makefile", True, True)
	
#------------------------------------------------------

if __name__ == '__main__':
	if len(sys.argv) < 2:
		Usage() 
		
	theProjectRelativePath 		= os.path.expandvars(sys.argv[1])
	
	theProjectBuildMode 		= None
	if len(sys.argv) > 2:
		theProjectBuildMode 	= sys.argv[2]
		
	theTarget 					= None
	if len(sys.argv) > 3:
		theTarget 				= sys.argv[3]
		
	theRet = Build(theProjectRelativePath, theProjectBuildMode, theTarget)
	sys.exit( theRet )
	
	