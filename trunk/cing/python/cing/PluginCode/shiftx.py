"""
Adds shiftx method to predict chemical shifts. The shiftx program is included as binaries for Mac OSX and 32 bit
Linux in the bin directory.
"""
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.constants import * #@UnusedWildImport
from cing.core.parameters import cingPaths
from cing.core.parameters import validationSubDirectories
from glob import glob
from math import sqrt



if True: # block
    useModule = True
    # TODO: test if the binary is actually applicable to the system os.
    if not os.path.exists( cingPaths.shiftx ):
        NTmessage("Missing shiftx which is a dep for shiftx")
        useModule = False
    if not useModule:
        raise ImportWarning('shiftx')
#    NTmessage('Using shiftx')

contentFile = 'content.xml'

def shiftxPath(project, *args):
    """
    Return shiftx path from active molecule of project
    Creates directory if does not exist
    """
    return project.validationPath(validationSubDirectories['shiftx'], *args)
#end def

def parseShiftxOutput( fileName, molecule, chainId ):
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
        NTerror("Failed to find %s" % fileName)
        return True

    atomDict = molecule._getAtomDict(IUPAC, chainId)

    for line in AwkLike( fileName, commentString = '#', minNF = 4 ):
        if (line.float(4) != -666.000):
            lineCol1 = int(line.dollar[1].strip('*'))
            if chainId != None:
                atm = molecule.decodeNameTuple( (IUPAC, chainId, lineCol1, line.dollar[3]) )
            else:
                atm =None
                if atomDict.has_key( (lineCol1,line.dollar[3]) ):
                    atm = atomDict[ (lineCol1,line.dollar[3]) ]
            #end if
#            if not atm:
#                atm = molecule.decodeNameTuple( (IUPAC, None, lineCol1, line.dollar[3]), fromCYANA2CING=True )

            if not atm:
                pass
#                NTerror('parseShiftxOutput: chainId [%s] line %d (%s)', chainId, line.NR, line.dollar[0] )
                # happens for all LYS without HZ3.
            else:
                atm.shiftx.append( line.float(4) )
            #end if
        #end if
    #end for
#end def

def runShiftx( project, parseOnly=False, model=None   ):
    """
    Use shiftx program to predict chemical shifts
    Works only for protein residues.
    Adds a NTlist object with predicted values for each model as shiftx attribute
    to each atom for which there are predictions, or empty list otherwise.

    Throws warnings for non-protein residues.
    Returns shiftxStatus dict or None on error.

    Shiftx works on pdb files, uses only one model (first), so we have to write the files separately and analyze them
    one at the time.
    """

    if parseOnly:
        return restoreShiftx( project )

    if project.molecule == None:
        NTerror('runShiftx: no molecule defined')
        return None
    #end if
    if project.molecule.modelCount == 0:
        NTwarning('runShiftx: no models for "%s"', project.molecule)
        return None
    #end if
    if model != None and model >= project.molecule.modelCount:
        NTerror('runShiftx: invalid model (%d) for "%s"', model, project.molecule)
        return None
    #end if
    if not project.molecule.hasAminoAcid():
        NTmessage('runShiftx: not a single amino acid in the molecule so skipping this step.')
        return project

    NTmessage('==> Running shiftx' )

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
                    skippedAtoms.append( atm )
                #end for
            else:
                skippChain = False
            #end if
            if skippChain:
                skippedChains.append(chain)
        #end for
    #end for
    if skippedResidues:
        NTmessage('runShiftx: non-protein residues %s will be skipped.',  skippedResidues)

    if model!=None:
        models = NTlist( model )
    else:
        models = NTlist(*range( project.molecule.modelCount ))

    # initialize the shiftx attributes
    for atm in project.molecule.allAtoms():
        atm.shiftx = NTlist()
    #end for

    root = project.mkdir( project.molecule.name, project.moleculeDirectories.shiftx)
    baseName = 'model_%03d'
    shiftx = ExecuteProgram( pathToProgram=cingPaths.shiftx,
                             rootPath = root, redirectOutput = False)

    # Storage of results for later
    project.shiftxStatus.completed    = False
    project.shiftxStatus.parsed       = False
    project.shiftxStatus.version      = cing.cingVersion
    project.shiftxStatus.moleculeName = project.molecule.name # just to have it
    project.shiftxStatus.models       = models
    project.shiftxStatus.baseName     = baseName
    project.shiftxStatus.path         = root
    project.shiftxStatus.contentFile  = contentFile
    project.shiftxStatus.chains       = NTlist()    # list of (chainNames, outputFile) tuples to be parsed
    project.shiftxStatus.keysformat()


    for model in NTprogressIndicator(models):
        # set filenames
        rootname =  sprintf( baseName, model)
        model_base_name =  os.path.join( root, rootname )

        pdbFile = project.molecule.toPDB( model=model, convention = IUPAC  )
        if not pdbFile:
            NTerror("runShiftx: Failed to generate a pdb file for model: " + `model`)
            return None

        pdbFile.save( model_base_name + '.pdb'   )
        for chain in project.molecule.allChains():

            if chain in skippedChains:
