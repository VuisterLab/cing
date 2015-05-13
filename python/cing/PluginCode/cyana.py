"""
Adds CYANA import/export methods


Methods:
  Project.importUpl( uplFile, convention, lower ):
        import uplFile
        convention = CYANA or CYANA2
        return a DistanceRestraintList or None on error

  Project.importAco( acoFile ):
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
from cing.Libs import PyMMLib
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import isRootDirectory
from cing.core.classes import DihedralRestraint
from cing.core.classes import DihedralRestraintList
from cing.core.classes import DistanceRestraint
from cing.core.classes import DistanceRestraintList
from cing.core.constants import * #@UnusedWildImport
from cing.core.molecule import translateTopology
from glob import glob
from shutil import move
from shutil import rmtree
import shutil
import tarfile

def exportDihedralRestraint2cyana( dr, convention ):
    """Return string with distanceRestraint (dr) in cyana format or None on error
       ( 512 THR   PSI     116.0   148.0)
       convention = CYANA or CYANA2
       return dr or None on error
    """
    if not dr:
        nTerror('Error exportDihedralRestraint2cyana: undefined restraint\n' )
        return None
    #end if

    res, angleName, _db = dr.retrieveDefinition()
    if res:
        return sprintf( '%4d %-4s %-7s %6.1f %6.1f', # longest name seems to be EPSILON (7 chars)
                        res.resNum, res.translate(convention),
                        angleName, dr.lower, dr.upper
                      )
    else:
        nTerror('Error exportDihedralRestraint2cyana: cannot export dihedral restraint "%s"\n', str(dr) )
        return None
    #end if
    return dr
#end def
# add as a method to DihedralRestraint Class
DihedralRestraint.export2cyana = exportDihedralRestraint2cyana


def exportDihedralList2cyana( drl, path, convention)   :
    """Export a dihedralRestraintList (drl) to cyana format:
       convention = CYANA or CYANA2
       return drl or None on error
    """
    fp = open( path, 'w' )
    if not fp:
        nTerror('exportDihedralList2cyana: unable to open "%s"\n', path )
        return None
    #end def
    for dr in drl:
        fprintf( fp, '%s\n', dr.export2cyana( convention ) )
    #end for

    fp.close()
    nTmessage('==> Exported %s in %s format to "%s"', drl, convention, path)
    #end if
    return drl
#end def
# add as a method to DistanceRestraintList Class
DihedralRestraintList.export2cyana = exportDihedralList2cyana


def importAco( project, acoFile ):
    """Read Cyana acoFile
       ( 512 THR   PSI     116.0   148.0)
       convention = CYANA or CYANA2
       return a DihedralRestraintList or None on error
    """
    maxErrorCount = 50
    errorCount = 0
    # check the molecule
    if (not project or not project.molecule ):
        nTerror("importAco: initialize molecule first")
        return None
    #end if
    molecule = project.molecule
    # Sometimes set from other than CYANA coordinate file.
#    chainId = molecule.chains[0].name

    if not os.path.exists( acoFile ):
        nTerror('importAco: file "%s" not found\n', acoFile)
        return None
    #end if

    _dir,name,_ext = nTpath( acoFile )
    result     = project.dihedrals.new( name=name, status='keep')
    resNumDict = molecule.getResNumDict()

    nTmessage("Now reading: " + acoFile)
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
                    nTerror("Failed to decode all atoms from line:"+ line.dollar[0])
                if errorCount == (maxErrorCount+1):
                    nTerror("And so on")
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
        nTerror("Found number of errors importing upl file: %s" % errorCount)
#    nTmessage("Imported items: " + repr(len(result)))
    nTmessage('==> importAco: new %s from "%s"', result, acoFile )
    return result
#end def

def exportDistanceRestraint2cyana( dr, upper=True, convention=CYANA2 ):
    """
    Export a upper (upper=True) or lower (Upper=False) distance restraint in CYANA or CYANA2 format
    Return a string or None on error
    """
    if convention != CYANA and convention != CYANA2:
        nTerror('exportDistanceRestraint2cyana: invalid convention "%s"', convention)
        return None
    #end if

    first = True
    if upper:
        val = dr.upper
    else:
        val = dr.lower
    #end if
    if val == None:
        nTerror("Failed to get lower or upper bound value for %s" % str(dr))
        return None

    if val == 0.0: # this will interfere with Cyana's def for ambiguous restraints
        val = 0.01
    #end if
    

    for atm1,atm2 in dr.atomPairs:
        res1 = atm1.residue
        res2 = atm2.residue
        res1Name = res1.translate(convention)
        res2Name = res2.translate(convention)
        argList = [ res1.resNum, res1Name, atm1.translate(convention),
                    res2.resNum, res2Name, atm2.translate(convention)]
        if first:
            argList.append(val)
            result =    '%-3d %-4s %-4s  %-3d %-4s %-4s %7.2f' % tuple( argList )
            first = False
        else:
            argList.append(0.0)
            #Ambiguous
            result += '\n%-3d %-4s %-4s  %-3d %-4s %-4s %7.2f' % tuple( argList )
        #end if
    #end for
    return result
#end def
#Add as method to DistanceRestraint class
DistanceRestraint.export2cyana = exportDistanceRestraint2cyana

def exportDistancList2cyana( drl, path, convention=CYANA2)   :
    """Export a distanceRestraintList (drl) to cyana format:
       convention = CYANA or CYANA2
       generate both .upl and .lol files from path
       return drl or None on error
    """
    if convention != CYANA and convention != CYANA2:
        nTerror('exportDistancList2cyana: invalid convention "%s"', convention)
        return None
    #end if

    root, name, _tmp = nTpath(path)
    path = os.path.join(root,name)
    uplfile = open( path + '.upl', 'w' )
    if not uplfile:
        nTerror('exportDihedralList2cyana: unable to open "%s"\n', path + '.upl' )
        return None
    #end def
    lolfile = open( path + '.lol', 'w' )
    if not lolfile:
        nTerror('exportDihedralList2cyana: unable to open "%s"\n', path + '.lol' )
        return None
    #end def

    for dr in drl:
        fprintf( uplfile, '%s\n', dr.export2cyana( upper=True, convention=convention ) )
        fprintf( lolfile, '%s\n', dr.export2cyana( upper=False, convention=convention ) )
    #end for

    uplfile.close()
    lolfile.close()
    nTmessage('==> Exported %s in %s format to "%s" and "%s"', drl, convention, path+'.upl', path+'.lol')
    #end if
    return drl
#end def
# add as a method to DistanceRestraintList Class
DistanceRestraintList.export2cyana = exportDistancList2cyana


def importUpl( project, uplFile, convention, lower = 0.0 ):
    """
    Read Cyana upl file
    return a DistanceRestraintList or None on error
    """
    
    #print 'Convention: ' + convention
    
    maxErrorCount = 50
    errorCount = 0

    # check the molecule
    if not project or not project.molecule:
        nTerror("importUpl: initialize molecule first")
        return None
    #end if
    molecule = project.molecule
    # Sometimes set from other than CYANA coordinate file.
#    chainId = molecule.chains[0].name # assumed unkown rite?

    if not os.path.exists( uplFile ):
        nTerror('importUpl: file "%s" not found', uplFile)
        return None
    #end if

    _dir,name,_ext = nTpath( uplFile )
    result        = project.distances.new( name=name, status='keep')
    atomDict      = molecule.getAtomDict(convention)

    for line in AwkLike( uplFile, commentString="#", minNF=7 ):
#        if line.isComment():
##            nTdebug("Skipping upl file line with comment: [" + line.dollar[0] +']')
#            continue
#        if line.NF < 7:
##            nTdebug("Skipping upl file line with too few fields: [" + line.dollar[0] +']')
#            continue
        atmIdxList = [[1,3],[4,6]]
        atmList = []
#        i=0
        for atmIdx in atmIdxList:
#            nTdebug("Doing atmIdx: " + repr(atmIdx))
            t = (line.int(atmIdx[0]), line.dollar[atmIdx[1]])
            atm = None
            if atomDict.has_key(t):
                atm = atomDict[t]
#            atm = molecule.decodeNameTuple( (convention, None, line.int(atmIdx[0]), line.dollar[atmIdx[1]]),
#                                            fromCYANA2CING=True)
            if not atm:
                if errorCount <= maxErrorCount:
                    nTerror('Failed to decode for atom %s; line: %s', t, line.dollar[0] )
                if errorCount == maxErrorCount+1:
                    nTerror("And so on")
                errorCount += 1
#                i+=1
                continue
            atmList.append( atm )
#            i+=1
        if len(atmList) != 2:
            continue
        # Unpack convenience variables.
        atm1 = atmList[0]
        atm2 = atmList[1]
#        nTdebug("atom 1: " + repr(atm1))
#        nTdebug("atom 2: " + repr(atm2))
        upper = line.float(7)
        # ambiguous restraint, should be append to last one
        if upper == 0:
            result().appendPair( (atm1,atm2) )
            continue
        if not upper:
            nTerror("Skipping line without valid upper bound on line: [" + line.dollar[0]+']')
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
        nTerror("Found number of errors importing upl file: %s" % errorCount)

#    nTmessage("Imported upl items: " + repr(len(result)))
    nTmessage('==> importUpl: new %s from "%s"', result, uplFile )
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
    atomDict = molecule.getAtomDict(convention)
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
                    nTerror('importCyanaStereoFile: atom %s; line %d (%s)\n', line.dollar[i], line.NR, line.dollar[0] )
                else:
                    atm.stereoAssigned = True
                    count += 1
                    #print atm.nameTuple()
                    # Val, Ile methyls: Carbon implicit in CYANA defs
                    if atm.residue.db.name in ['VAL', 'LEU'] and atm.isMethylProton():        
                        heavy = atm.heavyAtom()
                        heavy.stereoAssigned = True
                        count += 1
                        #print heavy.nameTuple()
                    #end if
                #end if
            #end for
        #end if
    #end for
    nTmessage('==> Derived %d stereo assignments from "%s"', count, stereoFileName )
    return project
#end def

#-----------------------------------------------------------------------------
def export2cyana( project):
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

def autoDetectCyanaConvention(pdbFile):
    'Returns None on error or CYANA or CYANA2'
#    tmpProjectName = getRandomKey(size=10)
#    switchOutput(False) # disable standard out.
    countMap = CountMap()    
    countMap['HN'] = 0 # CYANA 1
    countMap['H'] = 0
    pdbRecords = PyMMLib.PDBFile(pdbFile)
    for _i,record in enumerate(pdbRecords):
        recordName = record._name.strip()
        if recordName != "ATOM":
            continue            
        # end if
        atmName = record.name.strip()
        if not (atmName == 'HN' or atmName == 'H'):
            continue 
        # end if
        countMap.increaseCount(atmName, 1)
    # end for
    overallCount = countMap.overallCount()
    if not overallCount:
        nTmessage("Assuming default CYANA2 convention because no amide protons counted at all.")
        return CYANA2
    # end if
    msg = "Amide protons counted of CYANA 1/2 (HN/H) are: %s/%s." % ( countMap['HN'], countMap['H'])
    if countMap['HN'] > countMap['H']:
        nTmessage("Autodetected CYANA convention because " + msg)
        return CYANA
    nTmessage("Autodetected CYANA2 convention because " + msg)
#    switchOutput(True) # disable standard out.
    return CYANA2
# end def

#-----------------------------------------------------------------------------
def cyana2cing( project, cyanaDirectory, convention=CYANA2, copy2sources=True, update=True,
                coordinateConvention=None, useAllInDirectory=False, autoDetectFormat=True, nmodels=None, **kwds):
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
    If useAllInDirectory is set than only but all the files in the directory will matched
    based on filename extension.
    If autoDetectFormat is set and no convention is specified then the PDB file will be queried for 
    distinguishing CYANA from CYANA2.    
     
    Return list of sources or None on error.
    """
