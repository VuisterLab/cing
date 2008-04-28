from cing import authorList
from cing import cingRoot
from cing import cingVersion
from cing import programName
from cing.Libs.Geometry import violationAngle
from cing.Libs.NTutils import NTaverage
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTfill
from cing.Libs.NTutils import NTindent
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import NTsort
from cing.Libs.NTutils import NTtoXML
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import XML2obj
from cing.Libs.NTutils import XMLhandler
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import obj2XML
from cing.Libs.NTutils import removedir
from cing.Libs.NTutils import sprintf
from cing.Libs.NTutils import val2Str
from cing.core.constants import COLOR_GREEN
from cing.core.constants import COLOR_ORANGE
from cing.core.constants import COLOR_RED
from cing.core.constants import LOOSE
from cing.core.constants import NOSHIFT
from cing.core.molecule import Atom
from cing.core.molecule import Molecule
from cing.core.molecule import NTdihedralOpt
from cing.core.molecule import NTdistanceOpt
from cing.core.molecule import dots
from cing.core.parameters import cingPaths
from cing.core.parameters import directories
from cing.core.parameters import moleculeDirectories
from cing.core.parameters import parameters
from cing.core.parameters import plotParameters
from cing.core.parameters import plugins
from cing.core.sml import SMLhandler
from shutil import rmtree
import math
import os
import shutil
import sys
import time



projects = NTlist()

#-----------------------------------------------------------------------------
# Cing classes and routines
#-----------------------------------------------------------------------------

class Project( NTdict ):

    """
-------------------------------------------------------------------------------
Project: Top level Cing project class
-------------------------------------------------------------------------------

                                   ccpnResidue
                                        ^
                         ccpnChain      |     ccpnAtom
                             ^          |        ^
             ccpnMolecule    |          |        |  Coordinate
                 ^           |          |        |  ^
                 |           |          |        |  |
                 v           v          v        v  v
  Project ->  Molecule <-> Chain <-> Residue <-> Atom <-> Resonance <- Peak
     ^                                  |          |
     |                                  v          v
     v                    NTdb <-> ResidueDef <-> AtomDef
  ccpnProject

  Project.ccpn     = ccpnProject    (Molecule.ccpn      =  ccpnMolecule and so on)
  ccpnProject.cing = Project        (ccpnMolecule.cing  =  Molecule and so on)

  ccpnProject :: (memops.Implementation.Project)
  ccpnMolecule = ccpnProject.molSystems[0]   :: (ccp.molecule.MolSystem.MolSystem)
  ccpnChain   in ccpnMolecule.sortedChains() :: (ccp.molecule.MolSystem.Chain)
  ccpnResidue in ccpnChain.sortedResidues()  :: (ccp.molecule.MolSystem.Residue)
  ccpnAtom    in ccpnResidue.sortedAtoms()   :: (ccp.molecule.MolSystem.Atom)

  Project  -> molecules[Molecule-1, Molecule-2, ...] # Molecules name list
           -> molecule <-> ... (See Molecule)        # 'Current' molecule

           -> peakLists[<Peaklist [<Peak>, ...]>]
          <-> distances[<DistanceRestraintList[<DistanceRestraint>, ...]>]
          <-> dihedrals[<DihedralRestraintList[<DihedralRestraint>, ...]>]

           -> parameters
           -> directories
           -> cingPaths
           -> plotParameters
           -> plugins
  _____________________________________________________________________________

    Methods:

    to open a project:
        project = Project.open( name, status = 'old' )    Open an existing project
        project = Project.open( name, status = 'new' )    Open a new project
        project = Project.open( name, status = 'create' ) Open an existing project
                                                          if it exists or new project
                                                          otherwise

    to initialize a Molecule:
        project.initializeMolecule( name, sequenceFile, convention )

                                    convention = CYANA, CYANA2, INTERNAL, LOOSE

    to save a project:
        project.save()

    to export:
        project.export()

    to export and save:
        project.close()

    to initialize the resonance lists:
        project.initResonances()

    to merge the resonance lists:
        project.mergeResonances( order=None, status='reduce' )
                                status='reduce' results in reducing the resonances
                                list to one merged entry

    to define and add a new PeakList to project:
        peakList = project.newPeakList( name, status='keep' ):

    to define and add a new DistanceRestraintList to project:
        distanceRestraintList = project.distances.new( name, status='keep' ):

    """
    def __init__( self, name ):

        root, name = Project.rootPath( name )

        NTdict.__init__(   self,
                           __CLASS__                = 'Project',

                           version                  =  cingVersion,

                           root                     =  root,
                           name                     =  name.strip(),
                           created                  =  time.asctime(),

                           molecules                =  NTlist(),    # list of names
                           molecule                 =  None,        # Current Molecule instance

                           peakListNames            =  NTlist(),    # list to store peaklist names for save and restore
                           distanceListNames        =  NTlist(),    # list to store distancelist names names for save and restore
                           dihedralListNames        =  NTlist(),    # list to store dihedrallist names for save and restore
                           rdcListNames             =  NTlist(),    # list to store rdclist names for save and restore

                           history                  =  History(),

                           contentIsRestored        =  False,
                           storedInCcpnFormat       =  False,       #


                         # store a reference to te global things we might need
                           gui                      =  None,        # Reference to CingGui instance
                           parameters               =  parameters,
                           directories              =  directories,
                           moleculeDirectories      =  moleculeDirectories,
                           cingPaths                =  cingPaths,
                           plotParameters           =  plotParameters,
                           plugins                  =  plugins
                         )

#       self.peakLists  =  NTlist()
        # These lists are dynamic and will be filled  on restoring a project
        self.peaks      =  ProjectList( self, PeakList,              directories.peaklists,  '.peaks' )
        self.distances  =  ProjectList( self, DistanceRestraintList, directories.restraints, '.distances' )
        self.dihedrals  =  ProjectList( self, DihedralRestraintList, directories.restraints, '.dihedrals' )
        self.rdcs       =  ProjectList( self, RDCRestraintList,      directories.restraints, '.rdcs' )

        self.saveXML( 'version',
                      'name',  'created',
                      'molecules',
                      'peakListNames','distanceListNames','dihedralListNames','rdcListNames',
                      'storedInCcpnFormat',
                      'history'
                    )
#
#        if not os.path.exists( self.root ):
#            os.mkdir( self.root )
#            # Save the project data
#            obj2XML( self, path = self.path( cingPaths.project ) )
#        #end if
#
#        # Check the subdirectories
#        for dir in directories.values():
#            self.mkdir( dir )
#        #end for

    #end def

    def criticize(self):
        for drl in self.distances:
            if drl.criticize():
                self.colorLabel = setMaxColor( self, drl.colorLabel )
        if self.colorLabel:
            return True

    #-------------------------------------------------------------------------
    # Path stuff
    #-------------------------------------------------------------------------

    def path( self, *args ):
        """Return joined args as path relative to root of project
        """
        return os.path.join( self.root, *args )
    #end def

    def rootPath( name ):
        """Static method returning Root,name of project from name

        name can be:
            simple_name_string
            directory.cing
            directory.cing/
            directory.cing/project.xml

        GWV  6 Dec 2007: to allow for relative paths.
        JFD 17 Apr 2008: fixed bugs caused by returning 2 values.
        """
        root,name,ext = NTpath(name)
        if name == '' or name == 'project': # indicate we had a full path
            root,name,ext = NTpath( root )
        #end if
        if (len(ext)>0 and ext != '.cing'):
            NTerror('FATAL ERROR: unable to parse "%s"\n', name )
#            exit(1) # no more hard exits for we might call this from GUI or so wrappers
            return None

        rootp = os.path.join(root, name + '.cing')
        #print '>>',rootp,name

        return rootp, name

    rootPath = staticmethod( rootPath )

    def mkdir( self, *args ):
        """Make a directory relative to to root of project from joined args.
           Check for presence.
           Return the result
        """
        dir = self.path( *args )
        if not os.path.exists( dir ):
