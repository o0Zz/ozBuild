import zipfile, os, sys, glob, fnmatch

#------------------------------------------------------

def Usage(anExitCode):
	print "Usage:"
	print "    " + sys.argv[0] + " <output.zip> [OPTIONS]"
	print "Options:"
	print "    -h:                          This help screen"
	print "    -root <Directory root path>: Where is located zip root"
	print "    -include <Included pattern>: A comma separated included pattern (Dirs/files)"
	print "    -exclude <Excluded pattern>: A comma separated excluded pattern (Dirs/files)"
	print ""
	print "i.e:"
	print "    " + sys.argv[0] + " \"MyProject\\Win64\\Release\output.zip\" -root \"MyProject\\Win64\\Release\" -include \".\\*.exe,*.\\css\""
	print ""
	sys.exit(anExitCode)
	
#------------------------------------------------------

def SplitFolders(aPath):
	folders = []
	while 1:
		aPath, folder = os.path.split(aPath)

		if folder != "":
			folders.append(folder)
		else:
			if aPath != "":
				folders.append(aPath)

			break

	folders.reverse()
	return folders
	
#------------------------------------------------------

def ZipFile(aPath, aZip, anIncludePattern, anExcludePattern):
	lFolderList = SplitFolders(aPath)

	thefIncludeFound = False
	for theInc in anIncludePattern:
		if (fnmatch.fnmatch(aPath, theInc)) or (os.path.basename(aPath) == theInc) or (theInc in lFolderList) or (os.path.abspath(theInc) == os.path.abspath(aPath)):
			thefIncludeFound = True
			break

	for theExclude in anExcludePattern:
		if (fnmatch.fnmatch(aPath, theExclude)) or (os.path.basename(aPath) == theExclude) or (theExclude in lFolderList):
			thefIncludeFound = False
			break
	
	if thefIncludeFound:
		print "Zipping " + os.path.relpath(aPath)
		aZip.write(aPath, os.path.relpath(aPath), compress_type=zipfile.ZIP_DEFLATED)
	else:
		print "Ignoring " + os.path.relpath(aPath)
		
#------------------------------------------------------

def ZipDir(aPath, aZip, anIncludePattern, anExcludePattern):
	for root, dirs, files in os.walk(aPath):
		for file in files:
			ZipFile(os.path.join(root, file), aZip, anIncludePattern, anExcludePattern)
	
#------------------------------------------------------

if __name__ == '__main__':

	if len(sys.argv) < 2:
		Usage(1) 
	
	theOutputZipPath 			= os.path.expandvars(sys.argv[1])	
	theExcludePattern 			= []
	theIncludePattern			= []
	theRoot 					= ""
	
	try:
		theZipFile = zipfile.ZipFile(theOutputZipPath, "w")
	except:
		print "*** Error: Unable to open zip file: " + os.path.abspath(theOutputZipPath)
		sys.exit(1)

	#Parse parameters
	i = 2
	while i < len(sys.argv):
		if sys.argv[i][0] == '-': #Option ?
			if sys.argv[i] == '-h':
				Usage(0)
			elif sys.argv[i] == '-root' and len(sys.argv) > i+1:
				i = i + 1
				theRoot = sys.argv[i]
			elif sys.argv[i] == '-include' and len(sys.argv) > i+1:
				i = i + 1
				theIncludePattern = sys.argv[i].split(",")
			elif sys.argv[i] == '-exclude' and len(sys.argv) > i+1:
				i = i + 1
				theExcludePattern = sys.argv[i].split(",")
			else:
				print "Invalid parameter: " + sys.argv[i]
				Usage(1)
		else: #File list
			theIncludePattern.append(sys.argv[i])
			
		i = i + 1
		
	if len(theIncludePattern) == 0:
		theIncludePattern = ["*.*"]
	
	if len(theRoot)	== 0:
		theRoot, theZipFilename = os.path.split(theOutputZipPath)
	
	print theIncludePattern

		#Change working dir
	theAbsoluteRootFolder = os.path.abspath(theRoot)
	os.chdir(theAbsoluteRootFolder)
	print "Working directory: " + theAbsoluteRootFolder
	
	ZipDir(theAbsoluteRootFolder, theZipFile, theIncludePattern, theExcludePattern)