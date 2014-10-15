"""
Adds shiftx method to predict chemical shifts. The shiftx program is included as binaries for Mac OSX and 32 bit
Linux in the bin directory.

"""
import cing
from cing import constants
from cing.core import validation
from cing.core import sml
from cing.Libs import Adict
from cing.Libs import io

from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.constants import * #@UnusedWildImport
from cing.core.parameters import cingPaths
from cing.constants.definitions import validationDirectories
from glob import glob
from math import sqrt

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

# def shiftxPath(project, *args):
#     """
#     Return shiftx path from active molecule of project
#     Creates directory if does not exist
#     """
#     return project.validationPath(validationDirectories['shiftx'], *args)
#end def

def shifxDefaults():
    """Return shiftx default dict
    """
    defs = Adict.Adict()
    defs.completed    = False
    defs.parsed       = False
    defs.present      = False
    defs.saved        = False
    defs.saveVersion  = __version__
    defs.runVersion   = __version__
    defs.models       = []
    defs.baseName     = 'model_%03d'
    defs.directory    = constants.SHIFTX_KEY
    defs.smlFile      = constants.SHIFTX_KEY + '.sml'
    defs.chains       = NTlist()    # list of (chainNames, outputFile) tuples to be parsed

    return defs
#end def


class ShiftxResult(validation.ValidationResult):
    """Class to store shiftx results
    """
    KEY     = constants.SHIFTX_KEY
    DATA    = 'data'
    AVERAGE = 'average'
    SD      = 'sd'

    def __init__(self, **kwds):
        validation.ValidationResult.__init__( self, **kwds)
        self.setdefault(ShiftxResult.DATA, NTlist())
        self.setdefault(ShiftxResult.AVERAGE, NaN)
        self.setdefault(ShiftxResult.SD, NaN)
    #end def

    @staticmethod
    def endHandler(qDict, project=None):
        # Restore linkage
        # Needs a valid project
        # Needs a valid object key
        # Adds to validation
        if project is None:
            return None
        if constants.OBJECT_KEY not in qDict:
            nTerror('ShiftxResult.endHandler: object key not found ==> skipped item')
            return None
        theObject = project.getByPid(qDict[constants.OBJECT_KEY])
        if theObject is None:
            nTerror('ShiftxResult.endHandler: invalid object Pid %s, ==> skipped', qDict[constants.OBJECT_KEY])
            return None

        #end if
        #v3:
        validation.setValidationResult(theObject, constants.SHIFTX_KEY, qDict)
        #LEGACY:
        theObject['shiftx'] = qDict[ShiftxResult.DATA]
        return qDict
    #end def
#end class

#register ShiftxResult SML handler
ShiftxResult.SMLhandler = sml.SMLAnyDictHandler(ShiftxResult,'ShiftxResult',
                                                encodeKeys = [constants.OBJECT_KEY],
                                                endHandler = ShiftxResult.endHandler,
                                               )


def _resetShiftx(defs, molecule):
    """Reset the shiftx references in the data
    """
    for atm in molecule.allAtoms():
        #LEGACY:
        atm.shiftx = NTlist()
        validation.setValidationResult(atm, constants.SHIFTX_KEY, None)
    #end for
    defs.present = False
#end def