#            NTdebug( "project.mkdir: %s" % dir )
            os.makedirs(  dir )
        return dir
    #end def

    def moleculePath(self, subdir=None, *args ):
        """ Path relative to molecule.
        Return path or None in case of error.
        """
        if not self.molecule:
            return None
        if subdir == None:
            return self.path( self.molecule.name )

        return self.path( self.molecule.name, moleculeDirectories[subdir], *args )

    def htmlPath(self, *args ):
        """ Path relative to molecule's html directory.
        Return path or None in case of error.
        """
        return self.moleculePath( 'html', *args )
    #end def
    #-------------------------------------------------------------------------
    # actions open/restore/save/close/export/updateProject
    #-------------------------------------------------------------------------


    def exists( name ):
        rootp, _n = Project.rootPath( name )
        if os.path.exists( rootp ):
            return True
        return False
    #end def
    exists = staticmethod( exists )
    

    def open( name, status = 'create', restore=True ):
        """Static method open returns a new/existing Project instance depending on status
           Project data is restored when restore == True.
        """
        global projects

        #print '>>', name, status

        if (status == 'new'):
            root,dummy = Project.rootPath( name )
            if os.path.exists( root ):
                removedir( root )
            #end if
            os.mkdir( root )
            pr = Project( name )
            pr.addHistory( 'New project'  )
            # Save the project data
            obj2XML( pr, path = pr.path( cingPaths.project ) )

        elif (status == 'create'):
            root,dummy = Project.rootPath( name )
            if os.path.exists( root ):
                return Project.open( name, 'old')
            else:
                return Project.open( name, 'new')
            #end if

        elif (status == 'old'):
            root,newName = Project.rootPath( name )
            if not os.path.exists( root ):
                NTerror('ERROR Project.open: unable to open Project "%s"\n', name )
                return None
            #end if

            # Restore Project from xml-file
            pfile = os.path.join( root, cingPaths.project )
            if not os.path.exists( pfile ):
                NTerror('ERROR Project.open: missing Project file "%s"\n', pfile )
                return None
            #end if
            pr = XML2obj( pfile )
            # This allows renaming/relative adressing at the shell level
            pr.root = root
            pr.name = newName

            # Optional restore the content
            if restore:
                pr.restore()
            #end if
        else:
            NTerror('ERROR Project.open: invalid status option "%s"\n', status )
            return None
        #end if

        # Check the subdirectories
        for dir in directories.values():
            pr.mkdir( dir )
        #end for

        projects.append( pr )
        NTdebug(pr.format())
        return pr
    #end def
    open = staticmethod( open )

    def close( self ):
        global projects
        #self.export()
        self.save()
        projects.remove(self)
        return None
    #end def

    def save( self):
        NTmessage('' + dots*5 +'' )
        NTmessage(   '==> Saving %s', self )

        # Save the molecules
        for molName in self.molecules:
            self[molName].save( path = self.path( directories.molecules, molName ))

        # Save the lists
        for pl, nameList in [(self.peaks,     'peakListNames'),
                             (self.distances, 'distanceListNames'),
                             (self.dihedrals, 'dihedralListNames'),
                             (self.rdcs,      'rdcListNames' )
                            ]:
            self[nameList] = pl.save()
            # Patch for XML bug
            self.saveXML( nameList )
        #end for

#        self.peakListNames = self.peaks.save()
#        #Patch for XML bug
#        self.saveXML('peakListNames')
#
#        # Save the distanceRestaintsLists
#        self.distanceListNames = self.distances.save()
#        #Patch for XML bug
#        self.saveXML('distanceListNames')
#
#        # Save the dihedralRestaintsLists
#        self.dihedralListNames = self.dihedrals.save()
#        #Patch for XML bug
#        self.saveXML('dihedralListNames')
#
#        # Save the rdcRestaintsLists
#        self.rdcListNames = self.rdcs.save()
#        #Patch for XML bug
#        self.saveXML('rdcListNames')

        # Call Plugin registered functions
        for p in self.plugins.values():
            for f,o in p.saves:
                f( self, o )
            #end for
        #end for

        # Save the project data
        obj2XML( self, path = self.path( cingPaths.project ) )

        self.addHistory( 'Saved project' )
    #end def

    def restore(self ):
        """
        Restore the project: molecules and lists
        """
        # Molecules
        for molName in self.molecules:
            self.molecule = Molecule.open( self.path( directories.molecules, molName ) )
            self[molName] = self.molecule
            # generate/check the required directories for export and HTML data
            for dir in moleculeDirectories.values():
                self.mkdir( self.molecule.name, dir )
            #end for
        #end for

        # restore the lists
        for pl, nameList in [(self.peaks,     'peakListNames'),
                             (self.distances, 'distanceListNames'),
                             (self.dihedrals, 'dihedralListNames'),
                             (self.rdcs,      'rdcListNames' )
                            ]:
            pl.restore( self[nameList]  )
        #end for

        # Plugin registered functions
        for p in self.plugins.values():
            for f,o in p.restores:
                f( self, o )
            #end for
        #end for

        self.updateProject()
    #end def

    def export( self):
        """Call export routines from the plugins to export the project
        """
        NTmessage('' + dots*5 +'' )
        NTmessage(   '==> Exporting %s', self )

        for p in self.plugins.values():
            for f,o in p.exports:
                f( self, o )
            #end for
        #end for
    #end def

    def updateProject( self ):
        """Do all administrative things after actions
        """
        if self.molecule: self[self.molecule.name] = self.molecule
    #end def

    #-------------------------------------------------------------------------
    # actions Molecule
    #-------------------------------------------------------------------------
    def appendMolecule( self, molecule ):
        if not molecule: return None

        # generate the required directories for export and HTML data
        for dir in moleculeDirectories.values():
            self.mkdir( molecule.name, dir )
        #end for

        # Store names and references
        self.molecule = molecule
        self.molecules.append( molecule.name )
        self[molecule.name] = self.molecule

        # Save it to make sure we can restore it later
        self.molecule.save( path = self.path( directories.molecules, molecule.name )   )
        return self.molecule

    #end def

    def newMolecule( self, name, sequenceFile, convention = LOOSE ):
        """Return Molecule instance or None on error
        """
        uname = self.uniqueKey(name)
        molecule = Molecule.initialize( uname,
                                        path = sequenceFile,
                                        convention=convention
                                       )
        if not molecule:
            return None
        self.appendMolecule( molecule )

        self.addHistory( sprintf('Initialized molecule "%s" from "%s"', uname, sequenceFile ) )
        return self.molecule
    #end def
    initializeMolecule = newMolecule # keep old name


    #-------------------------------------------------------------------------
    # Resonances stuff
    #-------------------------------------------------------------------------

    def mergeResonances( self, order=None, selection=None, status='reduce' ):

        """ Merge resonances for all the atoms
            check all the resonances in the list, optionally using selection
            and take the first one which has a assigned value,
            append or reduce the resonances list to this entry depending on status.

        """

        if not self.molecule:
            NTerror('Project.mergeResonances: No molecule defined\n')
            return
        #end if

        for atom in self.molecule.allAtoms():
            if ( len(atom.resonances) == 0 ):
                NTerror('mergeResonances: zero length resonance list for atom "%s"\n',
                         atom
                       )
                return
            else:
                rm = None
                if (selection == None or atom.name in selection):
                    for res in atom.resonances:
                        if (res.value != NOSHIFT):
                            rm=res
                            break
                        #end if
                    #end for
                #end if
            #end if

            if (rm):
                atom.resonances.append(rm)
            else:
                rm = atom.resonances[0]
                atom.resonances.append(rm)
            #end if

            # Optionally reduce the list
            if (status == 'reduce'):
                atom.resonances = NTlist( atom.resonances() )
                self.molecule.resonanceCount = 1
            else:
                self.molecule.resonanceCount = len( atom.resonances )
        NTmessage("==> Merged resonances")

    def initResonances( self ):

        """ Initialize resonances for all the atoms
        """
        if not self.molecule:
            NTerror('Project.initResonances: No molecule defined\n')
            return
        self.molecule.initResonances()

    #-------------------------------------------------------------------------
    # actions other
    #-------------------------------------------------------------------------

    def addHistory( self, line, timeStamp = True ):
        self.history( line, timeStamp )
    #end def

    def newPeakList( self, name, status='keep'):
        """Dummy for compatibility
        """
        return self.peaks.new( name = name, status=status)
    #end def

    def appendPeakList( self, peaklist):
        """Append peaklist; dummy for compatibility
        """
        self.peaks.append( peaklist )
        return peaklist
    #end def



    def header( self, dots = '---------'  ):
        """Subclass header to generate using __CLASS__, name and dots.
        """
        return sprintf('%s %s: %s %s', dots, self.__CLASS__, self.name, dots)
    #end def

    def __str__( self ):
        return sprintf('<Project %s>', self.name )
    #end def

    def __repr__(self):
        return str(self)

    def format( self ):
        dots =              '-----------'
        self.__FORMAT__   =  self.header( dots ) + '\n' + \
                            'created:    %(created)s\n' +\
                            'molecules:  %(molecules)s\n' +\
                            '            %(molecule)s\n' +\
                            'peaks:      %(peaks)s\n' +\
                            'distances:  %(distances)s\n' +\
                            'dihedrals:  %(dihedrals)s\n' +\
                            'rdcs:       %(rdcs)s\n' +\
                             self.footer( dots )
        return NTdict.format( self )
    #end def

    def removeFromDisk(self):
        """Removes True on error. If no cing project is found on disk None (Success) will
        still be returned. Note that you should set the nosave option on the project
        before exiting."""
        pathString, _name = self.rootPath(self.name)
        if not os.path.exists(pathString):
            NTwarning("No cing project is found at: " + pathString)
            return None
        NTmessage("Removing existing cing project")
        if rmtree( pathString ):
            NTerror("Failed to remove existing cing project")
            return True

#end class

#-----------------------------------------------------------------------------

class XMLProjectHandler( XMLhandler ):
    """Project handler class"""
    def __init__( self ):
        XMLhandler.__init__( self, name='Project')
    #end def

    def handle( self, node ):
        attrs = self.handleDictElements( node )
        if attrs == None: return None
        result = Project( name = attrs['name'] )

        # update the attrs values
        result.update( attrs )

        return result
    #end def
#end class

#register this handler
projecthandler = XMLProjectHandler()

