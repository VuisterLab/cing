from cing import __author__
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqCcpn import CCPN_LOWERCASE_STR

__author__ += 'Tim Stevens '

class RPF():
    def __init__(self, project):
        self.project = project


    def toRPFFile(self, fileName):
        """Return None on error"""

        nTmessage("starting toRPFFile")

        if not hasattr(self.project, CCPN_LOWERCASE_STR):
            nTdebug("Failed to find ccpn attribute project. Happens when no CCPN project was read first.") # TODO: change when cing to ccpn code works.
            return

        self.ccpnProject = self.project[ CCPN_LOWERCASE_STR ]
        if not self.ccpnProject:
            nTmessage("Failed to find ccpn project.")
            return

        ccpnFolder = self.project.ccpnFolder
        if ccpnFolder.endswith(".tgz") or ccpnFolder.endswith(".tar.gz"):
            head, tail = os.path.split(ccpnFolder)
            print head, tail
            baseNameList = tail.split('.')
            print "baseNameList %s" % baseNameList
            baseName = baseNameList[0]
            ccpnFolder = os.path.join(head, baseName)

        if not ccpnFolder:
            nTerror("No CCPN project folder defined thus no RPF export possible.")
            return

        if not os.path.exists(ccpnFolder):
            nTerror("No CCPN project folder available at [%s] thus no RPF export possible." % ccpnFolder)
            return

        inputDir, projectName = os.path.split(ccpnFolder)
        if inputDir == '':
            inputDir = '.'
        if projectName == '':
            nTerror("Failed to get ccpnProjectName from: ccpnProject.ccpnFolder [%s]" % self.ccpnProject.ccpnFolder)
            return

        if os.path.exists(fileName):
            os.unlink(fileName)

        if not fileName.endswith('.str'):
            nTerror("Failed to get a descent str file name from: [%s]" % fileName)
            return

        outputDir, tail = os.path.split(fileName)
        if outputDir == '':
            outputDir = '.'
        if tail == '':
            nTerror("Failed to get a descent str file name from: [%s]" % fileName)
            return

        scriptFileName = "$CINGROOT/python/cing/Scripts/FC/convertCcpn2RPF.py"
        logFileName = tail.replace(".str", "")
        logFileName += "_convertCcpn2RPF.log"
        convertProgram = ExecuteProgram("python -u %s" % scriptFileName,
                rootPath = outputDir, redirectOutputToFile = logFileName)
        nTmessage("Running Wim Vranken's FormatConverter from script %s" % scriptFileName )
        exitCode = convertProgram("%s %s %s" % (projectName, inputDir, fileName))
        if exitCode:
            nTerror("Failed convertProgram with exit code: " + repr(exitCode))
            return
        if not os.path.exists(fileName):
            nTerror("Failed to find result file [%s]" % fileName)
            return
        nTmessage("==> NMR-STAR project written at %s" % fileName)
        return True # Just to be explicit.