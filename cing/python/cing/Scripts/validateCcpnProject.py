"""
python -u $CINGROOT/python/cing/Scripts/validateCcpnProject.py ccpnProjectDir
"""
from cing import verbosityDebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTexit
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import stripExtension
from cing.Libs.NTutils import stripExtensions
from cing.core.classes import Project
from glob import glob
import cing
import os
import sys

class ValidateCcpnProject():

    def validate(self, pathProject):
        if os.chdir(pathProject):
            pass
#            endError("Failed to change to dir: %s" % pathProject)

#        logToLog('Now in pathProject: ' + pathProject)

        project = Project( self.entryId )
        if project.removeFromDisk():
            NTexit("Failed to remove potentially old project: [%s]" % self.entryId )
        project = Project.open( self.entryId, status='new' )
        pdbList = glob('*.pdb')
        uplList = glob('*.upl')
        acoList = glob('*.aco')
        seqList = glob('*.seq')
        protList = glob('*.prot')
        peakList = glob('*.peaks')
        if not pdbList:
            NTexit("Failed to find a coordinate file with pdb extension" )
        pdbFile = pdbList[0]

        project.initPDB( pdbFile=pdbFile, convention = self.pdbConvention )

        kwds = {}
        if uplList:
            kwds[ 'uplFiles' ] = stripExtensions( uplList )
        if acoList:
            kwds[ 'acoFiles' ] = stripExtensions( acoList )
        if seqList:
            kwds[ 'seqFile' ] = stripExtension( seqList[0] )
        if protList:
            if seqList:
                kwds[ 'protFile' ] = stripExtension(protList[0])
            else:
                NTwarning( "Converter for ccpn also needs a seq file before a prot file can be imported" )
        if peakList:
#            NTdebug('found peakList: [%s]' % peakList)
            kwds[ 'peakFiles' ] = stripExtensions( peakList )
        if project.ccpn2cing(ccpnDirectory=".", convention=self.restraintsConvention,
                        copy2sources = True, **kwds ) == None:
            NTexit('Failed to project.ccpn2cing')
        project.save()

        if not project.validate(htmlOnly=self.htmlOnly,
                            doProcheck = self.doProcheck,
                            doWhatif=self.doWhatif ):
            NTerror('Failed to project.validate')



if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    v = ValidateCcpnProject( sys.argv[1] )
    if v.validate():
        NTerror('Failed to ValidateCcpnProject.validate')