#
#-----------------------------------------------------------------------------
class ProjectList( NTlist ):
    """Generic Project list class
       Creates classDef instance when calling the new() method
    """
    def __init__( self, project, classDef, savePath, extention ):
        NTlist.__init__( self )
        self.project  = project
        self.classDef = classDef
        self.savePath = savePath
        self.extention = extention
    #end def

    def append( self, *args ):
        """Append *args to self, storing a.name in project
        """
        for a in args:
            a.name = self.project.uniqueKey( a.name )
            self.project[a.name] = a
            NTlist.append( self, a )
        #end for
    #end def

    def new( self, name,*args, **kwds ):
        """Create a new classDef instance, append to self
        """
        uname = self.project.uniqueKey(name)
        instance = self.classDef( name = uname, *args, **kwds )
        self.append ( instance )
        s = sprintf('New "%s" instance named "%s"', self.className(), uname )
        self.project.history( s )
        NTmessage('==> %s', s )
        #end if
        return instance
    #end def

    def save(self):
        """
        Save the lists of self to savePath/name.extention
        savePath relative to project

        Use SML methods

        Return a list of names
        """
        saved = NTlist()
        for l in self:
            if l.status == 'keep':
                fname = self.project.path( self.savePath, l.name + self.extention )
                self.classDef.SMLhandler.toFile( l, fname )
                saved.append(l.name)
        #end for
        return saved
    #end def

    def restore(self, names ):
        """
        Use the SMLhandler instance of classDef to restore the list.
        Names is a list instance containing the names to of the lists to restore.
        """
        for name in names:
            fname = self.project.path( self.savePath, name + self.extention )
            _l = self.classDef.SMLhandler.fromFile( fname, self.project)
        #end for
    #end def

    def className(self):
        """Return a string describing the class of lists of this project list
        """
        # eg. to extract from <class 'cing.classes.PeakList'>
        return str(self.classDef)[8:-2].split(".")[-1:][0]
    #end def

#end class Project
#
#-----------------------------------------------------------------------------
# Two handy (?) routines
#-----------------------------------------------------------------------------

def encode( objects ):
    """Return a list of nametuples encoding the molecule objects (chains, residues, atoms)
    """
    result = NTlist()
    for obj in objects:
        if (obj == None):
            result.append(None)
        else:
            result.append( obj.nameTuple() )
        #end if
    #end for
    return result
#end def

def decode( nameTuples, molecule ):
    """
    Return a list molecular objects, decoding the nametuples for molecule
    """
    result = NTlist()
    for nt in nameTuples:
        if molecule == None or nt == None:
            result.append(None)
        else:
            result.append( molecule.decodeNameTuple( nt ) )
        #end if
    #end for
    return result
#end def

#
#-----------------------------------------------------------------------------

PeakIndex = 1
class Peak( NTdict ):
    """Peak class:
       Peaks point to resonances
       Resonances point to atoms
       by GV 20070723: added hasHeight, hasVolume attributes to the class
       GV 28092007: Moved from molecule.py to project.py
    """
    def __init__( self,
                  dimension=1,
                  positions=None,
                  height=0.00, heightError = 0.00, hasHeight = False,
                  volume=0.00, volumeError = 0.00, hasVolume = False,
                  resonances=None,
                  **kwds
                ):

        NTdict.__init__( self, __CLASS__  = 'Peak', **kwds )
#       several external programs need an index
        global PeakIndex
        self.peakIndex = PeakIndex
        PeakIndex += 1

        self.__FORMAT__ =  self.header(dots) + '\n' +\
                           'dimension:  %(dimension)dD\n' +\
                           'positions:  %(positions)s\n' +\
                           'height:     %(height)10.3e %(heightError)10.3e\n'   +\
                           'volume:     %(volume)10.3e %(volumeError)10.3e\n' +\
                           'resonances: %(resonances)s\n' +\
                           self.footer(dots)

        self.dimension=dimension

        # Copy the poistions and resonances argumnet to assure they become
        # NTlist objects
        if resonances:
            self.resonances = NTlist( *resonances )
        else:
            self.resonances = NTfill( None, dimension )
        #end if

        if positions:
            self.positions = NTlist( *positions )
        else:
            self.positions = NTfill( NOSHIFT, dimension )
        #end if

        self.height = height
        self.heightError = heightError
        self.hasHeight = hasHeight
        self.volume = volume
        self.volumeError = volumeError
        self.hasVolume  = hasVolume
    #end def

    def isAssigned( self, axis ):
        if (axis >= self.dimension): return False
        if (axis >= len(self.resonances) ): return False
        if (self.resonances[axis] == None): return False
        if (self.resonances[axis].atom == None): return False
        return True
    #end def

    def getAssignment( self, axis):
        """Return atom instances in case of an assignment or None
        """
        if (self.isAssigned( axis ) ):
            return self.resonances[axis].atom
        #end if
        return None
    #end def

    def __str__( self ):
        return sprintf( 'Peak %4d (%dD)   %s   %10.3e %10.3e %10.3e %10.3e   %s',
                         self.peakIndex, self.dimension,
                         self.positions.format('%8.3f '),
                         self.height, self.heightError, self.volume, self.volumeError,
                         self.resonances.zap('atom')
                       )
    #end def

    def header( self, dots = '---------'  ):
        """Subclass header to generate using __CLASS__, peakIndex and dots.
        """
        return sprintf('%s %s: %d %s', dots, self.__CLASS__, self.peakIndex, dots)
    #end def
#end class

class SMLPeakHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'Peak' )
    #end def

    def handle(self, line, fp, project=None):
        pk = Peak( *line[2:] )
        return self.dictHandler(pk, fp, project)
    #end def

### REMARK: This restoring of resonances is dangerous, because it is not guranteed that the order and hence last
#           resonance of atoms is always the same. Needs reviewing !!!
    def endHandler(self, pk, project):
        if project == None:
            NTerror('Error SMLPeakHandler.endHandler: Undefined project\n')
            return None
        #end if
        pk.resonances = NTfill(None,pk.dimension)
        # Check if we have to make the linkage
        if pk.atoms and project.molecule:
            #print '>>',pk.atoms
            for i in range(pk.dimension):
                if pk.atoms[i] != None:
                    atm = project.molecule.decodeNameTuple(pk.atoms[i])
                    pk.resonances[i] = atm.resonances()
                else:
                    pk.resonances[i] = None
                #end if
            #end for
        #end if
        return pk
    #end def

    def toSML(self, peak, fp):
        """
        """
        fprintf( fp, '%s\n', self.startTag )
        for a in ['dimension','positions',
                  'height','heightError','hasHeight',
                  'volume','volumeError','hasVolume'
                 ]:
            fprintf( fp, '    %-15s = %s\n', a, repr(peak[a]) )
        #end for
        rl = []
        for r in peak.resonances.zap('atom'):
            if (r != None):
                rl.append(r.nameTuple())
            else:
                rl.append(None)
            #endif
        fprintf( fp, '    %-15s = %s\n', 'atoms', repr( rl ) )
        fprintf( fp, '%s\n', self.endTag )
    #end def

#end class
Peak.SMLhandler = SMLPeakHandler()

#-----------------------------------------------------------------------------
class PeakList( NTlist ):

    def __init__( self, name, status='keep' ):
        NTlist.__init__( self )
        self.name = name
        self.status = status
        self.listIndex = -1 # list is not appended to anything yet
    #end def

    def peakFromAtoms( self, atoms, onlyAssigned=True ):
        """Append a new Peak based on atoms list
           Return Peak instance, or None
        """
        if (None not in atoms):     # None value in atoms indicates atom not present
            if (onlyAssigned and (False in map( Atom.isAssigned, atoms ))):
                pass                # Check atom assignments, if only assigned and not all assignments
                                    # present we skip it
            else:                   # all other cases we add a peak
                s = []
                r = []
                for a in atoms:
                    s.append( a.shift() )
                    r.append( a.resonances() )
                #end for
                peak = Peak( dimension = len(atoms),
                             positions = s,
                             resonances = r
                           )
                self.append( peak )
                return peak
            #end if
        #end if
        return None
    #end def
#
#    def toFile(self, fileName)   :
#        """
#        Save peaks to fileName for restoring later with fromFile method
#        """
#
#        fp = open( fileName, 'w' )
#        if not fp:
#            NTerror('PeakList.toFile: opening "%s"\n', fileName)
#            return
#        #end if
#        fprintf( fp, '<PeakList> %s %s\n', self.name, self.status )
#        for peak in self:
#            peak.toStream( fp )
#        #end for
#        fprintf( fp, '</PeakList>\n' )
#
#
#        NTmessage('==> Saved %s to "%s"', str(self), fileName )
#        #end if
#    #end def


    def __str__( self ):
        return sprintf( '<PeakList "%s" (%s,%d)>',self.name,self.status,len(self) )
    #end def

    def __repr__(self):
        return str(self)
    #end def

    def format( self ):
        s = sprintf( '%s PeakList "%s" (%s,%d) %s\n', dots, self.name,self.status,len(self), dots )
        for peak in self:
            s = s + str(peak) + '\n'
        #end for
        return s
    #end def

#    def toSMLfile(self, fileName)   :
#        return self.SMLhandler.list2SMLfile( self, fileName  )
#    #end def
#
#    def fromSMLfile(fileName, project)   :
#        """
#        Restore PeakList from SMLfile fileName
#        """
#        pl = PeakList.SMLhandler.fromFile( fileName, project )
#        if pl:
#            NTmessage('==> Restored %s from "%s"', pl, fileName )
#        #end if
#        return pl
#    #end def
#    fromSMLfile = staticmethod( fromSMLfile )
#end class


class SMLPeakListHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'PeakList' )
    #end def

    def handle(self, line, fp, project=None):
        pl = PeakList( *line[2:] )
        if not self.listHandler(pl, fp, project): return None
        if project: project.peaks.append( pl )
        return pl
    #end def

    def toSML(self, pl, fp):
        return self.list2SML( pl, fp )
