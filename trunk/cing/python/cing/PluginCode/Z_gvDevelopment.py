"""

GVprocheck( ranges=None, verbose = True )

Molecule:
    procheck: <Procheck> object

Residue
    procheck: NTdict instance with procheck values for this residue

"""
#@PydevCodeAnalysisIgnore
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.parameters import cingPaths
from cing.core.molecule import dots
from cing.PluginCode.Whatif import Whatif
import cing #@Reimport

import os #@Reimport
from math import cos, sin, pi
from cing.Libs.svd import SVDfit


class PseudoRotation( SVDfit ):
    """
    Class to calculate PseudoRotation and pucker amplitudes of sugars in oligonucleotides
    (Altona and Sundaraligam, JACS, 94, 8205 1972).

    Definition:

        tauJ = tauM * cos( P + 0.8*pi*J )           (eq. 1 Altona and Sundaraligam)

        J = 0,1,2,3,4
        P = phaseangle
        tauM = pucker amplitude

    rewrite:

        tauJ = tauM * cos(P) * cos(tetaJ)  - tauM * sin(P) * sin(tetaJ)

        tetaJ = 0.8*pi*J

    rewrite:

        tauJ = c0 * cos(tetaJ) + c1 * sin(tetaJ)

        c0 = tauM*cos(P)
        c1 = -tauM*sin(P)

    solve c0,c1 by svd, with tetaJ as running variable, calculate

        P = atan(-c1/c0)
        tauM = c0/cos(P)

    # map of tauJ onto IUPAC dihedral angle defs
    angleMap = [
                    (0, 'NU2'),
                    (1, 'NU3'),
                    (2, 'NU4'),
                    (3, 'NU0'),
                    (4, 'NU1')
                ]
    """

    # map of tauJ onto IUPAC dihedral angle defs
    angleMap = [
                 (0, 'NU2'),
                 (1, 'NU3'),
                 (2, 'NU4'),
                 (3, 'NU0'),
                 (4, 'NU1')
               ]

    def __init__(self):
        tetas = []
        for J,dihed in self.angleMap:
            tetaJ = 0.8*pi*(J)
            tetas.append( tetaJ )
        #end for

        SVDfit.__init__(self, tetas, None, self.cos_sin, 2)
    #end def

    def calculate( self, residue ):
        """Calculate the PseudoRotation angles and pucker amplitudes
           for all models of residue.

           return a (Ntlist,NTlist,ETclassification) tuple with the PseudoRotation angles
           and pucker amplitudes, or (None,None,None) on error.

        """
        from cing import printf, NTerror, NTlist
        from math import atan2

        if not residue.hasProperties('nucleic'):
            NTerror('PseudoRotation.calculate: residue %s is not nucleic acid', residue)
            return (None,None,None)
        #end if

        diheds = []
        for J,dihed in self.angleMap:
            if dihed not in residue:
                NTerror('PseudoRotation.calculate: dihedral "%s" not defined for residue %s', dihed, residue)
                return (None,None,None)
            #end if
            diheds.append( residue[dihed] )
        #end for
        #print diheds

        nmodels = len(diheds[0])
        Plist = NTlist()
        tauMlist = NTlist()
        for i in range(nmodels):
            taus = []
            for d in diheds:
                taus.append(d[i])
            #end for

            # Do fit and calculate P and pucker
            c = self.fit(taus)
            P = atan2(-c[1],c[0])
            tauM = c[0]/cos(P)
            P = P/pi*180.0 # convert to degrees

            Plist.append(P)
            tauMlist.append(tauM)

            #printf( '%1d %8.2f %8.2f\n',i, P, tauM )
        #end for

        Plist.cAverage()
        Plist.limit(Plist.cav-180.0,Plist.cav+180.0) # Center around circular average,
        Plist.average()                              # to calculate sd in this step
        Plist.limit(0.0,360.0)                       # and rescale to 0,360 range
        tauMlist.average()

        ETname = self.getETnomenclature(Plist.cav,Plist.sd)
        return Plist,tauMlist,ETname
    #end def

    # ET definitions from: http://www.chem.qmul.ac.uk/iupac/misc/pnuc2.html#200
    # encoding superscript-lowerscript-E/T; underscore denotes 'absence'
    angleDefs = [( -9,   9, '32T'),
                 (  9,  27, '3_E'), # C3'-endo
                 ( 27,  45, '34T'),
                 ( 45,  63, '_4E'), # C4'-exo
                 ( 63,  81, 'O4T'),
                 ( 81,  99, 'O_E'), # O4'-endo
                 ( 99, 117, 'O1T'),
                 (117, 135, '_1E'), # C1'-exo
                 (135, 153, '21T'),
                 (153, 171, '2_E'), # C2'-endo
                 (171, 189, '23T'),
                 (189, 207, '_3E'), # C3'-exo
                 (207, 225, '43T'),
                 (225, 243, '4_E'), # C4'-endo
                 (243, 261, '4OT'),
                 (261, 279, '_OE'), # O4'-exo
                 (279, 297, '1OT'),
                 (297, 315, '1_E'), # C1'-endo
                 (315, 333, '12T'),
                 (333, 351, '_2E')  # C2'-exo
                 ]

    def getETnomenclature(self, pseudoAngle, error=0.0 ):
        """
        Return the E/T nomenclature corresponding to pseudoAngle+-error
        """
        #transform the pseudoAngle to [-9,351] range
        while pseudoAngle > 351.0:
            pseudoAngle -= 360.0
        while pseudoAngle < -9.0:
            pseudoAngle += 360.0

        if error == 0.0:
            for lower,upper,ETname in self.angleDefs:
                if pseudoAngle > lower and pseudoAngle <= upper:
                    return ETname
            #end for
        else:
            low = self.getETnomenclature( pseudoAngle - error, 0.0 )
            high = self.getETnomenclature( pseudoAngle + error, 0.0 )
            if low==high:
                return low
            else:
                return low + '/' + high
            #endif
        #end if

        return None
    #end def

    def cos_sin( teta, na ):
        """Return cos and sin for teta; NB na==2
        """
        from math import cos, sin, pi
        return [cos(teta),sin(teta)]
    #end def
    cos_sin = staticmethod(cos_sin)

