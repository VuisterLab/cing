"""
Adds shiftx method to predict chemical shifts. The shiftx program is included as binaries for Mac OSX and 32 bit
Linux in the bin directory.

"""
import os
import math

import cing
from cing import constants
import cing.constants.definitions as cdefs
from cing.core import validation
from cing.Libs import Adict
from cing.Libs import io
import cing.Libs.jsonTools as jsonTools

from cing.Libs.AwkLike import AwkLike

#from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTlist

from cing.Libs.NTutils import nTerror
from cing.Libs.NTutils import nTwarning
from cing.Libs.NTutils import nTmessage
from cing.Libs.NTutils import nTdebug
from cing.Libs.NTutils import nTaverage
from cing.Libs.NTutils import nTdetail
from cing.Libs.NTutils import ExecuteProgram

from cing.Libs.fpconst import NaN

__version__ = cing.__version__

# if True: # block
#     useModule = True
#     # TODO: test if the binary is actually applicable to the system os.
#     if not os.path.exists( cingPaths.shiftx ):
#         nTmessage("Missing shiftx which is a dependency for shiftx")
#         useModule = False
#     if not useModule:
#         raise ImportWarning('shiftx')
# #    nTmessage('Using shiftx')


def shiftxStatus():
    """Return shiftx default status dict
    """
    defs = Adict.Adict()
    defs.completed    = False
    defs.parsed       = False
    defs.version      = __version__
    defs.models       = []
    defs.baseName     = 'model_%03d'
    defs.directory    = constants.SHIFTX_KEY
    defs.chains       = []    # list of (chainNames, outputFile) tuples to be parsed
    return defs
#end def


class ShiftxResult(validation.ValidationResult):
    """Class to store shiftx results; all related to atoms
    """
    KEY     = constants.SHIFTX_KEY
    DATA    = 'data'
    AVERAGE = 'average'
    SD      = 'sd'

    def __init__(self):
        validation.ValidationResult.__init__(self)
        self.setdefault(ShiftxResult.DATA, [])
        self.setdefault(ShiftxResult.AVERAGE, NaN)
        self.setdefault(ShiftxResult.SD, NaN)
    #end def
#end class


class ShiftxResultJsonHandler(jsonTools.handlers.AnyDictHandler):
    """Handler for the ShiftxsResult class
    """
    namespace = cing.constants.SHIFTX_KEY
    cls = ShiftxResult
    encodedKeys = [cing.constants.OBJECT_KEY]
#end class
ShiftxResultJsonHandler.handles(ShiftxResult)


class QshiftxResult(validation.ValidationResult):
    """Class to store residue Q-factor shiftx results
    """
    KEY         = constants.SHIFTX_KEY
    ALL_ATOMS   = 'allAtoms'
    BACKBONE    = 'backbone'
    HEAVY_ATOMS = 'heavyAtoms'
    PROTONS     = 'protons'

    def __init__(self):
        validation.ValidationResult.__init__(self)
        self.setdefault(ShiftxResult.ALL_ATOMS, NaN)
        self.setdefault(ShiftxResult.BACKBONE, NaN)
        self.setdefault(ShiftxResult.HEAVY_ATOMS, NaN)
        self.setdefault(ShiftxResult.PROTONS, NaN)
    #end def
#end class


#LEGACY
def legacyQshiftDict():
    """
    return a legacy dict used to store the shiftx Qfactor results
    """
    return  NTdict(allAtoms = None, backbone=None, heavyAtoms=None, protons=None, residue = None,
                   __FORMAT__ = \
    constants.dots + ' shiftx Qfactor %(residue)s ' + constants.dots + """
    allAtoms:   %(allAtoms)6.3f
    backbone:   %(backbone)6.3f
    heavyAtoms: %(heavyAtoms)6.3f
    protons:    %(protons)6.3f"""
    )
#end def


class QshiftxResultJsonHandler(jsonTools.handlers.AnyDictHandler):
    """Handler for the QshiftxResult class
    """
    namespace = cing.constants.SHIFTX_KEY
    cls = QshiftxResult
    encodedKeys = [cing.constants.OBJECT_KEY]

    def restore(self, data):
        result = QshiftxResult()
        self._restore(data, result)
        #restore LEGACY
        if result[constants.OBJECT_KEY] is not None and \
           isinstance(result[constants.OBJECT_KEY], cing.core.classes.Project):
            qshiftDict = legacyQshiftDict()
            for k in [QshiftxResult.ALL_ATOMS, QshiftxResult.BACKBONE,
                      QshiftxResult.HEAVY_ATOMS, QshiftxResult.PROTONS]:
                qshiftDict[k] = result[k]
            qshiftDict['residue'] = result[constants.OBJECT_KEY]
            result[constants.OBJECT_KEY].Qshift = qshiftDict
        #end if
    #end def
