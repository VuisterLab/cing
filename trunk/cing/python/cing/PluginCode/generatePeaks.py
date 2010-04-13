"""
Adds methods to generate peaks

Methods:
    generatePeaks( project, experimentName, axisOrder=None, onlyAssigned = True, skipResidues = [] )

    listPredefinedExperiments()


----------- Experiment: CBCACONH -----------
dimensions: 3
axis: 'HN' or 'H'
axis: 'N'
axis: 'CA' or 'CB' or 'CACB'
----------- Experiment: CCH -----------
dimensions: 3
axis: 'C'
axis: 'C2' or 'CH'
axis: 'H'
----------- Experiment: CCONH -----------
dimensions: 3
axis: 'HN' or 'H'
axis: 'N'
axis: 'C'
----------- Experiment: HAHBCONH -----------
dimensions: 3
axis: 'HN' or 'H'
axis: 'N'
axis: 'HA' or 'HB' or 'HAHB'
----------- Experiment: HNCA -----------
dimensions: 3
axis: 'HN' or 'H'
axis: 'N'
axis: 'CA'
----------- Experiment: HNCACB -----------
dimensions: 3
axis: 'HN' or 'H'
axis: 'N'
axis: 'CA' or 'CB' or 'CACB'
----------- Experiment: HNCAHA -----------
dimensions: 3
axis: 'HN' or 'H'
axis: 'N'
axis: 'HA'
----------- Experiment: HNCOCA -----------
dimensions: 3
axis: 'HN' or 'H'
axis: 'N'
axis: 'CA'
----------- Experiment: CBCACONH -----------
dimensions: 3
axis: 'HN' or 'H'
axis: 'N'
axis: 'CA' or 'CB' or 'CACB'
----------- Experiment: HAHBCONH -----------
dimensions: 3
axis: 'HN' or 'H'
axis: 'N'
axis: 'HA' or 'HB' or 'HAHB'
----------- Experiment: N15_HSQC -----------
dimensions: 2
axis: 'HN' or 'H'
axis: 'N'

"""
#===========================================================================
# imports
#===========================================================================
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import sprintf
from cing.core.molecule import dots
from cing.core.molecule import translateTopology

#===========================================================================
# Dictionary with experiment names
expDict = NTdict()

#===========================================================================
# Baseclass for experiments
#===========================================================================

class ExperimentDef( dict ):
    """Base class for experiments"""
    global expdict

    name      = 'NoName'
    dimension = 0
    peaks     = []
    nuclei    = []

    def __init__( self, residue, axisOrder=None ):
        dict.__init__( self )
        self.residue = residue

        #define the nuclei
        for dim in range(self.dimension):
            for n in self.nuclei[dim]:
                self[n] = dim
            #end for
        #end for

        if (axisOrder):
            axis = axisOrder.strip().split(':')
            self.axisOrder = []
            for a in axis:
                if (a not in self):
                    NTerror('ERROR: axis "%s" not defined for experiment "%s"\n%s, using default\n',
                             a, self.name, str(self)
                           )
                    self.axisOrder = range( self.dimension )
                    break
                #end if
                self.axisOrder.append( self[a] )
            #end for
        else:
            self.axisOrder = range( self.dimension )
        #endif

        self.definePeaks()
    #end def

    def definePeaks( self ):
        """Method to be subclassed for different exps (if needed)
           It should define the peaks list
        """
        pass
    #end def

    def __next__( self ):
        return self
    #end def

    def __iter__( self ):
        for peak in self.peaks:
            atoms = translateTopology( self.residue, peak ).reorder( self.axisOrder )
            yield atoms
    #end def

    def __str__( self ):
        return sprintf('<Experiment: %s (%dD)>',self.name, self.dimension )
    #end def

    def describe( exp ):
        """Static method: ExperimentDef.describe( experiment )
        """
        s = sprintf('%s Experiment: %s %s\ndimensions: %d',
                       dots, exp.name, dots, exp.dimension
                      )
        for dim in range(exp.dimension):
            s = s + sprintf( '\naxis: %s', str(exp.nuclei[dim])[1:-1].replace(', ',' or ') )
        return s
    #end def
    describe = staticmethod(describe)
#end class