#end class


def procheckString2float( string ):
    """Convert a string to float, return None in case of value of 999.90
    """
    result = float( string )
    if result == 999.90:
        return None
    else:
        return result
    #end if
#end def


class gvProcheck:
    #TODO: subclass this from ExecuteProgram
    """
    From Jurgen:

    Column id
    ^ Fortran variable
    ^ ^        Explanation
    ##############################
    ###################################################
    1 NXRES    residue number in procheck
    2 AA3      residue name
    3 BRKSYM   chain id as in PDB file
    4 SEQBCD   resdiue id as in PDB file??
    5 SUMMPL   secondary structure classification (DSSP?)
    6 MCANGS 1 phi
    7 MCANGS 2 psi
    8 MCANGS 3 omega
    9 SCANGS 1 chi 1
    0 SCANGS 2 chi 2
    1 SCANGS 3 chi 3
    2 SCANGS 4 chi 4
    3 HBONDE   Hydrogen bond energy
    4 DSDSTS ? statistics?
    5 MCANGS ?
    6 BVALUE   Crystallographic B factor
    7 MCBVAL   Mainchain B value
    8 SCBVAL   Sidechain B value
    9 OOIS 1 ?
    0 OOIS 2 ?
    1 MCBSTD Main chain bond standard deviation?
    2 SCBSTD Side chain bond standard deviation?


    #0000000000000000000000000000000000000000000000000000000000000000000000
      55GLY A  62 T-147.73 -20.13-166.50 999.90 999.90 999.90 999.90  -0.87   0.00 999.90   0.00  0.000  0.000 11 38  0.000  0.000
      56ASP A  63 e -78.77 161.06-173.97 -56.24 -71.93 999.90 999.90  -0.76   0.00  34.42   0.00  0.000  0.000 13 50  0.000  0.000
      57ARG A  64 E-104.07 124.65 166.81 177.50-170.21 179.43-172.18  -2.12   0.00  37.30   0.00  0.000  0.000 12 56  0.000  0.000
      58VAL A  65 E -87.26 117.24 175.76-157.64 999.90 999.90 999.90  -3.33   0.00  33.46   0.00  0.000  0.000 14 67  0.000  0.000
      59LEU A  66 E -99.01 -36.19-179.02  50.71 149.42 999.90 999.90  -2.74   0.00  31.00   0.00  0.000  0.000 13 50  0.000  0.000
      95PRO!A 102   -69.35 999.90 999.90 -24.86 999.90 999.90 999.90   0.00   0.00  37.72   0.00  0.000  0.000  4 13  0.000  0.000
      96TYR!B 205   999.90 -55.02-171.34-143.34 -89.71 999.90 999.90   0.00   0.00  34.80   0.00  0.000  0.000  2  5  0.000  0.000
      97LEU B 206    61.37 179.80 171.30-145.66  66.98 999.90 999.90   0.00   0.00  31.07   0.00  0.000  0.000  3  5  0.000  0.000
    """
    procheckDefs = NTdict(
    #   field       (startChar, endChar, conversionFunction)
        line      = (  0,  4, int ),
        resName   = (  4,  7, str ),
        chain     = (  8,  9, str ),
        resNum    = ( 10, 13, int ),
        secStruct = ( 14, 15, str ),
        PHI       = ( 15, 22, procheckString2float ),
        PSI       = ( 22, 29, procheckString2float ),
        OMEGA     = ( 29, 36, procheckString2float ),
        CHI1      = ( 36, 43, procheckString2float ),
        CHI2      = ( 43, 50, procheckString2float ),
        CHI3      = ( 50, 57, procheckString2float ),
        CHI4      = ( 57, 64, procheckString2float )
    )

    def __init__(self, project ):
        """
        Procheck class allows running procheck_nmr and parsing of results
        """
        self.molecule     = project.molecule
        self.rootPath     = project.mkdir( project.molecule.name, project.moleculeDirectories.procheck  )