#end class
PeakList.SMLhandler = SMLPeakListHandler()

def getAtomsFromAtomPairs(atomPairs):
    result = []
    for atomPair in atomPairs:
        for atom in atomPair:
            for real_atm in atom.realAtoms():
                result.append( real_atm )
    return result

#-----------------------------------------------------------------------------
class DistanceRestraint( NTdict ):
    """DistanceRestraint class:
       atomPairs: list of (atom_1,atom_2) tuples,
       lower and upper bounds
    """
    DR_MAXALL_DEFAULT_POOR_VALUE = 0.5
#    dr_maxall_poor = cingCriticismDict.getDeepByKeys(
#        ANY_ENTITY_LEVEL, 'dr_maxall', POOR_PROP,1,default=DR_MAXALL_DEFAULT_POOR_VALUE)
    dr_maxall_poor = DR_MAXALL_DEFAULT_POOR_VALUE

    def __init__( self, atomPairs=[], lower=0.0, upper=0.0, **kwds ):

        NTdict.__init__(self,__CLASS__  = 'DistanceRestraint',
                               atomPairs  = NTlist(),
                               lower      = lower,
                               upper      = upper,
                               **kwds
                        )
        self.id         = -1       # Undefined index number

        self.distances  = None     # list with distances for each model; None: not yet defined
        self.av         = 0.0      # Average distance
        self.sd         = 0.0      # sd on distance
        self.min        = 0.0      # Minimum distance
        self.max        = 0.0      # Max distance
        self.violations = None     # list with violations for each model; None: not yet defined
        self.violCount1 = 0        # Number of violations over 0.1A
        self.violCount3 = 0        # Number of violations over 0.3A
        self.violCount5 = 0        # Number of violations over 0.5A
        self.violMax    = 0.0      # Maximum violation
        self.violAv     = 0.0      # Average violation
        self.violSd     = 0.0      # Sd of violations
        self.error      = False    # Indicates if an error was encountered when analyzing restraint

        for pair in atomPairs:
            self.appendPair( pair )
        #end for
    #end def

    def criticize(self):
        critiqued = False
        ## Order of next two checks matters
        if self.max >= DistanceRestraint.dr_maxall_poor:
            self.colorLabel = COLOR_ORANGE
            critiqued = True
        if self.max >= DistanceRestraint.dr_maxall_bad:
            self.colorLabel = COLOR_RED
            critiqued = True
        if critiqued:
            for atom in getAtomsFromAtomPairs(self.atomPairs):
                atom.appendCritique( self, cascade = True )
        return critiqued



    def appendPair( self, pair ):
        # check if atom already present, keep order
        # otherwise: keep atom with lower residue index first
        a0 = self.atomPairs.zap(0)
        a1 = self.atomPairs.zap(1)
        if (pair[0] in a0 or pair[1] in a1):
            self.atomPairs.append( pair )
        elif (pair[0] in a1 or pair[1] in a0):
            self.atomPairs.append( (pair[1],pair[0]) )
        elif (pair[0].residue.resNum > pair[1].residue.resNum):
            self.atomPairs.append( (pair[1],pair[0]) )
        else:
            self.atomPairs.append( pair )
    #end def

    def calculateAverage(self):
        """
        Calculate R-6 average distance and violation
        for each model.
        return (av,sd,min,max) tuple, or (None, None, None, None) on error
        """

        modelCount = 0
        if len(self.atomPairs) :
            modelCount = self.atomPairs[0][0].residue.chain.molecule.modelCount
        #end if

        if modelCount == 0:
            NTerror('Error DistanceRestraint.calculateAverage: No structure models (%s)\n', self)
            return (None, None, None, None)
        #end if

        self.distances  = NTlist() # list with distances for each model
        self.av         = 0.0      # Average distance
        self.sd         = 0.0      # sd on distance
        self.min        = 0.0      # Minimum distance
        self.max        = 0.0      # Max distance
        self.violations = NTlist() # list with violations for each model
        self.violCount1 = 0        # Number of violations over 0.1A
        self.violCount3 = 0        # Number of violations over 0.3A
        self.violCount5 = 0        # Number of violations over 0.5A
        self.violMax    = 0.0      # Maximum violation
        self.violAv     = 0.0      # Average violation
        self.violSd     = None     # Sd of violations
        self.error      = False    # Indicates if an error was encountered when analyzing restraint

        if modelCount>0:
            for i in range( modelCount):
                d = 0.0
                for atm1,atm2 in self.atomPairs:
                    #expand pseudoatoms
                    atms1 = atm1.realAtoms()
                    atms2 = atm2.realAtoms()
                    for a1 in atms1:
                        #print '>>>', a1.format()
                        if (len( a1.coordinates ) > i ):
                            for a2 in atms2:
                                if (len(a2.coordinates) > i ):
                                    tmp = NTdistanceOpt( a1.coordinates[i], a2.coordinates[i] )
                                    d += math.pow( tmp, -6.0 )
                                else:
                                    self.error = True
                                #end if
                            #end for
                        else:
                            self.error = True
                        #end if
                    #end for
                #end for
                try:
                    self.distances.append( math.pow(d, -0.166666666666666667) )
                except:
                    NTerror("AtomPair (%s,%s) without coordinates"%
                             (atm1, atm2))
                    self.error = True
                    self.colorLabel = COLOR_RED
                    return (None, None, None, None)
                #end try
            #end for

            self.av, self.sd, self.n = NTaverage( self.distances )
            self.min = min( self.distances )
            self.max = max( self.distances )

            # calculate violations
            for d in self.distances:
                if (d < self.lower):
                    self.violations.append( d-self.lower )
                elif (d > self.upper):
                    self.violations.append( d-self.upper )
                else:
                    self.violations.append( 0.0 )
                #end if
            #end for

            # analyze violations
            for d in self.violations:
                dabs = math.fabs(d)
#               print '>>', d,dabs
                if ( dabs > 0.1): self.violCount1 += 1
                if ( dabs > 0.3): self.violCount3 += 1
                if ( dabs > 0.5): self.violCount5 += 1
            #end for
            if self.violations:
                self.violAv, self.violSd, dummy = NTaverage( map(math.fabs,self.violations) )
                self.violMax = max( map(math.fabs,self.violations) )
        #end if

        return (self.av,self.sd,self.min,self.max )

    #end def

    def listViolatingModels(self, cutoff = 0.3 ):
        """
        Examine for violations larger then cutoff, return list of violating models or None on error
        Requires violations attribute (obtained with calculateAverage method.
        """
        if not self.has_key('violations'):
            return None

        violatingModels = NTlist()
        #TODO: check if the below self.violations was meant when JFD changed from just 'violations'
        for i in range( len(self.violations) ):
            if (math.fabs( self.violations[i]) > cutoff):
                violatingModels.append( i )
            #end if
        #end for

        return violatingModels
    #end def

    def _names(self):
        """
        Internal routine: generate string from atomPairs
        """
        s = ''
        for p in self.atomPairs:
            s = s + sprintf('(%-11s - %11s)   ', p[0]._Cname(1), p[1]._Cname(1))
        #end for
        return s.strip()
    #end def

    def __str__(self):
        return sprintf('<DistanceRestraint %d>', self.id )
    #end def

    def format( self ):
        return  \
            sprintf('%-25s (Target: %4.1f %4.1f)  (Models: av %4s sd %4s min %4.1f max %4.1f)'+\
                    '(Violations: av %6s max %6.1f counts %2d,%2d,%2d) %s',
                        str(self),
                        self.lower, self.upper,
                val2Str(self.av,         "%6.1f", 6),
                val2Str(self.sd,         "%7.3f", 7),
                self.min, self.max,
                val2Str(self.violAv,     "%4.1f", 4),
                self.violMax, self.violCount1, self.violCount3, self.violCount5,
                self._names())
    #end def
#end class

class SMLDistanceRestraintHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'DistanceRestraint' )
    #end def

    def handle(self, line, fp, project=None):
        dr = DistanceRestraint( *line[2:] )
        return self.dictHandler(dr, fp, project)
    #end def

    def endHandler(self, dr, project):
        # Parse the atomPairs tuples, map to molecule
        if project == None or project.molecule == None: return dr
        aps = dr.atomPairs
        dr.atomPairs = NTlist()
        for ap in aps:
            dr.appendPair( (project.molecule.decodeNameTuple(ap[0]), project.molecule.decodeNameTuple(ap[1])) )
        #end for
        return dr
    #end def

    def toSML(self, dr, stream ):
        """
        """
        fprintf( stream, "%s\n", self.startTag )
        for a in ['lower','upper' ]:
            fprintf( stream, '    %-15s = %s\n', a, repr(dr[a]) )
        #end for

        rl = []
        for r in dr.atomPairs:
            rl.append((r[0].nameTuple(),r[1].nameTuple()))
        #end for
        fprintf( stream, '    %-15s = %s\n', 'atomPairs', repr( rl ) )
        fprintf( stream, "%s\n", self.endTag )
    #end def
#end class
DistanceRestraint.SMLhandler = SMLDistanceRestraintHandler()

def setMaxColor(o, colorLabel):
    if colorLabel == COLOR_RED:
        o.colorLabel = colorLabel
    elif not o.has_key( 'colorLabel' ):
        o.colorLabel = colorLabel
