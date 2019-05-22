import sys, os, subprocess, version, build_utils

#------------------------------------------------------

def Usage():
	print "Usage: "
	print "     " +sys.argv[0] + " <build.gradle full path> [Target]"
	print ""
	print "i.e:"
	print "      " + sys.argv[0] + " \"MyAndroidProject/build.gradle\""
	sys.exit(1)

#------------------------------------------------------
#Allow to set android sdk path
def GenerateLocalProperties(iFileFullPath):
	version.RemoveReadOnlyFlag(iFileFullPath)
	
	print "Opening: " + str(iFileFullPath)
	FD = open(iFileFullPath, "wb")
	if not FD:
		return

	if os.name == "nt":
		FD.write("sdk.dir=C:\\\\Users\\\\" + os.getenv('username') + "\\\\AppData\\\\Local\\\\Android\\\\Sdk\r\n")
	else:
		FD.write("sdk.dir=/opt/android-sdk-linux/\r\n")
	FD.close()

#------------------------------------------------------

def Build(iProjectRelativePath, iProjectBuildMode, iTarget):
	theProjectPath, theProjectFilename = os.path.split(iProjectRelativePath)
	
		#Change working dir
	os.chdir(os.path.abspath(theProjectPath))

	GenerateLocalProperties("local.properties")
	
	if os.name == "nt":
		theCmd = "gradlew.bat"
		theCloseFds = False		
	else:
		if os.path.exists("./gradlew"):
			os.chmod("./gradlew", 0555) #Read / Execution
		theCmd = "./gradlew"
		theCloseFds = True
		
	if iProjectBuildMode != None:
		theCmd = theCmd + " " + iProjectBuildMode
		
	return build_utils.executeCommand(theCmd, "Gradle", True, theCloseFds)
	
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
	
	