#        self.runProcheck  = ExecuteProgram( cing.paths.procheck_nmr,
#                                            rootPath = self.rootPath,
#                                            redirectOutput= False
#                                          )
        self.ranges  = None
        self.summary = None
    #end def

    def run(self, ranges=None ):
        NTmessage('==> Running procheck_nmr, ranges %s, results in "%s" ...', ranges, self.rootPath)

        # Convert the ranges and translate into procheck_nmr format
        selectedResidues = self.molecule.ranges2list( ranges )
        NTsort(selectedResidues, 'resNum', inplace=True)
        # reduce this sorted list to pairs start, stop
        self.ranges = selectedResidues[0:1]
        for i in range(0,len(selectedResidues)-1):
            if ((selectedResidues[i].resNum < selectedResidues[i+1].resNum - 1) or
                (selectedResidues[i].chain != selectedResidues[i+1].chain)
               ):
                self.ranges.append(selectedResidues[i])
                self.ranges.append(selectedResidues[i+1])
            #end if
        #end for
        self.ranges.append(selectedResidues[-1])
        NTdebug( 'Procheck ranges %d', self.ranges )
        #generate the ranges file
        path = os.path.join( self.rootPath, 'ranges')
        fp = open( path, 'w' )
        for i in range(0,len(self.ranges),2):
            fprintf( fp, 'RESIDUES %3d %2s  %3d %2s\n', self.ranges[i].resNum, self.ranges[i].chain.name,
                                                        self.ranges[i+1].resNum, self.ranges[i+1].chain.name
                   )
        #end for
        fp.close()

        #export a PDB file
        path = os.path.join( self.rootPath, self.molecule.name + '.pdb')
        #print path
        self.molecule.toPDBfile( path, convention=cing.PDB )

        # run procehck
        runProcheck  = ExecuteProgram( cingPaths.procheck_nmr,
                                       rootPath = self.rootPath,
                                       redirectOutput= True
                                    )
        runProcheck( self.molecule.name +'.pdb ranges' )
        del( runProcheck )

        # Parse results
        self.parseResult()
    #end def

    def _parseProcheckLine( self, line ):
        """
        Internal routine to parse a single line
        Return result, which is a dict type or None
        on error (i.e. too short line)
        """
    #    print ">>", line
        result = {}
        if (len(line) >= 64):
            for field,fieldDef in self.procheckDefs.iteritems():
                c1,c2,func = fieldDef
                result[ field ] = func(line[c1:c2])
            #end for
        else:
            return None
        #end if

    #    print result
        return result
    #end def

    def parseResult( self ):
        """
        Get summary

        Parse procheck .rin files and store result in procheck NTdict
        of each residue of mol

        """
        path = os.path.join( self.rootPath, sprintf('%s.sum', self.molecule.name) )
        fp = open( path, 'r' )
        if not fp:
            NTerror('gvProcheck.parseResult: %s not found', path)
        else:
            self.summary = ''.join(fp.readlines())
            fp.close()
        #end if

        for i in range(1,self.molecule.modelCount+1):
            path = os.path.join( self.rootPath, sprintf('%s_%03d.rin', self.molecule.name, i) )
            #print '> parsing >', path

            for line in AwkLike( path, minLength = 64, commentString = "#" ):
                result = self._parseProcheckLine( line.dollar[0] )
                chain   = result['chain']
                resNum  = result['resNum']
                residue = self.molecule.decodeNameTuple((cing.PDB,chain,resNum,None))
                if not residue:
                    NTerror('Procheck.parseResult: residue not found (%s,%d)', chain, resNum )
                else:

                    residue.setdefault( 'procheck', NTstruct() )
                    for field,value in result.iteritems():
                        residue.procheck.setdefault( field, NTlist() )
                        residue.procheck[field].append( value )
                    #end for
                #end if
                del( result )
            #end for
        #end for
    #end def
#end class



def procheck_old( project, ranges=None ):
    """
    Adds <Procheck> instance to molecule. Run procheck and parse result
    """
    if not project.molecule:
        NTerror('ERROR procheck: no molecule defined\n')
        return None
    #end if

    if project.molecule.has_key('procheck'):
        del(project.molecule.procheck)
    #end if

    pcheck = gvProcheck( project )
    if not pcheck: return None

    pcheck.run( ranges=ranges )
    project.molecule.procheck = pcheck

    return project.molecule.procheck
#end def

from math import sqrt
from cing.Libs.NTutils import NTfill, NTlist, printf, fprintf, sprintf, getDeepByKeys
from cing.Libs.fpconst import NaN, isNaN

#import yasaramodule as yasara

