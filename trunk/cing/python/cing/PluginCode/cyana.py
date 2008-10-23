"""
Adds CYANA import/export methods


Methods:
  Project.importUpl( uplFile, convention, lower ):
        import uplFile
        convention = CYANA or CYANA2
        return a DistanceRestraintList or None on error

  Project.importAco( acoFile, convention ):
        Read Cyana acoFile
        convention = CYANA or CYANA2
        return a DihedralRestraintList or None on error

  Project.export2cyana():
        Export restraints in CYANA and CYANA2 formats

  DihedralRestraint.export2cyana( convention ):
        Return string with distanceRestraint (dr) in cyana format or None on error
        convention = CYANA or CYANA2

  DihedralRestraintList.export2cyana( path, convention    ):
        Export a dihedralRestraintList (drl) to cyana format:
        convention = CYANA or CYANA2
        return drl or None on error

"""
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import sprintf
from cing.core.classes import DihedralRestraint
from cing.core.classes import DihedralRestraintList
from cing.core.classes import DistanceRestraint
from cing.core.classes import DistanceRestraintList
from cing.core.constants import CYANA
from cing.core.constants import CYANA2
from cing.core.molecule import translateTopology
import os
import shutil
#from cing.Libs.NTutils import printWarning
#import sys

#==============================================================================
# CYANA stuff
#==============================================================================

#-----------------------------------------------------------------------------
def exportDihedralRestraint2cyana( dr, convention ):
    """Return string with distanceRestraint (dr) in cyana format or None on error
       ( 512 THR   PSI     116.0   148.0)
       convention = CYANA or CYANA2
       return dr or None on error
    """
    if not dr:
        NTerror('Error exportDihedralRestraint2cyana: undefined restraint\n' )
        return None
    #end if

    res, angleName, _db = dr.retrieveDefinition()
    if res:
        return sprintf( '%4d %-4s %-6s %6.1f %6.1f',
                        res.resNum, res.db.translate( convention ),
                        angleName, dr.lower, dr.upper
                      )
    else:
        NTerror('Error exportDihedralRestraint2cyana: cannot export dihedral restraint "%s"\n', str(dr) )
        return None
    #end if
    return dr
#end def
# add as a method to DihedralRestraint Class
DihedralRestraint.export2cyana = exportDihedralRestraint2cyana


def exportDihedralRestraintList2cyana( drl, path, convention)   :
    """Export a dihedralRestraintList (drl) to cyana format:
       convention = CYANA or CYANA2
       return drl or None on error
    """
    fp = open( path, 'w' )
    if not fp:
        NTerror('exportDihedralRestraintList2cyana: unable to open "%s"\n', path )
        return None
    #end def
    for dr in drl:
        fprintf( fp, '%s\n', dr.export2cyana( convention ) )
    #end for

    fp.close()
    NTmessage('==> Exported %s in %s format to "%s"', drl, convention, path)
    #end if
    return drl
#end def
# add as a method to DistanceRestraintList Class
DihedralRestraintList.export2cyana = exportDihedralRestraintList2cyana


def importAco( project, acoFile, convention ):
    """Read Cyana acoFile
       ( 512 THR   PSI     116.0   148.0)
       convention = CYANA or CYANA2
       return a DihedralRestraintList or None on error
    """
    maxErrorCount = 50
    errorCount = 0
    # check the molecule
    if (not project or not project.molecule ):
        NTerror("importAco: initialize molecule first")
        return None
    #end if
    molecule = project.molecule
    # Sometimes set from other than CYANA coordinate file.
#    chainId = molecule.chains[0].name

    if not os.path.exists( acoFile ):
        NTerror('importAco: file "%s" not found\n', acoFile)
        return None
    #end if

    dir,name,_ext = NTpath( acoFile )
    result     = project.dihedrals.new( name=name, status='keep')
    resNumDict = molecule._getResNumDict()

    NTdebug("Now reading: " + acoFile)
    for line in AwkLike( acoFile, commentString = '#' , minNF = 5):

        resNum = line.int(1)
        res    = None
        if resNum in resNumDict:
            res = resNumDict[resNum]

        angle  = line.dollar[3]
        lower  = line.float(4)
        upper  = line.float(5)
        if res and angle in res.db:
            atoms = translateTopology( res, res.db[angle].atoms )
#            print '>', atoms, res, res.db[angle]
            if None in atoms:
                if errorCount <= maxErrorCount:
                    NTerror("Failed to decode all atoms from line:"+ line.dollar[0])
                if errorCount == (maxErrorCount+1):
                    NTerror("And so on")
                errorCount += 1
                continue
            else:
                r = DihedralRestraint( atoms = atoms, lower=lower, upper=upper,
                                            angle = angle, residue = res
                                          )
                #print r.format()
                result.append( r )
            #end if
        #end if
    #end for

    if errorCount:
        NTerror("Found number of errors importing upl file: " + `errorCount`)
