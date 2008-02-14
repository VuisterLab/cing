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
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import sprintf
from cing.core.classes import DihedralRestraint
from cing.core.classes import DihedralRestraintList
from cing.core.classes import DistanceRestraint
from cing.core.constants import CYANA
from cing.core.constants import CYANA2
from cing.core.molecule import translateTopology
from cing.Libs.NTutils import printError
from cing.Libs.NTutils import printMessage
from cing.Libs.NTutils import printDebug
import os
import shutil

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

#-----------------------------------------------------------------------------
def exportDihedralRestraintList2cyana( drl, path, convention)   :
    """Export a dihedralRestraintList (drl) to cyana format:
       convention = CYANA or CYANA2
       return drl or None on error
    """
    fp = open( path, 'w' )
    if not fp: 
        NTerror('ERROR exportDihedralRestraintList2cyana: unable to open "%s"\n', path )
        return None
    #end def
    for dr in drl:
        fprintf( fp, '%s\n', dr.export2cyana( convention ) )
    #end for
    
    fp.close()
    NTmessage('==> Exported %s in %s format to "%s"\n', drl, convention, path)
    #end if
    return drl
#end def
# add as a method to DistanceRestraintList Class
DihedralRestraintList.export2cyana = exportDihedralRestraintList2cyana

#-----------------------------------------------------------------------------
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
        NTerror("ERROR importAco: initialise molecule first\n")
        return None
    #end if
    molecule = project.molecule
  
    if not os.path.exists( acoFile ):
        NTerror('ERROR importAco: file "%s" not found\n', acoFile)
        return None
    #end if
         
    dir,name,_ext = NTpath( acoFile )
    result       = project.dihedrals.new( name=name, status='keep')   
    
    printDebug("Now reading: " + acoFile)
    for line in AwkLike( acoFile, commentString = '#' , minNF = 5):
        resNum = line.int(1)
        res    = molecule.decodeNameTuple( (convention, 'A', resNum, None ) )
        angle  = line.dollar[3]
        lower  = line.float(4)
        upper  = line.float(5)
        if res and angle in res.db:
            atoms = translateTopology( res, res.db[angle].atoms )
#            print '>', atoms, res, res.db[angle]
            if None in atoms:
                if errorCount <= maxErrorCount:
                    printError("Failed to decode all atoms from line:"+ line.dollar[0])
                if errorCount == (maxErrorCount+1):
                    printError("And so on")
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
        printError("Found number of errors importing upl file: " + `errorCount`)
    printMessage("Imported items: " + `len(result)`)
    NTmessage('==> importAco: new %s from "%s"\n', result, acoFile )  
    return result
#end def


#-----------------------------------------------------------------------------
def importUpl( project, uplFile, convention, lower = 0.0 ):
    """Read Cyana upl file
       return a DistanceRestraintList or None on error
    """
    maxErrorCount = 50
    errorCount = 0
  
    # check the molecule
    if not project or not project.molecule:
        NTerror("ERROR importUpl: initialise molecule first\n")
        return None
    #end if
    molecule = project.molecule
  
    if not os.path.exists( uplFile ):
        NTerror('ERROR importUpl: file "%s" not found\n', uplFile)
        return None
    #end if
   
    dir,name,_ext = NTpath( uplFile )
#    result       = project.newDistanceRestraintList( name )
    result       = project.distances.new( name=name, status='keep')   
    
    for line in AwkLike( uplFile, commentString="#" ):
        if not line.isComment() and line.NF >= 7:
        
            atm1 = molecule.decodeNameTuple( (convention, 'A', line.int(1), line.dollar[3]) )
            atm2 = molecule.decodeNameTuple( (convention, 'A', line.int(4), line.dollar[6]) )

            if not atm1 or not atm2:
                if errorCount <= maxErrorCount:
                    printError("Failed to decode name tuple using residue number and atom name from line:"+ line.dollar[0])
                if errorCount == (maxErrorCount+1):
                    printError("And so on")
                errorCount += 1
                continue
            
            upper = line.float(7)

            if upper == 0.0 and atm1 != None and atm2 != None:
                # ambigious restraint, should be append to last one
                result().appendPair( (atm1,atm2) )
            elif atm1 != None and atm2 != None:
                r = DistanceRestraint( atomPairs= [(atm1, atm2)], lower=lower, upper=upper )
                # also store the Candid info if present
                if (line.NF >= 9):
                    r.peak = line.int( 9 ) 
                if (line.NF >= 11):
                    r.SUP = line.float( 11 ) 
                if (line.NF >= 13):
                    r.QF = line.float( 13 ) 
                result.append( r )
            else:
                if errorCount <= maxErrorCount:
                    printError("invalid restraint on line:"+ line.dollar[0])
                if errorCount == (maxErrorCount+1):
                    printError("And so on")
                errorCount += 1
                continue
            #end if
        #end if
    #end for 
    if errorCount:
        printError("Found number of errors importing upl file: " + `errorCount`)
    printMessage("Imported upl items: " + `len(result)`)
    NTmessage('==> importUpl: new %s from "%s"\n', result, uplFile )
    #end if
  
    return result
