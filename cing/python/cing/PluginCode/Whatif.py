"""
Whatif Module
First version: gv June 3, 2007
"""
# Fix these strings so we can get some automated code checking by pydev extensions.
# Also, we want to put these defs on top before the imports to prevent cycle in
# look up.
from cing import issueListUrl
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTplot import * #@UnusedWildImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import removeEmptyFiles
from cing.PluginCode.required.reqMatplib import MATPLIB_STR
from cing.PluginCode.required.reqWhatif import * #@UnusedWildImport
from cing.core.constants import * #@UnusedWildImport
from cing.core.parameters import cingPaths
from cing.core.parameters import plugins
from cing.setup import PLEASE_ADD_EXECUTABLE_HERE
from glob import glob
from shutil import copy
from string import upper

#if cingPaths.whatif == None or cingPaths.whatif == PLEASE_ADD_EXECUTABLE_HERE:
#    NTdebug("No whatif installed.")
#    raise ImportWarning(WHATIF_STR)
#NTmessage('Using Whatif')

scriptFileName = "whatif.script"

class WhatifResult( NTdict ):
    """
    Class to store valueList, qualList Whatif results per model
    """
    def __init__(self, checkID, level, modelCount ):
        NTdict.__init__( self, __CLASS__ = 'WhatifResult',
                         checkID = checkID,
                         alternate = None,
                         level   = level,
                         comment = Whatif.explain(checkID),
                       )
#        # Initialize the lists
        if cingNameDict.has_key(checkID):
            self.alternate = cingNameDict[checkID]
        for c  in  [ VALUE_LIST_STR, QUAL_LIST_STR]:
            self[c] = NTfill( None, modelCount)

        #self.keysformat()
    #end def

    def average(self, fmt='%5.2f +/- %4.2f'):
        """Return average of valueList as NTvalue object
        """
        theList = self[VALUE_LIST_STR]
        return NTaverage2(theList, fmt=fmt)

    def __str__(self):
        return '<WhatifResult %(checkID)s>' % self
    #end def

    def format(self):
        return sprintf(
"""%s WhatifResult %s (%s) %s
comment   = %s
alternate = %s
valueList = %s
qualList  = %s
""",                   dots, self.checkID, self.level, dots,
                       self.comment, self.alternate, self.valueList, self.qualList
                      )
#end class

class Whatif( NTdict ):
    """
    Class to use WHAT IF checks.

    Whatif.checks:                  NTlist instance of individual parsed checks
    Whatif.molSpecificChecks:       NTlist instance of those check pertaining to
                                    molecules; i.e Level : MOLECULE. Not implemented in What If yet.
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

    All file references relative to rootPath ('.' by default) using the .path()
    method.

    Instantiated only from runWhatif
    """

#              'Bond max Z',
    DEFAULT_RESIDUE_POOR_SCORES = {}
    DEFAULT_RESIDUE_BAD_SCORES = {}

    DEFAULT_RESIDUE_BAD_SCORES[  RAMCHK_STR ] =  -1.3
    DEFAULT_RESIDUE_POOR_SCORES[ RAMCHK_STR ] =  -1.0 # Guessing on basis of 1ai0, 1brv

    DEFAULT_RESIDUE_BAD_SCORES[  BBCCHK_STR ] =    3.0
    DEFAULT_RESIDUE_POOR_SCORES[ BBCCHK_STR ] =   10.0 # Guessing on basis of 1ai0, 1brv

    DEFAULT_RESIDUE_BAD_SCORES[  C12CHK_STR ] =  -1.2
    DEFAULT_RESIDUE_POOR_SCORES[ C12CHK_STR ] =  -0.9 # Guessing on basis of 1ai0, 1brv

    NUMBER_RESIDUES_PER_SECONDS = 7 # Was 13 before.

    debugCheck = 'BNDCHK'

    recordKeyWordsToIgnore = { # Using a dictionary for fast key checks below.
                              "Bad":None,
                              "Date":None,
                              "DocURL":None,
                              "ID":None,
                              "LText":None,
                              "Poor":None,
                              "Program":None,
                              "Text":None,
                              "Version":None
                              }
#    recordKeyWordsToIgnore.append( "IGNORE" ) # Added by JFD

    scriptBegin = """
# CING generated What If (WI) script
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
# Skip generation of EPS files in order to speed up this ordeal.
SETWIF 473 1
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

# Read again for separate options.
getmol
$pdb_file

# dolog # Fails as of yet with wsvacc due to a bug in WI
# wsvacc_$modelNumberString.log
# # Returns for each atom in the input file its solvent accessibility in A**2. Waters are neglected by this service.
# 0

# Get's written to OUTPUT.TXT but that's undocumented so I rather not use it...
%wsvacc

$mv OUTPUT.TXT wsvacc_$modelNumberString.log
# nolog

$mv check.db check_$modelNumberString.db

# Initialize the soup
%inisou

# Keep the line above empty.
"""

    scriptQuit = """

$sleep 10

end y
"""
#was:
#fullstop y

# Run whatif with the script



    def __init__( self, rootPath = '.', molecule=None, ranges = None, **kwds ):
        NTdict.__init__( self, __CLASS__ = 'Whatif', **kwds )
        self.checks                = None
        self.molSpecificChecks     = None
        self.residueSpecificChecks = None
        self.atomSpecificChecks    = None
        self.residues              = None
        self.atoms                 = None
        if not molecule:
            NTerror('Whatif.__init__: no molecule defined')
        self.molecule              = molecule
        self.rootPath              = rootPath
        self.ranges                = ranges
    #end def

    def path( self, *args ):
        """Return path relative to rootPath """
        return os.path.join( self.rootPath, *args )
    #end def