def mkYasaraMacros( project ):
    """
    Generate the Yasara macros in the moleculeDirectories.yasara dir.
    """
    if not project.molecule:
        NTerror('mkYasaraMacros: no molecule defined')
        return
    #end if
    mkYasaraByResidueMacro(project, ['procheck','gf'],
                           minValue=-3.0,maxValue=1.0,
                           reverseColorScheme=True,
                           path=project.moleculePath('yasara','gf.mcr')
                          )

    mkYasaraByResidueMacro(project, ['Qshift','backbone'],
                           minValue=0.0,maxValue=0.05,
                           reverseColorScheme=False,
                           path=project.moleculePath('yasara','Qshift.mcr')
                          )

    mkYasaraByResidueROGMacro(project,path=project.moleculePath('yasara','rog.mcr'))
#end def


def mkMacros( project ):
    """
    Generate the macros in the moleculeDirectories.macros dir.
    """
    # Only one kind thus far
    NTmessage('==> Generating Macros')
    mkYasaraMacros(project)
#end def



def mkYasaraByResidueMacro( project, keys,
                            minValue=0.0, maxValue=1.0, reverseColorScheme=False,
                            path=None
                           ):

#    NTdebug('mkYasaraByResidueMacro: keys: %s, minValue: %s maxValue: %s', keys, minValue, maxValue)

    if path:
        stream = open( path, 'w')
    else:
        stream = sys.stdout
    #end if

    fprintf( stream, 'Console off\n' )
    fprintf( stream, 'ColorRes All, Gray\n' )
    fprintf( stream, 'PropRes All, -999\n' )
    if reverseColorScheme:
        fprintf( stream, 'ColorPar Property Min,red,%f\n', minValue )
        fprintf( stream, 'ColorPar Property Max,blue,%f\n', maxValue )
    else:
        fprintf( stream, 'ColorPar Property Min,blue,%f\n', minValue )
        fprintf( stream, 'ColorPar Property Max,red,%f\n', maxValue )

    for res in project.molecule.allResidues():
        value = getDeepByKeysOrAttributes( res, *keys )
#        if res.has_key(property) and res[property] != None and not isNaN(res[property]):
        if value != None and not isNaN(value):
            fprintf( stream,'PropRes Residue %d,%.4f\n', res.resNum, value)
    #end for

    fprintf( stream, 'ColorAll Property\n' )
    fprintf( stream, 'Console on\n' )

    if path:
        stream.close()
#end def

def mkYasaraByResidueROGMacro( project, path=None ):
    if path:
        stream = open( path, 'w')
#     else:
#         stream = sys.stdout
#     #end if

    if path:
        fprintf( stream, 'Console off\n' )
        fprintf( stream, 'ColorRes  All, Gray\n')
    else:
        yasara.Console('off')
        yasara.ColorRes( 'All, Gray' )


    YasaraColorDict = dict( green=240, orange=150, red=120)

    for res in project.molecule.allResidues():
        cmd = sprintf('residue %d,%s', res.resNum, YasaraColorDict[res.rogScore.colorLabel] )
        if path:
            fprintf( stream, 'ColorRes %s\n', cmd )
        else:
            yasara.ColorRes( cmd )
    #end for

    if path:
        fprintf( stream, 'Console on\n' )
        stream.close()
    else:
        yasara.Console('on')
#end def



"""
======================COPYRIGHT/LICENSE START==========================

ValidationBasic.py: Part of the CcpNmr Analysis program

Copyright (C) 2004 Wayne Boucher and Tim Stevens (University of Cambridge)

=======================================================================

This file contains reserved and/or proprietary information
belonging to the author and/or organisation holding the copyright.
It may not be used, distributed, modified, transmitted, stored,
or in any way accessed, except by members or employees of the CCPN,
and by these people only until 31 December 2005 and in accordance with
the guidelines of the CCPN.

A copy of this license can be found in ../../../license/CCPN.license.

======================COPYRIGHT/LICENSE END============================

for further information, please contact :

- CCPN website (http://www.ccpn.ac.uk/)

- email: ccpn@bioc.cam.ac.uk

- contact the authors: wb104@bioc.cam.ac.uk, tjs23@cam.ac.uk
=======================================================================

If you are using this software for academic purposes, we suggest
quoting the following references:

===========================REFERENCE START=============================
R. Fogh, J. Ionides, E. Ulrich, W. Boucher, W. Vranken, J.P. Linge, M.
Habeck, W. Rieping, T.N. Bhat, J. Westbrook, K. Henrick, G. Gilliland,
H. Berman, J. Thornton, M. Nilges, J. Markley and E. Laue (2002). The
CCPN project: An interim report on a data model for the NMR community
(Progress report). Nature Struct. Biol. 9, 416-418.

Wim F. Vranken, Wayne Boucher, Tim J. Stevens, Rasmus
H. Fogh, Anne Pajon, Miguel Llinas, Eldon L. Ulrich, John L. Markley, John
Ionides and Ernest D. Laue. The CCPN Data Model for NMR Spectroscopy:
Development of a Software Pipeline. Accepted by Proteins (2004).

===========================REFERENCE END===============================

"""