#    NTmessage("Imported items: " + `len(result)`)
    NTmessage('==> importAco: new %s from "%s"', result, acoFile )
    return result
#end def

def exportDistanceRestraint2cyana( dr, upper=True, convention=CYANA2 ):
    """
    Export a upper (upper=True) or lower (Upper=False) distance restraint in CYANA or CYANA2 format
    Return a string or None on error
    """
    if convention != CYANA and convention != CYANA2:
        NTerror('exportDistanceRestraint2cyana: invalid convention "%s"', convention)
        return None
    #end if

    first = True
    if upper:
        val = dr.upper
    else:
        val = dr.lower
    #end if

    if val == 0.0: # this will interfere with Cyana's def for ambigious restraints
        val = 0.01
    #end if

    for atm1,atm2 in dr.atomPairs:
        if first:
            result = sprintf('%-3d %-4s %-4s  %-3d %-4s %-4s %7.2f',
                             atm1.residue.resNum, atm1.residue.translate(convention), atm1.translate(convention),
                             atm2.residue.resNum, atm2.residue.translate(convention), atm2.translate(convention),
                             val
                            )
            first = False
        else:
            #Ambigous
            result = result + '\n' + \
                     sprintf('%-3d %-4s %-4s  %-3d %-4s %-4s %7.2f',
                             atm1.residue.resNum, atm1.residue.translate(convention), atm1.translate(convention),
                             atm2.residue.resNum, atm2.residue.translate(convention), atm2.translate(convention),
                             0.0
                            )
        #end if
    #end for
    return result
#end def
#Add as method to DistanceRestraint class
DistanceRestraint.export2cyana = exportDistanceRestraint2cyana

def exportDistanceRestraintList2cyana( drl, path, convention=CYANA2)   :
    """Export a distanceRestraintList (drl) to cyana format:
       convention = CYANA or CYANA2
       generate both .upl and .lol files from path
       return drl or None on error
    """
    if convention != CYANA and convention != CYANA2:
        NTerror('exportDistanceRestraintList2cyana: invalid convention "%s"', convention)
        return None
    #end if

    root, name, _tmp = NTpath(path)
    path = os.path.join(root,name)
    uplfile = open( path + '.upl', 'w' )
    if not uplfile:
        NTerror('exportDihedralRestraintList2cyana: unable to open "%s"\n', path + '.upl' )
        return None
    #end def
    lolfile = open( path + '.lol', 'w' )
    if not lolfile:
        NTerror('exportDihedralRestraintList2cyana: unable to open "%s"\n', path + '.lol' )
        return None
    #end def

    for dr in drl:
        fprintf( uplfile, '%s\n', dr.export2cyana( upper=True, convention=convention ) )
        fprintf( lolfile, '%s\n', dr.export2cyana( upper=False, convention=convention ) )
    #end for

    uplfile.close()
    lolfile.close()
    NTmessage('==> Exported %s in %s format to "%s" and "%s"', drl, convention, path+'.upl', path+'.lol')
    #end if
    return drl
#end def
# add as a method to DistanceRestraintList Class
DistanceRestraintList.export2cyana = exportDistanceRestraintList2cyana


def importUpl( project, uplFile, convention, lower = 0.0 ):
    """Read Cyana upl file
       return a DistanceRestraintList or None on error
    """
    maxErrorCount = 50
    errorCount = 0

    # check the molecule
    if not project or not project.molecule:
        NTerror("importUpl: initialize molecule first")
        return None
    #end if
    molecule = project.molecule
    # Sometimes set from other than CYANA coordinate file.
#    chainId = molecule.chains[0].name # assumed unkown rite?

    if not os.path.exists( uplFile ):
        NTerror('importUpl: file "%s" not found', uplFile)
        return None
    #end if

    dir,name,_ext = NTpath( uplFile )
    result        = project.distances.new( name=name, status='keep')
    atomDict      = molecule._getAtomDict(convention)

    for line in AwkLike( uplFile, commentString="#", minNF=7 ):
#        if line.isComment():
##            NTdebug("Skipping upl file line with comment: [" + line.dollar[0] +']')
#            continue
#        if line.NF < 7:
##            NTdebug("Skipping upl file line with too few fields: [" + line.dollar[0] +']')
#            continue
        atmIdxList = [[1,3],[4,6]]
        atmList = []
        i=0
        for atmIdx in atmIdxList:
#            NTdebug("Doing atmIdx: " + `atmIdx`)
            t = (line.int(atmIdx[0]), line.dollar[atmIdx[1]])
            atm = None
            if atomDict.has_key(t):
                atm = atomDict[t]
#            atm = molecule.decodeNameTuple( (convention, None, line.int(atmIdx[0]), line.dollar[atmIdx[1]]),
#                                            fromCYANA2CING=True)
            if not atm:
                if errorCount <= maxErrorCount:
                    NTerror('Failed to decode for atom %s; line: %s', t, line.dollar[0] )
                if errorCount == maxErrorCount+1:
                    NTerror("And so on")
                errorCount += 1
                i+=1
                continue
            atmList.append( atm )
            i+=1
        if len(atmList) != 2:
            continue
        # Unpack convenience variables.
        atm1 = atmList[0]
        atm2 = atmList[1]
#        NTdebug("atom 1: " + `atm1`)
#        NTdebug("atom 2: " + `atm2`)
        upper = line.float(7)
        if not upper:
            NTerror("Skipping line without valid upper bound on line: [" + line.dollar[0]+']')
            continue

        # ambiguous restraint, should be append to last one
        if upper == 0:
            result().appendPair( (atm1,atm2) )
            continue


        r = DistanceRestraint( atomPairs= [(atm1,atm2)], lower=lower, upper=upper )
        result.append( r )
        # also store the Candid info if present
        if line.NF >= 9:
            r.peak = line.int( 9 )
        if line.NF >= 11:
            r.SUP = line.float( 11 )
        if line.NF >= 13:
            r.QF = line.float( 13 )
    #end for
    if errorCount:
        NTerror("Found number of errors importing upl file: " + `errorCount`)

#    NTmessage("Imported upl items: " + `len(result)`)
    NTmessage('==> importUpl: new %s from "%s"', result, uplFile )
#    sys.exit(1)
    return result
#end def

def importCyanaStereoFile( project, stereoFileName, convention ):
    """Import stereo assignments from CYANA
       return project or None on error.

CYANA stereo file:

var info echo
echo:=off
info:=none
atom stereo "HB2  HB3   509"   # GLU-
atom stereo "QG1  QG2   511"   # VAL
atom stereo "HB2  HB3   513"   # HIS
atom stereo "QG1  QG2   514"   # VAL
atom stereo "HG2  HG3   516"   # GLU-
atom stereo "HA1  HA2   519"   # GLY

    """
    if project.molecule == None:
        return None

    molecule = project.molecule
    atomDict = molecule._getAtomDict(convention)
    count = 0
    for line in AwkLike( stereoFileName, minNF=5 ):
        if line.dollar[1] == 'atom' and line.dollar[2] == 'stereo':
            resnum = int (line.dollar[5].strip('"') )
            for i in [3,4]:
                atm = None
                t = (resnum, line.dollar[i].strip('"'))
                if atomDict.has_key(t):
                    atm = atomDict[t]
#                atm = molecule.decodeNameTuple( (convention, 'A', resnum, line.dollar[i].strip('"')) )
                if atm == None:
                    NTerror('importCyanaStereoFile: atom %s; line %d (%s)\n', line.dollar[i], line.NR, line.dollar[0] )
                else:
                    atm.stereoAssigned = True
                    count += 1
                    #print atm.nameTuple()
                    if atm.residue.db.name in ['VAL', 'LEU'] and atm.isMethylProton():        # Val, Ile methyls: Carbon implicit in CYANA defs
                        heavy = atm.heavyAtom()
                        heavy.stereoAssigned = True
                        count += 1
                        #print heavy.nameTuple()
                    #end if
                #end if
            #end for
        #end if
    #end for
    NTmessage('==> Derived %d stereo assignments from "%s"', count, stereoFileName )
    return project
#end def

#-----------------------------------------------------------------------------
def export2cyana( project, tmp=None ):
    """Export restraints in CYANA and CYANA2 formats
    """
    for drl in project.dihedrals:
        if (drl.status == 'keep'):
            #Xeasy/Cyana 1.x format
            drlFile = project.path( project.directories.xeasy, drl.name+'.aco' )
            drl.export2cyana( drlFile, convention=CYANA)
            #Cyana 2.x format
            drlFile = project.path( project.directories.xeasy2, drl.name+'.aco' )
            drl.export2cyana( drlFile, convention=CYANA2)
        #end if
    #end for
    for drl in project.distances:
        if (drl.status == 'keep'):
            #Xeasy/Cyana 1.x format
            drlFile = project.path( project.directories.xeasy, drl.name ) # extensions get appended
            drl.export2cyana( drlFile, convention=CYANA)
            #Cyana 2.x format
            drlFile = project.path( project.directories.xeasy2, drl.name ) # extensions get appended
            drl.export2cyana( drlFile, convention=CYANA2)
        #end if
    #end for