#end class
QshiftxResultJsonHandler.handles(QshiftxResult)


def _resetShiftx(project):
    """Reset the shiftx references
    """
    for res in project.molecule.allResidues():
        project.validationData.setResult(res, constants.SHIFTX_KEY, None)
        #LEGACY:

    for atm in project.molecule.allAtoms():
        project.validationData.setResult(atm, constants.SHIFTX_KEY, None)
        #LEGACY:
        atm.shiftx = NTlist()
    #end for
#end def


def _parseShiftxOutput( fileName, project, chainId ):
    """
    Parse shiftx generated output (gv_version!).
    Store result in shiftx attribute (which is a NTlist type) of each atom

format file:

# Entries marked with a * may have inaccurate shift predictions.
# Entries marked with a value < -600 should be ignored
  501   H  N      116.3173
  501   H  CA      55.4902
  501   H  CB      29.9950
  501   H  C      169.8446
  501   H  H        8.4401
  or in 1y4o:
  1     G  N      109.7404
  1     G  CA      45.2787
  or in 1afp
  10    K  HZ3      3.7795 # A HZ3 that might not be present.


    Return True on error; eg. when the file is absent.
    """
    if not os.path.exists(fileName):
        nTerror("_parseShiftxOutput: Failed to find %s" % fileName)
        return True

    if project is None:
        nTerror("_parseShiftxOutput: no project defined")
        return True

    molecule = project.molecule

    nTdebug('_parseShiftxOutput: parsing %s', fileName)

    atomDict = molecule.getAtomDict(constants.IUPAC, chainId)

    for line in AwkLike(fileName, commentString = '#', minNF = 4):
        shift = line.float(4)
        if shift != -666.000:
            lineCol1 = int(line.dollar[1].strip('*'))
            atmName = line.dollar[3]
            if chainId is not None:
                atm = molecule.decodeNameTuple( (constants.IUPAC, chainId, lineCol1, atmName) )
                #happens for all N-terminal H because the Nterminal residue has H1/2/3
                #fix:
                if atm is None and atmName == 'H':
                    atm = molecule.decodeNameTuple( (constants.IUPAC, chainId, lineCol1, 'H1') )
            else:
                atm = None
                if atomDict.has_key((lineCol1, atmName)):
                    atm = atomDict[(lineCol1, atmName)]
            #end if
            #print '>>', atm
            if not atm:
                pass
                nTdebug('parseShiftxOutput: chainId [%s] line %d (%s)', chainId, line.NR, line.dollar[0] )
                # happens for all LYS without HZ3.
            else:
                result = project.validationData.getResult(atm, constants.SHIFTX_KEY, ShiftxResult())
                if result is None:
                    io.error('_parseShiftxOutput: retrieving ShiftxResult for atom {0}\n', atm)
                else:
                    result.DATA.append(shift)
                    #LEGACY:
                    atm.shiftx.append(shift)
                #end if
            #end if
        #end if
    #end for
#end def


def parseShiftx(project, tmp=None):
    """
    Parse the output generated by the shiftx program
    """
    if project is None:
        nTmessage("parseShiftx: No project defined")
        return True

    if project.molecule is None:
        nTmessage("parseShiftx: No molecule defined")
        return True

    defs = project.getStatusDict(constants.SHIFTX_KEY, **shiftxStatus())

    if not defs.completed:
        nTmessage("parseShiftx: No shiftx was run")
        return True

    path = project.validationPath(defs.directory)
    if not path:
        nTerror('parseShiftx: directory "%s" with shiftx data not found', path)
        return True

    _resetShiftx(project)
    #print '>>', defs, len(defs.chains)
    for chainId, fname in defs.chains:
        if _parseShiftxOutput(path / fname, project, chainId):
            return True
    #end for
    defs.parsed = True
    _calculatePseudoAtomShifts(project, len(defs.models))
    _averageShiftx(project)
    calcQshift(project)
    return False
#end def


