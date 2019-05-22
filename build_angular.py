import sys, os, subprocess, version, build_utils

#------------------------------------------------------

def Usage():
	print "Usage: "
	print "     " +sys.argv[0] + " <Full path to angular js project>"
	print ""
	print "i.e:"
	print "      " + sys.argv[0] + " \"MyAngularProject/\""
	sys.exit(1)

#------------------------------------------------------

def Build(iProjectRelativePath, iProjectBuildMode, iTarget):

		#Change working dir
	os.chdir(os.path.abspath(iProjectRelativePath))
	
	os.environ["PATH"] = os.environ["PATH"] + ";" + os.environ["APPDATA"] + "\\npm"
	
	theRet = build_utils.executeCommand("npm install -g angular-cli", "angular-cli", True)
	if theRet != 0:
		return theRet
	
	return build_utils.executeCommand("ng build --prod --env=prod", "NG", True)
	
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
	