#VALID_VALUE_TYPE_ATTRS = {type(0.0): 'floatValue',
#                          type(1): 'intValue',
#                          type('a'): 'textValue',
#                          type(True): 'booleanValue'}
#
#
## # # # # # #  C I N G  E X A M P L E  # # # # # # #
#
#def storeRogScores(ccpnEnsemble, scores, context='CING'):
#   # Assumes scores in same order as residues
#
#   keyword    = 'ROG'
#   definition = 'Overall per-residue validation score for display. ROG=Red/Orange/Green'
#   synonym    = 'Residue ROG Score'
#
#   validStore = getEnsembleValidationStore(ccpnEnsemble, context,
#                                           keywords=[keyword, ],
#                                           definitions=[definition, ],
#                                           synonyms=[synonym, ])
#
#   residues = []
#   for chain in ccpnEnsemble.sortedCoordChains():
#     residues.extend(chain.sortedResidues())
#
#   storeResidueValidations(validStore, context, keyword, residues, scores)
#
## # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
#
#def getEnsembleValidationStore(ensemble, context, keywords,
#                               definitions=None, synonyms=None):
#  """Descrn: Get a CCPN object to store validation results for an ensemble
#             in a given program context. Requires a list of keywords which will
#             be used in this context. Allows optional lists of definitions and
#             user-friendly synonyms for these keywords.
#     Inputs: MolStructure.StructureEnsemble, Word, List of Words,
#             List of Lines, List of Words
#     Output: StructureValidation.StructureValidationStore
#  """
#
#  memopsRoot = ensemble.root
#  eid = '%s_%s' % (context, ensemble.guid)
#  validStore = ensemble.findFirstStructureValidationStore(name=eid)
#
#  if validStore is None:
#    validStore = memopsRoot.newStructureValidationStore(name=eid,
#                                      structureEnsemble=ensemble)
#
#  validStore.nmrProject = memopsRoot.currentNmrProject
#
#  keywordStore = memopsRoot.findFirstKeywordDefinitionStore(context=context)
#
#  if not keywordStore:
#    keywordStore = memopsRoot.newKeywordDefinitionStore(context=context)
#
#  for i, keyword in enumerate(keywords):
#    keywordDefinition = keywordStore.findFirstKeywordDefinition(keyword=keyword)
#
#    if not keywordDefinition:
#      keywordDefinition = keywordStore.newKeywordDefinition(keyword=keyword)
#
#    if definitions and (i < len(definitions)):
#      keywordDefinition.explanation = definitions[i]
#
#    if synonyms and (i < len(synonyms)):
#      keywordDefinition.name = synonyms[i]
#
#  return validStore
#
#
#def getValidationObjects(validStore, className, context, keyword):
#  """Descrn: Find a given class of validation objects in a validation store
#             in a given (program) context, with a given keyword.
#     Inputs: StructureValidation.StructureValidationStore, Word, Word, Word
#     Output: List of StructureValidation.Validations
#  """
#  return validStore.findAllValidationResults(context=context,
#                                             keyword=keyword,
#                                             className=className)
#
#
#def replaceValidationObjects(validStore, className, keyword, context, dataList):
#  """Descrn: Store validation data as CCPN validation objects,
#             overwriting all previous records of such information
#             in the validation store object. Finds a given class of
#             validation objects a given keyword in a given context.
#             The input data list is a 2-tuple containing a list of the
#             CCPN objects validated and the value associated with that
#             validation. Note that the validated CCPN object types must
#             match the type required by the validation object className.
#             *NOTE* this is a slow function and should often be replaced
#             with a class-specific equivalent.
#     Inputs: StructureValidation.StructureValidationStore, Word, Word, Word,
#             List of 2-Tuples of (List of CCPN objects, )
#     Output: None
#  """
#
#  for validObj in getValidationObjects(validStore, className, keyword, context):
#    validObj.delete()
#
#  newObject = getattr(validStore, 'new%s' % className)
#
#  validatedObjAttr = None
#
#  for validatedObjects, value in dataList:
#    validObj = newObject(context=context, keyword=keyword)
#
#    if not validatedObjAttr:
#      for role in validObj.metaclass.roles:
#        if role.locard == 0:
#          validatedObjAttr = role.name
#
#    if validatedObjAttr:
#      setattr(validObj, validatedObjAttr, validatedObjects)
#
#    valueAttr = VALID_VALUE_TYPE_ATTRS.get(type(value), 'textValue')
#    setattr(validObj, valueAttr, value)
#
#
#def getResidueValidation(validStore, residue, context, keyword):
#  """Descrn: Get any existing residue validation results from a CCPN
#             validation store which have the given keywords in the
#             given (program) context.
#             *NOTE* This function may be quicker than using the generic
#             getValidationObjects() because the link is queried from the
#             validated object, not the validation store, which often
#             has fewer total validation objects.
#     Inputs: StructureValidation.StructureValidationStore,
#             MolStructure.Residue, Word, Word
#     Output: StructureValidation.ResidueValidation
#  """
#
#  # Define data model call to find exting result
#  findValidation = residue.findFirstResidueValidation
#
#  validObj = findValidation(structureValidationStore=validStore,
#                            context=context, keyword=keyword)
#
#  return validObj
#
#
#def storeResidueValidations(validStore, context, keyword, residues, scores):
#  """Descrn: Store the per-residue scores for a an ensemble within
#             CCPN validation objects.
#             *NOTE* This function may be quicker than using the generic
#             replaceValidationObjects() because it is class specifc
#     Inputs: StructureValidation.StructureValidationStore,
#             List of MolStructure.Residues, List if Floats
#     Output: List of StructureValidation.ResidueValidations
#  """
#
#  validObjs = []
#
#  # Define data model call for new result
#  newValidation = validStore.newResidueValidation
#
#  for i, residue in enumerate(residues):
#
#    score = scores[i]
#
#    # Find any existing residue validation objects
#    validObj = getResidueValidation(validStore, residue, context, keyword)
#
#    # Validated object(s) must be in a list
#    residueObjs = [residue, ]
#
#    # Make a new validation object if none was found
#    if not validObj:
#      validObj = newValidation(context=context, keyword=keyword,
#                               residues=residueObjs)
#
#    # Set value of the score
#    validObj.floatValue = score
#
#    validObjs.append(validObj)
#
#  return validObjs

