import sys, os, datetime, re, subprocess, fnmatch

#------------------------------------------------------

def RemoveReadOnlyFlag(filename):
	if os.path.exists(filename) and not os.access(filename, os.W_OK):
		print "Removing read only flag on: \"" + filename + "\""
		os.chmod(filename, 0666) #Read / Write
		
#------------------------------------------------------

	#This function will return the version path of a project
	#i.e: 	Input: 	C:\FullPath\1.1\MyProject
	#		Return: C:\FullPath\1.1\
def GetVersionRootFolder(path):
	while 1:
		path, folder = os.path.split(path)

		if folder == "":
			break
			
		if re.match("^[0-9.]+$", folder):
			return os.path.join(path, folder)
			
	return ""
	
#------------------------------------------------------

	#Extract the version from a path
def ExtractVersion(path):
	theMajor = 0
	theMinor = 0
	theMicro = 255
	
	theRootFolder = GetVersionRootFolder(path)
	if len(theRootFolder) > 0:
		path, version = os.path.split(theRootFolder)
		theVersionSplit = version.split(".")
		if len(theVersionSplit) > 0:
			theMajor = int(theVersionSplit[0])
		if len(theVersionSplit) > 1:
			theMinor = int(theVersionSplit[1])
		if len(theVersionSplit) > 2:
			theMicro = int(theVersionSplit[2])

	return theMajor, theMinor, theMicro
	
#------------------------------------------------------

	#Extract the P4 revision