#                NTdebug('Skipping chain code [%s]: no protein residues' % (chain.name))
                pass
            else:
#                NTdebug('Doing chain code [%s]' % (chain.name))
                # quotes needed because by default the chain id is a space now.
    #            chainId =  "'" + chain.name + "'"
                # According to the readme in shiftx with the source this is the way to call it.
                chainId =  "1" + chain.name
                outputFile = rootname + '_' + chain.name + '.out'
                project.shiftxStatus.chains.append( (chain.name, outputFile) )

                shiftx(chainId, rootname + '.pdb', outputFile )
                outputFile = os.path.join(root,outputFile)
    #            outputFile = os.path.abspath(outputFile)
#                NTdebug('runShiftx: Parsing file: %s for chain Id: [%s]' % (outputFile,chain.name))
                if parseShiftxOutput( outputFile, project.molecule, chain.name ):
                    NTerror("Failed parseShiftxOutput for %s" % outputFile) # TODO: check if continuation is reasonable.
            #end if
        #end for
        del( pdbFile )
    #end for

    # Restore the 'default' state
    for atm in skippedAtoms:
        atm.pdbSkipRecord = False

    # Average the methyl proton shifts and b-methylene
    _averageMethylAndMethylene( project, models )

    # Calculate average's for each atom
    averageShiftx(project)

    calcQshift( project )

    # store the status as xmlFile
    project.shiftxStatus.completed    = True
    project.shiftxStatus.parsed       = True
    obj2XML( project.shiftxStatus, path=os.path.join( root, contentFile ))
    project.shiftxStatus.keysformat()

    return project.shiftxStatus
#end def


def _averageMethylAndMethylene( project, models ):
    """
    Routine to average the methyl proton shifts and b-methylene, before calculating average per atom
    """
    nmodels = len(models)
#    NTdebug('shiftx: doing _averageMethylAndMethylene')
    for atm in project.molecule.allAtoms():
        if atm.isCarbon():

            protons = atm.attachedProtons(includePseudo=False)
            if len(protons) >= 2:
                skip = False
                for p in protons:
                    if len(p.shiftx) == 0:  # No prediction for this proton
                                            # Do not average
                        skip = True
                        #print p, p.shiftx
                        break
                    #end if
                #end for

                if not skip:
                    shiftsComplete = True # fails for issue 201 with entry 2e5r For atom [<Atom MET57.CE>] proton [<Atom MET57.HE2>]
                    shifts  = NTfill(0.0,nmodels)
                    for i in range(nmodels):
                        for p in protons:
                            if len(p.shiftx) > i:
                                shifts[i] += p.shiftx[i]
                            else:
                                NTerror("For atom [%s] proton [%s] no shiftx found; skipping _averageMethylAndMethylene" % (atm, p) )
                                shiftsComplete = False
                            # end if
                        #end for
                        shifts[i] /= len(protons)
                    #end for
                    ps = protons[0].pseudoAtom()
                    if shiftsComplete:
                        ps.shiftx = shifts
                    else:
                        ps.shiftx = NTlist() # just an empty list.
                    #end if
                #end if
            #end if
        #end if
    #end for
#end def

def averageShiftx( project, tmp=None ):
    """Average shiftx array for each atom
    """

#    NTdebug('shiftx: doing averageShiftx')
    if project.molecule == None:
        return
    #end if

    for atm in project.molecule.allAtoms():
        # Set averages
        if atm.has_key('shiftx'):
            atm.shiftx.average()
            if atm.shiftx.av == None:
                atm.shiftx.av = NaN
                atm.shiftx.sd = NaN
            #end if
        #end if
    #end for
#end def