#    nTdebug("In %s found convention %s" % ( getCallerName(), convention))
    sources   = NTlist()
    sourceDir = project.mkdir( project.directories.sources, 'Cyana' )

    if useAllInDirectory:
#        nTdebug("Reseting all keywords in cyana2cing and determining the input from filename extensions.")
        kwds = {}
    # end if
    kwds.setdefault('seqFile',  None)
    kwds.setdefault('protFile', None)
    kwds.setdefault('stereoFile', None)
    kwds.setdefault('pdbFile',  None)
#    kwds.setdefault('nmodels',  None) now a named parameter
    # Can be a list of comma-separated string
    for f in ['peakFiles','uplFiles','acoFiles']:
        kwds.setdefault(f,  [])
        if isinstance( kwds[f], str ):
            kwds[f] = kwds[f].split(',')
#    nTdebug( '>>'+ repr(kwds) )
        #end if
    #end for    
    mapExtension2KwdTuple = { # Nice to have an overview of the different types here.
        'pdb':   (0, 'pdbFile'),
        'seq':   (0, 'seqFile'),
        'prot':  (0, 'protFile'),
        'stereo':(0, 'stereoFile'),        
        'peaks': (1, 'peakFiles'),
        'upl':   (1, 'uplFiles'),
        'aco':   (1, 'acoFiles'),                        
    }
    if useAllInDirectory:
