"""
    Whatif Module
    First version: gv June 3, 2007
    Second version by jfd.
"""
from cing.Libs.NTutils import NTdict
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import printWarning
from cing.Libs.NTutils import CodeError
from cing.Libs.NTutils import ExecuteProgram
from cing.Libs.NTutils import printMessage
from cing.Libs.NTutils import sprintf
from cing.Libs.NTutils import printDebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import printError
from cing.Libs.NTutils import NTwarning
from cing.core.parameters import cingPaths
from glob import glob
from shutil import copy
import os
import time


class Whatif( NTdict ):
    """
    Class to use WHAT IF checks.

    Whatif.checks:                  NTlist instance of individual parsed checks
    Whatif.molSpecificChecks:       NTlist instance of those check pertaining to
                                    molecules; i.e Level : MOLECULE. TODO: implement in What If and here..
    Whatif.residueSpecificChecks:   NTlist instance of those check pertaining to
                                    residues; i.e Level : RESIDUE.
    Whatif.atomSpecificChecks:      NTlist instance of those check pertaining to
                                    atoms; i.e Level : ATOM.
    Whatif.residues:                NTdict instance with results of all
                                    residueSpecificChecks, sorted by key residue.
    Whatif.atoms:                   NTdict instance with results of all
                                    atomSpecificChecks sorted by key atom.

    Individual checks:
    NTdict instances with keys pointing to NTlist instances;

    All file refereces relative to rootPath ('.' by default) using the .path()
    method.
    TODO:   - Use hydrogen atoms
            - For more details see: http://spreadsheets.google.com/pub?key=p1emRxxfe3f4PkJ798dwPIg

    BUGS:   - ALTATM and TOPPOS occurs twice in 1ai0 check_001.db.
    """
    #define some more user friendly names
    # List of defs at:
    # http://www.yasara.org/pdbfinder_file.py.txt
    # http://swift.cmbi.ru.nl/whatif/html/chap23.html
    # All are in text record of file to be parsed so they're kind of redundant.
    nameDefs =[
                ('ACCLST', 'Relative accessibility'),
                ('ALTATM', 'Amino acids inside ligands check/Attached group check'),
                ('ANGCHK', 'Angles'),
                ('BA2CHK', 'Hydrogen bond acceptors'),
                ('BBCCHK', 'Backbone normality'),
                ('BH2CHK', 'Hydrogen bond donors'),
                ('BMPCHK', 'Bumps'),
                ('BNDCHK', 'Bond lengths'),
                ('BVALST', 'B-Factors'),
                ('C12CHK', 'Chi-1 chi-2'),
                ('CHICHK', 'Torsions'),
                ('CCOCHK', 'Inter-chain connection check'),
                ('CHICHK', 'Torsion angle check'),
                ('DUNCHK', 'Duplicate atom names in ligands'),
                ('EXTO2',  'Test for extra OXTs'),
                ('FLPCHK', 'Peptide flip'),
                ('HNDCHK', 'Chirality'),
                ('HNQCHK', 'Flip HIS GLN ASN hydrogen-bonds'),
                ('INOCHK', 'Accessibility'),
                ('MISCHK', 'Missing atoms'),
                ('MO2CHK', 'Missing C-terminal oxygen atoms'),
                ('NAMCHK', 'Atom names'),
                ('NQACHK', 'Qualities'),
                ('PC2CHK', 'Proline puckers'),
                ('PDBLST', 'List of residues'),
                ('PL2CHK', 'Connections to aromatic rings'),
                ('PL3CHK', 'Side chain planarity with hydrogens attached'),
                ('PLNCHK', 'Protein side chain planarities'),
                ('PRECHK', 'Missing backbone atoms.'),
                ('PUCCHK', 'Ring puckering in Prolines'),
                ('QUACHK', 'Directional Atomic Contact Analysis'),
                ('RAMCHK', 'Ramachandran'),
                ('ROTCHK', 'Rotamers'),
                ('SCOLST', 'List of symmetry contacts'),
                ('TO2CHK', 'Missing C-terminal groups'),
                ('TOPPOS', 'Ligand without know topology'),
                ('WGTCHK', 'Atomic occupancy check'),
                ('Hand',   '(Pro-)chirality or handness check')
               ]

    nameDict = NTdict()
    for n1,n2 in nameDefs:
        nameDict[n1] = n2