#    def _dictDictList( self, theDict, name, key ):
#        """
#            Internal routine that returns a NTlist instance for theDict[name][key].
#            Also put in translated key.
#        """
#        d = theDict.setdefault( name, NTdict() )
#        d[self.nameDict[key]] = d.setdefault( key, NTlist() )

    def _characterizeEnsembleScore(self, checkId, value, default=None):
        """Return characterization of Whatif value for ensemble checkId
        """

        if checkId == QUACHK_STR:
            if value < -3.0:
                return 'bad'
            elif value < -2.0:
                return 'poor'
            else:
                return default

        if checkId == NQACHK_STR:
            if value < -4.0:
                return 'bad'
            elif value < -3.0:
                return 'poor'
            else:
                return default

        if checkId == RAMCHK_STR:
            if value < -4.0:
                return 'bad'
            elif value < -3.0:
                return 'poor'
            else:
                return default

        if checkId == ROTCHK_STR:
            if value < -4.0:
                return 'bad'
            elif value < -3.0:
                return 'poor'
            else:
                return default

        if checkId == BBCCHK_STR:
            if value < -4.0:
                return 'bad'
            elif value < -3.0:
                return 'poor'
            else:
                return default

        # 2nd part
        if checkId == BNDCHK_STR:
            if value < 0.666:
                return 'tight'
            elif value > 1.5:
                return 'loose'
            else:
                return default

        if checkId == ANGCHK_STR:
            if value < 0.666:
                return 'tight'
            elif value > 1.5:
                return 'loose'
            else:
                return default

        if checkId == OMECHK_STR:
            if value > 7.0:
                return 'loose'
            elif value < 4.0:
                return 'tight'
            else:
                return default

        if checkId == PLNCHK_STR:
            if value < 0.666:
                return 'tight'
            elif value > 2.0:
                return 'loose'
            else:
                return default

        if checkId == HNDCHK_STR:
            if value > 0.0 and value > 1.5: #GV strange clause!
                return 'loose'
            else:
                return default

        if checkId == INOCHK_STR:
            if value > 1.16:
                return 'unusual'
            else:
                return default

        return default
    #end def

    def _processWhatifSummary( self, fileName='pdbout.txt' ):
        """Parse the Whatif summary indicated by fileName.

           Store the overall check data according to each model as WhatifResult instances
           in molecule[WHATIF_STR] NTdict instance.

           Return None on success or True on error.
           """
        if not os.path.exists(fileName):
            NTerror('Whatif._processWhatifSummary: file "%s" not found.', fileName)
            return True

        self.molecule[WHATIF_STR] = NTdict()

        modelIdx = -1

        for line in AwkLike( fileName, minNF = 1, separator=':' ):
            l = line.dollar[0]
            if len(l) < 2: # to prevent recursion bug in AwkLike code.
                continue
#            NTdebug("Read line: "+l)
#            NTdebug("DEBUG: read line dollar 1: [%s]" % line.dollar[1])
#            NTdebug("DEBUG: read line dollar 2: [%s]" % line.dollar[2])

            if l.find( 'Summary report for users of a structure') > 0:
#                NTdebug('Found summary report and increasing model idx: %d' % modelIdx)
                modelIdx += 1
                continue

            checkId = None
            if l.startswith( '  1st generation packing quality'):
                checkId = QUACHK_STR
            if l.startswith( '  2nd generation packing quality'):
                checkId = NQACHK_STR
            if l.startswith( '  Ramachandran plot appearance'):
                checkId = RAMCHK_STR
            if l.startswith( '  chi-1/chi-2 rotamer normality'):
                checkId = C12CHK_STR
            if l.startswith( '  Backbone conformation'):
                checkId = BBCCHK_STR
# Second part.
            if l.startswith( '  Bond lengths'):
                checkId = BNDCHK_STR
            if l.startswith( '  Bond angles'):
                checkId = ANGCHK_STR
            if l.startswith( '  Omega angle restraints'):
                checkId = OMECHK_STR
            if l.startswith( '  Side chain planarity'):
                checkId = PLNCHK_STR
            if l.startswith( '  Improper dihedral distribution'):
                checkId = HNDCHK_STR
            if l.startswith( '  Inside/Outside distribution'):
                checkId = INOCHK_STR

            if not checkId:
#                NTdebug("Failed to find any specific check, continuing to look")
                continue

#            NTdebug("Processing checkId %s" % checkId)

            # if needed add WhatifResult instance
            # Do not use setdefault() as it generate too much overhead this way
            if not self.molecule[WHATIF_STR].has_key(checkId):
                self.molecule[WHATIF_STR][checkId] = WhatifResult( checkId, level='MOLECULE', modelCount = self.molecule.modelCount)
                # optionally add reference to alternate Cing name
                cingId = cingCheckId( checkId )
                if cingId != checkId:
                    self.molecule[WHATIF_STR][cingId] = self.molecule[WHATIF_STR][checkId]

            # Happens for entry 2kqu line:
            #   Bond angles           STOP Normal end of WHAT IF.
            if len(line.dollar) < 3:
                NTerror("Failed to find at least two elements after splitting the line on a colon;  ")
                NTmessage("See also issue: %s%d" % (issueListUrl, 242))
                return True


            valueStringList  = line.dollar[2].strip().split()
#            NTdebug("valueStringList: %s" % valueStringList)
            if not valueStringList:
                NTerror("Failed to get valueStringList for check [%s] from line: [%s]" % (checkId, line))
                return True

            # Very rarely it happens that the end-message of whatif gets intermingled with the values parsed here:
