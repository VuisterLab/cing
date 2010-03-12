"""
Reads a Regine .pkr peak list.

Example input is in
$CINGROOT/Tests/data//org/1brv/brsvg.pkr

Format input:
# .pkr
 1,1,2,99,1,2,'Jurgen','20-HG1|20-HN'
 2.340,0.050,0.041,9.049,0.026,0.026,2.000
 26
 0
 0.0000E+00,8.0715E+06
 20,5,20,1
"""
from cing.Libs.NTutils import Lister
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import readTextFromFile
from cing.core.classes import Peak
from cing.core.classes import PeakList
from cing.core.constants import XPLOR

class Regine(Lister):

    def __init__(self, project, offSet = 0, dimension = 2 ):
        self.project = project
        self.offSet = offSet
        self.dimension = dimension
        self.chainName = None # set in readPeakList

    def readPeakList(self, fn, status='keep'):
        """ Six lines per peak
 1,1,2,99,1,2,'Jurgen','20-HG1|20-HN'
                       ^ assignment info
 2.340,0.050,0.041,9.049,0.026,0.026,2.000
 ^ Chemical shift 1
                   ^ Chemical shift 2
 26
 0
 0.0000E+00,8.0715E+06
            ^ peak volume
 20,5,20,1
"""
        NTmessage("Reading: %s" % fn)
        txt = readTextFromFile(fn)

        _path,name,_ext = NTpath( fn )
        peakList = PeakList( name=name, status=status )

        splitLineList = txt.splitlines()
        # Init here after some content is added; can't be done in constructor of class.
        self.chainName = self.project.molecule.allChains()[0].name

        i = 0
        while i < len(splitLineList):
#            NTdebug("Working on line %d (line 1 in block)" % i)
# 1,1,2,99,1,2,'Jurgen','20-HG1|20-HN'
#                       ^ assignment info
            line = splitLineList[i]
            wordList = line.split(',')
            assignmentListStr = wordList[ - 1]
            assignmentListStr = assignmentListStr.replace("'", '')
            barIdx = assignmentListStr.find('|')
            resonances = []
            if barIdx > 0:
                assignmentListStrList = assignmentListStr.split('|')
                for loc in assignmentListStrList:
                    resId, atomName = loc.split('-')
                    resId = int(resId)
                    resonanceListAtomName = self.getResonanceListForLoc(resId, atomName)
                    resonances.append(resonanceListAtomName)

            # work on line 2 for peak positions
# 2.340,0.050,0.041,9.049,0.026,0.026,2.000
# ^ Chemical shift 1
#                   ^ Chemical shift 2
            i += 1
            line = splitLineList[i]
#            NTdebug("Working on CS line 2: [%s]" % line)
            wordList = line.split(',')
            peakPosition1 = float(wordList[0])
            peakPosition2 = float(wordList[3])
            positions = [peakPosition1, peakPosition2]

            # work on line 5 for peak volume
            i += 3
            line = splitLineList[i]
#            NTdebug("Working on volume line 5 (%d) : [%s]" % (i,line))
            wordList = line.split(',')
            wordList = line.split(',')
            volume = float(wordList[ - 1])

            peak = Peak(self.dimension,
                  positions = positions,
                  volume = volume,
                  resonances = resonances)

            # Use the Lister class for a string representation.
#            NTdebug("Found peak: %r" % peak)
            peakList.append( peak )
            # skip to next line 1
            i += 2
        return peakList


    def getResonanceListForLoc(self, resId, atomName):
        resNum = resId + self.offSet
        chainName = self.chainName
        nameTuple = (XPLOR, chainName, resNum, atomName)
        atom = self.project.molecule.decodeNameTuple(nameTuple)
#        NTdebug("atom = decodeNameTuple(XPLOR, chainName, resNum, atomName): %s = %s %s %s [%s]" % (
#                 atom, XPLOR, chainName, resNum, atomName))
        if not atom:
#            NTwarning("Failed to find loc: [%s],[%s],[%s]" % (resId, resNum, atomName)) # TODO check; message disabled for improving other debugging.
            return None
        return atom.resonances()

#-----------------------------------------------------------------------------
def importReginePeakList(project, fn, offSet = 0, status='keep'):
    offSet = 157 # specific to 1brv
    r = Regine(project, offSet = offSet)
    NTmessage("regine: %r" % r)
    peakList = r.readPeakList(fn)
    project.peaks.append( peakList )
    project.addHistory( 'Imported Xeasy peaks from "%s"' % fn )


# register the functions
methods = []
saves = []
restores = []
exports = [(importReginePeakList, None)]