VALID_VALUE_TYPE_ATTRS = {type(0.0): 'floatValue',
                          type(1): 'intValue',
                          type('a'): 'textValue',
                          type(True): 'booleanValue'}


# # # # # # #  C I N G  E X A M P L E  # # # # # # #

def storeRogScores(ccpnEnsemble, scores, context='CING'):
   # Assumes scores in same order as residues

   keyword    = 'ROG'
   definition = 'Overall per-residue validation score for display. ROG=Red/Orange/Green'
   synonym    = 'Residue ROG Score'

   validStore = getEnsembleValidationStore(ccpnEnsemble, context,
                                           keywords=[keyword, ],
                                           definitions=[definition, ],
                                           synonyms=[synonym, ])

   residues = []
   for chain in ccpnEnsemble.sortedCoordChains():
     residues.extend(chain.sortedResidues())

   storeResidueValidations(validStore, context, keyword, residues, scores)

# # # # # # # # # # # # # # # # # # # # # # # # # # #



def getEnsembleValidationStore(ensemble, context, keywords=None,
                               definitions=None, synonyms=None,
                               software=None):
  """Descrn: Get a CCPN object to store validation results for an ensemble
             in a given program context. Requires a list of keywords which will
             be used in this context. Allows optional lists of definitions and
             user-friendly synonyms for these keywords.
             Optional argument for passing software specification (otherwise
             defaults to current CcpNmr Analysis)
     Inputs: MolStructure.StructureEnsemble, Word, List of Words,
             List of Lines, List of Words, Method.Software
     Output: Validation.ValidationStore
  """

  if not keywords:
    keywords = []

  memopsRoot = ensemble.root
  eid = '%s_%s' % (context, ensemble.guid)
  validStore = ensemble.findFirstValidationStore(name=eid)

  if validStore is None:
    software = getSoftware(memopsRoot)
    validStore = memopsRoot.newValidationStore(name=eid, software=software,
                                               structureEnsemble=ensemble)

  validStore.nmrProject = memopsRoot.currentNmrProject

  keywordStore = memopsRoot.findFirstKeywordDefinitionStore(context=context)

  if not keywordStore:
    keywordStore = memopsRoot.newKeywordDefinitionStore(context=context)

  for i, keyword in enumerate(keywords):
    keywordDefinition = keywordStore.findFirstKeywordDefinition(keyword=keyword)

    if not keywordDefinition:
      keywordDefinition = keywordStore.newKeywordDefinition(keyword=keyword)

    if definitions and (i < len(definitions)):
      keywordDefinition.explanation = definitions[i]

    if synonyms and (i < len(synonyms)):
      keywordDefinition.name = synonyms[i]

  return validStore


def getValidationObjects(validStore, className, context, keyword):
  """Descrn: Find a given class of validation objects in a validation store
             in a given (program) context, with a given keyword.
     Inputs: Validation.ValidationStore, Word, Word, Word
     Output: List of Validation.Validations
  """
  return validStore.findAllValidationResults(context=context,
                                             keyword=keyword,
                                             className=className)