def restoreShiftx( project, tmp=None ):
    """restore shiftx results for project.molecule
    Return project or None on error
    """

    root = project.moleculePath( 'shiftx' )

    if project.molecule == None:
        NTmessage('restoreShiftx: no molecule defined')
        return None
    #end if

    # initialize the shiftx attributes
    for atm in project.molecule.allAtoms():
        atm.shiftx = NTlist()
    #end for

    # Older versions; initialize the required keys of shiftxStatus
    if project.version < 0.881:
        xmlFile = os.path.join( root, contentFile )

        if os.path.exists( xmlFile ):
            NTdetail('==> Restoring shiftx results')
#            NTdebug('Using xmlFile "%s"', xmlFile)
        else:
            NTwarning('Shiftx results xmlFile "%s" not found', xmlFile)
            return None
        #end if

        shiftxResult = XML2obj( xmlFile )
        if not shiftxResult:
            return None

        project.shiftxStatus.update( shiftxResult )
        project.shiftxStatus.path = root
        project.shiftxStatus.parsed = False
        project.shiftxStatus.completed = True
    #end if

    project.shiftxStatus.keysformat()
#    NTdebug( 'project.shiftxStatus:\n%s', project.shiftxStatus.format() )

    if not project.shiftxStatus.completed:
        return project


    if project.shiftxStatus.moleculeName != project.molecule.name:
        NTwarning('restoreShiftx: current molecule name "%s" does not match xmlFile "%s"',
                   project.molecule.name, project.shiftxStatus.moleculeName
                 )

    # This needs fixing; current fix for projects  with longer root paths
    _tmp1 = project.shiftxStatus.path.split('/')[-2:] # last two directories
    _tmp2 = root.split('/')[-2:] # last two directories
    if _tmp1 != _tmp2:
        NTwarning('restoreShiftx: current shiftx root path "%s" does not match xmlFile "%s"',
                   root, project.shiftxStatus.path
                 )

    NTmessage("==> Restoring shiftx results")
    for chainName, outputFile in project.shiftxStatus.chains:
        parseShiftxOutput( os.path.join(root,outputFile), project.molecule, chainName )
    #end for

    # Average the methyl proton shifts and b-methylene
    _averageMethylAndMethylene( project, project.shiftxStatus.models )

    # Calculate average's for each atom
    averageShiftx(project)

    calcQshift( project )

    project.shiftxStatus.parsed = True
    project.shiftxStatus.keysformat()


    return project
#end def

def _calcQshift( atmList ):
    """
    Calculate Qshift value for list of atoms
    """
    # for each model + av + heavyatom + proton + bb
    sumDeltaSq    = 0.0
    sumMeasuredSq = 0.0
    for atm in atmList:
        if atm.has_key('shiftx') and len(atm.shiftx)>0 and atm.isAssigned():
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
            Qshift=sqrt(sumDeltaSq/sumMeasuredSq)
    else:
            Qshift=NaN

    return Qshift
#end def


def calcQshift( project, tmp=None ):
    """Calculate per residue Q factors between assignment and shiftx results
    """
    if not project.molecule:
        NTmessage('calcQshift: no molecule defined')
        return None
    #end if
    NTdetail('==> calculating Q-factors for chemical shift')
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
            if a.isBackbone(): bb.append(a)
            if a.isProton(): protons.append(a)
            else: heavy.append(a)
        #end for

        res.Qshift.allAtoms   = _calcQshift( atms )
        res.Qshift.backbone   = _calcQshift( bb )
        res.Qshift.heavyAtoms = _calcQshift( heavy )
        res.Qshift.protons    = _calcQshift( protons )
    #end for
#end def

def removeTempFiles( todoDir ):
#    whatifDir        = project.mkdir( project.molecule.name, project.moleculeDirectories.whatif  )
    NTdebug("Removing temporary files generated by shiftx")
    try:
#        removeListLocal = ["prodata", "ps.number", "aqua.cmm", "resdefs.dat", "mplot.in", '.log' ]
        removeList = []
#        for fn in removeListLocal:
#            removeList.append( os.path.join(todoDir, fn) )

        for extension in [ "*.pdb" ]:
            for fn in glob(os.path.join(todoDir,extension)):
                removeList.append(fn)
        for fn in removeList:
            if not os.path.exists(fn):
                NTdebug("shiftx.removeTempFiles: Expected to find a file to be removed but it doesn't exist: " + fn )
                continue
#            NTdebug("Removing: " + fn)
            os.unlink(fn)
    except:
        NTdebug("shiftx.removeTempFiles: Failed to remove all temporary files that were expected")
#end def

# register the functions
methods  = [(runShiftx,None),
            (averageShiftx,None),
            (calcQshift,None),
           ]
#saves    = []
restores = [
            (restoreShiftx, None),
           ]
#exports  = []