#  Side chain planarity           : STOP Normal end of WHAT IF.
#  0.324 (tight)
            # So wrap this parse in a try.
            try:
                value = float(valueStringList[0])
            except:
                NTerror("Failed to parse value as a float for check [%s] for line [%s] from What If string [%s]; setting value to a None" % (
                    checkId,line,valueStringList[0]))
                NTmessage("See also issue: %s%d" % (issueListUrl, 242))
                value = None

#            NTdebug('modelIdx: %d' % modelIdx)
            if modelIdx < 0:
                # This is expected for when What If wasn't offered any protein residues.
#TODO: only report useful info.
#                NTmessage('Failed to have increased model idx at least once for checkId %s' % checkId)
                continue

            ensembleValueList = getDeepByKeysOrAttributes( self.molecule, WHATIF_STR, checkId, VALUE_LIST_STR )
            ensembleValueList[modelIdx] = value

            ensembleQualList = getDeepByKeysOrAttributes( self.molecule, WHATIF_STR, checkId, QUAL_LIST_STR )
            ensembleQualList[modelIdx] = self._characterizeEnsembleScore(checkId, value)
        # end for line
        self.molecule[WHATIF_STR].keysformat()
    #end def

    def _makeSummary(self):
        """
        Return a Whatif summary from overall Molecule scores
        """
        # GV summaryCheckIdList moved to Class
        summaryCheckIdMandatoryList = [ BNDCHK_STR, ANGCHK_STR ]
        valueList = [ ]
        qualList  = [ ]
        for checkId in summaryCheckIdList:
            ensembleValueList = getDeepByKeysOrAttributes( self.molecule, WHATIF_STR, checkId, VALUE_LIST_STR)
            if not ensembleValueList:
                msg = "empty ensembleValueList for checkId %s" % checkId
                if checkId in summaryCheckIdMandatoryList:
                    NTwarning(msg)
#                else:
#                    NTdebug(msg)
                ensembleValueList = NTlist()
            # end if
            ensembleValueList.average()
            valueList.append(ensembleValueList)
#            NTdebug('ensembleValueList found: %s' % valueList[-1])

            q = self._characterizeEnsembleScore(checkId, ensembleValueList.av, None)
            if q != None:
                qualList.append( '('+q+')' )
            else:
                qualList.append( '' )
       # end for
        fmt = "%7.3f"
        spaceCount = 7
        rangesStr = ', ranges "all"' # None is not nice to print.
        if self.ranges:
            residueCount = self.molecule.ranges2resCount(self.ranges)
            rangesStr = ', ranges "%s" (%s residues)' % (self.ranges, residueCount)

        summary = """
WHATIF summary report of molecule "%s"%s

- This is an overall summary of the quality of the structure as
  compared with current reliable structures.
- The first part of the table shows a number of constraint-independent
  quality indicators.
- The second part of the table mostly gives an impression of how well
  the model conforms to common refinement constraint values.
- The standard deviation shows the variation over models in the ensemble
  where appropriate.

Structure Z-scores, positive is better than average:
    1st generation packing quality : %s +/- %s %s
    2nd generation packing quality : %s +/- %s %s
    Ramachandran plot appearance   : %s +/- %s %s
    chi-1/chi-2 rotamer normality  : %s +/- %s %s
    Backbone conformation          : %s +/- %s %s

RMS Z-scores, should be close to 1.0:
    Bond lengths                   : %s +/- %s %s
    Bond angles                    : %s +/- %s %s
    Omega angle restraints         : %s +/- %s %s
    Side chain planarity           : %s +/- %s %s
    Improper dihedral distribution : %s +/- %s %s
    Inside/Outside distribution    : %s +/- %s %s
"""         % (self.molecule.name, rangesStr,
               val2Str(valueList[0].av,fmt, spaceCount),val2Str(valueList[0].sd,fmt, spaceCount), qualList[0],
               val2Str(valueList[1].av,fmt, spaceCount),val2Str(valueList[1].sd,fmt, spaceCount), qualList[1],
               val2Str(valueList[2].av,fmt, spaceCount),val2Str(valueList[2].sd,fmt, spaceCount), qualList[2],
               val2Str(valueList[3].av,fmt, spaceCount),val2Str(valueList[3].sd,fmt, spaceCount), qualList[3],
               val2Str(valueList[4].av,fmt, spaceCount),val2Str(valueList[4].sd,fmt, spaceCount), qualList[4],
               val2Str(valueList[5].av,fmt, spaceCount),val2Str(valueList[5].sd,fmt, spaceCount), qualList[5],
               val2Str(valueList[6].av,fmt, spaceCount),val2Str(valueList[6].sd,fmt, spaceCount), qualList[6],
               val2Str(valueList[7].av,fmt, spaceCount),val2Str(valueList[7].sd,fmt, spaceCount), qualList[7],
               val2Str(valueList[8].av,fmt, spaceCount),val2Str(valueList[8].sd,fmt, spaceCount), qualList[8],
               val2Str(valueList[9].av,fmt, spaceCount),val2Str(valueList[9].sd,fmt, spaceCount), qualList[9],
               val2Str(valueList[10].av,fmt, spaceCount),val2Str(valueList[10].sd,fmt, spaceCount), qualList[10]
               )

        self.molecule[WHATIF_STR].summary = summary

        self.molecule[WHATIF_STR].keysformat()
        return summary
    #end def


    def _parseCheckdb( self, modelCheckDbFileName, model ):
        """Parse check_001.db etc. Generate references to
           all checks. Storing the check data according to residue and atom.
           Return self on success or True on error.

        Example of parsed data structure:
        E.g. check can have attributes like:
        [                                          # checks
            {                                      # curCheck
            "checkID":  "BNDCHK"
            "level":    "RESIDUE"
            "type":     "FLOAT"
            "locId": {                             # curLocDic
                "'A- 189-GLU'"                     # curLocId
                    : {                            # curListDic
                    "valeList": [ 0.009, 0.100 ]
                    "qualList": ["POOR", "GOOD" ]
                    },
                "'A- 188-ILE'": {
                    "valeList": [ 0.01, 0.200 ]
                    "qualList": ["POOR", "GOOD" ]
                    }}},]
           """

        # Parser uses sense of current items as per below.
        curModelId = model
        curCheck   = None # Can be used to skip ahead.
        curLocId   = None
        curLocDic  = None
        curListDic = None
        isTypeFloat= False

        if not self.checks: # This will be called multiple times so don't overwrite.
            self.checks = NTlist()

        if not os.path.exists(modelCheckDbFileName):
            NTerror('Whatif._parseCheckdb: file "%s" not found.', modelCheckDbFileName)
            return True

        for line in AwkLike( modelCheckDbFileName, minNF = 3 ):
