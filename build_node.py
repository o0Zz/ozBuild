import sys, os, subprocess, version, build_utils

#------------------------------------------------------

def Usage():
	print "Usage: "
	print "     " +sys.argv[0] + " <package.json>"
	print ""
	print "i.e:"
	print "      " + sys.argv[0] + " \"MyProject/package.json\""
	sys.exit(1)

#------------------------------------------------------

def Build(iProjectRelativePath, iProjectBuildMode, iTarget):
	theProjectPath, theProjectFilename = os.path.split(iProjectRelativePath)
	
		#Change working dir
	os.chdir(os.path.abspath(theProjectPath))

	return build_utils.executeCommand("npm install", "npm", True)
	
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
	