#===========================================================================
# Predefined experiments for generating peaks
#===========================================================================
class N15_HSQC( ExperimentDef ):
    name      = 'N15_HSQC'
    dimension = 2
    peaks     = [
                 [(0,'HN'),(0,'N')]
                ]
    nuclei    = [
                 ['HN','H'],
                 ['N'],
                ]
#end class
expDict['N15_HSQC'] = N15_HSQC

#===========================================================================

class HNCA( ExperimentDef ):
    name      = 'HNCA'
    dimension = 3
    peaks     = [
                 [(0,'HN'),(0,'N'),( 0,'CA')],  # Intra-residual CA peak
                 [(0,'HN'),(0,'N'),(-1,'CA')],  # Sequential CA peak
                ]
    nuclei    = [
                 ['HN','H'],
                 ['N'],
                 ['CA']
                ]
#end class
expDict['HNCA'] = HNCA

#===========================================================================

class HNCOCA( ExperimentDef ):
    name      = 'HNCOCA'
    dimension = 3
    peaks     = [
                 [(0,'HN'),(0,'N'),(-1,'CA')],  # Sequential CA peak
                ]
    nuclei    = [
                 ['HN','H'],
                 ['N'],
                 ['CA']
                ]
#end class
expDict['HNCOCA'] = HNCOCA

#===========================================================================

class HNCAHA( ExperimentDef ):
    name      = 'HNCAHA'
    dimension = 3
    peaks     = [
                 [(0,'HN'),(0,'N'),( 0,'HA')],   # Intra-residual HA peak
                 [(0,'HN'),(0,'N'),(-1,'HA')],   # Sequential HA peak
                 [(0,'HN'),(0,'N'),( 0,'HA1')],  # Intra-residual gly HA1 peak
                 [(0,'HN'),(0,'N'),(-1,'HA1')],  # Sequential gly HA1 peak
                 [(0,'HN'),(0,'N'),( 0,'HA2')],  # Intra-residual gly HA2 peak
                 [(0,'HN'),(0,'N'),(-1,'HA2')],  # Sequential gly HA2 peak
                 [(0,'HN'),(0,'N'),( 0,'QA')],   # Intra-residual gly QA peak
                 [(0,'HN'),(0,'N'),(-1,'QA')],   # Sequential gly QA peak
                ]
    nuclei    = [
                 ['HN','H'],
                 ['N'],
                 ['HA']
                ]
#end class
expDict['HNCAHA'] = HNCAHA

#===========================================================================

class HNCACB( ExperimentDef ):
    name      = 'HNCACB'
    dimension = 3
    peaks     = [
                 [(0,'HN'),(0,'N'),( 0,'CA')],  # Intra-residual CA peak
                 [(0,'HN'),(0,'N'),(-1,'CA')],  # Sequential CA peak
                 [(0,'HN'),(0,'N'),( 0,'CB')],  # Intra-residual CB peak
                 [(0,'HN'),(0,'N'),(-1,'CB')],  # Sequential CB peak
                ]
    nuclei    = [
                 ['HN','H'],
                 ['N'],
                 ['CA','CB','CACB']
                ]
#end class
expDict['HNCACB'] = HNCACB

#===========================================================================

class CBCACONH( ExperimentDef ):
    name      = 'CBCACONH'
    dimension = 3
    peaks     = [
                 [(0,'HN'),(0,'N'),(-1,'CA')],  # Sequential CA peak
                 [(0,'HN'),(0,'N'),(-1,'CB')],  # Sequential CB peak
                ]
    nuclei    = [
                 ['HN','H'],
                 ['N'],
                 ['CA','CB','CACB']
                ]
#end class
expDict['CBCACONH'] = CBCACONH
expDict['HNCOCACB'] = CBCACONH

#===========================================================================

class HAHBCONH( ExperimentDef ):
    name      = 'HAHBCONH'
    dimension = 3
    peaks     = [
                 [(0,'HN'),(0,'N'),(-1,'HA')],   # Sequential HA peak
                 [(0,'HN'),(0,'N'),(-1,'HA1')],  # Sequential gly HA1 peak
                 [(0,'HN'),(0,'N'),(-1,'HA2')],  # Sequential gly HA2 peak
                 [(0,'HN'),(0,'N'),(-1,'QA')],   # Sequential gly QA peak
                 [(0,'HN'),(0,'N'),(-1,'HB')],   # Sequential HB peak
                 [(0,'HN'),(0,'N'),(-1,'HB2')],  # Sequential HB2 peak
                 [(0,'HN'),(0,'N'),(-1,'HB3')],  # Sequential HB3 peak
                 [(0,'HN'),(0,'N'),(-1,'QB')],   # Sequential QB peak
                ]
    nuclei    = [
                 ['HN','H'],
                 ['N'],
                 ['HA','HB','HAHB']
                ]
