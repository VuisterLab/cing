"""
Runs and retrieves DSSP
Add's runDssp method to project class
"""
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import ExecuteProgram
from cing.Libs.NTutils import ImportWarning
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTwarning
from cing.PluginCode.required.reqDssp import DSSP_STR
from cing.PluginCode.required.reqProcheck import CONSENSUS_SEC_STRUCT_FRACTION
from cing.PluginCode.required.reqProcheck import SECSTRUCT_STR
from cing.core.constants import IUPAC
from cing.core.parameters import cingPaths
from cing.setup import PLEASE_ADD_EXECUTABLE_HERE
from cing.setup import time
import os

if True: # block
    useModule = True
    if not cingPaths.dssp:
        NTdebug("Missing dssp which is a dep for dssp")
        useModule = False
    if not useModule:
        raise ImportWarning('dssp')
#    NTmessage('Using dssp')

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
            NTwarning('dssp: no models for "%s"', self.project.molecule)
            return None
        if export:
            if not self.project.molecule.hasAminoAcid():
                NTmessage('Dssp.run: skipping because no amino acid in this molecule')
                return
                
            for res in self.project.molecule.allResidues():
                if not res.hasProperties('protein'):
                    pass
#                    NTwarning('Dssp.run: non-protein residue %s found and will be written out for Dssp' % `res`)

            models = NTlist(*range(self.project.molecule.modelCount))
            # Can't use IUPAC here because aqua doesn't understand difference between
            # G and DG.(oxy/deoxy).
            for model in models:
                fullname = os.path.join(self.rootPath, 'model_%03d.pdb' % model)
                # DSSP prefers what?
#                NTdebug('==> Materializing model '+`model`+" to disk" )
                pdbFile = self.project.molecule.toPDB(model = model, convention = IUPAC)
                if not pdbFile:
                    NTerror("Dssp.run: Failed to write a temporary file with a model's coordinate")
                    return True
                pdbFile.save(fullname)
            #end for
        #end if

        NTmessage('==> Calculating secondary structure by DSSP')
        now = time.time()
        for model in models:
            fullname = 'model_%03d.pdb' % model
            fullnameOut = 'model_%03d.dssp' % model
            cmd = fullname + ' ' + fullnameOut
            if self.dssp(cmd):
                NTerror("Dssp.run: Failed to run DSSP; please consult the log file (.log etc). in the molecules dssp directory.")
                return True
            #end if
        #end for
        _taken = time.time() - now
#        NTdebug("Finished dssp successfully in %8.1f seconds", _taken)

        self.parseResult()

        self.project.dsspStatus.completed = True
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
#        NTdebug("Parse dssp files and store result in each residue for " + `modelCount` + " model(s)")

        for model in range(modelCount):
            fullnameOut = 'model_%03d.dssp' % model
            path = os.path.join(self.rootPath, fullnameOut)
            if not os.path.exists(path):
                NTerror('Dssp.parseResult: file "%s" not found', path)
                return True

#            NTmessage("Parsing " + path)
            isDataStarted = False
            for line in AwkLike(path):
                if line.dollar[0].find("RESIDUE AA STRUCTURE BP1 BP2") >= 0:
                    isDataStarted = True
                    continue
                if not isDataStarted:
                    continue
#                NTdebug("working on line: %s" % line.dollar[0])
                if not len(line.dollar[0][6:10].strip()):
#                    NTdebug('Skipping line without residue number')
                    continue
                result = self._parseLine(line.dollar[0], self.dsspDefs)
                if not result:
                    NTerror("Failed to parse dssp file the below line; giving up.")
                    NTerror(line.dollar[0])
                    return True
                chain = result['chain']
                resNum = result['resNum']
                residue = self.molecule.decodeNameTuple((None, chain, resNum, None))
                if not residue:
                    NTerror('in Dssp.parseResult: residue not found (%s,%d); giving up.' % (chain, resNum))
                    return True
                # For first model reset the dssp dictionary in the residue
                if model == 0 and residue.has_key('dssp'):
                    del(residue['dssp'])
                residue.setdefault('dssp', NTdict())

#                NTdebug("working on residue %s" % residue)
                for field, value in result.iteritems():
                    if not self.dsspDefs[field][3]: # Checking store parameter.
                        continue
                    # Insert for key: "field" if missing an empty  NTlist.
                    residue.dssp.setdefault(field, NTlist())
                    residue.dssp[field].append(value)
#                    NTdebug("field %s has values: %s" % ( field, residue.dssp[field]))
                #end for
            #end for
        #end for
        for residue in self.molecule.allResidues():
            if residue.has_key(DSSP_STR):
                residue[DSSP_STR].consensus = residue[DSSP_STR].secStruct.setConsensus(CONSENSUS_SEC_STRUCT_FRACTION)
                residue[DSSP_STR].keysformat()
        #end for
    #end def


#    def postProcess(self):
#        item = SECSTRUCT_STR
##        for item in [ SECSTRUCT_STR ]:
#        for res in self.project.molecule.allResidues():
#            if res.has_key( item ):
#                itemList = res[ item ]
#                c = itemList.setConsensus()
#                NTdebug('consensus: %s', c)

#end class

def runDssp(project, parseOnly = False)   :
    """
    Adds <Dssp> instance to molecule. Run dssp and parse result.
    Return None on error.
    """
    # check if dssp is present
    if cingPaths.dssp == None or cingPaths.dssp == PLEASE_ADD_EXECUTABLE_HERE:
        NTmessage("No whatif installed so skipping this step")
        return
    
    if not project.molecule:
        NTerror('dssp: no molecule defined')
        return None
    #end if

    if project.molecule.has_key('dssp'):
        del(project.molecule.dssp)
    #end if

    dcheck = Dssp(project)
    if not dcheck:
        NTerror("Failed to get dssp instance of project")
        return None

    if parseOnly:
        dcheck.parseResult()
    else:
        dcheck.run()
    project.molecule.dssp = dcheck

    return dcheck
#end def

def restoreDssp(project, tmp = None):
    """
    Optionally restore dssp results
    """
    if project.dsspStatus.completed:
        NTmessage('==> restoring dssp results')
        project.runDssp(parseOnly = True)
#end def



# register the functions
methods = [(runDssp, None)
           ]
#saves    = []
restores = [(restoreDssp, None)]
#exports  = []