#end def

#-----------------------------------------------------------------------------
def cyana2cing( project, cyanaDirectory, convention=CYANA2, copy2sources=True, update=True,
                coordinateConvention=None, **kwds):
    """
     kwds options:
                seqFile   = None,
                protFile  = None,
                stereoFile = None,
                peakFiles = [],
                uplFiles  = [],
                acoFiles  = [],
                pdbFile   = None,
                nmodels=None,


    Read the data from the cyanaDirectory and store in project.
    Optionally set to defaults by supplying 'default' as argument

    Return list of sources or None on error.
    """

    if not coordinateConvention:
        coordinateConvention = convention
    sources   = NTlist()
    sourceDir = project.mkdir( project.directories.sources, 'Cyana' )

    kwds.setdefault('seqFile',  None)
    kwds.setdefault('protFile', None)
    kwds.setdefault('stereoFile', None)
    kwds.setdefault('pdbFile',  None)
    kwds.setdefault('nmodels',  None)

    # peakFiles, uplFiles, acoFiles arguments can be a list of comma-separated string
    for f in ['peakFiles','uplFiles','acoFiles']:
        kwds.setdefault(f,  [])
        if isinstance( kwds[f], str ):
            kwds[f] = kwds[f].split(',')
    NTdebug( '>>'+ `kwds` )

    # look for pdb, initiate new Molecule instance.
    # This goes first so that peaks, upls and acos refer to this molecule
    if (kwds['pdbFile'] != None):
        pdbFile = os.path.join( cyanaDirectory, kwds['pdbFile'] + '.pdb')
        mol = project.initPDB( pdbFile, coordinateConvention, nmodels=kwds['nmodels'], update=update )
        if not mol:
            NTerror('Project.cyana2cing: parsing PDB-file "%s" failed', pdbFile)
            return None
        #end if
        NTdebug('Parsed PDB file "%s", molecule %s', pdbFile, mol)
        sources.append( pdbFile )

    if (kwds['seqFile'] != None and kwds['protFile'] != None):
        seqFile  = os.path.join( cyanaDirectory, kwds['seqFile']  +'.seq')
        protFile = os.path.join( cyanaDirectory, kwds['protFile'] +'.prot')
        if project.importXeasy( seqFile, protFile, convention ) != None:
            sources.append( seqFile, protFile )

    if (kwds['stereoFile'] != None):
        stereoFile = os.path.join( cyanaDirectory, kwds['stereoFile']  +'.cya')
        if project.importCyanaStereoFile( stereoFile, convention ):
            sources.append( stereoFile )


    for f in kwds['peakFiles']:
        if (kwds['seqFile'] != None and kwds['protFile'] != None):
            seqFile  = os.path.join( cyanaDirectory, kwds['seqFile']  + '.seq')
            protFile = os.path.join( cyanaDirectory, kwds['protFile'] + '.prot')
            pkFile   = os.path.join( cyanaDirectory, f + '.peaks')
            if project.importXeasyPeaks( seqFile,protFile,pkFile,convention ):
                sources.append( seqFile, protFile, pkFile )

    for f in kwds['uplFiles']:
        uplFile = os.path.join( cyanaDirectory, f + '.upl')
        if project.importUpl( uplFile, convention ):
            sources.append( uplFile )
#            project.patch.upl.append( uplFile )
        #end if
    #end for

    for f in kwds['acoFiles']:
        acoFile = os.path.join( cyanaDirectory, f + '.aco')
        if (project.importAco( acoFile, convention )):
            sources.append( acoFile )
#            project.patch.aco.append( acoFile )
        #end if
    #end for

    NTdebug( str(sources) )
    sources.removeDuplicates()
    if copy2sources:
        for f in sources:
            #print '>>', f, sourceDir
            shutil.copy( f, sourceDir )
        #end for
    #end if

    NTdebug( 'cyana2cing: %s', project.format())
    return sources
#end def

#def patchRestore( project, dummy = None ):
#    """Restore files from patches attribute
#    """
#    if project.has_key('patch'):
##        for f in project.patch.upl:
##            project.importUpl( f, project.patch.convention )
#        #end for
#        for f in project.patch.aco:
#            project.importAco( f, project.patch.convention )
#        #end for
#    #end if
##end def

#-----------------------------------------------------------------------------
# register the functions
methods  = [(importUpl, None),
            (importAco, None),
            (cyana2cing, None),
            (importCyanaStereoFile, None)
           ]
#saves    = []
#restores = []
exports  = [(export2cyana, None)
           ]