#            NTdebug("DEBUG: read: "+line.dollar[0])
            if line.dollar[2] != ':':
                NTwarning('Whatif._parseCheckdb: The line:\n   "%s"\nwas unexpectedly not parsed, expected second field to be a semicolon.',
                          line.dollar[0]
                         )
                continue

#            Split a line of the check.db file
            a      = line.dollar[0].split(':')
            key    = a[0].strip()
            value  = a[1].strip()

            if self.recordKeyWordsToIgnore.has_key(key):
                continue

            if key == 'CheckID':
                curCheck = None
                checkID = value # local var within this 'if' statement.
#                NTdebug("found check ID: " + checkID)
                if not nameDict.has_key( checkID ):
                    NTwarning("Whatif._parseCheckdb: Skipping an unknown CheckID: "+checkID)
                    continue
#                if self.debugCheck != checkID:
##                    NTdebug("Skipping a check not to be debugged: "+checkID)
#                    continue
                isTypeFloat = False

                if self.has_key( checkID ):
                    curCheck = self.get(checkID)
                else:
                    curCheck = NTdict()
                    self.checks.append( curCheck )
                    curCheck[CHECK_ID_STR] = checkID
                    self[ checkID ] = curCheck
#                    NTdebug("Appended check: "+checkID)
                # Set the curLocDic in case of the first time otherwise get.
                curLocDic = curCheck.setdefault(LOC_ID_STR, NTdict())
                continue
            if not curCheck: # First pick up a check.
                continue

#            NTdebug("found key, value: [" + key + "] , [" + value + "]")
            if key == "Text":
                curCheck[TEXT_STR] = value
                continue
            if key == "Level":
                curCheck[LEVEL_STR] = upper(value) # check Hand has level "Residue" which should be upped.
                continue
            if key == "Type":
                curCheck[TYPE_STR] = value
                if value == "FLOAT":
                    isTypeFloat = True
                continue
            if key == "Name":
                curLocId = value

                # do NOT!! use setdefault routine because it will generate many times
                # an expensive WhatifResult dummy first
                if not curLocDic.has_key( curLocId ):
                    curLocDic[curLocId] = WhatifResult(checkID, curCheck[LEVEL_STR], self.molecule.modelCount)

                curListDic = curLocDic[curLocId]
                continue

#           Only allow values so lines like:
#            #    Value :  1.000
#            #    Qual  : BAD
            if key == "Value":
                keyWord = VALUE_LIST_STR
            elif  key == "Qual":
                keyWord = QUAL_LIST_STR
            else:
                NTerror( "Whatif._parseCheckdb: Expected key to be Value or Qual but found key, value pair: [%s] [%s]" % ( key, value ))
                return None

            if curListDic==None or not curListDic.has_key( keyWord ):
                NTerror( "Whatif._parseCheckdb, line %d: Expected key %s for WhatifResult dict %s", line.NR, keyWord, curListDic)

            else:
                itemNTlist = curListDic[ keyWord ]
#            NTdebug("a itemNTlist: "+`itemNTlist` )

            if isTypeFloat:
                itemNTlist[curModelId] = float(value)
            else:
                itemNTlist[curModelId] = value
#            NTdebug("c itemNTlist: "+`itemNTlist` )
#            NTdebug("For key       : "+key)
#            NTdebug("For modelID   : "+`model`)
#            NTdebug("For value     : "+value)
#            NTdebug("For check     : "+`curCheck`)
#            NTdebug("For keyed list: "+`curCheck[key]`)
#            NTdebug("For stored key: "+`curCheck[key][modelId]`)
        #end for each line.

    def _processCheckdb( self   ):
        """
        Put parsed data of all models into CING data model as
        WhatifResult instances

        Return None for success

        Example of processed data structure attached to say a residue:

            whatif.ANGCHK.valueList : [ 0.009, 0.100 ]
            whatif.ANGCHK.qualList  : ["POOR", "GOOD" ]

            whatif.BNDCHK.valueList : [ 0.009, 0.100 ]
            whatif.BNDCHK.qualList  : [ None, None ]

        """

#        NTdetail("==> Processing the WHATIF results into CING data model")
        # Assemble the atom, residue and molecule specific checks
        # set the formats of each check easy printing
#        self.molecule.setAllChildrenByKey( WHATIF_STR, None)
#        self.molecule.whatif = self # is self and that's asking for luggage
        # Later