#        nTdebug("Determining the input from filename extensions.")
        for extension in mapExtension2KwdTuple.keys():
            pluralityIdx, keyWord = mapExtension2KwdTuple[extension]        
#            nTdebug("Match found for keyword %s and extension %s." % (keyWord, extension))
            globPattern = cyanaDirectory + '/*.' + extension
            fileList = glob(globPattern)
            if not fileList:
#                nTdebug("No match found for %s." % globPattern)
                continue
            # end if
            fileListLength = len(fileList)
            if pluralityIdx == 0:
                if fileListLength == 1:
                    pass
#                    nTdebug("From %s will read file: %s" % (globPattern, fileList))
                else:
                    nTwarning("From %s will read ONLY FIRST file: %s" % (globPattern, fileList[0]))
                # end if
                fn = fileList[0]
                fnBaseName = os.path.basename(fn).split('.')[0]
#                nTdebug("Appending singular %s to keyWord: %s" % (fnBaseName, keyWord))
                kwds[keyWord] = fnBaseName
                continue
            # end if
            kwds[keyWord] = []        
            for fn in fileList:
                fnBaseName = os.path.basename(fn).split('.')[0]
#                nTdebug("Appending potentially plural %s to keyWord: %s" % (fnBaseName, keyWord))
                kwds[keyWord].append(fnBaseName)
            # end for        
        # end for
    # end if
        
