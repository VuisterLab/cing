"""
python -u $CINGROOT/python/cing/Scripts/validateCyanaProject.py cyanaProjectDir
"""
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from glob import glob

class ValidateCyanaProject():
    def __init__(self, cyanaProjectDir, htmlOnly=False, doWhatif=True, doProcheck=True,
                 pdbConvention=CYANA2, restraintsConvention=CYANA2):
        """Retrieves all needed info from path"""

        self.htmlOnly               = htmlOnly # default is False but enable it for faster runs without some actual data.
        self.doWhatif               = doWhatif # disables whatif actual run
        self.doProcheck             = doProcheck
        self.pdbConvention          = pdbConvention
        self.restraintsConvention   = restraintsConvention

        if not ( os.path.exists(cyanaProjectDir) and os.path.isdir(cyanaProjectDir)):
            NTexit("Given path is not an existing directory: [%s]" % cyanaProjectDir )
        directory, basename, _extension = NTpath(cyanaProjectDir)
        if os.chdir(cyanaProjectDir):
            NTexit("Failed to change to directory: [%s]" % directory )
        self.entryId = basename
        NTmessage('Setting entry to: [%s]' % self.entryId )

    def validate(self):
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
                NTwarning( "Converter for cyana also needs a seq file before a prot file can be imported" )
        if peakList:
#            NTdebug('found peakList: [%s]' % peakList)
            kwds[ 'peakFiles' ] = stripExtensions( peakList )
        if project.cyana2cing(cyanaDirectory=".", convention=self.restraintsConvention,
                        copy2sources = True, **kwds ) == None:
            NTexit('Failed to project.cyana2cing')
        project.save()

        if not project.validate(htmlOnly=self.htmlOnly,
                            doProcheck = self.doProcheck,
                            doWhatif=self.doWhatif ):
            NTerror('Failed to project.validate')



if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    v = ValidateCyanaProject( sys.argv[1] )
    if v.validate():
        NTerror('Failed to ValidateCyanaProject.validate')