def runShiftx(project, parseOnly=False, model=None):
    """
    Use shiftx program to predict chemical shifts
    Works only for protein residues.

    Adds ShiftxResult instance to validation container of atoms
    LEGACY:
    Adds a NTlist object with predicted values for each model as shiftx attribute
    to each atom for which there are predictions, or empty list otherwise.

    Throws warnings for non-protein residues.
    Returns True on error.

    Shiftx works on pdb files, uses only one model (first), so we have to write the files separately and analyze them
    one at the time.
    """

    #LEGACY:
    if parseOnly:
        return parseShiftx(project)

    if cdefs.cingPaths.shiftx is None:
        nTmessage('runShiftx: no shiftx executable, skipping')
        return False # Gracefully return

    if project.molecule is None:
        nTerror('runShiftx: no molecule defined')
        return True

    if project.molecule.modelCount == 0:
        nTwarning('runShiftx: no models for "%s"', project.molecule)
        return True

    if model is not None and model >= project.molecule.modelCount:
        nTerror('runShiftx: invalid model (%d) for "%s"', model, project.molecule)
        return True

    if not project.molecule.hasAminoAcid():
        nTmessage('==> Skipping runShiftx because no amino acids are present.')
        return False

    nTmessage('==> Running shiftx')

    skippedAtoms = [] # Keep a list of skipped atoms for later
    skippedResidues = [] # Only used for presenting to end user not actually used for skipping.
    skippedChains = []

    for chain in project.molecule.allChains():
        skippChain = True
        for res in chain.allResidues():
            if not res.hasProperties('protein'):
                if not res.hasProperties('HOH'): # don't report waters
                    skippedResidues.append(res)
                for atm in res.allAtoms():
                    atm.pdbSkipRecord = True
                    skippedAtoms.append(atm)
                #end for
            else:
                skippChain = False
            #end if
            if skippChain:
                skippedChains.append(chain)
        #end for
    #end for
    if skippedResidues:
        nTmessage('==> runShiftx: %s non-protein residues will be skipped.' %  len(skippedResidues))

    defs = project.getStatusDict(constants.SHIFTX_KEY, **shiftxStatus())
    if model is not None:
        defs.models = NTlist(model)
    else:
        defs.models = NTlist(*range(project.molecule.modelCount))
    defs.baseName  = 'model_%03d'
    defs.completed = False
    defs.parsed    = False
    defs.chains    = []

    # initialize the shiftx attributes
    _resetShiftx(project)

    path = project.validationPath(defs.directory)
    if not path:
        return True
    if path.exists():
        nTdebug('runShiftx: removing %s with prior data', path)
        path.rmdir()
    path.makedirs()

    doShiftx = ExecuteProgram(pathToProgram=cdefs.cingPaths.shiftx,
                              rootPath=path, redirectOutput=False)
    startTime = io.now()

    for model in defs.models:
        # set filenames
        rootname =  defs.baseName % model
        nTdebug('runShiftx: doing model %s, path %s, rootname %s', model, path, rootname)

        # generate a pdbfile
        pdbFile = project.molecule.toPDB(model=model, convention = constants.IUPAC)
        if not pdbFile:
            nTerror("runShiftx: Failed to generate a pdb file for model: %s", model)
            return True
        pdbFile.save(path / rootname+'.pdb')
        del pdbFile

        for chain in project.molecule.allChains():
            if chain not in skippedChains:
                # nTdebug('Doing chain code [%s]' % (chain.name))
                # quotes needed because by default the chain id is a space now.
                # chainId =  "'" + chain.name + "'"
                # According to the readme in shiftx with the source this is the way to call it.
                chainId =  "1" + chain.name
                outputFile = rootname + '_' + chain.name + '.out'
                defs.chains.append((chain.name, outputFile))
                doShiftx(chainId, rootname+'.pdb', outputFile)
            #end if
        #end for
    #end for

    #cleanup
    for pdbfile in path.glob('*.pdb'):
        pdbfile.remove()

    # Restore the 'default' state
    for atm in skippedAtoms:
        atm.pdbSkipRecord = False

    defs.completed = True
    # parse the results
    if parseShiftx(project):
        return True

    defs.date = io.now()
    defs.version = __version__
    defs.molecule = project.molecule.asPid
    defs.remark = 'Shiftx on %s completed in %.1f seconds on %s; data in %s' % \
                  (project.molecule, defs.date-startTime, defs.date, path)
    project.history(defs.remark)
    nTmessage('==> %s', defs.remark)
    return False
#end def