def replaceValidationObjects(validStore, className, keyword, context, dataList):
  """Descrn: Store validation data as CCPN validation objects,
             overwriting all previous records of such information
             in the validation store object. Finds a given class of
             validation objects a given keyword in a given context.
             The input data list is a 2-tuple containing a list of the
             CCPN objects validated and the value associated with that
             validation. Note that the validated CCPN object types must
             match the type required by the validation object className.
             *NOTE* this is a slow function and should often be replaced
             with a class-specific equivalent.
     Inputs: Validation.ValidationStore, Word, Word, Word,
             List of 2-Tuples of (List of CCPN objects, )
     Output: None
  """

  for validObj in getValidationObjects(validStore, className, keyword, context):
    validObj.delete()

  newObject = getattr(validStore, 'new%s' % className)

  validatedObjAttr = None

  for validatedObjects, value in dataList:
    validObj = newObject(context=context, keyword=keyword)

    if not validatedObjAttr:
      for role in validObj.metaclass.roles:
        if role.locard == 0:
          validatedObjAttr = role.name

    if validatedObjAttr:
      setattr(validObj, validatedObjAttr, validatedObjects)

    valueAttr = VALID_VALUE_TYPE_ATTRS.get(type(value), 'textValue')
    setattr(validObj, valueAttr, value)


def getResidueValidation(validStore, residue, context, keyword):
  """Descrn: Get any existing residue validation results from a CCPN
             validation store which have the given keywords in the
             given (program) context.
             *NOTE* This function may be quicker than using the generic
             getValidationObjects() because the link is queried from the
             validated object, not the validation store, which often
             has fewer total validation objects.
     Inputs: Validation.ValidationStore,
             MolStructure.Residue, Word, Word
     Output: Validation.ResidueValidation
  """

  # Define data model call to find exiting result
  findValidation = residue.findFirstResidueValidation

  validObj = findValidation(validationStore=validStore,
                            context=context, keyword=keyword)

  return validObj


#def parseWhatifSummary( wiSummary ):
#    from cing import NaN
#    foundWHATIF = False
#    for line in wiSummary.splitlines():
#        if not foundWHATIF and 'Structure Z-scores' in line:
#            foundWHATIF = True
#            break
#    #end for
#
#    #print foundWHATIF
#    rama = NaN
#    chi12 = NaN
#    bb = NaN
#    if foundWHATIF:
#        for i,line in enumerate(wiSummary.splitlines()):
#            #print i,'>',line
#            if 'Ramachandran plot appearance' in line:
#                rama = float(line[35:min(42,len(line)-1)])
#            if 'chi-1/chi-2 rotamer normality' in line:
#                chi12 = float(line[35:min(42,len(line)-1)])
#            if 'Backbone conformation' in line:
#                bb = float( line[35:min(42,len(line)-1)])
#        #end for
#    #end if
#    return (rama, chi12, bb)
##end def
from cing.PluginCode.required.reqWhatif import WHATIF_STR