#-----------------------------------------------------------------------------
class DistanceRestraintList( NTlist ):
    """
    Class based on NTlist that holds distanceRestraints.
    Also manages the "id's".
    Sort  by item of DistanceRestraint Class
    """
    def __init__( self, name, status='keep' ):
        NTlist.__init__( self )
        self.name   = name        # Name of the list
        self.status = status      # Status of the list; 'keep' indicates storage required
        self.Hbond  = False       # Hbond: fix to keep information about Hbond restraints from CCPN
        self.currentId  = 0       # Id for each element of list

        self.rmsd       = None    # rmsd per model, None indicate no analysis done
        self.rmsdAv     = 0.0
        self.rmsdSd     = 0.0
        self.violCount1 = 0       # Total violations over 0.1 A
        self.violCount3 = 0       # Total violations over 0.3 A
        self.violCount5 = 0       # Total violations over 0.5 A
    #end def

    def criticize(self):
        for dr in self:
            if dr.criticize():
                self.colorLabel = setMaxColor( self, dr.colorLabel )
        if self.colorLabel:
            return True

    def append( self, distanceRestraint ):
        distanceRestraint.id = self.currentId
        NTlist.append( self, distanceRestraint )
        self.currentId += 1
    #end def

    def analyze( self ):
        """
        Calculate averages for every restraint.
        Return <rmsd>, sd and total violations over 0.1, 0.3, 0.5 A as tuple
        or (None, None, None, None, None) on error
        """

        if (len( self ) == 0):
            NTerror('ERROR DistanceRestraintList.analyze: "%s" empty list', self.name )
            return (None, None, None, None, None)
        #end if

        modelCount = 0
        if len(self[0].atomPairs):
            modelCount = self[0].atomPairs[0][0].residue.chain.molecule.modelCount
        #end if

        if modelCount == 0:
            NTerror('DistanceRestraintList.analyze: "%s" modelCount 0', self.name )
            return (None, None, None, None, None)
        #end if

        self.rmsd  = NTfill( 0.0, modelCount )
        self.violCount1 =  0
        self.violCount3 =  0
        self.violCount5 =  0
        count = 0
        self.errors = NTlist() # Store reference to restraints with calc problems
        for dr in self:
            dr.calculateAverage()
            if dr.error:
                self.errors.append( dr )
            else:
                self.violCount1 += dr.violCount1
                self.violCount3 += dr.violCount3
                self.violCount5 += dr.violCount5
                for i in range(0, modelCount):
                    self.rmsd[i] += dr.violations[i]*dr.violations[i]
                #end for
                count += 1
            #end if
        #end for

        for i in range(0, modelCount):
            self.rmsd[i] = math.sqrt(self.rmsd[i]/count)
        #end for

        self.rmsdAv, self.rmsdSd, _n = NTaverage( self.rmsd )
        return (self.rmsdAv, self.rmsdSd, self.violCount1, self.violCount3, self.violCount5)
    #end def

    def sort(self, byItem ):
        """
        Sort the list byItem
        """
        NTsort( self, byItem, inplace=True)
        return self
    #end def

    def __str__( self ):
        return sprintf( '<DistanceRestraintList "%s" (%s,%d)>',self.name,self.status,len(self) )
    #end def

    def format( self ):
        return sprintf( '%s DistanceRestraintList "%s" (%s,%d) %s\n'+\
                        'rmsd: %7s %6s        Violations > 0.1,0.3,0.5: %d, %d, %d\n',
                      dots, self.name,self.status,len(self), dots,
                      val2Str(self.rmsdAv,         "%7.3f", 7),
                      val2Str(self.rmsdSd,         "%6.3f", 6),
                      self.violCount1, self.violCount3, self.violCount5)

    #end def

#    def toFile(self, fileName)   :
#        """
#        Save dihedralRestraints to fileName for restoring later with fromFile method
#        """
#
#        fp = open( fileName, 'w' )
#        if not fp:
#            NTerror('DistanceRestraintList.toFile: opening "%s"\n', fileName)
#            return
#        #end if
#        fprintf( fp, '<DistanceRestraintList> %s %s\n', self.name, self.status )
#        for restraint in self:
#            restraint.toStream( fp )
#        #end for
#        fprintf( fp, '</DistanceRestraintList>\n' )
#
#
#            NTmessage('==> Saved %s to "%s"', str(self), fileName )
#        #end if
#    #end def
#end class

class SMLDistanceRestraintListHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'DistanceRestraintList' )
    #end def

    def handle(self, line, fp, project=None):
        drl = DistanceRestraintList( *line[2:] )
        if not self.listHandler(drl, fp, project): return None
        project.distances.append( drl )
        return drl
    #end def

    def toSML(self, drl, fp):
        self.list2SML( drl, fp )
    #end def
#end class
DistanceRestraintList.SMLhandler = SMLDistanceRestraintListHandler()


#-----------------------------------------------------------------------------
class DihedralRestraint( NTdict ):
    """
        DihedralRestraint class:

       GV 2 Oct 2007: removed residue and angle attributes.
       If the 4 atoms consitute a known dihedral angle, this can
       be retrieved with the retrieveDefinition method

       GV&AWSS: 10 Oct 2007, upper-limit adjustment
    """
    def __init__( self, atoms, lower, upper, **kwds ):

        if upper<lower:
            upper+=360.0
        NTdict.__init__(self, __CLASS__  = 'DihedralRestraint',
                              atoms      = NTlist( *atoms ),
                              lower      = lower,
                              upper      = upper,
                              **kwds
                       )
        self.id         = -1       # Undefined index number
        self.dihedrals  = None     # list with dihedral values for each model, None indicates no analysis done
        self.cav        = 0.0      # Average dihedral value
        self.cv         = 0.0      # cv on dihedral
#        self.min        = 0.0      # Minimum dihedral
#        self.max        = 0.0      # Max dihedral
        self.violations = None     # list with violations for each model, None indicates no alalysis done
        self.violCount1 = 0        # Number of violations over 1 degree
        self.violCount3 = 0        # Number of violations over 3 degrees
        self.violCount5 = 0        # Number of violations over 5 degrees
        self.violMax    = 0.0      # Maximum violation
        self.violAv     = 0.0      # Average violation
        self.violSd     = 0.0      # Sd of violations
    #end def

    def calculateAverage(self):
        """Calculate the values and violations for each model
        return cav and cv tuple or (None, None) tuple on error
        """

        modelCount = 0
        if len(self.atoms):
            modelCount = self.atoms[0].residue.chain.molecule.modelCount
        #end if

        if (modelCount == 0):
            NTerror('Error DihedralRestraint: no structure models\n' )
            return (None,None)
        #end if

        if len(self.atoms) != 4 or (None in self.atoms):
            NTerror('Error DihedralRestraint: invalid dihedral definition %s\n', self.atoms )
            return (None,None)
        #end if

        if None in self.atoms.zap('meanCoordinate'):
            NTerror('Error DihedralRestraint: atom without coordinates %s\n', self.atoms )
            return (None,None)
        #end if

        #set the default values
        self.dihedrals  = NTlist() # list with dihedral values for each model
        self.cav        = 0.0      # Average dihedral value
        self.cv         = 0.0      # cv on dihedral
#        self.min        = 0.0      # Minimum dihedral
#        self.max        = 0.0      # Max dihedral
        self.violations = NTlist() # list with violations for each model
        self.violCount1 = 0        # Number of violations over 1 degree
        self.violCount3 = 0        # Number of violations over 3 degrees
        self.violCount5 = 0        # Number of violations over 5 degrees
        self.violMax    = 0.0      # Maximum violation
        self.violAv     = 0.0      # Average violation
        self.violSd     = 0.0      # Sd of violations

        for i in range(modelCount):
            d = NTdihedralOpt(
                            self.atoms[0].coordinates[i],
                            self.atoms[1].coordinates[i],
                            self.atoms[2].coordinates[i],
                            self.atoms[3].coordinates[i]
                          )
            self.dihedrals.append( d )
        #end for

        #find the range to store these dihedral values
        #limit = 0.0
        #if limit > self.lower: limit = -180.0
        #self.dihedrals.limit(limit, limit+360.0)

        plotpars =plotParameters.getdefault( self.retrieveDefinition()[1],
                                             'dihedralDefault' )

        self.dihedrals.limit(plotpars.min, plotpars.max)

        # Analyze violations, account for periodicity
        for d in self.dihedrals:
            v = violationAngle(value=d, lowerBound=self.lower, upperBound=self.upper)
            fv = math.fabs(v)
            self.violations.append( v )
            if fv > 1.0: self.violCount1 += 1
            if fv > 3.0: self.violCount3 += 1
            if fv > 5.0: self.violCount5 += 1
            if fv > self.violMax: self.violMax = fv
            #end if
        #end for
        self.violAv,self.violSd,_n = self.violations.average()

        self.cav,self.cv,_n = self.dihedrals.cAverage(plotpars.min, plotpars.max)
        return( self.cav, self.cv )
    #end def

    def listViolatingModels(self, cutoff = 3.0 ):
        """
        Examine for violations larger then cutoff, return list of violating models or None on error
        Requires violations attribute (obtained with calculateAverage method).
        """
        if not self.has_key('violations'):
            return None

        violatingModels = NTlist()
        for i in range(0, len(self.violations) ):
            if (math.fabs( self.violations[i]) > cutoff):
                violatingModels.append( i )
            #end if
        #end for

        return violatingModels
    #end def

    def retrieveDefinition(self):
        """
        Retrieve a (<Residue>, angleName, <AngleDef>) tuple from
        the molecule.dihedralDict
        or
        (None,None,None) on error
        """
        if (not self.atoms or (None in self.atoms)):
            return (None,None,None)
        #end if
        mol = self.atoms[0].residue.chain.molecule

        if mol.dihedralDict.has_key(tuple(self.atoms)):
            return mol.dihedralDict[tuple(self.atoms)]
        else:
            return (None,None,None)
        #end if
    #end def

    def __str__(self):
        return sprintf('<DihedralRestraint %d>', self.id )
    #end def

    def format( self ):
        return  \
            sprintf('%-25s (Target: %6.1f %6.1f)  (Models: cav %6s cv %4s)  '+\
                    '(Violations: av %4s max %4.1f counts %2d,%2d,%2d) %s',
                        self, self.lower, self.upper,
                val2Str(self.cav,         "%6.1f", 6),
                val2Str(self.cv,          "%4.1f", 4),
                val2Str(self.violAv,      "%4.1f", 4),
                self.violMax, self.violCount1, self.violCount3, self.violCount5,
                        self.atoms.format('%-11s ')
                       )

    #end def