def _parseShiftxOutput( fileName, molecule, chainId ):
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

    nTdebug('_parseShiftxOutput: parsing %s', fileName)

    atomDict = molecule.getAtomDict(IUPAC, chainId)

    for line in AwkLike(fileName, commentString = '#', minNF = 4):
        shift = line.float(4)
        if shift != -666.000:
            lineCol1 = int(line.dollar[1].strip('*'))
            atmName = line.dollar[3]
            if chainId != None:
                atm = molecule.decodeNameTuple( (IUPAC, chainId, lineCol1, atmName) )
                #happens for all N-terminal H because the Nterminal residue has H1/2/3
                #fix:
                if atm is None and atmName == 'H':
                    atm = molecule.decodeNameTuple( (IUPAC, chainId, lineCol1, 'H1') )
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
                result = validation.getValidationResult(atm, constants.SHIFTX_KEY)
                if result is None:
                    result = ShiftxResult()
                    validation.setValidationResult(atm, constants.SHIFTX_KEY, result)
                #end if
                result[ShiftxResult.DATA].append(shift)
                #LEGACY:
                atm.shiftx.append(shift)
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

    defs = project.getStatusDict(constants.SHIFTX_KEY, **shifxDefaults())

    if not defs.completed:
        nTmessage("parseShiftx: No shiftx was run")
        return True

    path = project.validationPath(defs.directory)
    if not path:
        nTerror('parseShiftx: directory "%s" with shiftx data not found', path)
        return True

    _resetShiftx(defs, project.molecule)
    #print '>>', defs, len(defs.chains)
    for chainId, fname in defs.chains:
        if _parseShiftxOutput(path / fname, project.molecule, chainId):
            return True
    #end for
    defs.present = True
    _calculatePseudoAtomShifts(project.molecule, len(defs.models))
    _averageShiftx(project.molecule)
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

    if project.molecule == None:
        nTerror('runShiftx: no molecule defined')
        return True

    if project.molecule.modelCount == 0:
        nTwarning('runShiftx: no models for "%s"', project.molecule)
        return True

    if model != None and model >= project.molecule.modelCount:
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

    defs = project.getStatusDict(constants.SHIFTX_KEY, **shifxDefaults())
    if model!=None:
        defs.models = NTlist(model)
    else:
        defs.models = NTlist(*range(project.molecule.modelCount))
    defs.baseName  = 'model_%03d'
    defs.completed = False
    defs.parsed    = False
    defs.chains    = NTlist()

    # initialize the shiftx attributes
    _resetShiftx(defs, project.molecule)

    path = project.validationPath(defs.directory)
    if not path:
        return True
    if path.exists():
        nTdebug('runShiftx: removing %s with prior data', path)
        path.rmdir()
    path.makedirs()

    doShiftx = ExecuteProgram(pathToProgram=cingPaths.shiftx,
                              rootPath=path, redirectOutput=False)
    startTime = io.now()

    for model in defs.models:
        # set filenames
        rootname =  defs.baseName % model
        nTdebug('runShiftx: doing model %s, path %s, rootname %s', model, path, rootname)

        # generate a pdbfile
        pdbFile = project.molecule.toPDB(model=model, convention = IUPAC)
        if not pdbFile:
            nTerror("runShiftx: Failed to generate a pdb file for model: %s", model)
            return True
        pdbFile.save(path / rootname+'.pdb')
        del(pdbFile)

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
    defs.runVersion = __version__
    defs.molecule = project.molecule.asPid()
    defs.remark = 'Shiftx on %s completed in %.1f seconds on %s; data in %s' % \
                  (project.molecule, defs.date-startTime, defs.date, path)
    project.history(defs.remark)
    nTmessage('==> %s', defs.remark)
    return False
#end def

#OBSOLETE: superseded by _calculatePseudoAtomShifts
# def _averageMethylAndMethylene( project, models ):
#     """
#     Routine to average the methyl proton shifts and b-methylene, before calculating average per atom
#     """
#     nmodels = len(models)
# #    nTdebug('shiftx: doing _averageMethylAndMethylene')
#     for atm in project.molecule.allAtoms():
#         if atm.isCarbon():
#
#             protons = atm.attachedProtons(includePseudo=False)
#             if len(protons) >= 2:
#                 skip = False
#                 for p in protons:
#                     if len(p.shiftx) == 0:  # No prediction for this proton
#                                             # Do not average
#                         skip = True
#                         #print p, p.shiftx
#                         break
#                     #end if
#                 #end for
#
#                 if not skip:
#                     shiftsComplete = True # fails for issue 201 with entry 2e5r For atom [<Atom MET57.CE>] proton [<Atom MET57.HE2>]
#                     shifts  = nTfill(0.0,nmodels)
#                     for i in range(nmodels):
#                         for p in protons:
#                             if len(p.shiftx) > i:
#                                 shifts[i] += p.shiftx[i]
#                             else:
#                                 nTerror("For atom [%s] proton [%s] no shiftx found; skipping _averageMethylAndMethylene" % (atm, p) )
#                                 shiftsComplete = False
#                             # end if
#                         #end for
#                         shifts[i] /= len(protons)
#                     #end for
#                     ps = protons[0].pseudoAtom()
#                     if shiftsComplete:
#                         ps.shiftx = shifts
#                     else:
#                         ps.shiftx = NTlist() # just an empty list.
#                     #end if
#                 #end if
#             #end if
#         #end if
#     #end for
# #end def

def _calculatePseudoAtomShifts(molecule, nmodels):
    """
    Calculate the shift of the methylene and methyl pseudoAtom protons
    Replaces _averageMethylAndMethylene
    """
    for atm in molecule.atomsWithProperties('isMethyl','isCarbon') + \
               molecule.atomsWithProperties('isMethylene','isCarbon'):
        protons = atm.attachedProtons(includePseudo=False)
        pseudo  = protons[0].pseudoAtom()
        if pseudo is None:
            continue
        # check if the data are there
        shiftxProtons = [validation.getValidationResult(p, constants.SHIFTX_KEY) for p in protons]
        if None in shiftxProtons:
            continue
        shiftxPseudo = validation.getValidationResult(pseudo, constants.SHIFTX_KEY, ShiftxResult())

        # average the data:
        for i in range(nmodels):
            shifts = [p[ShiftxResult.DATA][i] for p in shiftxProtons]
            shiftxPseudo[ShiftxResult.DATA].append(sum(shifts)/len(protons))
        #end for
        #LEGACY:
        pseudo.shiftx = shiftxPseudo[ShiftxResult.DATA]
    #end for
#end def

def _averageShiftx(molecule):
    """Average shiftx data array for each atom
    return True on error
    """
