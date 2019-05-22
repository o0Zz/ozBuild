import sys, os
import build_iar, build_visualstudio, build_embarcadero, build_keil, build_makefile, build_gradle, build_node, build_pro, version, glob

#------------------------------------------------------

kProjectExentionList = [
	[ '.ewp', build_iar ],
	[ '.sln', build_visualstudio ],
	[ '.csproj', build_visualstudio ],
	[ '.vcproj', build_visualstudio ],
	[ '.dproj', build_embarcadero ],
	[ '.uvprojx,.uvproj', build_keil ],
	[ 'Makefile', build_makefile ],
	[ '.gradle', build_gradle ],
	[ 'package.json', build_node ],
	[ '.pro', build_pro ]
]

#------------------------------------------------------

def Usage():
	print ("")
	print ("This script will automatically detect the project you want to build and will invoke the builder with common parameters")
	print ("If you need some specific parameters, please invoke build_* script instead")
	print ("")
	print ("Usage:")
	print ("    " + sys.argv[0] + " <Project FullPath IAR/VS/EMBARCADERO/KEIL/Makefile/GRADLE/NodeJS> [Debug|Release] [Build|Rebuild|Clean]")
	print ("")
	print ("i.e:")
	print ("    " + sys.argv[0] + " \"MyProject.ewp\" Debug")
	print ("")
	sys.exit(1)
	
#------------------------------------------------------

if __name__ == '__main__':
	if len(sys.argv) < 2:
		Usage() 
	
	theProjectRelativePath 						= os.path.expandvars(sys.argv[1])
	theProjectBuildMode							= None
	theProjectTarget							= None
	if len(sys.argv) > 2:
		theProjectBuildMode 					= sys.argv[2]
	if len(sys.argv) > 3:
		theProjectTarget 						= sys.argv[3]
	theProjectPath, theProjectFilename 			= os.path.split(theProjectRelativePath)

	print ("-----------------------------------------------------------------------------")
	print ("ENVIRONMENT VARIABLES:")
	print ("-----------------------------------------------------------------------------")
	for key in os.environ.keys():
		print ("%30s %s" % (key, os.environ[key]))
	print ("-----------------------------------------------------------------------------")
	sys.stdout.flush()
	
	version.FindAndReplaceVersionFiles(theProjectPath, "build_version.h")
	version.FindAndReplaceVersionFiles(theProjectPath, "build_version.java")
	version.FindAndReplaceVersionFiles(theProjectPath, "build_version.cs")
	version.FindAndReplaceVersionFiles(theProjectPath, "build_version.json")
	version.FindAndReplaceVersionFiles(theProjectPath, "build.gradle")
	version.FindAndReplaceVersionFiles(theProjectPath, "*.nuspec")
	
	theRetCode = 3
	for project in kProjectExentionList:
		theExtensions = project[0].split(',')
		theScript = project[1]
		for theExtension in theExtensions:
			if theProjectFilename.lower().find(theExtension.lower()) != -1:
				if theRetCode != 0:
					theRetCode = 2
				for theProjectAbsPath in glob.glob(os.path.abspath( theProjectRelativePath )):
					theRetCode = 0
					try:
						theRet = theScript.Build(theProjectAbsPath, theProjectBuildMode, theProjectTarget)
						if theRet != 0:
							print ("*** Build return code(1): " + str(theRet))
							sys.exit(theRet)
					except Exception as e:
						print ("*** Build exception: " + str(e))
						sys.exit(2)
	if theRetCode == 3:
		print ("*** Build Error: Unable to determine project type from filename: " + theProjectFilename)
	elif theRetCode == 2:
		print ("*** Build Error: Unable to find project to build in: " + theProjectRelativePath)
	else:
		print ("*** Build SUCCESS !")

	sys.exit(theRetCode)