#    nTdebug("In %s found convention %s" % ( getCallerName(), convention))
    if not convention:
        convention = CYANA2
        if autoDetectFormat:
            if not kwds['pdbFile']:
                nTdebug("Convention %s will be assumed as no PDB file was given." % CYANA2)
            else:
                pdbFile = os.path.join( cyanaDirectory, kwds['pdbFile'] + '.pdb')
                convention = autoDetectCyanaConvention(pdbFile)
                if convention:
                    nTdebug("Detected convention: %s" % convention)
                else:
                    nTwarning("No CYANA like convention detected")
            # end if
        # end if
    # end if
    if not coordinateConvention:
        coordinateConvention = convention
    # end if
   
    # look for pdb, initiate new Molecule instance.
    # This goes first so that peaks, upls and acos refer to this molecule
    if kwds['pdbFile']:
        pdbFile = os.path.join( cyanaDirectory, kwds['pdbFile'] + '.pdb')
        mol = project.initPDB( pdbFile, coordinateConvention, nmodels=nmodels, update=update )
        if not mol:
            nTerror('Project.cyana2cing: parsing PDB-file "%s" failed', pdbFile)
            return None
        #end if
        nTmessage('Parsed PDB file "%s", molecule %s', pdbFile, mol)
        sources.append( pdbFile )
    #end if
    if kwds['seqFile'] and kwds['protFile']:
        seqFile  = os.path.join( cyanaDirectory, kwds['seqFile']  +'.seq')
        protFile = os.path.join( cyanaDirectory, kwds['protFile'] +'.prot')
        if project.importXeasy( seqFile, protFile, convention ) != None:
            sources.append( seqFile, protFile )
        #end if
    #end if
    if kwds['stereoFile']:
        # renamed to .stereo to fit normal extension as coming in to iCing.
        # JFD realizing that this may limit the more extensive features already in the importer now.
        stereoFile = os.path.join( cyanaDirectory, kwds['stereoFile']  +'.stereo')
        if project.importCyanaStereoFile( stereoFile, convention ):
            sources.append( stereoFile )
        # end if
    # end if
    for f in kwds['peakFiles']:
        if (kwds['seqFile'] != None and kwds['protFile'] != None):
            seqFile  = os.path.join( cyanaDirectory, kwds['seqFile']  + '.seq')
            protFile = os.path.join( cyanaDirectory, kwds['protFile'] + '.prot')
            pkFile   = os.path.join( cyanaDirectory, f + '.peaks')
            if project.importXeasyPeaks( seqFile, protFile, pkFile, convention ):
                sources.append( seqFile, protFile, pkFile )
        # end if
    # end for
    for f in kwds['uplFiles']:
        uplFile = os.path.join( cyanaDirectory, f + '.upl')
        if project.importUpl( uplFile, convention ):
            sources.append( uplFile )