#            nameDict[n2] = n1 # Removed for efficiency.
    #end for
    nameDict.keysformat()

    recordKeyWordsToIgnore = { # Using a dictionary for fast key checks below.
                              "Bad":None,
                              "Date":None,
                              "DocURL":None,
                              "ID":None,
                              "LText":None,
                              "Poor":None,
                              "Program":None,
                              "Text":None,
                              "Text":None,
                              "Version":None
                              }
#    recordKeyWordsToIgnore.append( "IGNORE" ) # Added by JFD


    scriptBegin = """
# Generate WI script
# Set WI options
# Truncating errors in a PDBOUT table
SETWIF 593 100
# Should Q atoms be considered hydrogen atoms?
SETWIF 1505 1
# Read all models
#SETWIF 847 1
# Not adding C-terminal O if missing
SETWIF 1071 1
# We have an NMR structure (curiously set to No here)
SETWIF 1503 0
# IUPAC atom nomenclature
SETWIF 142 1
# Cutoff for reporting in the INP* routines (*100)
SETWIF 143 400
# General debug flag
# Should prevent problems such as:
# > 1b9q and many others: broken backbone/ERROR reading DSSP file
# > 1ehj Zero length in torsion calculation
SETWIF 1012 0
"""
    scriptPerModel = """
# Read the one model
%fulchk
$pdb_file
xxx

$mv check.db check_$modelNumberString.db

# Initialize the soup
%inisou

# Keep the line above empty.
"""

    scriptQuit = """
fullstop y
"""

# Run whatif with the script



    def __init__( self, rootPath = '.', molecule = None, **kwds ):
        NTdict.__init__( self, __CLASS__ = 'Whatif', **kwds )
        self.checks                = None
        self.molSpecificChecks     = None
        self.residueSpecificChecks = None
        self.atomSpecificChecks    = None
        self.residues              = None
        self.atoms                 = None
        self.molecule              = molecule
        self.rootPath              = rootPath
    #end def

    def path( self, *args ):
        """Return path relative to rootPath """
        return os.path.join( self.rootPath, *args )
    #end def

    def _splitLine( self, line ):
        """
            Internal routine to split a lineof the check.db file
            Return key, value tuple from line
        """
        a = line.split(':')
        return a[0].strip(),a[1].strip()
    #end def

    def _dictDictList( self, theDict, name, key ):
        """
            Internal routine that returns a NTlist instance for theDict[name][key].
            Also put in translated key.
        """
        d = theDict.setdefault( name, NTdict() )
        l = d.setdefault( key, NTlist() )
        if key in Whatif.nameDict():
            d[Whatif.nameDict[key]] = l
        #end if
        return l
    #end def

    def _parseCheckdb( self, modelCheckDbFileName = None, model = None, verbose = True ):
        """
            Parse check_001.db etc. Generate references to
            all checks. Storing the check data according to residue and atom.
            Return self on succes or None on error.
        """
        checkID = None # Just to keep pydev from complaining.
        isTypeFloat = False
        if not self.checks: # This will be called multiple times so don't overwrite.
            self.checks = NTlist()
        for line in AwkLike( modelCheckDbFileName ):
#            printDebug("DEBUG: read: "+line.dollar[0])
            if line.NF < 3:
                continue
            if line.dollar[2] != ':':
                printWarning("The line below was unexpectedly not parsed")
                printWarning(line.dollar[0])

            key, value = self._splitLine( line.dollar[0] )
            if Whatif.recordKeyWordsToIgnore.has_key(key):
                continue

#            printDebug("found key, value: [" + key + "] , [" + value + "]")
            if key == "Level":
                self[checkID]["Level"] = value
                continue
            if key == "Type":
                self[checkID]["Type"] = value
                if self[checkID]["Type"] == "FLOAT":
#                    printDebug("Setting type to float")
                    isTypeFloat = True
                continue
            if key == "Name":
                self[checkID]["Name"] = value
                continue
            if key == 'CheckID':
                checkID = value