#end class
expDict['HAHBCONH'] = HAHBCONH
expDict['HNCOHAHB'] = HAHBCONH

#===========================================================================

class CCONH( ExperimentDef ):
    name      = 'CCONH'
    dimension = 3
    peaks     = []
    nuclei    = [
                 ['HN','H'],
                 ['N'],
                 ['C']
                ]

    def definePeaks( self ):
        previous = self.residue.sibling( -1 )
        if not previous: return

        # I don't have in the database yet what are aliphatic and aromatic atoms
        carbons = NTlist()
        for atm in previous.atoms:
            if (atm.db.spinType == '13C' and
                atm.db.shift.average < 100.0
               ):
                carbons.append( atm )
        #end for
#        print '>>',carbons

        self.peaks = NTlist()
        #Generate all CCONH peaks of carbons
        for C in carbons:
            self.peaks.append( [(0,'HN'),(0,'N'),(-1,C.name)] )
        #end for
#        print len(self.peaks)
    #end def
#end class
expDict['CCONH'] = CCONH

#===========================================================================

class CCH( ExperimentDef ):
    name      = 'CCH'
    dimension = 3
    peaks     = []
    nuclei    = [
                 ['C'],
                 ['C2','CH'],
                 ['H']
                ]

    def definePeaks( self ):
        # I don't have in the database yet what are aliphatic and aromatic atoms
        carbons = NTlist()
        for atm in self.residue.atoms:
            if (atm.db.spinType == '13C' and
                atm.db.shift.average < 100.0
               ):
                carbons.append( atm )
        #end for
#        print '>>',carbons

        self.peaks = NTlist()
        #Generate all CCH peaks of carbons
        for C2 in carbons:
            for H in C2.observableProtons( includePseudo = True ):
                for C1 in carbons:
                    self.peaks.append( [(0,C1.name),(0,C2.name),(0,H.name)] )
                #end for
            #end for
        #end for
#        print len(self.peaks)
    #end def
#end class
expDict['CCH'] = CCH

#===========================================================================
def listPredefinedExperiments( project, *expNames ):
    """Give a listing of the predefined experiments or experimentName
       that can be used with generatePeaks
    """
    if len(expNames) == 0:
        expNames = expDict.keys()
    #end if

    for expName in expNames:
        expName = expName.strip().upper()
        if expName in expDict:
            NTmessage('%s', ExperimentDef.describe( expDict[expName] ) )
        else:
            NTerror('listPredefinedExperiments: no such experiment "%s"\n',
                     expName
                   )
        #end if
    #end for
#end def

def generatePeaks( project, experimentName, axisOrder=None, onlyAssigned  = True, skipResidues = [] ):
    """Generation of peaks
            experimentName: string identifying the experiment
            axisOrder:      string of colon-separated nuclei defining the order of
                            the axis; e.g. 'H:CA:N'
    """
    expName = experimentName.strip().upper()
    if expName not in expDict:
        NTerror('generatePeaks: experiment "%s" not defined\n\n', experimentName )
        project.listPredefinedExperiments()
        return None
    #end if
    exp = expDict[expName]

    # new peak list
    peakList = project.peaks.new( experimentName, status='keep' )

    # Generate peaks for all residues
    for residue in project.molecule.allResidues():
        if (residue.db.name in skipResidues):
            pass
        else:
            for atoms in exp( residue, axisOrder ):
                peakList.peakFromAtoms( atoms, onlyAssigned=onlyAssigned )
            #end for
        #end if
    #end for
    NTmessage('... Appended %d peaks', len( peakList ) )

    return peakList
#end def



# register the functions
methods  = [(generatePeaks, None), (listPredefinedExperiments, None) ]
#saves    = []
#restores = []
#exports  = []