def _calculatePseudoAtomShifts(project, nmodels):
    """
    Calculate the shift of the methylene and methyl pseudoAtom protons
    Replaces _averageMethylAndMethylene
    """
    molecule = project.molecule
    for atm in molecule.atomsWithProperties('isMethyl','isCarbon') + \
               molecule.atomsWithProperties('isMethylene','isCarbon'):
        protons = atm.attachedProtons(includePseudo=False)
        pseudo  = protons[0].pseudoAtom()
        if pseudo is None:
            continue
        # check if the data are there
        shiftxProtons = [project.validationData.getResult(p, constants.SHIFTX_KEY) for p in protons]
        if None in shiftxProtons:
            continue
        shiftxPseudo = project.validationData.getResult(pseudo, constants.SHIFTX_KEY, ShiftxResult())

        # average the data:
        for i in range(nmodels):
            shifts = [p[ShiftxResult.DATA][i] for p in shiftxProtons]
            shiftxPseudo[ShiftxResult.DATA].append(sum(shifts)/len(protons))
        #end for
        #LEGACY:
        pseudo.shiftx = shiftxPseudo[ShiftxResult.DATA]
    #end for
#end def


def _averageShiftx(project):
    """Average shiftx data array for each atom
    return True on error
    """
#    nTdebug('shiftx: doing averageShiftx')
    molecule = project.molecule
    if molecule is None:
        nTerror('_averageShiftx: no molecule defined')
        return True
    #end if

    for atm in molecule.allAtoms():
        # Set averages
        shiftx = project.validationData.getResult(atm, constants.SHIFTX_KEY)
        if shiftx is not None:
            av,sd,n = nTaverage(shiftx.data)
            if av is None:
                shiftx[ShiftxResult.AVERAGE] = NaN
                shiftx[ShiftxResult.SD] = NaN
                #LEGACY:
                atm.shiftx.av = NaN
                atm.shiftx.sd = NaN
            else:
                shiftx[ShiftxResult.AVERAGE] = av
                shiftx[ShiftxResult.SD] = sd
                #LEGACY:
                atm.shiftx.av = av
                atm.shiftx.sd = sd
            #end if
        #end if
    #end for
#end def


def _calcQshift(project, atmList):
    """
    Calculate Qshift value for list of atoms
    """
    sumDeltaSq    = 0.0
    sumMeasuredSq = 0.0
    for atm in atmList:
        shiftxResult = project.validationData.getResult(atm, constants.SHIFTX_KEY)
        if shiftxResult is not None and \
           len(shiftxResult.DATA)>0 and \
            atm.isAssigned(resonanceListIdx=constants.RESONANCE_LIST_IDX_ANY):
            measured = atm.shift()
            sumMeasuredSq += measured**2
            # delta with shiftx average
            sumDeltaSq = (measured-shiftxResult.AVERAGE)**2
            #print atm, measured, av
        #end if
    #end for

    if sumMeasuredSq >0.0:
        qshift=math.sqrt(sumDeltaSq/sumMeasuredSq)
    else:
        qshift=NaN
    # end if
    return qshift
#end def


def calcQshift(project):
    """Calculate per residue Q factors between assignment and shiftx results
    """
    if project is None:
        nTmessage('calcQshift: no project defined')
        return None
    #end if

    if not project.molecule:
        nTmessage('calcQshift: no molecule defined')
        return None
    #end if
    nTdetail('==> Calculating Q-factors for chemical shift')
    for res in project.molecule.allResidues():
        atms = res.allAtoms()
        bb = NTlist()
        heavy = NTlist()
        protons = NTlist()

        for a in atms:
            if a.isBackbone():
                bb.append(a)
            if a.isProton():
                protons.append(a)
            else:
                heavy.append(a)
        #end for

        result = project.validationData.getResult(res, constants.SHIFTX_KEY, QshiftxResult())
        if result is None:
            nTmessage('calcQshift: error setting QshiftResult for residue %s', res)
            return None
        #end if
        result[QshiftxResult.ALL_ATOMS]   = _calcQshift(project, atms)
        result[QshiftxResult.BACKBONE]    = _calcQshift(project, bb)
        result[QshiftxResult.HEAVY_ATOMS] = _calcQshift(project, heavy)
        result[QshiftxResult.PROTONS]     = _calcQshift(project, protons)

        #LEGACY
        qshiftDict = legacyQshiftDict()
        for k in [QshiftxResult.ALL_ATOMS, QshiftxResult.BACKBONE,
                  QshiftxResult.HEAVY_ATOMS, QshiftxResult.PROTONS]:
            qshiftDict[k] = result[k]
        qshiftDict['residue'] = res
        res.Qshift = qshiftDict
    #end for
#end def

# register the functions
methods  = [(runShiftx,None),
            (parseShiftx,None),
           ]
#saves    = []
#restores = []
#exports  = []