#                printDebug("found check ID: " + checkID)
                if not Whatif.nameDict.has_key( checkID ):
                    printError("Read an unknown CheckID: "+checkID)
                    return None # Perhaps continue here and demote error above to a warning?
                isTypeFloat = False
                if not self.has_key( checkID ):
                    self[checkID] = NTdict( CheckID = checkID )
                    self.checks.append( self[checkID] )
                    printDebug("Appended check: "+checkID)
                continue
            #end if

#           Only allow values so lines like:
#            #    Value :  1.000
#            #    Qual  : BAD
            if key not in ( "Value", "Qual", ):
                printError( "Unexpected key, value")
                return None
            if not self[checkID].has_key(key):
                valueNTList = NTlist()
                for dummy in range(self.molecule.modelCount): # Shorter code for these 2 lines please JFD.
                    valueNTList.append(None)
                self[checkID].setdefault(key,valueNTList)
            if isTypeFloat and key == "Value":
                self[checkID][key][model] = float(value)
            else:
                self[checkID][key][model] = value
#            printDebug("For checkID   : "+checkID)
#            printDebug("For key       : "+key)
#            printDebug("For modelID   : "+`model`)
#            printDebug("For value     : "+value)
#            printDebug("For check     : "+`self[checkID]`)
#            printDebug("For keyed list: "+`self[checkID][key]`)
#            printDebug("For stored key: "+`self[checkID][key][model]`)
        #end for each line.

        # TODO: finish code hre.
        # Example of parsed data structure at this point:
#        self['HNDCHK']={
#            "Name": [ "A-   9-MET- C  nv", "A-   9-MET- C  nv"],
#            "Vale": [ 0.009, 0.100 ],
#                        }

    """ Put parsed data of all models into CING data model.
    """
    def _processCheckdb( self, verbose = True ):
        printMessage("Now processing the check results into CING data model")
        # Assemble the atom, residue and molecule specific checks
        # set the formats of each check easy printing
        self.molSpecificChecks     = NTlist()
        self.residueSpecificChecks = NTlist()
        self.atomSpecificChecks    = NTlist()

        self.mols     = NTdict(MyName="Mol")
        self.residues = NTdict(MyName="Res")
        self.atoms    = NTdict(MyName="Atom")
        levelIdList     = ["MOLECULE", "RESIDUE", "ATOM" ]
        selfLevels      = [ self.mols, self.residues, self.atoms ]
        selfLevelChecks = [ self.molSpecificChecks, self.residueSpecificChecks, self.atomSpecificChecks ]
        # sorting on mols, residues, and atoms
        printMessage("  for self.checks: " + `self.checks`)
        printMessage("  for self.checks count: " + `len(self.checks)`)
        for check in self.checks:
            if 'Level' not in check:
                raise CodeError("no Level attribute in check dictionary: "+check.CheckID)
            printDebug("attaching check: "+check.CheckID+" of type: "+check.Type + " to level: "+check.Level)
            idx = levelIdList.index( check.Level )
            if idx < 0:
                raise CodeError("Unknown Level ["+check.Level+"] in check:"+check.CheckID+' '+check.Text+"\n")
            selfLevelChecks[idx].append( check )
            check.keysformat()
        #end for

        checkIter = iter(selfLevelChecks)
        for levelEntity in selfLevels:
            levelCheck = checkIter.next()
            levelCheckStr = `levelCheck`
            # Ok so there is not Java substring method as in Java. Using a slice causes a
#            if len(levelCheckStr) > 80:
            levelCheckStr = levelCheckStr[0:80]
            printDebug("working on levelEntity: " + levelEntity.MyName +"levelCheck: " + levelCheckStr)
            for check in levelCheck:
                printDebug( 'check        : ' + `check`)
                printDebug( 'check.CheckID: ' + check.CheckID)
                if not ('Name' in check and 'Value' in check):
                    printError("Failed to find Name and Value attribute for this check.")
                    return None
                name = check.Name
                if not 'Qual' in check:
                    for value in check.Value:
                        self._dictDictList( levelEntity, name, check.CheckID ).append( value )
                else:
                    for value,qual in zip(check.Value, check.Qual):
                        self._dictDictList( levelEntity, name, check.CheckID ).append( (value, qual) )
                # JFD adds: this is a nice example to show how the values can be taken out again
                # JFD mods so it's clear from which residue value originates
                if len( levelEntity.values()):
                    print 'DEBUG below value is in residue:', levelEntity.values()[0]
                    print '>1', check.CheckID, levelEntity.values()[0].keys()
                    print '>2', check.CheckID, levelEntity.values()[0][check.CheckID]
            #end for
            # TODO: finish the code below.
