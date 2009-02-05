"""
    Wattos Module
    First version: jfd Dec 11, 2007
"""
from cing.core.constants import IUPAC
from cing.Libs.NTutils import ExecuteProgram
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import sprintf
import os
import time


class Wattos( NTdict ):
    """
    Class to use Wattos checks.
    First adding completeness check.
    """

    scriptTemplate = """
InitAll

SetProp
interactiveSession
false
SetProp
verbosity
3
SetProp
writeSessionOnExit
false

#Input file
ReadEntryPDB
INPUT_PDB_FILE

# Using same defaults as for FRED (NMR Restraints Grid) analysis.
CheckCompleteness
4
2
6
8
2
9
14
1.0
1
1
n
ob_standard.str
wattos_completeness_chk.str
n
wattos_completeness_chk

Quit
"""

    def __init__( self, rootPath = '.', molecule = None, **kwds ):
        NTdict.__init__( self, __CLASS__ = 'Wattos', **kwds )
        self.checks                = None
        self.molSpecificChecks     = None
        self.residueSpecificChecks = None
        self.atomSpecificChecks    = None
        self.residues              = None
        self.atoms                 = None
        self.molecule              = molecule
        self.rootPath              = rootPath
    #end def


def runWattos( project, tmp=None ):
    """
        Run and import the wattos results per model.
        All models in the ensemble of the molecule will be checked.
        Set wattos references for Molecule, Chain, Residue and Atom instances
        or None if no wattos results exist
        returns 1 on success or None on any failure.
    """
    if not project.molecule:
        NTerror("No project molecule in runWattos")
        return None

    path = project.path( project.molecule.name, project.moleculeDirectories.wattos )
    if not os.path.exists( path ):
        project.molecule.wattos = None
        for chain in project.molecule.allChains():
            chain.wattos = None
        for res in project.molecule.allResidues():
            res.wattos = None
        for atm in project.molecule.allAtoms():
            atm.wattos = None
        return None

    wattos = Wattos( rootPath = path, molecule = project.molecule )
    if project.molecule == None:
        NTerror('in runWattos: no molecule defined')
        return None

    if project.molecule.modelCount == 0:
        NTerror('in runWattos: no models for "%s"', project.molecule)
        return None

    wattosDir = project.mkdir( project.molecule.name, project.moleculeDirectories.wattos  )
    pdbFileName = 'project.pdb'
    fullname =  os.path.join( wattosDir, pdbFileName )
    pdbFile = project.molecule.toPDB( convention = IUPAC )
    if not pdbFile:
        NTerror("Failed to write a temporary PDB formatted coordinate file for ensemble.")
        return None
    pdbFile.save( fullname   )

    scriptComplete = Wattos.scriptTemplate
    scriptComplete = scriptComplete.replace("INPUT_PDB_FILE", pdbFileName)

    # Let's ask the user to be nice and not kill us
    # estimate to do **0.5 residues per minutes as with entry 1bus on dual core intel Mac.
    timeRunEstimated = 0.0025 *project.molecule.modelCount * len(project.molecule.allResidues())
    timeRunEstimatedInSecondsStr = sprintf("%4.0f",timeRunEstimated*60)
    NTmessage('==> Running Wattos read for an estimated (50,000 atoms/s): '+timeRunEstimatedInSecondsStr+" seconds; please wait")
    scriptFileName = "wattos.script"
    scriptFullFileName =  os.path.join( wattosDir, scriptFileName )
    open(scriptFullFileName,"w").write(scriptComplete)
#    wattosPath = "echo $CLASSPATH; java -Xmx512m -Djava.awt.headless=true Wattos.CloneWars.UserInterface -at"
    wattosPath = "java -Xmx512m -Djava.awt.headless=true Wattos.CloneWars.UserInterface -at"
    logFileName = "wattos_compl.log"
    wattosProgram = ExecuteProgram( wattosPath, rootPath = wattosDir,
                             redirectOutputToFile  = logFileName,
                             redirectInputFromFile = scriptFileName )
    # The last argument becomes a necessary redirection into fouling Wattos into
    # thinking it's running interactively.
    now = time.time()
    if True:
        wattosExitCode = wattosProgram()
    else:
        NTdebug("Skipping actual wattos execution for testing")
        wattosExitCode = 0

    NTdebug("Took number of seconds: " + sprintf("%8.1f", time.time() - now))
    if wattosExitCode:
        NTerror("Failed wattos checks with exit code: " + `wattosExitCode`)
        return None

    NTmessage('==> Parsing checks')
#    modelCheckDbFullFileName =  os.path.join( wattosDir, modelCheckDbFileName )
#    wattos._parseCheckdb( modelCheckDbFullFileName, 999 )

    NTwarning("Processing is to be continued from here on.")
    return 1
    if not wattos._processCheckdb():
        NTerror("Failed to process check db")
        return None
    # TODO: finish this code.
#    wattos.map2molecule()

    return wattos # Success
#end def

# register the functions
methods  = [(runWattos, None)]