#end class

class SMLDihedralRestraintHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'DihedralRestraint' )
    #end def

    def handle(self, line, fp, project=None):
        dr = DihedralRestraint( atoms=[], upper = 0.0 , lower =0.0 )
        return self.dictHandler(dr, fp, project)
    #end def

    def endHandler(self, dr, project):
        # Parse the atoms nameTuples, map to molecule
        dr.atoms = decode( dr.atoms, project.molecule )
#        atms = dr.atoms
#        dr.atoms = NTlist()
#        for atm in atms:
#            dr.append( project.molecule.decodeNameTuple(atm) )
#        #end for
    #end def

    def toSML(self, dr, stream ):
        """
        """
        fprintf( stream, "%s\n", self.startTag )
        for a in ['lower','upper' ]:
            fprintf( stream, '    %-15s = %s\n', a, repr(dr[a]) )
        #end for
        fprintf( stream, '    %-15s = %s\n', 'atoms', repr(encode(dr.atoms)) )

#        rl = []
#        for r in self.atoms:
#            rl.append(r.nameTuple())
#        #end for
#        fprintf( stream, '    %-15s = %s\n', 'atoms', repr( rl ) )

        fprintf( stream, "%s\n", self.endTag )
    #end def
#end class
DihedralRestraint.SMLhandler = SMLDihedralRestraintHandler()


#-----------------------------------------------------------------------------
class DihedralRestraintList( NTlist ):

    def __init__( self, name, status='keep' ):
        NTlist.__init__( self )
        self.name       = name
        self.status     = status
        self.currentId  = 0       # Id for each element of list

        self.rmsd       = None    # rmsd per model, None indicate no analysis done
        self.rmsdAv     = 0.0
        self.rmsdSd     = 0.0
        self.violCount1 = 0       # Total violations over 1 degree
        self.violCount3 = 0       # Total violations over 3 degrees
        self.violCount5 = 0       # Total violations over 5 degrees
    #end def

    def append( self, dihedralRestraint ):
        dihedralRestraint.id = self.currentId
        NTlist.append( self, dihedralRestraint )
        self.currentId += 1
    #end def

    def analyze( self, calculateFirst = True ):
        """
        Calculate averages for every restraint.
        Return <rmsd>, sd and total violations over 1, 3, and 5 degrees as tuple
        or (None, None, None, None, None) on error
        """
        if not len( self ):
            NTerror('DihedralRestraintList.analyze: "%s" empty list', self.name )
            return (None, None, None, None, None)
        #end if

        modelCount = 0
        if (len(self[0].atoms) > 0):
            modelCount = self[0].atoms[0].residue.chain.molecule.modelCount
        #end if

        if (modelCount == 0):
            NTerror('DihedralRestraintList.analyze: "%s" modelCount 0', self.name )
            return (None, None, None, None, None)
        #end if

        self.rmsd  = NTfill( 0.0, modelCount )
        self.violCount1 =  0
        self.violCount3 =  0
        self.violCount5 =  0
        for dr in self:
            if calculateFirst:
                (cav, _cv) = dr.calculateAverage()
                if not cav:
                    NTdebug("Failed to calculate average for: "+self.format())
            self.violCount1 += dr.violCount1
            self.violCount3 += dr.violCount3
            self.violCount5 += dr.violCount5
            for i in range(0, modelCount):
                self.rmsd[i] += dr.violations[i]*dr.violations[i]
            #end for
        #end for

        for i in range(0, modelCount):
            self.rmsd[i] = math.sqrt(self.rmsd[i]/len(self))
        #end for

        self.rmsdAv, self.rmsdSd, _n = NTaverage( self.rmsd )
        return (self.rmsdAv, self.rmsdSd, self.violCount1, self.violCount3, self.violCount5)
    #end def

    def sort(self, byItem ):
        """
        Sort the list byItem
        """
        NTsort( self, byItem, inplace=True)
        return self
    #end def

    def __str__( self ):
        return sprintf( '<DihedralRestraintList "%s" (%s,%d)>', self.name, self.status, len(self) )
    #end def

    def format( self ):
        return sprintf( '%s DihedralRestraintList "%s" (%s,%d) %s\n'+\
                        'rmsd: %7s %6s        Violations > 1,3,5 degree: %d, %d, %d\n',
                      dots, self.name,self.status,len(self), dots,
                      val2Str(self.rmsdAv,         "%7.3f", 7),
                      val2Str(self.rmsdSd,         "%6.3f", 6),
                      self.violCount1, self.violCount3, self.violCount5)
    #end def
#end class

class SMLDihedralRestraintListHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'DihedralRestraintList' )
    #end def

    def handle(self, line, fp, project=None):
        drl = DihedralRestraintList( *line[2:] )
        if not self.listHandler(drl, fp, project): return None
        project.dihedrals.append( drl )
        return drl
    #end def

    def toSML(self, drl, fp):
        self.list2SML( drl, fp )
    #end def
#end class
DihedralRestraintList.SMLhandler = SMLDihedralRestraintListHandler()


#-----------------------------------------------------------------------------
class RDCRestraint( NTdict ):
    """RDCRestraint class:
    """
    def __init__( self, atomPairs=[], lower=0.0, upper=0.0, **kwds ):

        NTdict.__init__(self, __CLASS__  = 'RDCRestraint',
                              atomPairs  = NTlist(),
                              lower      = lower,
                              upper      = upper,
                              **kwds
                       )
        self.id         = -1       # Undefined index number
        self.rdcs        = None     # list with backcalculated rdc values for each model, None indicates no analysis done

        for pair in atomPairs:
            self.appendPair( pair )
        #end for

    #end def

    def appendPair( self, pair ):
        # check if atom already present, keep order
        # otherwise: keep atom with lower residue index first
        a0 = self.atomPairs.zap(0)
        a1 = self.atomPairs.zap(1)
        if (pair[0] in a0 or pair[1] in a1):
            self.atomPairs.append( pair )
        elif (pair[0] in a1 or pair[1] in a0):
            self.atomPairs.append( (pair[1],pair[0]) )
        elif (pair[0].residue.resNum > pair[1].residue.resNum):
            self.atomPairs.append( (pair[1],pair[0]) )
        else:
            self.atomPairs.append( pair )
    #end def

    def calculateAverage(self):
        """Calculate the values and violations for each model
        """

        modelCount = 0
        if (len(self.atoms) > 0):
            modelCount = self.atoms[0].residue.chain.molecule.modelCount
        #end if

        if (modelCount == 0):
            NTerror('Error RDCRestraint: no structure models\n' )
            return (None,None)
        #end if

        if len(self.atoms) != 2 or None in self.atoms:
            NTerror('Error RDCRestraint: invalid rdc definition %s\n', self.atoms )
            return (None,None)
        #end if

        if None in self.atoms.zap('meanCoordinate'):
            NTerror('Error RDCRestraint: atom without coordinates %s\n', self.atoms )
            return (None,None)
        #end if

        #set the default values

        return( None, None )
    #end def

    def listViolatingModels(self, cutoff = 3.0 ):
        """
        Examine for violations larger then cutoff, return list of violating models or None on error
        Requires violations attribute (obtained with calculateAverage method).
        """
        if not self.has_key('violations'):
            return None

        violatingModels = NTlist()
        for i in range(0, len(self.violations) ):
            if (math.fabs( self.violations[i]) > cutoff):
                violatingModels.append( i )
            #end if
        #end for

        return violatingModels
    #end def

    def _names(self):
        """
        Internal routine: generate string from atomPairs
        """
        s = ''
        for p in self.atomPairs:
            s = s + sprintf('(%-11s - %11s)   ', p[0]._Cname(1), p[1]._Cname(1))
        #end for
        return s.strip()
    #end def

    def __str__(self):
        return sprintf('<RDCRestraint %d>', self.id )
    #end def

    def format( self ):
#        s = '('
#        for p in self.atoms:
#            s = s + sprintf('%-11s ', p._Cname(1) )
#        #end for
#        s = s.strip() + ')'
        return  sprintf('%-25s (Target: %6.1f %6.1f) %s',
                        str(self), self.lower, self.upper,
                        self._names()
                       )

    #end def
#end class

class SMLRDCRestraintHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'RDCRestraint' )
    #end def

    def handle(self, line, fp, project=None):
        dr = RDCRestraint( atoms=[], upper = 0.0 , lower =0.0 )
        return self.dictHandler(dr, fp, project)
    #end def

    def endHandler(self, dr, project):
        # Parse the atoms nameTuples, map to molecule
        dr.atoms = decode( dr.atoms, project.molecule )
#        atms = dr.atoms
#        dr.atoms = NTlist()
#        for atm in atms:
#            dr.appendPair( project.molecule.decodeNameTuple(atm) )
#        #end for
    #end def

    def toSML(self, dr, stream ):
        """
        """
        fprintf( stream, "%s\n", self.startTag )
        for a in ['lower','upper' ]:
            fprintf( stream, '    %-15s = %s\n', a, repr(dr[a]) )
        #end for
        fprintf( stream, '    %-15s = %s\n', 'atoms', repr(encode(dr.atoms)) )

#        rl = []
#        for r in self.atoms:
#            rl.append(r.nameTuple())
#        #end for
#        fprintf( stream, '    %-15s = %s\n', 'atoms', repr( rl ) )
        fprintf( stream, "%s\n", self.endTag )
    #end def
#end class
RDCRestraint.SMLhandler = SMLRDCRestraintHandler()


#-----------------------------------------------------------------------------
class RDCRestraintList( NTlist ):

    def __init__( self, name, status='keep' ):
        NTlist.__init__( self )
        self.name       = name
        self.status     = status
        self.currentId  = 0       # Id for each element of list

        self.rmsd       = None    # rmsd per model, None indicate no analysis done
        self.rmsdAv     = 0.0
        self.rmsdSd     = 0.0
    #end def

    def append( self, RDCRestraint ):
        RDCRestraint.id = self.currentId
        NTlist.append( self, RDCRestraint )
        self.currentId += 1
    #end def

    def analyze( self, calculateFirst = True ):
        """
        Calculate averages for every restraint.

        """
        if (len( self ) == 0):
            NTerror('RDCRestraintList.analyze: "%s" empty list', self.name )
            return (None, None, None, None, None)
        #end if

        modelCount = 0
        if (len(self[0].atoms) > 0):
            modelCount = self[0].atoms[0].residue.chain.molecule.modelCount
        #end if

        if (modelCount == 0):
            NTerror('RDCRestraintList.analyze: "%s" modelCount 0', self.name )
            return (None, None, None, None, None)
        #end if

        self.rmsd  = NTfill( 0.0, modelCount )
        self.violCount1 =  0
        self.violCount3 =  0
        self.violCount5 =  0
        for dr in self:
            if calculateFirst: dr.calculateAverage()
            self.violCount1 += dr.violCount1
            self.violCount3 += dr.violCount3
            self.violCount5 += dr.violCount5
            for i in range(0, modelCount):
                self.rmsd[i] += dr.violations[i]*dr.violations[i]
            #end for
        #end for

        for i in range(0, modelCount):
            self.rmsd[i] = math.sqrt(self.rmsd[i]/len(self))
        #end for

        self.rmsdAv, self.rmsdSd, dummy_n = NTaverage( self.rmsd )
        return (self.rmsdAv, self.rmsdSd, self.violCount1, self.violCount3, self.violCount5)
    #end def

    def sort(self, byItem ):
        """
        Sort the list byItem
        """
        NTsort( self, byItem, inplace=True)
        return self
    #end def

    def __str__( self ):
        return sprintf( '<RDCRestraintList "%s" (%s,%d)>', self.name, self.status, len(self) )
    #end def

    def format( self ):
        s = sprintf( '%s RDCRestraintList "%s" (%s,%d) %s\n' +\
                     'rmsd: %7.3f %6.3f\n',
                      dots, self.name,self.status,len(self), dots,
                      self.rmsdAv, self.rmsdSd )
        return s
    #end def
#end class

class SMLRDCRestraintListHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'RDCRestraintList' )
    #end def

    def handle(self, line, fp, project=None):
        drl = RDCRestraintList( *line[2:] )
        if not self.listHandler(drl, fp, project): return None
        project.rdcs.append( drl )
        return drl
    #end def

    def toSML(self, drl, fp):
        self.list2SML( drl, fp )
    #end def
#end class
RDCRestraintList.SMLhandler = SMLRDCRestraintListHandler()
#-----------------------------------------------------------------------------

class History( NTlist ):
    """Cing history storage class
    """

    def __call__( self, line, timeStamp = True ):
        if timeStamp:
            self.append( (time.asctime(), line) )
        else:
            self.append( (None, line) )
        #end if
    #end def

    def __str__( self ):
        s = sprintf('%s History %s\n', dots, dots )
        for timeStamp,line in self:
            if timeStamp:
                s = s + sprintf('%s: %s\n', timeStamp, line )
            else:
                s = s + line + '\n'
            #end if
        #end for
        return s
    #end def

    format = __str__

    def toXML( self, depth=0, stream=sys.stdout, indent='\t', lineEnd='\n' ):
        NTindent( depth, stream, indent )
        fprintf( stream, "<History>")
        fprintf( stream, lineEnd )

        for a in self:
            NTtoXML( a, depth+1, stream, indent, lineEnd )
        #end for
        NTindent( depth, stream, indent )
        fprintf( stream, "</History>")
        fprintf( stream, lineEnd )
    #end def
#end class

#-----------------------------------------------------------------------------

class XMLHistoryHandler( XMLhandler ):
    """History handler class"""
    def __init__( self ):
        XMLhandler.__init__( self, name='History')
    #end def

    def handle( self, node ):
        items = self.handleMultipleElements( node )
        if items == None: return None
        result = History()
        for item in items:
            result.append( item )
        return result
    #end def
#end class

#register this handler
historyhandler = XMLHistoryHandler()


#-----------------------------------------------------------------------------

htmlObjects = NTlist() # A list of all htmlobject for rendering purposes

class HTMLfile:
    '''Description: Class to create a Html file; to be used with cing.css layout.
       Inputs: file name, title
       Output: a Html file.
    '''

    # A list of all htmlobject for rendering purposes
    #htmlObjects = NTlist() # Local track-keeping list

    def __init__( self, fileName, title = None ):
        '''Description: __init__ for HTMLfile class.
           Inputs: file name, title
           Output: an instanciated HTMLfile obj.

           The file is immidiately tested by a quick open for writing and closing.
        '''

        self.fileName = os.path.normpath( fileName )
        self.stream = open( self.fileName, 'w' )
        self.stream.close()

        # definition of content-less  tags
        self.noContent = [ 'base','basefont','br','col','frame','hr','img',
                           'input','link','meta','ccsrule' ]

        self.title = title
        self.indent = 0

        # copy css and other files (only files! no dirs)
#        The content of this dir is being copied to each HTMLfile instance's location.
#        TODO: remove this redundancy.
        dirname,_base,_extention = NTpath( self.fileName )
        htmlPath = os.path.join(cingRoot,cingPaths.html) #e.g. 1brv.cing/HTML
        for f in os.listdir( htmlPath ):
            htmlFile = os.path.join(htmlPath,f)
            if os.path.isfile(htmlFile):
                shutil.copy( htmlFile, dirname )

        self._header    = NTlist()
        self._call      = NTlist()
        self._main      = NTlist()
        self._left      = NTlist()
        self._right     = NTlist()
        self._footer    = NTlist()

        htmlObjects.append( self )
    #end def

    # Having a del method might upset the gc.
#    def __del__(self):
#        print '>>deleting>', self.title, self.fileName
#        print self
#        if self in htmlObjects:
#            htmlObjects.remove(self)
#        del( self )
#    #end def

    def killHtmlObjects():  # note there is no 'self', it's going to be a static method!
        """ Remove all objects from the htmlObjects list
            """
        while htmlObjects.pop():
            pass # I think this should work to clear the list

    killHtmlObjects = staticmethod( killHtmlObjects)

    def _appendTag( self, htmlList, tag, *args, **kwds ):
        '''Description: core routine for generating Tags.
           Inputs: HTMLfile obj, list, tag, openTag, closeTag, *args, **kwds.
           Output: list.
        '''
        self.indent += 1
        htmlList.append( self._generateTag( tag, *args, **kwds ) )
        self.indent -= 1
    #end def

    def _generateTag( self, tag, *args, **kwds ):
        '''Description: core routine for generating Tags.
           Inputs: HTMLfile obj, tag, openTag, closeTag,
                   newLine, *args, **kwds.
           Output: list.
        '''

        #self.indent += 1

        if kwds.has_key('openTag'):
            openTag = kwds['openTag']
            del kwds['openTag']
        else:
            openTag = True

        if kwds.has_key('closeTag'):
            closeTag = kwds['closeTag']
            del kwds['closeTag']
        else:
            closeTag = True

        if kwds.has_key('newLine'):
            newLine = kwds['newLine']
            del kwds['newLine']
        else:
            newLine = True
        v = { True: None, False: -1 }

        #print '****', htmlList,'*',tag,'*', openTag,'*', closeTag, '*', args

        if openTag and closeTag:
            s = ( self.openTag( tag, *args, **kwds )[:-1] +
                  self.closeTag(tag)[self.indent:v[newLine]] )
        elif openTag:
            s = ( self.openTag( tag, *args, **kwds ) )
        elif closeTag:
            s = ( self.closeTag( tag, *args, **kwds ) )
        #end if
        #self.indent -=1

        return s
    #end def

    def header( self, tag, *args, **kwds ):
        self.indent +=1
        self._appendTag( self._header, tag, *args, **kwds )
        self.indent -=1
    #end def

    def __call__( self, tag, *args, **kwds ):
        "Write openTag, content, closeTag (if appropriate)"
        self.indent +=1
        self._appendTag( self._call, tag, *args, **kwds )
        self.indent -=1
    #end def

    def main( self, tag, *args, **kwds ):
        self.indent +=1
        self._appendTag( self._main, tag, *args, **kwds )
        self.indent -=1
    #end def

    def left( self, tag, *args, **kwds ):
        self.indent +=1
        self._appendTag( self._left, tag, *args, **kwds )
        self.indent -=1
    #end def

    def right( self, tag, *args, **kwds ):
        self.indent +=1
        self._appendTag( self._right, tag, *args, **kwds )
        self.indent -=1
    #end def

    def footer( self, tag, *args, **kwds ):
        self._appendTag( self._footer, tag, *args, **kwds )
    #end def

    def render(self):
        '''Description: write container to file Html.
           Inputs: a HTMLfile obj.
           Output: written lines and close file.

           JFD notes it is simpler to code this as constructing the whole content
           first and then writing. It would be just as fast for the size
           of html files we render.
        '''

        self.stream = open( self.fileName, 'w' )
