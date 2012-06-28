"""
Runs and retrieves DSSP
Add's runDssp method to project class
"""
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqDssp import DSSP_STR
from cing.PluginCode.required.reqProcheck import SECSTRUCT_STR
from cing.core.constants import * #@UnusedWildImport
from cing.core.parameters import PLEASE_ADD_EXECUTABLE_HERE
from cing.core.parameters import cingPaths
from glob import glob

if True: # block
    useModule = True
#    if not cingPaths.dssp:
    if cingPaths.dssp == None or cingPaths.dssp == PLEASE_ADD_EXECUTABLE_HERE:
        nTdebug("Missing dssp which is an optional dep")
        useModule = False
    if not useModule:
        raise ImportWarning('dssp')
#    nTmessage('Using dssp')

class Dssp:
    """
  #  RESIDUE AA STRUCTURE BP1 BP2  ACC     N-H-->O    O-->H-N    N-H-->O    O-->H-N    TCO  KAPPA ALPHA  PHI   PSI    X-CA   Y-CA   Z-CA
    1  171 A V              0   0   93      0, 0.0     5,-0.2     0, 0.0    15,-0.2   0.000 360.0 360.0 360.0 -52.6    3.5    2.1    4.4
    2  172 A P    >>  -     0   0   44      0, 0.0     3,-2.1     0, 0.0     4,-1.3  -0.069 360.0-124.7 -47.1 138.0    0.9   -0.6    3.1
    3  173 A a  H 3> S+     0   0   20     14,-1.6     4,-1.5     1,-0.3     5,-0.2   0.829 109.8  59.6 -60.3 -35.2   -1.7    0.7    0.5
    4  174 A S  H 34 S+     0   0   55     13,-0.3    -1,-0.3    15,-0.2    14,-0.1   0.597 112.6  42.2 -60.4 -15.1   -4.8   -0.5    2.6
    5  175 A T  H <4 S+     0   0   94     -3,-2.1    -2,-0.2     7,-0.1    -1,-0.2   0.619 105.8  59.5-106.4 -23.3   -3.4    1.9    5.4
    6  176 A b  H >< S-     0   0   15     -4,-1.3     3,-0.8    -5,-0.2    -2,-0.2   0.878  79.5-174.8 -69.4 -42.1   -2.4    5.0    3.1
    7  177 A E  T 3< S-     0   0  154     -4,-1.5     3,-0.1     1,-0.2    -3,-0.1   0.794  70.9 -19.7  51.6  50.3   -6.1    5.3    1.9
    8  178 A G  T 3  S+     0   0   61      1,-0.2     2,-0.9    -5,-0.2    -1,-0.2   0.364  98.5 124.3 102.3  -2.4   -5.9    8.0   -0.8
01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
0    -    1         2         3         4         5         6         7    -    8         9         1
    """
    dsspDefs = NTdict(
                          # Keep rucksack from filling up over the years.
    #   field       (startChar, endChar, conversionFunction, store)
        resNum = (6, 10, int, False),
        chain = (11, 12, str, False)
    )
    dsspDefs[ SECSTRUCT_STR ] = (16, 17, str, True) # only one to store for now.

    def __init__(self, project):
        self.project = project
        self.molecule = project.molecule
        self.rootPath = project.mkdir(project.molecule.name, project.moleculeDirectories.dssp)
        self.redirectOutput = True
#        if cing.verbosity >= verbosityDetail:
#            self.redirectOutput=False
        self.dssp = ExecuteProgram(pathToProgram = cingPaths.dssp,
                                    rootPath = self.rootPath,
                                    redirectOutput = self.redirectOutput)
    # Return True on error ( None on success; Python default)
    def run(self, export = True):
        if self.project.molecule.modelCount == 0:
            nTwarning('dssp: no models for "%s"', self.project.molecule)
            return None
        if export:
            if not self.project.molecule.hasAminoAcid():
                nTmessage('==> Skipping Dssp because no amino acids are present.')
                return

            for res in self.project.molecule.allResidues():
                if not res.hasProperties('protein'):
                    pass
#                    nTwarning('Dssp.run: non-protein residue %s found and will be written out for Dssp' % repr(res))

            models = NTlist(*range(self.project.molecule.modelCount))
            # Can't use IUPAC here because aqua doesn't understand difference between
            # G and DG.(oxy/deoxy).
            for model in models:
                fullname = os.path.join(self.rootPath, 'model_%03d.pdb' % model)
                # DSSP prefers what?