#            for entity in levelEntity.values():
#                entity.keysformat()
#            levelEntity.keysformat()

        if verbose:
            printMessage('done with _processCheckdb')
        return 1 # for success
    #end def

    def _parseResAtmString( self, string ):
        """
            Internal routine to split the residue or atom identifier string
            of the check.db file.
            return a Molecule nametuple
        """
        elms = string.split('-')
        t = ['PDB',elms[0].strip(),int(elms[1])]
        if len(elms) == 4:
            t.append( elms[3].strip() )
        else:
            t.append( None )
        #end if

        return tuple( t )
    #end def

    def map2molecule( self ):
        """
            Replace the residue and atoms strings with references to the
            corresponding objects of molecule.
            Initiate a whatif attribute for every Molecule, Chain, Residue
            and Atom object.
        """
        for chain in self.molecule.allChains():
            chain.whatif = None
        #end for
        for res in self.molecule.allResidues():
            res.whatif = None
        #end for
        for atm in self.molecule.allAtoms():
            atm.whatif = None
        #end for

        self.molecule.whatif = self

        # Residues
        for r,c in self.residues.items():
            nameTuple = self._parseResAtmString( r )
            res = self.molecule.decodeNameTuple( nameTuple )
            #print '>',r, nameTuple, res
            if (res == None):
                raise CodeError('Error Whatif.map2molecule: mapping "%s" descriptor\n', r)
            else:
                res.whatif = c
            #endif
        #end for

        # Atoms
        for r,c in self.atoms.items():
            nameTuple = self._parseResAtmString( r )
            atm = self.molecule.decodeNameTuple( nameTuple )
            #print '>',r, nameTuple, atm
            if (atm == None):
                raise CodeError('Whatif.map2molecule: mapping "%s" descriptor\n', r)
            else:
                atm.whatif = c
            #endif
        #end for
    #end def

    def report( self ):
        return ''.join( file( self.path( Whatif.reportFile ), 'r').readlines())
    #end def
#end Class

def runWhatif( project, tmp=None ):
    """
        Run and import the whatif results per model.
        All models in the ensemble of the molecule will be checked.
        Set whatif references for Molecule, Chain, Residue and Atom instances
        or None if no whatif results exist
        returns 1 on success or None on any failure.
    """
    if not project.molecule:
        NTerror("No project molecule in runWhatCheck")
        return None

    path = project.path( project.molecule.name, project.moleculeDirectories.whatif )
    if not os.path.exists( path ):
        project.molecule.whatif = None
        for chain in project.molecule.allChains():
            chain.whatif = None
        for res in project.molecule.allResidues():
            res.whatif = None
        for atm in project.molecule.allAtoms():
            atm.whatif = None
        return None

    whatif = Whatif( rootPath = path, molecule = project.molecule )
    if project.molecule == None:
        NTerror('in runWhatif: no molecule defined\n')
        return None

    if project.molecule.modelCount == 0:
        NTerror('in runWhatif: no models for "%s"\n', project.molecule)
        return None

    for res in project.molecule.allResidues():
        if not (res.hasProperties('protein') or res.hasProperties('nucleic')):
            NTwarning('non-standard residue %s found and will be written out for What If' % `res`)

    models = NTlist(*range( project.molecule.modelCount ))

    whatifDir = project.mkdir( project.molecule.name, project.moleculeDirectories.whatif  )
#    TODO: check how to move this to a configurable location.

    #whatifPath       = os.path.join("/home","vriend","whatif")
    whatifPath       = os.path.dirname(cingPaths.whatif)
    whatifTopology   = os.path.join(whatifPath, "dbdata","TOPOLOGY.H")
    whatifExecutable = os.path.join(whatifPath, "DO_WHATIF.COM")

    copy(whatifTopology, os.path.join(whatifDir,"TOPOLOGY.FIL"))

    for model in models:
        modelNumber = model + 1
        fullname =  os.path.join( whatifDir, sprintf('model_%03d.pdb', modelNumber) )
        # WI prefers IUPAC like PDB now. In CING the closest is BMRBd?
        printMessage('==> Materializing model '+`modelNumber`+" to disk" )
        pdbFile = project.molecule.toPDB( model=model, convention = "BMRB" )
        if not pdbFile:
            printError("Failed to write a temporary file with a model's coordinate")
            return None
        pdbFile.save( fullname, verbose = False )
    #end for model

    scriptComplete = Whatif.scriptBegin
    for model in models:
        modelNumber = model + 1
        modelNumberString = sprintf('%03d', modelNumber)
        modelFileName = 'model_'+modelNumberString+".pdb"