#    nTdebug('shiftx: doing averageShiftx')
    if molecule is None:
        nTerror('_averageShiftx: no molecule defined')
        return True
    #end if

    for atm in molecule.allAtoms():
        # Set averages
        shiftx = validation.getValidationResult(atm, constants.SHIFTX_KEY)
        if shiftx is not None:
            av,sd,n = NTaverage(shiftx.data)
            if av == None:
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


def saveShiftx(project, tmp=None):
    """
    Save shiftx results to sml file
    Returns True on error.
    Returns None on success.
    """
    if project is None:
        nTmessage("saveShiftx: No project defined")
        return True

    if project.molecule is None:
        nTmessage("saveShiftx: No molecule defined")
        return True
    # save the data
    return project._savePluginData(constants.SHIFTX_KEY,
                                   smlFile=constants.SHIFTX_KEY+'.sml',
                                   saved=True,
                                   saveVersion=__version__)
#end def

# pylint: disable=C0102
def restoreShiftx(project, tmp=None):
    """
    Restore shiftx results from sml file.
    Return True on error
    """
    if project == None:
        nTmessage("restoreShiftx: No project defined")
        return True

    if project.molecule == None:
        return False # Gracefully returns

    # Reset the data
    defs = project.getStatusDict(constants.SHIFTX_KEY, **shifxDefaults())
    _resetShiftx(defs, project.molecule)
    #restore the data
    if project._restorePluginData(constants.SHIFTX_KEY, present=True):
        return True
    _calculatePseudoAtomShifts(project.molecule, len(defs.models))
    _averageShiftx(project.molecule)
    calcQshift(project)
    return False
#end def


def _calcQshift( atmList ):
    """
    Calculate Qshift value for list of atoms
    """
    # for each model + av + heavyatom + proton + bb
    sumDeltaSq    = 0.0
    sumMeasuredSq = 0.0
    for atm in atmList:
        if atm.has_key('shiftx') and len(atm.shiftx)>0 and atm.isAssigned(resonanceListIdx=RESONANCE_LIST_IDX_ANY):
            atm.shiftx.average()
            measured = atm.shift()
            sumMeasuredSq += measured**2
            # delta with shiftx average
            sumDeltaSq = (measured-atm.shiftx.av)**2
            #print atm, measured, av
#            sumDeltaSq[project.molecule.modelCount] += (av-measured)**2
#            if not atm.isProton():
#                sumDeltaSq[project.molecule.modelCount+1] += (av-measured)**2
#            if atm.isProton():
#                #print atm, measured, av
#                sumDeltaSq[project.molecule.modelCount+2] += (av-measured)**2
#            if not atm.isBackbone():
#                sumDeltaSq[project.molecule.modelCount+3] += (av-measured)**2
        #end if
    #end for

    if sumMeasuredSq >0.0:
        qshift=sqrt(sumDeltaSq/sumMeasuredSq)
    else:
        qshift=NaN
    # end if

    return qshift
#end def


#TODO: check this code
def calcQshift( project, tmp=None ):
    """Calculate per residue Q factors between assignment and shiftx results
    """
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
        res.Qshift  = NTdict(allAtoms = None, backbone=None, heavyAtoms=None, protons=None,
                             residue = res,
                             __FORMAT__ = \
dots + ' shiftx Qfactor %(residue)s ' + dots + """
allAtoms:   %(allAtoms)6.3f
backbone:   %(backbone)6.3f
heavyAtoms: %(heavyAtoms)6.3f
protons:    %(protons)6.3f"""

                        )

        for a in atms:
            if a.isBackbone():
                bb.append(a)
            if a.isProton():
                protons.append(a)
            else:
                heavy.append(a)
        #end for

        res.Qshift.allAtoms   = _calcQshift( atms )
        res.Qshift.backbone   = _calcQshift( bb )
        res.Qshift.heavyAtoms = _calcQshift( heavy )
        res.Qshift.protons    = _calcQshift( protons )
    #end for
#end def

#OBSOLETE:
# def removeTempFiles( todoDir ):
# #    whatifDir        = project.mkdir( project.molecule.name, project.moleculeDirectories.whatif  )
#     nTdebug("Removing temporary files generated by shiftx")
#     try:
# #        removeListLocal = ["prodata", "ps.number", "aqua.cmm", "resdefs.dat", "mplot.in", '.log' ]
#         removeList = []
# #        for fn in removeListLocal:
# #            removeList.append( os.path.join(todoDir, fn) )
#
#         for extension in [ "*.pdb" ]:
#             for fn in glob(os.path.join(todoDir,extension)):
#                 removeList.append(fn)
#         for fn in removeList:
#             if not os.path.exists(fn):
#                 nTdebug("shiftx.removeTempFiles: Expected to find a file to be removed but it doesn't exist: " + fn )
#                 continue
# #            nTdebug("Removing: " + fn)
#             os.unlink(fn)
#     except:
#         nTdebug("shiftx.removeTempFiles: Failed to remove all temporary files that were expected")
# #end def

# register the functions
methods  = [(runShiftx,None),
            (calcQshift,None),
            (parseShiftx,None),
           ]
saves    = [(saveShiftx, None),
           ]
restores = [
            (restoreShiftx, None),
           ]
#exports  = []