#                nTdebug('==> Materializing model '+repr(model)+" to disk" )
                pdbFile = self.project.molecule.toPDB(model = model, convention = IUPAC)
                if not pdbFile:
                    nTerror("Dssp.run: Failed to write a temporary file with a model's coordinate")
                    return True
                pdbFile.save(fullname)
            #end for
        #end if

        nTmessage('==> Calculating secondary structure by DSSP')
        now = time.time()
        for model in models:
            fullname = 'model_%03d.pdb' % model
            fullnameOut = 'model_%03d.dssp' % model
            cmd = fullname + ' ' + fullnameOut
            if self.dssp(cmd):
                nTerror("Dssp.run: Failed to run DSSP; please consult the log file (.log etc). in the molecules dssp directory.")
                return True
            #end if
        #end for
        _taken = time.time() - now
#        nTdebug("Finished dssp successfully in %8.1f seconds", _taken)

#        self.project.dsspStatus.completed = True
        self.project.status.dssp.completed = True
        self.parseResult()
        return True
    #end def


    def _parseLine(self, line, defs):
        """
        Internal routine to parse a single line
        Return result, which is a dict type or None
        on error (i.e. too short line)
 e.g.   field       (startChar, endChar, conversionFunction)
        resName   = (  4,  7, str ),
        """
        result = {}
        if len(line) < 65:
            return None
        for field, fieldDef in defs.iteritems():
            c1, c2, func, _dummy = fieldDef
            result[ field ] = func(line[c1:c2])
        return result


    def parseResult(self):
        """
        Parse .dssp files and store result in dssp NTdict
        of each residue of mol.
        Return True on error.
        """
        modelCount = self.molecule.modelCount
#        nTdebug("Parse dssp files and store result in each residue for " + repr(modelCount) + " model(s)")

        for model in range(modelCount):
            fullnameOut = 'model_%03d.dssp' % model
            path = os.path.join(self.rootPath, fullnameOut)
            if not os.path.exists(path):
                nTerror('Dssp.parseResult: file "%s" not found', path)
                return True

#            nTmessage("Parsing " + path)
            isDataStarted = False
            for line in AwkLike(path):
                if line.dollar[0].find("RESIDUE AA STRUCTURE BP1 BP2") >= 0:
                    isDataStarted = True
                    continue
                if not isDataStarted:
                    continue
#                nTdebug("working on line: %s" % line.dollar[0])
                if not len(line.dollar[0][6:10].strip()):
#                    nTdebug('Skipping line without residue number')
                    continue
                result = self._parseLine(line.dollar[0], self.dsspDefs)
                if not result:
                    nTerror("Failed to parse dssp file the below line; giving up.")
                    nTerror(line.dollar[0])
                    return True
                chain = result['chain']
                resNum = result['resNum']
                residue = self.molecule.decodeNameTuple((None, chain, resNum, None))
                if not residue:
                    nTerror('in Dssp.parseResult: residue not found (%s,%d); giving up.' % (chain, resNum))
                    return True
                # For first model reset the dssp dictionary in the residue
                if model == 0 and residue.has_key('dssp'):
                    del(residue['dssp'])
                residue.setdefault('dssp', NTdict())

#                nTdebug("working on residue %s" % residue)
                for field, value in result.iteritems():
                    if not self.dsspDefs[field][3]: # Checking store parameter.
                        continue
                    # Insert for key: "field" if missing an empty  NTlist.
                    residue.dssp.setdefault(field, NTlist())
                    residue.dssp[field].append(value)
#                    nTdebug("field %s has values: %s" % ( field, residue.dssp[field]))
                #end for
            #end for
        #end for
        for residue in self.molecule.allResidues():
            if residue.has_key(DSSP_STR):
#                residue[DSSP_STR].consensus = residue[DSSP_STR].secStruct.setConsensus(CONSENSUS_SEC_STRUCT_FRACTION)
                residue[DSSP_STR].consensus = residue[DSSP_STR].secStruct.setConsensus(useLargest=True)
                residue[DSSP_STR].keysformat()
        #end for
        self.project.status.dssp.parsed = True
    #end def