#        fullname =  os.path.join( whatifDir, modelFileName )
        scriptModel = Whatif.scriptPerModel.replace("$pdb_file", modelFileName)
        scriptModel = scriptModel.replace("$modelNumberString", modelNumberString)
        scriptComplete += scriptModel
    #end for model
    scriptComplete += Whatif.scriptQuit
    # Let's ask the user to be nice and not kill us
    # estimate to do (400/7) residues per minutes as with entry 1bus on dual core intel Mac.
    totalNumberOfResidues = project.molecule.modelCount * len(project.molecule.allResidues())
    timeRunEstimatedInSeconds    = totalNumberOfResidues / 13.
    timeRunEstimatedInSecondsStr = sprintf("%.0f",timeRunEstimatedInSeconds)
    printMessage('==> Running What If checks on '+`totalNumberOfResidues`+
                 " residues for an estimated (13 protonated residues/s): "+timeRunEstimatedInSecondsStr+" seconds; please wait")
    if totalNumberOfResidues < 100:
        printMessage("It takes longer per residue for small molecules and few models")
    scriptFileName = "whatif.script"
    scriptFullFileName =  os.path.join( whatifDir, scriptFileName )
    open(scriptFullFileName,"w").write(scriptComplete)
    whatifProgram = ExecuteProgram( whatifExecutable, rootPath = whatifDir,
                             redirectOutput = True, redirectInputFromDummy = True )
    # The last argument becomes a necessary redirection into fouling What If into
    # thinking it's running interactively.
    now = time.time()
    if True:
        whatifExitCode = whatifProgram("script", scriptFileName )
    else:
        printDebug("Skipping actual whatif execution for testing")
        whatifExitCode = 0

    printDebug("Took number of seconds: " + sprintf("%8.1f", time.time() - now))
    if whatifExitCode:
        printError("Failed whatif checks with exit code: " + `whatifExitCode`)
        return None

    try:
        removeListLocal = ["PDBFILE", "pdbout.tex"]
        removeList = []
        for fn in removeListLocal:
            removeList.append( os.path.join(whatifDir, fn) )

#        for extension in [ "*.eps", "*.pdb", "*.LOG", "*.PDB", "*.DAT", "*.SCC", "*.sty", "*.FIG"]:
        for extension in [ "*.LOG", "*.DAT", "*.SCC", "*.sty", "*.FIG"]:
            for fn in glob(os.path.join(whatifDir,extension)):
                removeList.append(fn)
        for fn in removeList:
            if not os.path.exists(fn):
                printDebug("Expected to find a file to be removed but it doesn't exist: " + fn )
                continue
            printDebug("Removing: " + fn)
            os.unlink(fn)
    except:
        printWarning("Failed to remove all temporary what if files that were expected")

    for model in models:
        modelNumber = model + 1
        modelNumberString = sprintf('%03d', modelNumber)
        fullname =  os.path.join( whatifDir, sprintf('model_%03d.pdb', modelNumber), '.pdb' )
        del( fullname ) #TODO: isn't it os.unlink?
        modelCheckDbFileName = "check_"+modelNumberString+".db"
        printMessage('==> Parsing checks for model '+modelCheckDbFileName)
        modelCheckDbFullFileName =  os.path.join( whatifDir, modelCheckDbFileName )
        whatif._parseCheckdb( modelCheckDbFullFileName, model )
    #end for model

    printWarning("TODO: Processing is to be continued from here on.")
    return 1
    if not whatif._processCheckdb():
        printError("Failed to process check db")
        return None

#    whatif.map2molecule()

    return whatif # Success
#end def

# register the functions
methods  = [(runWhatif, None)]