#        self.molSpecificChecks     = NTlist()
        self.residueSpecificChecks = NTlist()
        self.atomSpecificChecks    = NTlist()

#        self.mols     = NTdict(MyName="Mol")
        self.residues = NTdict(MyName="Res")
        self.atoms    = NTdict(MyName="Atom")

        levelIdList     = [ RES_LEVEL, ATOM_LEVEL ]
        selfLevels      = [ self.residues, self.atoms ]
        selfLevelChecks = [ self.residueSpecificChecks, self.atomSpecificChecks ]
        # sorting on mols, residues, and atoms
#        NTmessage("  for self.checks: " + `self.checks`)
#        NTdebug("  for self.checks count: " + `len(self.checks)`)

#        msgBadWiDescriptor = "See also %s%s" % (issueListUrl,10)
#        msgBadWiDescriptor += "\n or %s%s" % (issueListUrl,4)

        for check in self.checks:
            if LEVEL_STR not in check:
                NTerror("Whatif._processCheckdb: no level attribute in check dictionary: "+check[CHECK_ID_STR])
                NTerror("check dictionary: "+`check`)
                return True
#            NTdebug("attaching check: "+check[CHECK_ID_STR]+" of type: "+check[TYPE_STR] + " to level: "+check[LEVEL_STR])
            if check[LEVEL_STR] == 'MOLECULE':
#                NTdebug("Skipping any check related to this level for now; for now only the check labeled FATAL")
                continue
            idx = levelIdList.index( check[LEVEL_STR] )
            if idx < 0:
                NTerror("Whatif._processCheckdb: Unknown Level ["+check[LEVEL_STR]+"] in check:"+check[CHECK_ID_STR]+' '+check[TEXT_STR])
                return True
            selfLevelChecks[idx].append( check )
            check.keysformat()
        #end for

        checkIter = iter(selfLevelChecks)
        for _levelEntity in selfLevels:
            levelCheck = checkIter.next()
#            NTdebug("working on levelEntity: " + levelEntity.MyName +"levelCheck: " + `levelCheck`[:80])
            for check in levelCheck:
#                checkId = check[CHECK_ID_STR]
#                NTdebug( 'check        : ' + `check`)
#                NTdebug( 'check[CHECK_ID_STR]: ' + checkId)
                if not check.has_key(LOC_ID_STR):
#                    NTdebug("Whatif._processCheckdb: There is no %s attribute, skipping check: [%s]" % ( LOC_ID_STR, check ))
#                    NTdebug("  check: "+ `check`)
                    continue
                curLocDic = check[LOC_ID_STR]
                if not curLocDic:
#                    NTdebug("Skipping empty locationsDic")
                    continue

                for curLocId in curLocDic.keys():
                    curListDic = curLocDic[curLocId]
#                    NTdebug("Working on curLocId:   " + `curLocId`)
#                    NTdebug("Working on curListDic: " + `curListDic`)

                    nameTuple = self.translateResAtmString( curLocId )
                    if not nameTuple:
#                        NTwarning(msgBadWiDescriptor+'\nWhatif._processCheckdb: parsing entity "%s" what if descriptor' % curLocId)
                        NTwarning('Whatif._processCheckdb: parsing entity "%s" what if descriptor' % curLocId)
                        continue
                    entity = self.molecule.decodeNameTuple( nameTuple ) # can be a chain, residue or atom level object
                    if not entity:
                        NTdebug('Whatif._processCheckdb: mapping entity "%s" descriptor, tuple %s', curLocId, nameTuple)
                        continue
                    #NTdebug("adding to entity: " + `entity`)
                    entityWhatifDic = entity.setdefault(WHATIF_STR, NTdict())
                    #NTdebug("adding to entityWhatifDic: " + `entityWhatifDic`)

                    # GV direct linking using the WhatifResult object
                    entityWhatifDic[curListDic.checkID] = curListDic
                #end for
            #end for
        #end for
    #end def

    def translateResAtmString( self, string, convention=IUPAC):
        """Internal routine to split the residue or atom identifier string
            of the check.db file. E.g.:
            A- 187-HIS- CB
            A- 177-GLU
            return None for error

            Version of whatif Version  : 8.0 (20100310-0056) uses formats like:
Name   :    0 ; A    ;  171 ; VAL  ; _
Name   :    0 ; A    ;  171 ; VAL  ; _    ;  CA  ; _
Name   :    0 ; A    ;   40 ; THR  ; _    ; HG21 ; _

                ^ Chain Id
                        ^ Res Id            ^ Atom Id
            """
        # New or old format.
        if string.find(';')>=0:
            try:
                a = string.split(';')
                a = [el.strip() for el in a]
#In [5]: [el.strip() for el in a.split(';')]
#Out[5]: ['Name   :    0', 'A', '171', 'VAL', '_', 'CA', '_']
#                for i,_s in enumerate(a): # stupid construction; jfd needs to look up list comprehension.
#                    a[i] = a[i].strip()

                chId = a[1]
                resId = int(a[2])
                atomId = None
                if len(a) == 7: # Is there an atom name too?
                    atomId = a[5]
                return tuple( [convention,chId,resId,atomId] )
            except:
                return None
        else:
            try:
                a = string.split('-')
                t = [convention,a[0].strip(),int(a[1]), None]
                if len(a) == 4: # Is there an atom name too?#                print '>', a
                    try:
                        _i = int(a[3])    # @TODO this is a whatif bug and should not be possible
                    except:
                        t[3] = a[3].strip()
                return tuple( t )
            except:
                return None
    #end def

    def report( self ):
        return ''.join( file( self.path( Whatif.reportFile ), 'r').readlines())

    def explain( checkID=None ):
        """
        Static method to return a textual explanation of whatif checkID or all checkID's if None

        Returns None if no such explanation exists
        """
        if checkID == None:
            return nameDict.format()
        elif checkID!=None and nameDict.has_key(checkID):
            return nameDict[checkID]
        else:
            return None
    #end def
    explain = staticmethod(explain)