#    def postProcess(self):
#        item = SECSTRUCT_STR
##        for item in [ SECSTRUCT_STR ]:
#        for res in self.project.molecule.allResidues():
#            if res.has_key( item ):
#                itemList = res[ item ]
#                c = itemList.setConsensus()
#                nTdebug('consensus: %s', c)

#end class

def dsspDefault():
    """ define the default dssp dict"""
    return NTdict(
                  directory    = 'Dssp',
                  dsspTemplate = 'model_%03d.dssp',
                  pdbTemplate  = 'model_%03d.pdb',
                  molecule     = None,
                  completed    = False,
                  parsed       = False
                 )
#end def

def runDssp(project, parseOnly=False)   :
    """
    Adds <Dssp> instance to molecule. Run dssp and parse result.
    (ParseOnly is only for backward compatibility)

    Return None on error.
    """
    # check if dssp is present
    if cingPaths.dssp == None or cingPaths.dssp == PLEASE_ADD_EXECUTABLE_HERE:
        nTmessage("runDssp: No whatif installed so skipping runDssp")
        return

    if not project:
        nTerror('runDssp: no project defined')
        return None
    #end if

    if not project.molecule:
        nTerror('runDssp: no molecule defined')
        return None
    #end if

    # Legacy code: to be removed
    if parseOnly:
        if restoreDssp( project ):
            return None
        return project.molecule.dssp
    # end legacy code

    project.status.dssp = dsspDefault()
    project.status.dssp.molecule = project.molecule.nameTuple()
    project.status.dssp.keysformat()

    if project.molecule.has_key('dssp'):
        del(project.molecule.dssp)
    #end if

    dcheck = Dssp(project)
    if not dcheck:
        nTerror("runDssp: Failed to get dssp instance of project")
        return None

    dcheck.run()
    project.molecule.dssp = dcheck

    project.history(sprintf('Ran dssp on molecule %s', project.molecule))

    return dcheck
#end def

def restoreDssp(project, tmp = None):
    """
    Restore dssp results if present

    Return True on error
    """
    nTmessage('==> Restoring dssp results')
    
    if not project:
        nTerror('restoreDssp: no project defined')
        return True
    #end if

    if not project.molecule:
        return True
    #end if
#    for res in project.molecule.allResidues():
#        res.dssp = None

    project.status.setdefault('dssp', dsspDefault())
    # old parameter
    if getDeepByKeysOrAttributes( project, 'dsspStatus', COMPLETED_STR):
        project.status.dssp.completed = True
        project.status.dssp.molecule = project.molecule.nameTuple()
        project.dsspStatus = None # key is removed on next save
    project.status.dssp.keysformat()
    project.status.keysformat()

    if not project.status.dssp.completed:
        return

    project.status.dssp.parsed = False

    if project.molecule.has_key('dssp'):
        del(project.molecule.dssp)
    #end if

    dcheck = Dssp(project)
    if not dcheck:
        nTerror("restoreDssp: Failed to get dssp instance of project")
        return True

    nTmessage('==> Restoring DSSP results')
    dcheck.parseResult()
#    nTdetail('==> Restored dssp results')
    project.molecule.dssp = dcheck
#end def

def removeTempFiles( todoDir ):
#    whatifDir        = project.mkdir( project.molecule.name, project.moleculeDirectories.whatif  )
    nTdebug("Removing temporary files generated by Dssp")
    try:
#        removeListLocal = ["DSSPOUT", "TOPOLOGY.FIL", "PDBFILE.PDB", "PDBFILE", "pdbout.tex", "pdbout.txt", 'fort.79']
        removeList = []
#        for fn in removeListLocal:
#            removeList.append( os.path.join(whatifDir, fn) )

        for extension in [ "*.out*", "*.pdb" ]:
            for fn in glob(os.path.join(todoDir,extension)):
                removeList.append(fn)
        for fn in removeList:
            if not os.path.exists(fn):
                nTdebug("dssp.removeTempFiles: Expected to find a file to be removed but it doesn't exist: " + fn )
                continue
#            nTdebug("Removing: " + fn)
            os.unlink(fn)
    except:
        nTdebug("dssp.removeTempFiles: Failed to remove all temporary what if files that were expected")
#end def


# register the functions
methods = [(runDssp, None)
           ]
#saves    = []
restores = [(restoreDssp, None)]
#exports  = []