#end def

#-----------------------------------------------------------------------------
def export2cyana( project, tmp=None ):
    """Export restraints in CYANA and CYANA2 formats
    """
    for drl in project.dihedrals:
        if (drl.status == 'keep'):
            #Xeasy/Cyana 1.x format
            drlFile = project.path( project.directories.xeasy, drl.name+'.aco' )
            drl.export2cyana( drlFile, convention=CYANA,   )
            #Cyana 2.x format
            drlFile = project.path( project.directories.xeasy2, drl.name+'.aco' )
            drl.export2cyana( drlFile, convention=CYANA2,   )
        #end if
    #end for
#end def

#-----------------------------------------------------------------------------
def cyana2cing( project, cyanaDirectory, convention=CYANA2, copy2sources=False, **kwds):
    """
     kwds options:
                seqFile   = None, 
                protFile  = None,  
                peakFiles = [],
                uplFiles  = [],
                acoFiles  = [],
                pdbFile   = None, nmodels=None,

    
    Read the data from the cyanaDirectory and store in project.
    Optionally set to defaults by supplying 'default' as argument
    
    Return list of sources or None on error.
    """
    
    sources   = NTlist()
    sourceDir = project.mkdir( project.directories.sources, 'Cyana' )
    
    kwds.setdefault('seqFile',  None)
    kwds.setdefault('protFile', None)
    kwds.setdefault('pdbFile',  None)
    kwds.setdefault('nmodels',  None)

    # peakFiles, uplFiles, acoFiles arguments can be a list of comma-separated string
    for f in ['peakFiles','uplFiles','acoFiles']:
        kwds.setdefault(f,  [])        
        if isinstance( kwds[f], str ):
            kwds[f] = kwds[f].split(',')
        #end if
    #end for
    printDebug( '>>'+ `kwds` )
        

    #print '>>',kwds
    
    # look for default seqfile
#    d,s,e = NTpath( matchfilelist( cyanaDirectory +'/*.seq')[0] )    
#    defaults = NTdict(
#        seqFile   = s,
#        protFile  = 'all-final',
#        pdbFile   = 'final',
#        peakFiles = ['c13','aro','n15'],
#        uplFiles  = ['final'],
#        acoFiles  = ['talos']
#    )
#    
#    # set defaults
#    for f,value in defaults.items():
#        if kwds[f] == 'default' or 'default' in kwds:
#            kwds[f] = defaults[f]
#        #end if
#    #end for
    
    # look for pdb, initiate new Molecule instance.
    # This goes first so that peaks, upls and acos refer to this molecule
    if (kwds['pdbFile'] != None):
        pdbFile = os.path.join( cyanaDirectory, kwds['pdbFile'] + '.pdb')
        project.initPDB( pdbFile, convention, nmodels=kwds['nmodels'] )
        sources.append( pdbFile )
    #end if
    
    if (kwds['seqFile'] != None and kwds['protFile'] != None):
        seqFile  = os.path.join( cyanaDirectory, kwds['seqFile']  +'.seq')
        protFile = os.path.join( cyanaDirectory, kwds['protFile'] +'.prot')
        if project.importXeasy( seqFile, protFile, convention ):            
            sources.append( seqFile, protFile )
        #end if
    #end if
    
    for f in kwds['peakFiles']:    
        if (kwds['seqFile'] != None and kwds['protFile'] != None):
            seqFile  = os.path.join( cyanaDirectory, kwds['seqFile']  + '.seq')
            protFile = os.path.join( cyanaDirectory, kwds['protFile'] + '.prot')
            pkFile   = os.path.join( cyanaDirectory, f + '.peaks')
            if project.importXeasyPeaks( seqFile,protFile,pkFile,convention ):                       
                sources.append( seqFile, protFile, pkFile )
            #end if
        #end if
    #end for
    
#    # patches for saveing upl,aco files
#    project.patch = NTdict( upl= NTlist(), aco=NTlist(), convention = convention )
#    project.saveXML('patch','__SAVEXML__')
#    project.patch.saveXML('aco','upl','convention','__SAVEXML__')
    
    #end if
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

    sources.removeDuplicates()
    if copy2sources:
        for f in sources:
            #print '>>', f, sourceDir
            shutil.copy( f, sourceDir )
        #end for
    #end if
    
    printDebug( project.format())
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
            (cyana2cing, None)
           ]
#saves    = []
#restores = []
exports  = [(export2cyana, None)
           ]