#end Class


def createHtmlWhatif(project, ranges=None):
    """ Read out wiPlotList to see what get's created. """

    if not getDeepByKeysOrAttributes(plugins, MATPLIB_STR, IS_INSTALLED_STR):
        NTdebug('Skipping createHtmlWattos because no matplib installed.')
        return
    from cing.PluginCode.matplib import MoleculePlotSet #@UnresolvedImport

    mol = project.molecule
#    wiPlotList.append( ('_01_backbone_chi','QUA/RAM/BBC/C12') )
    # The following object will be responsible for creating a (png/pdf) file with
    # possibly multiple pages
    # Level 1: row
    # Level 2: against main or alternative y-axis
    # Level 3: plot parameters dictionary (extendable).
    keyLoLoL = []
    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          QUACHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = shortNameDict[  QUACHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          RAMCHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = shortNameDict[  RAMCHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          BBCCHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = shortNameDict[  BBCCHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowAlte = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          C12CHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowAlte[ KEY_LIST_STR] = [ WHATIF_STR,          ROTCHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = shortNameDict[  C12CHK_STR ]
    plotAttributesRowAlte[ YLABEL_STR]   = shortNameDict[  ROTCHK_STR ]
#        plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR]   = True
    keyLoLoL.append( [ [plotAttributesRowMain], [plotAttributesRowAlte] ] )

#    printLink = os.path.join(
#                project.rootPath( project.name )[0],
#                project.molecule.name,
#                project.moleculeDirectories.whatif,
#                mol.name + wiPlotList[-1][0] + ".pdf" )

#gv
    printLink = project.moleculePath( 'whatif', mol.name + wiPlotList[0][0] + ".pdf" )

    moleculePlotSet = MoleculePlotSet(project=project, ranges=ranges, keyLoLoL=keyLoLoL )
    moleculePlotSet.renderMoleculePlotSet( printLink, createPngCopyToo=True  )

#    wiPlotList.append( ('_02_bond_angle','BND/ANG/NQA/PLNCHK') )
    keyLoLoL = []
    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          BNDCHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = shortNameDict[  BNDCHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          ANGCHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = shortNameDict[  ANGCHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          NQACHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = shortNameDict[  NQACHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowAlte = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          PLNCHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowAlte[ KEY_LIST_STR] = [ WHATIF_STR,          PL2CHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = shortNameDict[  PLNCHK_STR ]
    plotAttributesRowAlte[ YLABEL_STR]   = shortNameDict[  PL2CHK_STR ]
#        plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR]   = True
    keyLoLoL.append( [ [plotAttributesRowMain], [plotAttributesRowAlte] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          PL3CHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = shortNameDict[  PL3CHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )

#    printLink = os.path.join(
#                project.rootPath( project.name )[0],
#                mol.name,
#                project.moleculeDirectories.whatif,
#                mol.name + wiPlotList[-1][0] + ".pdf" )
#gv
    printLink = project.moleculePath( 'whatif', mol.name + wiPlotList[1][0] + ".pdf" )

    moleculePlotSet = MoleculePlotSet(project=project, ranges=ranges, keyLoLoL=keyLoLoL )
    moleculePlotSet.renderMoleculePlotSet( printLink, createPngCopyToo=True  )


#    wiPlotList.append( ('_03_steric_acc_flip','BMP/ACC/FLP/CHI') )
    keyLoLoL = []
    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          BMPCHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = shortNameDict[  BMPCHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowAlte = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          ACCLST_STR,         VALUE_LIST_STR ]
    plotAttributesRowAlte[ KEY_LIST_STR] = [ WHATIF_STR,          INOCHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = shortNameDict[  ACCLST_STR ]
    plotAttributesRowAlte[ YLABEL_STR]   = shortNameDict[  INOCHK_STR ]
#        plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR]   = True
    keyLoLoL.append( [ [plotAttributesRowMain], [plotAttributesRowAlte] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          FLPCHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = shortNameDict[  FLPCHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          CHICHK_STR,         VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR]   = shortNameDict[  CHICHK_STR ]
    keyLoLoL.append( [ [plotAttributesRowMain] ] )


#    printLink = os.path.join(
#                project.rootPath( project.name )[0],
#                mol.name,
#                project.moleculeDirectories.whatif,
#                mol.name + wiPlotList[-1][0] + ".pdf" )
#gv
    printLink = project.moleculePath( 'whatif', mol.name + wiPlotList[2][0] + ".pdf" )

    moleculePlotSet = MoleculePlotSet(project=project, ranges=ranges, keyLoLoL=keyLoLoL )
    moleculePlotSet.renderMoleculePlotSet( printLink, createPngCopyToo=True  )
#end def


def runWhatif( project, ranges=None, parseOnly=False ):
    """
        Run and import the whatif results per model.

        All models in the ensemble of the molecule will be checked.
        Set whatif references for Molecule, Chain, Residue and Atom instances
        or None if no whatif results exist

        returns True on error.
    """

    if cingPaths.whatif == None or cingPaths.whatif == PLEASE_ADD_EXECUTABLE_HERE:
        NTmessage("No whatif installed so skipping this step")
        return

    if not project.molecule:
        NTerror("runWhatif: no molecule defined")
        return True
    mol = project.molecule
    if mol.modelCount == 0:
        NTwarning('runWhatif: no models for "%s"', mol)
        return

    path = project.moleculePath( 'whatif' )
    if not os.path.exists( path ):
        NTerror('runWhatif: path "%s" does not exist', path)
        return True

    #Specific Whatif requirement : no spaces in path because it will crash
    absPath = os.path.abspath(path)
    if len(absPath.split()) > 1:
        NTerror('runWhatif: absolute path "%s" contains spaces. This will crash Whatif.', absPath)
        return True

    if ranges == None:
        ranges = mol.ranges
    # core Whatif object, allows running and parsing of whatif
    whatif = Whatif( rootPath = path, molecule = mol, ranges = ranges )
    mol.runWhatif = whatif
    del ranges # only use whatif.ranges now.
    useRanges = mol.useRanges(whatif.ranges)
#    NTdebug("In runWhatif ranges: %s useRanges %s" % (whatif.ranges, useRanges))

    residueList = mol.allResidues()
    if useRanges:
        residueList = mol.ranges2list(whatif.ranges)
        if residueList == None:
            NTerror("Failed ranges2list in Whatif")
            return True
        if not residueList:
            NTerror("Empty list of residues in Whatif")
            return True
        whatif.ranges = mol.rangesToExpandedRanges(whatif.ranges)
        if mol.rangesIsAll(whatif.ranges):
            NTerror("Non fatal code error but ranges can't be all if they are to be 'used'; don't worry code will still function fine.")

    numberOfResidues = len(residueList)
    if numberOfResidues == 0:
        NTerror("No residues to run Whatif on")
        return True

    models = NTlist(*range( mol.modelCount ))

    whatifDir = project.mkdir( mol.name, project.moleculeDirectories.whatif  )
    whatifStatus = project.whatifStatus

    if not parseOnly:

        whatifPath       = os.path.dirname(cingPaths.whatif)
        whatifTopology   = os.path.join(whatifPath, "dbdata","TOPOLOGY.H")
        whatifExecutable = os.path.join(whatifPath, "DO_WHATIF.COM")


        whatifStatus.nonStandardResidues = NTlist()
        whatifStatus.path                = path
        whatifStatus.models              = models
        whatifStatus.completed           = False
        whatifStatus.parsed              = False
        whatifStatus.time                = None
        whatifStatus.exitCode            = None


        for res in residueList:
            if not (res.hasProperties('protein') or res.hasProperties('nucleic')):
                if not res.hasProperties('HOH'): # don't report waters
                    NTmessage('runWhatif: non-standard residue %s found and will be written out for What If' % `res`)
                whatifStatus.nonStandardResidues.append(repr(res))
        #end for

        copy(whatifTopology, os.path.join(whatifDir,"TOPOLOGY.FIL"))

        for model in models:
            fullname =  os.path.join( whatifDir, sprintf('model_%03d.pdb', model) )
            # WI prefers IUPAC like PDB now. In CING the closest is IUPAC?
#            NTdebug('==> Materializing model '+`model`+" to disk" )
            pdbFile = mol.toPDB( fullname, model=model, ranges=whatif.ranges, convention = IUPAC)
#                                 useRangesForLoweringOccupancy=useRanges )
            if not pdbFile:
                NTerror("runWhatif: Failed to write a temporary file with a model's coordinate")
                return True

        scriptComplete = Whatif.scriptBegin
        for model in models:
            modelNumberString = sprintf('%03d', model)
            modelFileName = 'model_'+modelNumberString+".pdb"
            scriptModel = Whatif.scriptPerModel.replace("$pdb_file", modelFileName)
            scriptModel = scriptModel.replace("$modelNumberString", modelNumberString)
            scriptComplete += scriptModel
        scriptComplete += Whatif.scriptQuit
        # Let's ask the user to be nice and not kill us
        # estimate to do (400/7) residues per minutes as with entry 1bus on dual core intel Mac.
        totalNumberOfResidues = mol.modelCount * numberOfResidues
        timeRunEstimatedInSeconds    = totalNumberOfResidues / Whatif.NUMBER_RESIDUES_PER_SECONDS

        timeRunEstimatedList = timedelta2HoursMinutesAndSeconds(timeRunEstimatedInSeconds)
        # Uncorrected for discarded residues.
        msg = '==> Running What If checks on %s residues, %s model(s) for an estimated (%s residues/s):' % (
              numberOfResidues, mol.modelCount, Whatif.NUMBER_RESIDUES_PER_SECONDS)
        msg += ' %s hours, %s minutes and %s seconds; please wait' % timeRunEstimatedList
        NTmessage(msg)
#        if totalNumberOfResidues < 100:
#            NTmessage("It takes much longer per residue for a small molecule/ensemble")

        scriptFullFileName =  os.path.join( whatifDir, scriptFileName )
        open(scriptFullFileName,"w").write(scriptComplete)
        whatifProgram = ExecuteProgram( whatifExecutable, rootPath = whatifDir,
                                        redirectOutput = True, redirectInputFromDummy = True )
        # The last argument becomes a necessary redirection into fouling What If into
        # thinking it's running interactively.
        now = time.time()
        whatifExitCode = whatifProgram("script", scriptFileName )
#        NTdebug("Took number of seconds: " + sprintf("%8.1f", time.time() - now))
        whatifStatus.exitCode  = whatifExitCode
        whatifStatus.time      = sprintf("%.1f", time.time() - now)
#        NTdebug('runWhatif: exitCode %s,  time: %s', whatifStatus.exitCode, whatifStatus.time)
        whatifStatus.keysformat()

        if whatifExitCode:
            NTerror("runWhatif: Failed whatif checks with exit code: " + `whatifExitCode`)
            return True

        whatifStatus.completed = True
#        NTdebug("Setting what if status completed to %s" % whatifStatus.completed)
    else:
#        NTdebug("Skipping actual whatif execution")
        whatifExitCode = 0
    #end if


#    NTdebug('Parsing whatif checks ')

    # clear the whatif data structure
    if mol.has_key(WHATIF_STR):
        del(mol[WHATIF_STR])
    for chain in mol.allChains():
        if chain.has_key(WHATIF_STR):
            del(chain[WHATIF_STR])
    for res in mol.allResidues():
        if res.has_key(WHATIF_STR):
            del(res[WHATIF_STR])
    for atm in mol.allAtoms():
        if atm.has_key(WHATIF_STR):
            del(atm[WHATIF_STR])

    whatifStatus.parsed = False
#    for model in NTprogressIndicator(models):
    for model in models:
        modelNumberString = sprintf('%03d', model)
#        fullname =  os.path.join( whatifDir, sprintf('model_%03d.pdb', model) )
#        os.unlink( fullname )
        modelCheckDbFileName = "check_"+modelNumberString+".db"
#        NTmessageNoEOL('.')
        modelCheckDbFullFileName =  os.path.join( whatifDir, modelCheckDbFileName )

        if whatif._parseCheckdb( modelCheckDbFullFileName, model ):
            NTerror("\nrunWhatif: Failed to parse check db %s", modelCheckDbFileName)
            return True
        #end if
    #end for

    if whatif._processCheckdb():
        NTerror("runWhatif: Failed to process check db")
        return True

#    pathPdbOut = os.path.join(path, 'pdbout.txt' ) has only one model!
    pathPdbOut = os.path.join(path, 'DO_WHATIF.out0' )
    if not os.path.exists(pathPdbOut): # Happened for 1ao2 on production machine; not on development...
        NTerror("Path does not exist: %s" % (pathPdbOut))
        return True

    if whatif._processWhatifSummary(pathPdbOut):
        NTerror("runWhatif: Failed to process WHATIF summary file")
        return True

    whatif._makeSummary()

    # complete the whatif data structure with NoneObjects
    if not mol.has_key(WHATIF_STR):
        mol[WHATIF_STR] = NoneObject
    for chain in mol.allChains():
        if not chain.has_key(WHATIF_STR):
            chain[WHATIF_STR] = NoneObject
        else:
            chain[WHATIF_STR].keysformat()
    for res in mol.allResidues():
        if not res.has_key(WHATIF_STR):
            res[WHATIF_STR] = NoneObject
        else:
            # check and initiate altenative cingId names
            for checkId, item in res[WHATIF_STR].items():
                cingId = cingCheckId( checkId )
                if cingId != checkId:
                    res[WHATIF_STR][cingId] = item
#            for key1, key2 in [('RAMCHK', 'ramanchandran'),
#                               ('BBCCHK', 'backbone'),
#                               ('CHICHK', 'chi1'),
#                               ('C12CHK', 'janin')
#                              ]:
#                if res[WHATIF_STR].has_key(key1):
#                    res[WHATIF_STR][key2] = res[WHATIF_STR][key1]
#                else:
#                    res[WHATIF_STR][key2] = NoneObject
            #end for
            res[WHATIF_STR].keysformat()
        #end if

    for atm in mol.allAtoms():
        if not atm.has_key(WHATIF_STR):
            atm[WHATIF_STR] = NoneObject
        else:
            atm[WHATIF_STR].keysformat()

    # set formats on the whatif data structure
    whatif.keysformat()

    whatifStatus.parsed = True
    whatifStatus.keysformat()

    # Clean up junk.
    if 1: # DEFAULT 1
        removeTempFiles( whatifDir )
#end def


def removeTempFiles( whatifDir ):
    removeEmptyFiles( whatifDir )
#    whatifDir        = project.mkdir( mol.name, molDirectories.whatif  )
#    NTdebug("Removing temporary files generated by What If")
    try:
        # do NOT remove pdbout.txt.
        # Now pdbout.txt is no longer parsed, it may be removed I guess unless we want it again for fixing an issue
        # on this but then we need all not just the last model.
        removeListLocal = [scriptFileName, "DSSPOUT", "TOPOLOGY.FIL", "PDBFILE.PDB", "PDBFILE", "pdbout.tex", 'fort.79', 'DONE']
        removeList = []
        for fn in removeListLocal:
            removeList.append( os.path.join(whatifDir, fn) )

        for extension in '*.eps *.pdb *.OUT *.LOG *.DAT *.SCC *.sty *.FIG *.ATM DAVADRUG.* PRODRUG.*'.split():
            for fn in glob(os.path.join(whatifDir,extension)):
                removeList.append(fn)
        for fn in removeList:
            if not os.path.exists(fn):
#                NTdebug("Whatif.removeTempFiles: Expected to find a file to be removed but it doesn't exist: " + fn )
                continue
#            NTdebug("Removing: " + fn)
            os.unlink(fn)
    except:
        NTdebug("Whatif.removeTempFiles: Failed to remove all temporary what if files that were expected")

#end def


def restoreWhatif( project, tmp=None ):
    """
    Optionally restore whatif results
    """
    if project.whatifStatus.completed:
        NTmessage('==> Restoring whatif results')
        project.runWhatif(parseOnly=True)
#end def


# register the function
methods  = [
            (runWhatif, None),
            (createHtmlWhatif, None),
            ]
#saves    = []
restores = [(restoreWhatif, None)]
#exports  = []