#        NTdebug('writing to file: %s' % self.fileName)
        self.indent = 0

        self.stream.write(self.openTag('!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"'))
        self.stream.write(self.openTag('html'))
        self.stream.write(self.openTag('head'))
        if self.title:
            self.stream.write( self._generateTag( 'title', self.title ))

        self.stream.write(self._generateTag( 'link',
            rel="stylesheet", type="text/css", media="screen", href=cingPaths.css))
        self.stream.write(self.closeTag('head'))
        self.stream.write(self.openTag('body'))
        self.stream.write(self.openTag('div', id="container"))
        self.indent += 1

        self.stream.write( self.openTag('div', id = 'header') )
        self.stream.writelines(self._header)
        self.stream.write(self.closeTag('div', '<!-- end header -->'))

        self.stream.write( self.openTag('div', id = 'main') )
        self.stream.writelines(self._call + self._main)

        for divId, htmlList in [ ('left', self._left), ('right', self._right) ]:

            if htmlList:
                self.indent += 1

                self.stream.write( self.openTag('div', id = divId) )
                self.stream.writelines(htmlList)
                self.stream.write(self.closeTag('div',sprintf('<!-- end %s -->',
                                                              divId)))
                self.indent -= 1
        self.stream.write(self.closeTag('div', '<!-- end main -->'))
        self.stream.write(self._generateTag( 'br', style="clear: both;" ))

        self.indent = 0

        self.stream.write(self.closeTag('div', '<!-- end container -->'))

        self.stream.write(self.openTag('div', id = 'footer'))
        #self.defaultFooter()
        self.stream.writelines(self._footer)
        msg = programName + ' ' + cingVersion + ' '
        i=0
        n=len(authorList)
        for author in authorList:
            i+=1
            msg +=  '<a href="mailto:%s">%s</a>' % ( author[1],author[0])
            if i==(n-1):
                msg += ' and '
            elif i<n:
                msg += ', '
        self.stream.write(self._generateTag( 'p', msg))
        self.stream.write(self.closeTag('div', '<!-- end footer -->'))

        self.stream.write(self.closeTag('body'))
        self.stream.write(self.closeTag('html'))

        self.stream.close()

    def tag( self, tag, *args, **kwds ):
        "Return (openingTag, content, closingTag) triple"

        #print '*****', tag, [args], (kwds)
        openTag = sprintf('<%s',tag)
        for key,value in kwds.iteritems():
            openTag = openTag + sprintf(' %s="%s"', key, value)
        #end for

        if (tag in self.noContent):
            openTag = openTag +  '/>'
        else:
            openTag = openTag +  '>'
        #end if

        content = ''.join(args)
        if (tag in self.noContent):
            closeTag = ''
        else:
            closeTag = sprintf('</%s>',tag)
        #end if
        return (openTag,content,closeTag)
    #end def

    def openTag( self, tag, *args, **kwds ):
        "Write openTag, content; NO closeTag"
        openTag, content, dummyCloseTag = self.tag( tag, *args, **kwds )
        return sprintf( '%s%s%s\n', '' + '\t' * self.indent, openTag, content )
    #end def

    def closeTag( self, tag, *args, **kwds ):
        "Write closeTag *args"
        dummyOpenTag, content, closeTag = self.tag( tag, *args, **kwds )
        return sprintf( '%s%s%s\n', '' + '\t' * self.indent, closeTag, content )
    #end def

    def findHtmlLocation(self, source, destination, id=None ):
        '''Description: given 2 Cing objects returns the relative path between them.
           Inputs: Cing objects souce, destination
           Output: string path or None or error

           E.g. input: source.htmlLocation[0]     : test_HTMLfile.cing/index.html
                       destination.htmlLocation[0]: test_HTMLfile.cing/moleculeName/HTML/indexMolecule.html
                output                            : moleculeName/HTML/indexMolecule.html
        '''
        # Debugger perspecitive put at source (me)
        # Destination is the target.
        for item in [source, destination]:
            if not hasattr(item,'htmlLocation'):
                NTerror('No htmlLocation attribute associated to obj %s\n', item)
                return None

        # Strip leading dot for rest of algorithm.
        # Normalize path, eliminating double slashes, etc.
        sourcePath = os.path.normpath(     source.htmlLocation[0])
        destPath   = os.path.normpath(destination.htmlLocation[0])
        # Get default id.
        destId     = destination.htmlLocation[1]
        # Or override.
        if id:
            destId = '#' + id

        listSourcePath = sourcePath.split('/')
        listDestPath   = destPath.split('/')

        # JFD next code is disabled because the comparison might shortcircuit
        # when identical names are matched 'by accident'.
#        for index in range(lenSP):
#            if listSourcePath[index] != listDestPath[index]:
#                #location = index * ['..'] + listDestPath
#                break
#        i = lenSP - 1 - index
#        locationList = (index + i) * ['..'] + listDestPath
#        loc = ''
#        for item in location:
#            loc = os.path.join(loc,item)
#        loc = os.path.join( *locationList )

        # How far away (in dir changes) am I from the first (left/cing) dir?
        # The list will look like:  list: ['test_HTMLfile.cing', 'index.html']
        # One jump is one directory.
        # E.g. 1brv/1brv/index.html has 2 jumps.

        toLeftNumberOfJumpsSource = len(listSourcePath) - 1
        toLeftNumberOfJumpsDest   = len(listDestPath)   - 1

        # Any same leading directories may be ommited.
        # using the fact that they are rooted in the same starting dir (curdir)
        toLeftNumberOfJumpsSourceNew = toLeftNumberOfJumpsSource
        i = 0
        while i < toLeftNumberOfJumpsDest and i < toLeftNumberOfJumpsSource:
            if listSourcePath[i] == listDestPath[i]:
                toLeftNumberOfJumpsSourceNew -= 1
            else:
                break
            i += 1
        jumpsToRemove = toLeftNumberOfJumpsSource - toLeftNumberOfJumpsSourceNew
        listDestPathNew = listDestPath[jumpsToRemove:]
        locationList = toLeftNumberOfJumpsSourceNew * ['..']
        locationList += listDestPathNew
        loc = os.path.join( *locationList )
        loc = os.path.normpath(loc) # I don't think it's needed anymore but can't hurt either.
        return loc + destId

    def insertHtmlLink( self, section, source, destination, text=None, id=None ):
        '''Description: create the html command for linking Cing objects.
           Inputs: section (main, header, left etc.), source obj., destination
                   obj., html text, id.
           Output: <a class="red" href="link">text</a> inside section

           Example call: project.html.insertHtmlLink( main, project, item, text=item.name )
        '''

        if not section:
            NTerror("No HTML section defined here\n")
            return None

        if not source:
            NTerror("No Cing object source defined here\n")
            return None

        if not destination:
            NTerror("No Cing object destination defined here\n")
            return None

        link = self.findHtmlLocation( source, destination, id )
#        NTdebug('From source: [%s] to destination [%s] id [%s] using relative link: %s' % (source, destination, id,link))
        #if not destination.has_key('colorLabel'):
        if not hasattr(destination, 'colorLabel'):
            destination.colorLabel = COLOR_GREEN

        # solution for avoiding python 'class' command with html syntax
        kw = {'class':destination.colorLabel, 'href':link}
        section('a', text, **kw)
    #end def

    def insertHtmlLinkInTag( self, tag, section, source, destination, text=None,
                             id=None):
        '''Description: create the html command for linking Cing objs inside a tag.
           Inputs: tag, section (main, header, left etc.), source obj.,
                   destination obj., html text, id.
           Output: <h1><a class="red" href="link">text</a></h1> inside section

        Example call:
                    project.html.insertHtmlLinkInTag( 'li', main, project, item, text=item.name )

        '''

        section(tag, closeTag=False)
        self.insertHtmlLink(section, source, destination, text=text, id=id)
        section(tag, openTag=False)

#end class

#-----------------------------------------------------------------------------
def path( *args ):
    """
    Return a path from arguments relative to cing root
    """
    return os.path.join( cingRoot, *args )
#end def

def shift( atm ):
    return atm.shift()
#end def