class CingSummaryDict( NTdict ):
    """
    Simple class to store CING summary result as a dict for easy retrieval
    """

    def __init__( self ):
        NTdict.__init__( self,
                         __CLASS__           = 'CingSummaryDict',

                         version             = cing.cingVersion,

                         name                = None,

                         totalResidueCount   = 0,
                         proteinResidueCount = 0,
                         nucleicResidueCount = 0,

                         # CING scores in %
                         CING_red            = NaN,
                         CING_orange         = NaN,
                         CING_green          = NaN,
                         CING_residueROG     = NTlist(),

                         # Procheck scores
                         PC_core            = NaN,
                         PC_allowed         = NaN,
                         PC_generous        = NaN,
                         PC_disallowed      = NaN,
                         PC_gf              = None,

                         # WHATIF scores done again later; just here to make sure for the format statement
                         WI_ramachandran    = None,
                         WI_bbNormality     = None,
                         WI_rotamer         = None,

                         distances          = NTlist(),
                         dihedrals          = NTlist(),
                         rdcs               = NTlist(),

                        # single line format
                         __FORMAT__ = '%(name)-10s   ' +\
                                      'RESIDUES: tot %(totalResidueCount)3d  prot %(proteinResidueCount)3d  nucl %(nucleicResidueCount)3d   ' +\
                                      'ROG(%%): %(CING_red)5.1f %(CING_orange)5.1f %(CING_green)5.1f    ' +\
                                      'PROCHECK(%%): %(PC_core)5.1f %(PC_allowed)5.1f %(PC_generous)5.1f %(PC_disallowed)5.1f  gf: %(PC_gf)-15s  ' +\
                                      'WHATIF: rama %(WI_ramachandran)-15s bb %(WI_bbNormality)-15s rotamer %(WI_rotamer)-15s '

                    )
        # Add all Whatif summary check Id's
        for checkId in Whatif.summaryCheckIdList:
            key = 'WI_' + Whatif.cingCheckId(checkId)
            self[key] = None

        self.saveAllXML()
    #end def

    def getSummaryFromProject( self, project ):
        """
        Extract the data from project
        """

        self.name = project.name

        # Residue counts (total, protein, nucleic)
        self.totalResidueCount   = len( project.molecule.allResidues() )
        proteinResidues = project.molecule.residuesWithProperties('protein' )
        self.proteinResidueCount = len( proteinResidues )
        nucleicResidues = project.molecule.residuesWithProperties('nucleic' )
        self.nucleicResidueCount = len( nucleicResidues )

        # ROG scores
        rog = NTlist( 0, 0, 0 ) # Counts for red, orange, green.
        for residue in project.molecule.allResidues():
            if residue.rogScore.isRed():
                rog[0] += 1
            elif residue.rogScore.isOrange():
                rog[1] += 1
            else:
                rog[2] += 1
            self.CING_residueROG.append( (residue._Cname(-1), residue.rogScore) )
        #end for
        total = reduce(lambda x, y: x+y+0.0, rog) # total expressed as a float because of 0.0
        for i,x in enumerate(rog): rog[i] = rog[i]*100.0/total
        self.CING_red    = round(rog[0],1)
        self.CING_orange = round(rog[1],1)
        self.CING_green  = round(rog[2],1)

        # Procheck (core, allowed,  generous, disallowed) (%), average g_factor
        if self.proteinResidueCount > 0 and project.molecule.has_key('procheck') and project.molecule.procheck:
            self.PC_core       = project.molecule.procheck.summary.core
            self.PC_allowed    = project.molecule.procheck.summary.allowed
            self.PC_generous   = project.molecule.procheck.summary.generous
            self.PC_disallowed = project.molecule.procheck.summary.disallowed
            self.PC_gf  = proteinResidues.zap('procheck','gf').average2(fmt='%6.3f +/- %5.3f')
        #end if

        # Whatif
        if self.proteinResidueCount > 0 and project.whatifStatus.completed and project.whatifStatus.parsed:
            for checkId in Whatif.summaryCheckIdList:
                if project.molecule[WHATIF_STR].has_key(checkId):
                    key = 'WI_' + Whatif.cingCheckId(checkId)
                    self[key] = project.molecule[WHATIF_STR][checkId].average(fmt='%6.3f +/- %5.3f')
        #end if

        for drl in project.distances:
            self.distances.append( self.distanceRestraintListToTuple(drl) )

        for drl in project.dihedrals:
            self.dihedrals.append( self.dihedralRestraintListToTuple(drl) )

        return self
    #end def

    def distanceRestraintListToTuple(self, drl):
        """Return a single tuple of relevant results ed.
        """
        return (drl.name, drl.status,
                len(drl), len(drl.intraResidual), len(drl.sequential),len(drl.mediumRange),len(drl.longRange),len(drl.ambigious),
                NTvalue(drl.rmsdAv, drl.rmsdSd, fmt='%.4f +/ %.4f'), drl.violCountLower, drl.violCount1, drl.violCount3, drl.violCount5, str(drl.rogScore)
               )
    #end def

    def dihedralRestraintListToTuple(self, drl):
        """Return a single tuple of relevant results ed.
        """
        return (drl.name, drl.status,
                len(drl),
                NTvalue(drl.rmsdAv, drl.rmsdSd, fmt='%.4f +/ %.4f'), drl.violCount1, drl.violCount3, drl.violCount5, str(drl.rogScore)
               )
    #end def

    def save(self, path):
        """Save CingSummaryDict object as XML file.
        Return True on error
        """
        result = obj2XML( self, path=path )
        if result == None:
            NTerror('CingSummaryDict.save: saving to "%s"', path)
            return True
        #end if
    #end def

    def restore( path ):
        """
        Static method to restore CingSummaryDict object from XML-file path.
        Return None on error.
        """
        if not os.path.exists( path ):
            NTerror('CingSummaryDict.restore: path "%s" does not exist', path)
            return True
        #end if
        return XML2obj(path = path)
    #end def
#end class

class XMLCingSummaryDictHandler( XMLhandler ):
    """CingSummaryDict handler class"""
    def __init__(self):
        XMLhandler.__init__(self, name='CingSummaryDict')
    #end def

    def handle(self, node):
        attrs = self.handleDictElements(node)
        if attrs == None: return None
        result = CingSummaryDict()
        result.update(attrs)
        return result
    #end def
#end class
# Initiate an instance
xmlcingsummarydicthandler = XMLCingSummaryDictHandler()



def getCingSummaryDict( project ):
    """Get a CING summary dict from project
    Return summayDict or None on error
    """
    if not project:
        return None
    project.summaryDict = CingSummaryDict()
    project.summaryDict.getSummaryFromProject( project )
    return project.summaryDict
#end def

# register the functions
methods  = [(procheck_old, None),
            (mkYasaraByResidueROGMacro,None),
            (mkYasaraByResidueMacro,None),
            (mkYasaraMacros,None),
            (mkMacros,None),
            (getCingSummaryDict, None )

           ]
#saves    = []
#restores = []
#exports  = []