#            project.patch.upl.append( uplFile )
        #end if
    #end for

    for f in kwds['acoFiles']:
        acoFile = os.path.join( cyanaDirectory, f + '.aco')
        if (project.importAco( acoFile )):
            sources.append( acoFile )
#            project.patch.aco.append( acoFile )
        #end if
    #end for

    nTmessage( 'Added to source directory %s: sources %s' % (sourceDir, str(sources) ))
    sources.removeDuplicates()
    if copy2sources:
        for f in sources:
            #print '>>', f, sourceDir
            shutil.copy( f, sourceDir )
        #end for
    #end if
    nTmessage( 'cyana2cing:\n%s', project.format())
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
#            project.importAco( f )
#        #end for
#    #end if
##end def

def initCyana(project, cyanaFolder, modelCount = None, convention=None, coordinateConvention=None, autoDetectFormat=True):
    """
    Return True on success or None on failure
    cyanaFolder can be a directory or a .tgz.
    """
#    nTdebug("In %s found convention %s" % ( getCallerName(), convention))
    if not cyanaFolder:
        nTerror("cyanaFolder not specified")
        return None
    # end if
    if not os.path.exists( cyanaFolder ):
        nTerror('initCyana: cyanaFolder "%s" does not exist', cyanaFolder)
        return None
    # end if    
    if os.path.isfile(cyanaFolder) and ( cyanaFolder.endswith(".tgz") or cyanaFolder.endswith(".tar.gz")):
        try: # If present the target will be removed so it doesn't need to be overwritten.
            rmtree(project.name)
            nTmessage("Removed directory: %s" % project.name)
        except:
            pass
        # Get a TarFile class.
        cyanaRootDirectory = None
        tar = tarfile.open(cyanaFolder, "r:gz")
        tarFileNames = []
        for itar in tar:
#            nTdebug("working on: " + itar.name)
            if os.path.exists(itar.name):
                nTerror("Will not untar %s by overwriting current copy" % itar.name)
                return None
            if itar.name.count('._'):
#                nTdebug("Skipping special hidden file: " + itar.name)
                continue
            tar.extract(itar.name, '.') # itar is a TarInfo object
            if not cyanaRootDirectory: # pick only the first one.
                tarFileNames.append(itar.name)
                if isRootDirectory(itar.name):
                    cyanaRootDirectory = itar.name.replace("/", '')
                    if not cyanaRootDirectory:
                        nTerror("Skipping potential cyanaRootDirectory")
                    # end if            
                # end if            
            # end if            
        # end for
        tar.close()        
        if not cyanaRootDirectory:
            # in python 2.6 tarfile class doesn't append '/' in root dir anymore
            # sorting by length and taking the shortest, likely the root dir.
            tarFileNames.sort()
            cyanaRootDirectory = tarFileNames[0]
            if not os.path.isdir(cyanaRootDirectory):
                nTerror("No cyanaRootDirectory found in gzipped tar file: %s" % cyanaFolder)
                nTerror("First listed directory after sorting: %s" % cyanaRootDirectory)
                return None
            # end if
        # end if                
        if cyanaRootDirectory != project.name:
            nTmessage("Moving Cyana directory from [%s] to [%s]" % (cyanaRootDirectory, project.name))
            move(cyanaRootDirectory, project.name)
        # end if
        cyanaFolder = project.name # Now it is a folder.
    # end if
    if not os.path.exists(cyanaFolder):
        nTerror("cyanaFolder '%s' not found", cyanaFolder)
        return None
    # end if
    if not os.path.isdir(cyanaFolder):
        nTerror("cyanaFolder '%s' not not a directory", cyanaFolder)
        return None
    # end if
    sourceList = cyana2cing( project, cyanaFolder, 
                             convention=convention, coordinateConvention=coordinateConvention, 
                             useAllInDirectory=True, autoDetectFormat=autoDetectFormat)    
    return sourceList
# end def
#-----------------------------------------------------------------------------
# register the functions
methods  = [(initCyana, None),
            (importUpl, None),
            (importAco, None),
            (cyana2cing, None),
            (importCyanaStereoFile, None)
           ]
#saves    = []
#restores = []
exports  = [(export2cyana, None)
           ]