def ExtractRevision(path):
	theRootFolder = GetVersionRootFolder(path)
	
	#Step 1: We try to get revision from jenkins P4_CHANGELIST
	if "P4_CHANGELIST" in os.environ:
		return os.environ["P4_CHANGELIST"]
	
	#Step2: If we can't get it, we try to extract revision from command line
	print "Extracting revision from: " + theRootFolder
	theCmd = "p4 changes -m1 " + theRootFolder + "/...#have"
	print theCmd

		#This call will return "Change 3302 on 2016/04/12 by t.quemerais@TQS_Sandbox '[OWS3] Update project to IAR 5."
	p = subprocess.Popen(theCmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	output, err = p.communicate()

	print output, err

	theWords = output.split(' ')
	if len(theWords) > 1:
		return theWords[1]
	
	return "0"
	
#------------------------------------------------------

	#Generate a C/C++ header file
def GenerateVersionHeader(iFileFullPath, iMajor, iMinor, iMicro, iRevision, iDateTime):
	RemoveReadOnlyFlag(iFileFullPath)
	
	print "Opening: " + str(iFileFullPath)
	FD = open(iFileFullPath, "wb")
	if not FD:
		return

	FD.write("#ifndef _BUILD_VERSION_H_\r\n")
	FD.write("#define _BUILD_VERSION_H_\r\n")
	FD.write("\r\n")
	FD.write("#define BUILD_VERSION_MAJOR\t\t\t" 	+ str(iMajor) + "\r\n")
	FD.write("#define BUILD_VERSION_MINOR\t\t\t" 	+ str(iMinor) + "\r\n")
	FD.write("#define BUILD_VERSION_MICRO\t\t\t" 	+ str(iMicro) + "\r\n")
	FD.write("#define BUILD_VERSION_REVISION\t\t" 	+ str(iRevision) + "\r\n") 
	FD.write("#define BUILD_VERSION_MINIMAL_STR\t\""+ str(iMajor) + "." + str(iMinor) + "." + str(iMicro) + "\"\r\n")
	FD.write("#define BUILD_VERSION_FULL_STR\t\t\""	+ str(iMajor) + "." + str(iMinor) + "." + str(iMicro) + " r" + str(iRevision) + "\"\r\n")
	FD.write("\r\n")
	FD.write("#define BUILD_DATE_YEAR\t\t" 	+ str(iDateTime.year) + "\r\n")
	FD.write("#define BUILD_DATE_YEAR_MIN\t" 	+ str(iDateTime.year)[2:] + "\r\n")
	FD.write("#define BUILD_DATE_MONTH\t\t" 	+ str(iDateTime.month) + "\r\n")
	FD.write("#define BUILD_DATE_DAY\t\t" 	+ str(iDateTime.day) + "\r\n")
	FD.write("#define BUILD_DATE_HOUR\t\t" 	+ str(iDateTime.hour) + "\r\n")
	FD.write("#define BUILD_DATE_MIN\t\t" 	+ str(iDateTime.minute) + "\r\n")
	FD.write("#define BUILD_DATE_SEC\t\t" 	+ str(iDateTime.second) + "\r\n")
	FD.write("#define BUILD_DATE_STR\t\t\"" 	+ iDateTime.strftime('%Y-%m-%d %H:%M:%S') + "\"\r\n")
	FD.write("\r\n")
	FD.write("#endif\r\n")
	FD.close()
	
#------------------------------------------------------

	#Generate a C# .NET file
def GenerateVersionCS(iFileFullPath, iMajor, iMinor, iMicro, iRevision, iDateTime):
	RemoveReadOnlyFlag(iFileFullPath)
	
	print "Opening: " + str(iFileFullPath)
	FD = open(iFileFullPath, "wb")
	if not FD:
		return

	FD.write("using System.Reflection;\r\n")
	FD.write("[assembly: AssemblyVersion(\"" + str(iMajor) + "." + str(iMinor) + "." + str(iMicro) + "." + str(iRevision) + "\")]\r\n")
	FD.write("[assembly: AssemblyFileVersion(\"" + str(iMajor) + "." + str(iMinor) + "." + str(iMicro) + "." + str(iRevision) + "\")]\r\n")
	FD.write("\r\n")
	FD.close()
	
#------------------------------------------------------

	#Generate a Java file
def GenerateVersionJava(iFileFullPath, iMajor, iMinor, iMicro, iRevision, iDateTime):
	lPackageLine = "package com.company.XXX;"
	RemoveReadOnlyFlag(iFileFullPath)

	print "Opening: " + str(iFileFullPath)
	
	FD = open(iFileFullPath, "rb")
	if not FD:
		return
	lLines = FD.readlines()
	FD.close()
	
	for line in lLines:
		if line.find("package") != -1:
			lPackageLine = line

	FD = open(iFileFullPath, "wb")
	if not FD:
		return

	FD.write(lPackageLine + "\r\n")
	FD.write("\r\n")
	FD.write("public class BuildVersion {\r\n")
	FD.write("\r\n")
	FD.write("\tpublic static final int BUILD_VERSION_MAJOR =\t\t\t" 	+ str(iMajor) + ";\r\n")
	FD.write("\tpublic static final int BUILD_VERSION_MINOR =\t\t\t" 	+ str(iMinor) + ";\r\n")
	FD.write("\tpublic static final int BUILD_VERSION_MICRO =\t\t\t" 	+ str(iMicro) + ";\r\n")
	FD.write("\tpublic static final int BUILD_VERSION_REVISION =\t\t" 	+ str(iRevision) + ";\r\n") 
	FD.write("\tpublic static final String BUILD_VERSION_MINIMAL_STR =\t\""+ str(iMajor) + "." + str(iMinor) + "." + str(iMicro) + "\";\r\n")
	FD.write("\tpublic static final String BUILD_VERSION_FULL_STR =\t\t\""	+ str(iMajor) + "." + str(iMinor) + "." + str(iMicro) + " r" + str(iRevision) + "\";\r\n")
	FD.write("\r\n")
	FD.write("\tpublic static final int BUILD_DATE_YEAR =\t\t" 	+ str(iDateTime.year) + ";\r\n")
	FD.write("\tpublic static final int BUILD_DATE_YEAR_MIN =\t" 	+ str(iDateTime.year)[2:] + ";\r\n")
	FD.write("\tpublic static final int BUILD_DATE_MONTH =\t\t" 	+ str(iDateTime.month) + ";\r\n")
	FD.write("\tpublic static final int BUILD_DATE_DAY =\t\t" 	+ str(iDateTime.day) + ";\r\n")
	FD.write("\tpublic static final int BUILD_DATE_HOUR =\t\t" 	+ str(iDateTime.hour) + ";\r\n")
	FD.write("\tpublic static final int BUILD_DATE_MIN =\t\t" 	+ str(iDateTime.minute) + ";\r\n")
	FD.write("\tpublic static final int BUILD_DATE_SEC =\t\t" 	+ str(iDateTime.second) + ";\r\n")
	FD.write("\tpublic static final String BUILD_DATE_STR =\t\t\"" 	+ iDateTime.strftime('%Y-%m-%d %H:%M:%S') + "\";\r\n")
	FD.write("}")
	FD.write("\r\n")
	FD.close()
	
#------------------------------------------------------

	#Generate a Gradle version
def GenerateGradleVersion(iFileFullPath, iMajor, iMinor, iMicro, iRevision, iDateTime):
	RemoveReadOnlyFlag(iFileFullPath)

	print "Opening: " + str(iFileFullPath)
	
	FD = open(iFileFullPath, "rb")
	if not FD:
		return
	lLines = FD.readlines()
	FD.close()
	
	FD = open(iFileFullPath, "wb")
	for line in lLines:
		if line.find("versionName") != -1:
			FD.write("versionName '" + str(iMajor) + "." + str(iMinor) + "." + str(iMicro) + "'\r\n")
		else:
			FD.write(line)
	FD.close()
	
#------------------------------------------------------

	#Generate a Nuspec version
def GenerateNuspecVersion(iFileFullPath, iMajor, iMinor, iMicro, iRevision, iDateTime):
	RemoveReadOnlyFlag(iFileFullPath)

	print "Opening: " + str(iFileFullPath)
	
	FD = open(iFileFullPath, "rb")
	if not FD:
		return
	lLines = FD.readlines()
	FD.close()
	
	FD = open(iFileFullPath, "wb")
	for line in lLines:
		if line.find("<version>") != -1:
			FD.write("<version>" + str(iMajor) + "." + str(iMinor) + "." + str(iMicro) + "." + str(iRevision) + "</version>\r\n")
		else:
			FD.write(line)
	FD.close()
	
#------------------------------------------------------

	#Generate a JSON version
def GenerateJSONVersion(iFileFullPath, iMajor, iMinor, iMicro, iRevision, iDateTime):
	RemoveReadOnlyFlag(iFileFullPath)
	
	print "Opening: " + str(iFileFullPath)
	FD = open(iFileFullPath, "wb")
	if not FD:
		return

	FD.write('{\r\n')
	FD.write('	"build_version" :\r\n')
	FD.write('	{\r\n')
	FD.write('		"major" :			' + str(iMajor) + ',\r\n')
	FD.write('		"minor" :			' + str(iMinor) + ',\r\n')
	FD.write('		"micro" :			' + str(iMicro) + ',\r\n')
	FD.write('		"revision" : 		' + str(iRevision) + ',\r\n') 
	FD.write('		"minimal_str" :		"' + str(iMajor) + '.' + str(iMinor) + '.' + str(iMicro) + '",\r\n')
	FD.write('		"full_str" :		"' + str(iMajor) + '.' + str(iMinor) + '.' + str(iMicro) + ' r' + str(iRevision) + '",\r\n')
	FD.write('\r\n')
	FD.write('		"date_year" :		' + str(iDateTime.year) + ',\r\n')
	FD.write('		"date_year_min" :	' + str(iDateTime.year)[2:] + ',\r\n')
	FD.write('		"date_month" :		' + str(iDateTime.month) + ',\r\n')
	FD.write('		"date_day" :		' + str(iDateTime.day) + ',\r\n')
	FD.write('		"date_hour" :		' + str(iDateTime.hour) + ',\r\n')
	FD.write('		"date_min" :		' + str(iDateTime.minute) + ',\r\n')
	FD.write('		"date_sec" :		' + str(iDateTime.second) + ',\r\n')
	FD.write('		"date_str" :		"' + iDateTime.strftime('%Y-%m-%d %H:%M:%S') + '"\r\n')
	FD.write('	}\r\n')
	FD.write('}\r\n')
	
	FD.close()
	
#------------------------------------------------------

kGenerateFunctionList = [
	[ '.h', GenerateVersionHeader ],
	[ '.cs', GenerateVersionCS ],
	[ '.java', GenerateVersionJava ],
	[ '.gradle', GenerateGradleVersion ],
	[ '.json', GenerateJSONVersion ],
	[ '.nuspec', GenerateNuspecVersion ],
]

def FindAndReplaceVersionFiles(iPath, iVersionFilename):
	theAbsPath = os.path.abspath(iPath)
	theFullPath = os.path.join(theAbsPath, iVersionFilename)
	
	theRootFolder = GetVersionRootFolder(theAbsPath)
	theRevision = ExtractRevision(theAbsPath)
	theDateTime = datetime.datetime.now()
	
	thefFoundFiles = False
	
	if len(theRootFolder) == 0:
		print "*** WARNING: Unable to determine root folder, so we can't dermine version and can't patch osVersion*"
		return False
		
	print "Searching '" + iVersionFilename + "' in '" + theRootFolder + "'"
	
		#Search files in the root folder of this project and replace all version files
	for root, dirnames, filenames in os.walk(theRootFolder):
		#Allow wildcard 
		theFiltered = fnmatch.filter(filenames, iVersionFilename)
		for filename in theFiltered:
			for theGenerateFunctionExt in kGenerateFunctionList:
				theExtention = theGenerateFunctionExt[0]
				theGenerateFunction = theGenerateFunctionExt[1]
				if filename.endswith(theExtention):
					theMajor, theMinor, theMicro = ExtractVersion(root)
					theGenerateFunction(os.path.join(root, filename), theMajor, theMinor, theMicro, theRevision, theDateTime) #Invoke the correct generate function depending to the file extension
					thefFoundFiles = True
						
	return thefFoundFiles
	
	
#------------------------------------------------------

def Usage():
	print "Usage: "
	print "     " +sys.argv[0] + " <version file path>"
	print ""
	print "i.e:"
	print "      " + sys.argv[0] + " \"MyProject/build_version.h\""
	sys.exit(1)
	
#------------------------------------------------------

if __name__ == '__main__':

	if len(sys.argv) <= 1:
		Usage()
		sys.exit(1)

	theVersionFilePath = sys.argv[1]
	thePath, theVersionFilename  = os.path.split(theVersionFilePath)
	if not FindAndReplaceVersionFiles(thePath, theVersionFilename):
		print "ERROR: Unable to find version filename: " + str(theVersionFilePath)
		sys.exit(2)
		