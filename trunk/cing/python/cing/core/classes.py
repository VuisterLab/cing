"""
Implementation of the CING API's main classes.
Split into 3 for better performance.
"""

from ConfigParser import ConfigParser
from cing import cingPythonCingDir
from cing import cingRoot
from cing import cingVersion
from cing import header
from cing import issueListUrl
from cing.Libs.Geometry import violationAngle
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.cython.superpose import NTcVector #@UnresolvedImport @UnusedImport
from cing.Libs.cython.superpose import Rm6dist #@UnresolvedImport
from cing.Libs.disk import copydir
from cing.Libs.disk import remove
from cing.Libs.helper import getStartMessage
from cing.Libs.helper import getStopMessage
from cing.Libs.html import DihedralByProjectList
from cing.Libs.html import addPreTagLines
from cing.Libs.html import generateHtml
from cing.Libs.html import renderHtml
from cing.Libs.html import setupHtml
from cing.Libs.pdb import export2PDB
from cing.Libs.pdb import importPDB
from cing.Libs.pdb import initPDB
from cing.PluginCode.required.reqNih import TALOSPLUS_LIST_STR
from cing.PluginCode.required.reqWhatif import summaryCheckIdList
from cing.STAR.File import File
from cing.core.CingSummary import CingSummary
from cing.core.classes2 import * #@UnusedWildImport
from cing.core.constants import * #@UnusedWildImport
from cing.core.molecule import Atom
from cing.core.molecule import Ensemble
from cing.core.molecule import Molecule
from cing.core.molecule import nTdihedralOpt
from cing.core.molecule import nTdistanceOpt #@UnusedImport
from cing.core.parameters import cingPaths
from cing.core.parameters import directories
from cing.core.parameters import moleculeDirectories
from cing.core.parameters import plotParameters
from cing.core.parameters import plugins
from cing.core.parameters import validationSubDirectories
from cing.core.validate import checkForSaltbridges
from cing.core.validate import criticize
from cing.core.validate import criticizePeaks
from cing.core.validate import fixStereoAssignments
from cing.core.validate import partitionRestraints
from cing.core.validate import runCingChecks
from cing.core.validate import summaryForProject
from cing.core.validate import validate
from cing.core.validate import validateAssignments
from cing.core.validate import validateDihedralCombinations
from cing.core.validate import validateDihedrals
from cing.core.validate import validateModels
from cing.core.validate import validateRestraints
from glob import glob
from glob import glob1
from shutil import rmtree
import tarfile
__version__ = cing.__version__
__date__ = cing.__date__
__author__ = cing.__author__
__copyright__ = cing.__copyright__
__credits__ = cing.__credits__

projects = NTlist()

#: CRV stands for CRiteria Value CRS stands for CRiteria String
CRV_NONE = "-999.9"

#-----------------------------------------------------------------------------
# Cing classes and routines
#-----------------------------------------------------------------------------
# pylint: disable=R0902
class Project(NTdict): # pylint: disable=R0904

    """
-------------------------------------------------------------------------------
Project: Top level Cing project class
-------------------------------------------------------------------------------

  Project <-> molecules[<Molecule-1>, <Molecule-2>, ...]   #  Molecule instances list
           -> molecule                                     # 'Current' molecule

          <-> peaks[<Peaklist [<Peak>, ...]>]                                # Project peak lists
          <-> distances[<DistanceRestraintList[<DistanceRestraint>, ...]>]   # Project DistanceRestraint lists
          <-> dihedrals[<DihedralRestraintList[<DihedralRestraint>, ...]>]   # Project DihedralRestraint lists
          <-> rdcs[<RDCRestraintList[<RDCRestraint>, ...]>]                  # Project RDCRestraint lists

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

    to save a project:
        project.save()

    to export:
        project.export()

    to export and save:
        project.close()

    to initialize a Molecule:
        project.newMolecule( name, sequenceFile, convention )
                                    convention = CYANA, CYANA2, INTERNAL, LOOSE

    to initialize the resonance lists:
        project.initResonances()

    to merge the resonance lists:
        project.mergeResonances( order=None, status='reduce' )
                                status='reduce' results in reducing the resonances
                                list to one merged entry

    to define and add a new PeakList to project:
        peakList = project.peaks.new( name, status='keep' ):

    to define and add a new DistanceRestraintList to project:
        distanceRestraintList = project.distances.new( name, status='keep' ):
    Likewise for list of other restraint types (dihedrals, RDCs).

    """

    def __init__(self, name):

        root, name = Project.rootPath(name)

        NTdict.__init__(self, __CLASS__ = 'Project')

        self.version = cingVersion       
        self.root = root
        self.name = name.strip()
        self.created = time.asctime()      
        self.molecule = None # Current Molecule instance

        self.moleculeNames = NTlist() # list to store molecule names for save and restore
        self.peakListNames = NTlist() # list to store peaklist names for save and restore
        self.distanceListNames = NTlist() # list to store distancelist names names for save and restore
        self.dihedralListNames = NTlist() # list to store dihedrallist names for save and restore
        self.rdcListNames = NTlist() # list to store rdclist names for save and restore
        self.coplanarListNames = NTlist() # list to store  names for save and restore
        self.dihedralByProjectListNames = NTlist() # list to store  names for save and restore
        self.dihedralByResidue = NTtree( DIHEDRAL_BY_RESIDUE_STR ) # Used to be set in DihedralByResidueHTMLfile but that's too late.
        self.reports = NTlist() # list with validation reports names

        self.history = History()
        self.contentIsRestored = False # True if Project.restore() has been called
        self.storedInCcpnFormat = False

        self.procheckStatus = NTdict(completed = False, parsed = False, ranges = None)

        self.whatifStatus = NTdict(completed = False, parsed = False)
        self.wattosStatus = NTdict(completed = False, parsed = False)
        self.vascoStatus = NTdict(completed = False, parsed = False)
        self.shiftxStatus = NTdict(completed = False, parsed = False)
        self.x3dnaStatus  = NTdict(completed = False, parsed = False)
        self.status = NTdict() # General status dict for external programs

#        store a reference to the global things we might need
        self.gui = None # Reference to CingGui instance
        self.directories = directories
        self.moleculeDirectories = moleculeDirectories
        self.validationSubDirectories = validationSubDirectories
        self.cingPaths = cingPaths
        self.plotParameters = plotParameters
        self.plugins = plugins

        self.statusObjectNameList = 'procheckStatus dsspStatus whatifStatus wattosStatus vascoStatus shiftxStatus x3dnaStatus'.split()
        # These Project lists are dynamic and will be filled  on restoring a project
        # They also maintain some internal settings
        # new( name ), append( instance), save(), restore() and path( name ) and names() comprise core functionality
        self.molecules = ProjectList(project = self,
                                         classDef = Molecule,
                                         nameListKey = 'moleculeNames',
                                         basePath = directories.molecules + '/%s'
                                       )
        self.peaks = ProjectList(project = self,
                                         classDef = PeakList,
                                         nameListKey = 'peakListNames',
                                         basePath = directories.peaklists + '/%s.peaks'
                                       )
        self.distances = ProjectList(project = self,
                                         classDef = DistanceRestraintList,
                                         nameListKey = 'distanceListNames',
                                         basePath = directories.restraints + '/%s.distances'
                                       )
        self.distanceRestraintNTlist = RestraintList('distanceRestraintNTlist') # used for DB populated by validateRestraints

        self.dihedrals = ProjectList(project = self,
                                         classDef = DihedralRestraintList,
                                         nameListKey = 'dihedralListNames',
                                         basePath = directories.restraints + '/%s.dihedrals'
                                       )
        self.dihedralRestraintNTlist = RestraintList('dihedralRestraintNTlist')
        self.rdcs = ProjectList(project = self,
                                         classDef = RDCRestraintList,
                                         nameListKey = 'rdcListNames',
                                         basePath = directories.restraints + '/%s.rdcs'
                                       )
        self.coplanars = ProjectList(project = self,
                                         classDef = CoplanarList,
                                         nameListKey = 'coplanarListNames',
                                         basePath = directories.restraints + '/%s.coPlanars'
                                       )
        self.dihedralByProjectList = ProjectList(project = self,
                                         classDef = DihedralByProjectList,
                                         nameListKey = 'dihedralByProjectListNames',
                                         basePath = directories.molecules + '/%s.dihedralsByProjectList'# Will never need to be saved.
                                       )

#        self.dihedralByResidue = None # done above.


        # store reference to self
        #self[name] = self
        self.objectPath = self.path(cingPaths.project)
#        self.makeObjectPaths() # generates the objectPaths dict from the nameLists

        self.rogScore = ROGscore()
        self.summaryDict = CingSummary()

        self.valSets = NTdict()
        self.readValidationSettings(fn = None)
        self.nosave = False

        self.saveXML('version',
                      'name', 'created',
                      'moleculeNames',
                      'peakListNames', 'distanceListNames', 'dihedralListNames', 'rdcListNames', 
                      'coplanarListNames', 'dihedralByProjectListNames', 'dihedralByResidue',
                      'storedInCcpnFormat',
                      'reports',
                      'history',
                      'procheckStatus', 'whatifStatus', 'wattosStatus', 'shiftxStatus', 'status'
                    )
    #end def


    def readValidationSettings(self, fn = None):
        """Reads the validation settings from installation first and then overwrite any if a filename is given.
        This ensures that all settings needed are present but can be overwritten. It decouples development from
        production.
        """

        validationConfigurationFile = os.path.join(cingPythonCingDir, VAL_SETS_CFG_DEFAULT_FILENAME)
#        nTdebug("Using system validation configuration file: " + validationConfigurationFile)
        self._readValidationSettingsFromfile(validationConfigurationFile)
        validationConfigurationFile = None

        if fn:
            validationConfigurationFile = fn
#            nTdebug("Using validation configuration file: " + validationConfigurationFile)
        elif os.path.exists(VAL_SETS_CFG_DEFAULT_FILENAME):
            validationConfigurationFile = VAL_SETS_CFG_DEFAULT_FILENAME
#            nTdebug("Using local validation configuration file: " + validationConfigurationFile)
        if validationConfigurationFile:
            self._readValidationSettingsFromfile(validationConfigurationFile)

    #end def

    def _readValidationSettingsFromfile(self, fn):
        """Return True on error.   """
        if not fn:
            nTcodeerror("No input filename given at: _readValidationSettingsFromfile")
            return True

        if not os.path.exists(fn):
            nTcodeerror("Input file does not exist at: " + fn)
            return True

#        nTdebug("Reading validation file: " + fn)
        config = ConfigParser()
        config.readfp(open(fn))
        for item in config.items('DEFAULT'):
            key = item[0].upper()  # upper only.
            try:
                if item[1] == CRV_NONE:
                    value = None
                else:
                    value = float(item[1])
            except ValueError:
                try:
                    value = bool(item[1])
                except:
                    value = item[1]
            valueStr = repr(value)
            if self.valSets.has_key(key):
                valueFromStr = repr(self.valSets[key])
                if valueStr == valueFromStr:
                    continue  # no print
#                nTdebug("Replacing value for key " + key + " from " + valueFromStr + " with " + valueStr)
            else:
#                nTdebug("Adding              key " + key + " with value: " + valueStr)
                pass
            self.valSets[key] = value # name value pairs.
        #end for
        self.valSets.keysformat()
    #end def

    def getCingSummaryDict(self):
        """Get a CING summary dict from self
        Return summaryDict or None on error
        """
        self.summaryDict.getSummaryFromProject(self)
        return self.summaryDict
    #end def

    #-------------------------------------------------------------------------
    # Path stuff
    #-------------------------------------------------------------------------

    def path(self, *args):
        """Return joined args as path relative to root of project
        """
        return os.path.normpath(os.path.join(self.root, *args))
    #end def

    def rootPath(pathName):
        """Static method returning Root,name of project from pathName

        name can be:
            simple_name_string
            directory.cing
            directory.cing/
            directory.cing/project.xml

        GWV  6 Dec 2007: to allow for relative paths.
        JFD 17 Apr 2008: fixed bugs caused by returning 2 values.
        """
        root, name, ext = nTpath(pathName)
        if name == '' or name == 'project': # indicate we had a full path
            root, name, ext = nTpath(root)
        #end if
        if (len(ext) > 0 and ext != '.cing'):
            nTerror('FATAL: unable to parse "%s"; invalid extention "%s"\n', pathName, ext)
#            exit(1) # no more hard exits for we might call this from GUI or so wrappers
            return None, None

        rootp = os.path.join(root, name + '.cing')
#        nTdebug("rootp, name: [%s] [%s]" % (rootp, name))
        return rootp, name
    #end def
    rootPath = staticmethod(rootPath)

    def mkdir(self, *args):
        """Make a directory relative to to root of project from joined args.
           Check for presence.
           Return the result
        """
        d = self.path(*args)
        if not os.path.exists(d):
#            nTdebug( "project.mkdir: %s" % d )
            os.makedirs(d)
        return d
    #end def

    def moleculePath(self, subdir = None, *args):
        """ Path relative to molecule.
        Return path or None in case of error.
        """
        if not self.molecule:
            return None
        if subdir == None:
            return self.path(self.molecule.name)
#        nTdebug("moleculePath: subdir, moleculeDirectories[subdir] %s %s" % (subdir, moleculeDirectories[subdir]))
        return self.path(self.molecule.name, moleculeDirectories[subdir], *args)
    #end def

    def validationPath(self, *args):
        """Path relative to validation directory for molecule.
        Create directory if does not exist.

        **** Highly redundant with moleculePath at present time, but should replace it eventually ***

        Return pathName or None in case of error.
        """
        if not self.molecule:
            return None
        pathName = self.mkdir(self.molecule.name, *args) # should become self.mkdir( 'Validation', self.molecule.name )
        return pathName
    #end def


    def htmlPath(self, *args):
        """ Path relative to molecule's html directory.
        Return path or None in case of error.
        """
        return self.moleculePath('html', *args)
    #end def

    def decodeNameTuple(self, nameTuple):
        """Decode the 7-element nameTuple:

    (objectName, chainName, resNum, atomName, modelIndex, resonanceIndex, convention)

    Return Object or None on error.

    @TODO Now works for Molecule; Also implement for other project list object like PeakList, DistanceRestraintList, etc
        """
        if nameTuple == None or not self.has_key(nameTuple[0]):
            return None
        return self[nameTuple[0]].decodeNameTuple(nameTuple)

    #-------------------------------------------------------------------------
    # actions exists/open/restore/save/close/export/updateProject
    #-------------------------------------------------------------------------

    def exists(name):
        """Static method exists check for presence of Project directory derived from name
            returns True or False
        """
        rootp, _n = Project.rootPath(name)
        if os.path.exists(rootp):
            return True
        return False
    #end def
    exists = staticmethod(exists)

    def setStatusObjects(self, parsed=None, completed = None):
        'Only update the parameter that is not None (True or False)'
#             = 'procheckStatus dsspStatus whatifStatus wattosStatus vascoStatus shiftxStatus x3dnaStatus'.split()
        for statusObjectName in self.statusObjectNameList:
            if parsed != None:
                setDeepByKeys(self, parsed, statusObjectName, PARSED_STR)
            if completed != None:
                setDeepByKeys(self, completed, statusObjectName, COMPLETED_STR)
        # end for
    # end def

        
    def open(name, status = 'create', restore = True):
        """Static method open returns a new/existing Project instance depending on status.

           status == 'new': open a new project 'name'
           status == 'old: open existing project 'name'
                      project data is restored when restore == True.
           status == 'create': if project name if exists open as old, open as new otherwise.

           Returns Project instance or None on error.
        """
        # Using the global statement without assignment pylint: disable=W0602
        global projects

        #print '>>', name, status

        if (status == 'new'):
            root, dummy = Project.rootPath(name)
            if not root:
                return None
            if os.path.exists(root):
                removedir(root)
            #end if
            os.mkdir(root)
            pr = Project(name)
            pr.addHistory('New project')
            # Save the project data
            obj2XML(pr, path = pr.objectPath)
#            nTdebug('New project %s', pr)

        elif (status == 'create'):
            root, dummy = Project.rootPath(name)
            if not root:
                return None
            if os.path.exists(root):
                return Project.open(name, 'old', restore = restore)
            else:
                return Project.open(name, 'new', restore = restore)
            #end if

        elif status == 'old':
            possibleTgz = name + ".cing.tgz"
            possibleProjectDir = name + '.cing'
            if os.path.exists(possibleTgz) and not os.path.exists(possibleProjectDir):
#                nTdebug("Unpacking possibleTgz: " + possibleTgz)
                tar = tarfile.open(possibleTgz, "r:gz")
                for itar in tar:
                    tar.extract(itar.name, '.') # itar is a TarInfo object
#                    nTdebug("extracted: " + itar.name)
                tar.close()
                if not os.path.exists(possibleProjectDir):
                    nTerror('Project.open: Failed to find project in .tgz file. Unable to open Project "%s"', name)
                    return None
#            else:
#                if not os.path.exists(possibleTgz):
#                    nTdebug("No " + possibleTgz + " found.")
#                    nTdebug("Skipping .tgz because there's already a .cing")
#                else:

            root, newName = Project.rootPath(name)
            if not root:
                nTerror('Project.open: unable to open Project "%s" because root is [%s].', name, root)
                return None
            if not os.path.exists(root):
                nTerror('Project.open: unable to open Project "%s" because root [%s] was not found.', name, root)
                return None
            #end if

            # Restore Project info from xml-file
            pfile = os.path.join(root, cingPaths.project)
            if not os.path.exists(pfile):
                nTerror('Project.open: missing Project file "%s"', pfile)
                return None
            #end if
            pr = xML2obj(pfile)
            if pr == None:
                nTerror('Project.open: error parsing Project file "%s"', pfile)
                return None
            #end if
            # This allows renaming/relative addressing at the shell level
            pr.root = root
            pr.name = newName
            pr.objectPath = pfile

            pr.contentIsRestored = False

            pr.setStatusObjects(parsed=False)

            try:
                # <= 0.75 version have string
                pr.version = float(pr.version.strip('abcdefghijklmnopqrtsuvw ()!@#$%^&*').split()[0])
            except:
                pass

            if pr.version <= 0.75:
                nTmessage('Project.Open: converting from CING version %s', pr.version)
#                nTdebug('Project.open: conversion: old project settings\n%s', pr.format())

                # 0.75 version had moleculeNames stored in molecules attribute
                # >=0.76 version molecules is a ProjectList instance
                pr.moleculeNames = pr.molecules
                if 'molecules' in pr.__SAVEXML__:
                    pr.__SAVEXML__.remove('molecules')
                pr.saveXML('moleculeNames')

                # store the xmlFile and reopen to have correct settings
                if obj2XML(pr, path = pfile) != pr:
                    nTerror('Project.Open: conversion from version %s failed on write', pr.version)
                    return None
                pr = xML2obj(pfile)
                if pr == None:
                    nTerror('Project.Open: conversion from version %s failed on read', pr.version)
                    return None

                for molName in pr.moleculeNames:
                    pathName = pr.path(directories.molecules, molName) # old reference, versions 0.48-0.75
                    if pr.version <= 0.48:
                        pathName = pr.path('Molecules', molName) # old reference
                    # end if
#                    nTdebug('Project.open: trying molecule conversion from %s', pathName)
                    if not os.path.exists(pathName):
                        nTerror('Project.open: old molecule pathName "%s" does not exist.', pathName)
                        return None
                    mol = Molecule.openMol_075(pathName)
                    if not mol:
                        nTerror('Project.Open: conversion from version %s failed on molecule %s', pr.version, molName)
                        return None
                    removedir(pathName)
                    # Save molecule to new format
                    mol.save(pr.molecules.path(molName))
                #end for

                # restore
                pr.restore()
                # Save to consolidate
                pr.save()

            # changed for allowing to store special database entries.
            elif round(pr.version*1000) < 950: # i.e. versions 0.94 and lower
                for molName in pr.moleculeNames:
                    pathName = pr.molecules.path(molName)
                    mol = Molecule.openMol_094(pathName+'.molecule')
                    mol.save(pathName)
                    remove(pathName+'.molecule')
                #end for
                # restore
                pr.restore()
                # Save to consolidate
                pr.save()
            #end if

            # Optionally restore the content
            if restore and not pr.contentIsRestored:
                pr.restore()
            #end if
            nTmessage('Finished restoring project %s', pr)
        else:
            nTerror('ERROR Project.open: invalid status option "%s"', status)
            return None
        #end if

        # Check the subdirectories
        tmpdir = pr.path(directories.tmp)
        # have to use cing.verbosity to work?
        if os.path.exists(tmpdir) and cing.verbosity != cing.verbosityDebug:
            removedir(tmpdir)
        for d in directories.values():            
#            nTdebug('dir: %r' % d)
            pr.mkdir(d)
        #end for

        pr.addLog()

        projects.append(pr)
        return pr
    #end def
    open = staticmethod(open)

    def close(self, save = True):
        """
        Save project data and close project.
        TODO: Call destructor on self and its elements
        """
        # Using the global statement without assignment pylint: disable=W0602
        global projects
        #self.export()

        if save and not self.nosave:
            self.save()
        # remove the tmpdir
        tmpdir = self.path(directories.tmp)
        # have to use cing.verbosity to work?
        #print '>>', cing.verbosity, cing.verbosityDebug
        if os.path.exists(tmpdir) and cing.verbosity != cing.verbosityDebug:
            removedir(tmpdir)

        self.closeLog()

        projects.remove(self)
        return None
    #end def

    def superpose(self, ranges = None, backboneOnly = True, includeProtons = False, iterations = 2):
        """
        Calculate a superposition of current active molecule
        return rmsd result of molecule, or None on error

        """

        if not self.molecule:
            nTerror('Project.superpose: undefined molecule')
            return None
        #end if

        if self.molecule.modelCount == 0:
            nTerror('Project.superpose: no coordinates for %s\n', self.molecule)
            return None
        #end if

        if ranges == None: # not really needed here.
            ranges = self.molecule.ranges

        self.molecule.superpose(ranges = ranges, backboneOnly = backboneOnly,
                                   includeProtons = includeProtons, iterations = iterations
                                  )
        return self.molecule.rmsd
    #end def

    def save(self):
        """
        Save project data;

        Return True on success.
        """
        nTmessage('' + dots * 5 + '')
        nTmessage('==> Saving %s', self)

        # Save the molecules
        for mol in self.molecules:
            mol.save(mol.objectPath)
        self.moleculeNames = self.molecules.names()
        self.saveXML('moleculeNames')

        # Save the molecules and lists
        for pl in [self.peaks, self.distances, self.dihedrals, self.rdcs, self.coplanars]:
            self[pl.nameListKey] = pl.save() # Save returns a list of name; store these in project
            # Patch for XML bug
            self.saveXML(pl.nameListKey)
        #end for

        # Call Plugin registered functions
        for p in self.plugins.values():
            if (not p) or (not hasattr(p, 'saves')) or (not p.saves):
                pass
#                nTdebug("Skipping save for disabled plugin: %s" % p)
            else:
                for f, obj in p.saves:
#                    nTdebug("Save for plugin: %s with %s on object %s" % (p,f,obj))
                    f(self, obj)
            #end for
        #end for

        # Update version number since it is now saved with this cingVersion
        self.version = cingVersion
        # Save the project data to xml file
        if obj2XML(self, path = self.objectPath) != self:
            nTerror('Project.save: writing Project file "%s" failed', self.objectPath)
        #end if

        self.addHistory('Saved project')
        return True
    #end def

    def restore(self):
        """
        Restore the project: molecules and lists
        """
        if self.contentIsRestored:
            nTerror("Project.restore: content was already restored")
            return

        nTmessage('==> Restoring %s ... ', self)

        # Molecules
        for molName in self.moleculeNames:
            pathName = self.molecules.path(molName)
            mol = Molecule.open(pathName)
            if mol:
                mol.status = 'keep'
                self.appendMolecule(mol)
            #end if
        #end for

        # restore the lists
        for pl in [self.peaks, self.distances, self.dihedrals, self.rdcs, self.coplanars]:
            pl.restore()
        #end for

        # this is also done in runCingChecks, but should be here to assure restraint
        # partitioning and analysis for the external routines.
        # JFD TODO: why? the above is unclear to me now.
#        self.partitionRestraints()
#        self.analyzeRestraints()
#            l.criticize(self) now in criticize of validate plugin

        # Plugin registered functions
        for p in self.plugins.values():
            if p.isInstalled:
                for f, obj in p.restores:
#                    nTdebug("Restoring object [%s] with function [%s]" % (f,o))
                    f(self, obj)
                #end for
            #end if
        #end for
        #nTdebug("In classes#restore() doing runCingChecks without output generation.")
        self.runCingChecks(toFile=False)
        self.contentIsRestored = True
        self.updateProject()
    #end def

    def removeCcpnReferences(self):
        """To slim down the memory footprint; should allow garbage collection."""
        attributeToRemove = "ccpn"
        try:
            self.removeRecursivelyAttribute(attributeToRemove)
        except:
            nTerror("Failed removeCcpnReferences")

    def getSaveFrameAssign(self):
        """
        Return SSA saveframe embedded.
        Return None on error.
        """
        if not len(self.distances):
#            nTdebug("self.project.distances is empty.")
            return
        star_text = getDeepByKeysOrAttributes( self.distances, STEREO_ASSIGNMENT_CORRECTIONS_STAR_STR)
        if not star_text:
#            nTdebug("No SSA info embedded.")
            return
        starFile = File()
        if starFile.parse(text=star_text):
            nTerror( "In %s reading STAR text by STAR api" % getCallerName() )
            return
        if starFile.check_integrity():
            nTerror( "In %s STAR text failed integrity check." % getCallerName() )
            return
        sfList = starFile.getSaveFrames(category = "stereo_assignments")
        if not sfList or len(sfList) != 1:
            nTerror("In %s failed to get single saveframe but got list of: [%s]" % ( getCallerName(), sfList))
            return
        saveFrameAssign = sfList[0]
        return saveFrameAssign

    def getSsaTripletCounts(self):
        """
        Return counts tuple:
        Return None if not available.
        """
        saveFrameAssign = self.getSaveFrameAssign()
        if not saveFrameAssign:
#            nTdebug("No SSA saveframe embedded.")
            return
        tagTableAssignHeader = saveFrameAssign.tagtables[0]
        gI = tagTableAssignHeader.getInt
        tagNameList = """   Triplet_count
                            Swap_count
                            Deassign_count
        """.split()
        result = [ gI("_Stereo_assign_list."+tagName) for tagName in tagNameList]
        return tuple(result)

    def export(self):
        """Call export routines from the plugins to export the project
        """
        nTmessage('' + dots * 5 + '')
        nTmessage('==> Exporting %s', self)

        for p in self.plugins.values():
            for f, obj in p.exports:
                f(self, obj)
            #end for
        #end for
    #end def

    def updateProject(self):
        """Do all administrative things after actions
        """
        if self.molecule:
            self[self.molecule.name] = self.molecule
    #end def

    #-------------------------------------------------------------------------
    # actions Molecule
    #-------------------------------------------------------------------------
    def appendMolecule(self, molecule):
        """Append molecule to project.molecules; generate required internal directories.
        Return molecule or None on error.
        """
        if not molecule: 
            return None

        # Store names and references and append
        self.molecule = molecule
        self.molecules.append(molecule)
        self.createMoleculeDirectories(molecule)
        return self.molecule
    #end def

    def createMoleculeDirectories(self, molecule):
        """generate the required directories for export and HTML data."""
        # generate the required directories for export and HTML data
        for d in moleculeDirectories.values():
            self.mkdir(molecule.name, d)
        #end for
    #end def


    def newMolecule(self, name, sequenceFile, convention = LOOSE):
        """Return Molecule instance or None on error
        """
        uname = self.uniqueKey(name)
        molecule = Molecule.initialize(uname,
                                        path = sequenceFile,
                                        convention = convention,
                                        status = 'keep'
                                      )
        if not molecule:
            return None
        self.appendMolecule(molecule)

        self.addHistory(sprintf('Initialized molecule "%s" from "%s"', uname, sequenceFile))
        return molecule
    #end def
    #initializeMolecule = newMolecule # keep old name

    def restoreMolecule(self, name):
        """Restore molecule 'name'
        Return Molecule instance or None on error
        """
        pathName = self.molecules.path(name)
        mol = Molecule.open(pathName)

        if mol:
            mol.status = 'keep'
            self.appendMolecule(mol)
        #end if
        self.molecule = mol
        return mol
    #end def

    #-------------------------------------------------------------------------
    # Resonances stuff
    #-------------------------------------------------------------------------

    def mergeResonances(self, order = None, selection = None, append = True):
        """ Merge resonances for all the atoms
        """
        if not self.molecule:
            nTerror('Project.mergeResonances: No molecule defined\n')
            return
        #end if
        self.molecule.mergeResonances(order = order, selection = selection, append = append)
        nTdetail("==> Merged resonances")
    #end def

    def initResonances(self):
        """ Initialize resonances for all the atoms
        """
        if not self.molecule:
            nTerror('Project.initResonances: No molecule defined\n')
            return
        self.molecule.initResonances()
    #end def

    #-------------------------------------------------------------------------
    # actions other
    #-------------------------------------------------------------------------

    def addHistory(self, line, timeStamp = True):
        self.history(line, timeStamp)
    #end def

    def removeOlderLogs(self):
        """
        Remove all but last; because we're still writting to it.
        Match code to html#_generateLogsHtml
        """
        logsPattern = self.path(directories.logs, '*.txt')
        logFileList = glob(logsPattern)
        if not logFileList:
            nTmessage("No log files found")
            return
        logFileList.sort()
        for logFile in logFileList[:-1]:
            nTdebug("Removing older log file %s" % logFile)
            os.unlink(logFile)
    #end def

    def addLog(self):
        # Get first available new log file name like:
        # 2jsx.cing/2jsx/Cing/Logs/2jsx_2011-02-10_20-09-31.html
        date_stamp = getDateTimeStampForFileName()
        fn = "%s_%s.txt" % (self.name, date_stamp )
        logFilePath = self.path(directories.logs, fn)
        stream2 = open(logFilePath, 'w')
#        nTdebug("Opening %s" % logFilePath )
        addStreamnTmessageList(stream2)
        fprintf(stream2,header+'\n')
        fprintf(stream2,getStartMessage()+'\n')
#        nTdebug("Opened %s (should now show up in log too)" % logFilePath )
    #end def

    def closeLog(self):
#        nTdebug("Closing log" )
        if nTdebug.stream2 == None:
            nTdebug("Strange in project.removeLog stream2 was already closed.")
            return
        stream2 = nTdebug.stream2
        fprintf(stream2, getStopMessage(cing.starttime)+'\n')
        removeStreamnTmessageList()
#        nTdebug("Closed stream2 (should now NOT show up in log too)" )
    #end def

    def getLogFileNameList(self, latestListedFirst = True):
        """
        Returns a list of project log files sorted chronologically with latest first.
        NB the latest includes the current log.
        """
        logsDir = self.path(directories.logs)
        logFileList = glob1(logsDir, '*.txt')
        if logFileList:
            logFileList.sort()
            if latestListedFirst:
                logFileList.reverse() # Important to have latest on top because they might get long. Use p.removeOlderLogs() then.
            # end if
        # end if
#        l = len(logFileList)
#        nTdebug("Found %d logs: %s" % (l, str(logFileList)))
        return logFileList
#    def newPeakList( self, name, status='keep'):
#        """Dummy for compatibility
#        """
#        return self.peaks.new( name = name, status=status)
#    #end def

#    def appendPeakList( self, peaklist):
#        """Append peaklist; dummy for compatibility
#        """
#        self.peaks.append( peaklist )
#        return peaklist
#    #end def

    def analyzeRestraints(self):
        """
        Call analyze method for all restraint lists
        """
        nTdetail('==> Analyzing restraints')
        for drl in self.allRestraintLists():
            drl.analyze()
    #end def

    def allRestraintLists(self):
        """
        Return an NTlist instance with all restraints lists
        """
        return self.distances + self.dihedrals + self.rdcs

    def allRestraints(self, restraintLoL = None):
        """
        Return an RestraintList instance with all restraints
        parameter defaults to self.distances

        Sets a _parent attribute to find original list back like in NTtree.

        Return None for empty list because return needs to be specific
        and it can't when it's empty.

        Return True on error.
        """
        if restraintLoL == None:
            restraintLoL = self.distances
        if not restraintLoL:
            return None
        restraintList = restraintLoL[0]
        randomKey = getRandomKey()
        if restraintList.__CLASS__ == DRL_LEVEL:
            result = DistanceRestraintList('allRestraints_with_random_key_'+randomKey)
        elif restraintList.__CLASS__ == ACL_LEVEL:
            result = DihedralRestraintList('allRestraints_with_random_key_'+randomKey)
        elif restraintList.__CLASS__ == RDCL_LEVEL:
            result = RDCRestraintList('allRestraints_with_random_key_'+randomKey)

        for rL in restraintLoL:
            for r in rL:
                r._parent = rL
                result.append(r)
        return result

    def hasDistanceRestraints(self):
        for drList in self.distances:
            if len(drList):
                return True
        return False

    def header(self, mdots=dots):
        """Subclass header to generate using __CLASS__, name and dots.
        """
        return sprintf('%s %s: %s %s', dots, self.__CLASS__, self.name, mdots)
    #end def

    def __str__(self):
        return sprintf('<Project %s>', self.name)
    #end def

    def __repr__(self): # pylint: disable=W0221
        return str(self)

    def _list2string(self, theList, firstString, maxItems):
        result = firstString
        if len(theList) <= maxItems:
            result = result + str(theList)
        else:
            ls = len(firstString)
            result = result + '['
            for item in theList:
                result = result + sprintf('%s,\n%s ', item, ' '*ls)
            #end for
            result = result[:-1] + ']'
        #end if
        return result
    #end def

    def format(self): # pylint: disable=W0221
        result = self.header() + '\n' + \
                            'created:    %(created)s\n'
        result = result % self
        for firstString, item in [('molecules:  ', 'molecules'),
                                 ('peaks:      ', 'peaks'),
                                 ('distances:  ', 'distances'),
                                 ('dihedrals:  ', 'dihedrals'),
                                 ('rdcs:       ', 'rdcs'),
                                 ('coplanars:  ', 'coplanars'),
                                ]:
            result += self._list2string(self[item], firstString, 2) + '\n'
        #end for
        result += self.footer() # Project.footer defaults to NTdict 
        return result
    #end def

    def removeFromDisk(self):
        """Removes True on error. If no cing project is found on disk None (Success) will
        still be returned. Note that you should set the nosave option on the project
        before exiting."""
        pathString, _name = self.rootPath(self.name)
        if not os.path.exists(pathString):
#            nTdebug("No cing project is found at: " + pathString)
            return None
        nTmessage('Removing existing cing project "%s"', self)
        if rmtree(pathString):
            nTerror("Failed to remove existing cing project")
            return True

    # Convenience methods calls to validate.py.
    def initPDB(self, pdbFile, convention = IUPAC, name = None, nmodels = None, update = True, allowNonStandardResidue = True):
        """Initializes from a pdb file."""
        return initPDB(self, pdbFile, convention = convention, name = name, nmodels = nmodels, update = update, 
                       allowNonStandardResidue = allowNonStandardResidue)

    def importPDB(self, pdbFile, convention = IUPAC, nmodels = None):
        """Initializes from a pdb file."""
        return importPDB(self, pdbFile, convention = convention, nmodels = nmodels)

    def export2PDB(self, tmp = None):
        """Initializes from a pdb file."""
        return export2PDB(self, tmp = tmp)

    def validateAssignments(self):
        return validateAssignments(self)

    def validateDihedrals(self):
        return validateDihedrals(self)

    def validateDihedralCombinations(self):
        return validateDihedralCombinations(self)

    def validateModels(self):
        return validateModels(self)

    def validateRestraints(self, toFile = True):
        return validateRestraints(self, toFile = toFile)

    def criticizePeaks(self, toFile = True):
        return criticizePeaks(self, toFile = toFile)

    def fixStereoAssignments(self):
        return fixStereoAssignments(self)

    def summaryForProject(self, toFile = True):
        return summaryForProject(self, toFile = toFile)

    def criticize(self, toFile = True):
        return criticize(self, toFile = toFile)
    
    def decriticize(self):
        """
        Reset all Rog score objects in this project.
        
        Return True on error and None on success.
        """
    
#        nTdebug("Now in project#decriticize")
        
        self.rogScore.reset()
        # Project lists of lists
        projectLoL = []
        projectLoL += self.allRestraintLists() # distances, etc.        
        projectLoL += self.peaks     
        for projectList in projectLoL:
            if projectList.decriticize():
                nTerror("Failed to decriticize %s in project#decriticize" % str(projectList))
                return True
            #end if
        # end for
            
        if self.molecule:
            if self.molecule.decriticize():
                nTerror("Failed to decriticize %s in project#decriticize" % str(self.molecule))
                return True                
            #end if
        #end if
    #end def

    def validate(self, ranges = None, parseOnly = False, htmlOnly = False, doProcheck = True, doWhatif = True,
                 doWattos = True, doQueeny = True, doTalos = True,
                 filterVasco = False, filterTopViolations = False,
                 validateFastest = False, validateCingOnly = False, validateImageLess = False):
        return validate(self, ranges = ranges, parseOnly = parseOnly, htmlOnly = htmlOnly, doProcheck = doProcheck, doWhatif = doWhatif,
                        doWattos = doWattos, doQueeny = doQueeny, doTalos = doTalos,
                        filterVasco = filterVasco, filterTopViolations = filterTopViolations,
                        validateFastest = validateFastest, validateCingOnly = validateCingOnly, validateImageLess = validateImageLess)

    def runCingChecks(self, toFile=True, ranges = None):
        return runCingChecks(self, toFile=toFile, ranges = ranges)

    def checkForSaltbridges(self, cutoff = 0.5, toFile = False):
        return checkForSaltbridges(self, cutoff = cutoff, toFile = toFile)

    def partitionRestraints(self):
        return partitionRestraints(self)

    def setupHtml(self):
        return setupHtml(self)

    def renderHtml(self):
        return renderHtml(self)

    def generateHtml(self, htmlOnly = False):
        return generateHtml(self, htmlOnly = htmlOnly)

    def filterHighRestraintViol(self, restraintLoL = None, cutoff=2.0, maxRemove=3, toFile=True,
                                fileName = DISTANCE_RESTRAINT_LIST_HIGH_VIOLATIONS_FILTERED_STR):
        """
        Remove the largest violating distance restraints that meet a certain cutoff.
        Violation are not averaged over models for this purpose.
        Writes the removed restraints to a file.
    
        Return False on error.
    
        restraintLoL   Defaults to p.distances
        cutoff         Tolerance above which to delete.
        maxRemov       Maximum number of violations to remove. Largest violations will be removed.
        fileName       Enter file name (with path) for output of removed constraints.
        """
#        cutoff= 0.10 # DEFAULT: disabled
        nTmessage( "==> Doing filterHighDistanceViol with arguments: cutoff %s maxRemove %s" % ( cutoff, maxRemove))

        if restraintLoL == None:
            restraintLoL = self.distances

        if not restraintLoL:
#            nTdebug("No restraint list in filterHighDistanceViol.")
            return 1
        # end if
        # Get instance of DistanceRestraintList
        restraintList = self.allRestraints() # defaults to DRs
#        nTdebug("restraintList: %s" % restraintList)
        todoCount = len(restraintList)
        if not todoCount:
            nTdebug("No restraints in filterHighDistanceViol.")
            return 1
        # end if

        if not restraintList.analyze():
            nTerror("Failed to do restraintList.analyze()")
            return
        # end if
#        nTdebug("restraintList still: %s" % restraintList)
        restraintList.sort(byItem='violMax') # in place by default
        restraintList.reverse()
#        nTdebug("restraintList 3: %s" % restraintList)
        maxViol = restraintList[0].violMax
#        nTdebug("Highest violation is %.3f. (should be same as %.3f from list.)" % (maxViol, restraintList.violMax))
        toRemoveCount = min(maxRemove, todoCount)
#        restraintListToRemove = restraintList[:toRemoveCount] # slicing changes the data type from DistanceRestraintList to NTlist
        del restraintList[toRemoveCount:]
#        nTdebug("restraintListToRemove still: %s" % restraintList)

#        nTdebug("Checking %s restraints to remove." % toRemoveCount)

        toRemoveCount = 0
        for idx, r in enumerate( restraintList ):
#            nTdebug("Checking %s %s" % ( idx, r))
            if r.violMax >= cutoff:
#                nTdebug("toRemoveCount %s" % toRemoveCount)
                toRemoveCount = idx + 1 # First restraint to be maintained.
            else:
                break
        # end for

        if toRemoveCount == len(restraintList):
#            nTdebug("All restraints are high violating")
            pass
        else:
#            nTdebug("Restraints high violating found: %s" % toRemoveCount)
#            restraintListToRemove = restraintListToRemove[:toRemoveCount] # slice fails
            del restraintList[toRemoveCount:]
        if not toRemoveCount:
            if maxViol >= cutoff:
                nTerror('code bug in filterHighDistanceViol')
                return
            nTmessage("==> Nice, no restraints with violations above: %.3f (highest is: %.3f)" % (cutoff, maxViol))
            return 1

        if not restraintList.analyze():
            nTerror("Failed to do restraintList.analyze()")
            return
        # end if


        affectedRestraintLoL = NTlist()
        for r in restraintList:
            rL = r._parent
            rL.removeIfPresent(r)
            if affectedRestraintLoL.index(rL) < 0:
                affectedRestraintLoL.append(rL)
        for rL in affectedRestraintLoL:
            if not rL.analyze():
                nTerror("Failed to do restraintList.analyze()")
                return
            # end if
#            nTdebug("Left with: %s" % rL)
        #end for

        txt = restraintList.format(showAll=True)
        if toFile:
            fileName = self.path(self.molecule.name, self.moleculeDirectories.analysis, fileName)
            nTmessage( '==> %s, removed %s restraints and written to %s' % ( getCallerName(), len(restraintList), fileName))
            writeTextToFile(fileName, txt)
        else:
            nTmessage( "Removed distance restraints:\n" + txt)
        #end if
#        nTmessage("Finished filterHighDistanceViol")
        return True # success
    # end def
# end class


class XMLProjectHandler(XMLhandler):
    """Project handler class"""
    def __init__(self):
        XMLhandler.__init__(self, name = 'Project')
    #end def

    def handle(self, node):
        attrs = self.handleDictElements(node)
        if attrs == None: 
            return None
        result = Project(name = attrs['name'])

        # update the attrs values
        result.update(attrs)

        return result
    #end def
#end class

#register this handler
projecthandler = XMLProjectHandler()

class ProjectList(NTlist):
    """Generic Project list class: the list of lists of the project; e.g. molecules, peaks, ...
       Creates classDef instance when calling the new() method
    """
    def __init__(self, project, classDef, nameListKey, basePath):
        """
        nameList is key of project identifying list of names.
        This is done because of the update done in the Project.restore()
        method.
        """
        NTlist.__init__(self)
        self.project = project
        self.classDef = classDef
        self.nameListKey = nameListKey
        self.basePath = basePath # project(self.basePath % name) yields valid path
#        self.savePath = savePath
#        self.extention = extention
    #end def

    def path(self, name):
        #print '>>', self.basePath % name
        return self.project.path(self.basePath % name)

    def append(self, instance):  # pylint: disable=W0221
        """Append instance to self, storing instance.name in project
        """
        #print '>>',instance, self.project
        #print 'append>', instance.name,self.project.keys(),self.project.uniqueKey( instance.name )
        instance.name = self.project.uniqueKey(instance.name)
        NTlist.append(self, instance)
        # add reference in project
        self.project[instance.name] = instance
        instance.project = self.project
        instance.objectPath = self.path(instance.name)
        instance.projectList = self
    #end def

    def new(self, name, *args, **kwds):
        """Create a new classDef instance, append to self
        """
        uname = self.project.uniqueKey(name)
        instance = self.classDef(name = uname, *args, **kwds)
        self.append (instance)
        s = sprintf('New "%s" instance named "%s"', self.className(), uname)
        self.project.history(s)
#        nTdebug( s )
        #end if
        return instance
    #end def

    def save(self):
        """
        Save the lists of self to savePath/name.extension
        savePath relative to project

        Use SML methods

        Return a list of names
        """
        saved = NTlist()
        for myList in self:
#            nTdebug('myList is %s' % myList)
            if myList.status == 'keep':
                nTdetail('==> Saving %s to %s', myList, myList.objectPath)
                if self.classDef.SMLhandler.toFile(myList, myList.objectPath) == myList:
                    saved.append(myList.name)
            #end if
        #end for
        self.project[self.nameListKey] = saved
        # patch XML bug
        self.project.saveXML(self.nameListKey)
        return saved
    #end def

    def restore(self, names = None):
        """
        Use the SMLhandler instance of classDef to restore the list.
        if names=None;
            derive the list from the project[nameListKey]
        else:
            names is a list instance containing the names to of the lists to restore.
        """
        if not names:
            names = self.project[self.nameListKey]
        for name in names:
            path = self.path(name)
            myList = self.classDef.SMLhandler.fromFile(path, self.project) # Lists get append to project by SML routines
            if myList != None:
                nTdetail('==> Restored %s from %s', myList, path)
                myList.objectPath = path
            #end if
        #end for
    #end def

    def names(self, *patterns):
        "Return a list of names of self, optionally screen using pattern"
        names = NTlist()
        for myList in self:
            if len(patterns) == 0:
                names.append(myList.name)
            else:
                for p in patterns:
                    if matchString(myList.name, p):
                        names.append(myList.name)
                        break
                    #end if
                #end for
            #end if
        #end for
        return names

    def getListByName(self, name):
        "Return list by name or False"
        names = self.names()
        idx = names.index(name)
        if idx < 0:
            return
        return self[idx]

    def getListIdx(self, myList):
        "Return list by name or False"
        name = myList.name
        names = self.names()
        return names.index(name)

    def rename(self, oldName, newName):
        """
        Rename listitem oldName to newName
        return the listitem of None on error
        """
        if not oldName in self.names():
            nTerror('ProjectList.rename: old name "%s" not found', oldName)
            return None
        #end if
        if newName in self.project:
            nTerror('ProjectList.rename: new name "%s" already exists in %s', oldName, self.project)
            return None
        #end if
        myList = self.project[oldName]
        del(self.project[oldName])
        myList.name = newName
        self.project[newName] = myList
        myList.objectPath = self.path(myList.name)
        return myList
    #end def

    def getNextValidName(self, prefix = 'projectList_'):
        i = 1
        while i < 1000:
            posName = prefix + '%03d' % i
            if not posName in self.names():
                return posName
            i += 1
        nTerror("Failed to return ProjectList.getNextValidName")

    def delete(self, name):
        """
        Delete listitem name from the project
        return the listitem of None on error
        """
        if not name in self.names():
            nTerror('ProjectList.delete: name "%s" not found', name)
            return None
        #end if

        s = sprintf('Deleted instance named "%s"' % name)
        self.project.history(s)

        myList = self.project[name]
        del(self.project[name])
        NTlist.remove(self, myList)
        return myList
    #end def

    def className(self):
        """Return a string describing the class of lists of this project list
        """
        # eg. to extract from <class 'cing.classes.PeakList'>
        return str(self.classDef)[8:-2].split(".")[-1:][0]
    #end def
#end class ProjectList



# Routines to compare different Project instances this is therefore completely different from the ProjectList
# class where no such relation can be assumed.

class ProjectTree( NTtree ): # pylint: disable=R0904
    """
    Class to store multiple project instances
    Bit dirty as we use the NTtree class, but append Project instances (NTdict-derived) as children
    Emulate list like behavior by adding append method, 'id' and refs in dictionary: i.e. self[0] gives first entry.
    JFD TODO: perhaps give the 'Org' a parent status?
    """

    def __init__(self, name, root='.', ranges=None, groups = None, groupDefs = None, **kwds):
        NTtree.__init__(self, __CLASS__='ProjectTree', name=name, root=root, ranges=ranges, groups = groups, groupDefs = groupDefs, **kwds)
        self.entries = self._children
        self.next_id = 0
        self.moleculeMap = None
        self.mkdir()
    #end def

    def append(self, project ):
        if not project:
            return
        #self.entries.append(project)
        self.addChild2(project)
        project.id = self.next_id
        self.next_id += 1

        # add references
        self[project.id] = project
        self[project.name] = project
    #end

    def openProject(self, path, status='old'):
        """
        Open a project and append
        return project or None on error
        """
        project = Project.open( path, status=status)
        if not project:
            nTerror('ProjectTree.open: aborting')
            sys.exit(1)

        self.append( project )
        return project
    #end def

    def openCompleteTree( self ):
        """Open all project of specific target
        Return True on error.
        Added group name to Project instance.

        For an example of the groupDefs:
groupDefs = NTdict()
for i,g in enumerate(groups):
    groupDefs[g] = NTdict( id = i, color = colors[g], name=g, __FORMAT__ = 'Group %(name)-10s (%(id)2d), color %(color)s' )
        """
        if not self.groups:
            nTerror("Failed to find instance variable groups.")

        if not self.groupDefs:
            nTdebug("Will skip setting group defs.")

        for group in self.groups:
            entryId = self.name + group
            path = os.path.join(DATA_STR, entryId[1:3],  entryId, entryId + '.cing')
            nTdebug('opening %s', path)
            p = self.openProject( path )
            if not p:
                nTerror('Strange: no project, aborting')
                return True
            if p.molecule == None:
                nTerror('Strange: no molecule, aborting')
                return True
            p.target = self.name
            p.group  = group
            if getDeepByKeysOrAttributes( self.groupDefs, group):
                p.color = self.groupDefs[group].color
        #end for
        self.mapMolecules()
    #end def

    def _mapIt(self, p1, objects, p2):

        for c1 in objects:
            # find the corresponding object in p2
            ctuple1 = c1.nameTuple()
            ctuple2 = list(ctuple1)
            ctuple2[0] = p2.molecule.name
            ctuple2 = tuple(ctuple2)
            c2 = p2.decodeNameTuple(ctuple2)
            if c2==None:
                nTerror('ProjectTree._mapIt: error mapping %s to %s (derived from %s)', ctuple2, p2, p1)

            self.moleculeMap.setdefault(c1, NTdict())
            self.moleculeMap[c1][(p1.name,p1.molecule.name)] = c1
            self.moleculeMap[c1][(p2.name,p2.molecule.name)] = c2
            if c2 != None:
                self.moleculeMap.setdefault(c2, NTdict())
                self.moleculeMap[c2][(p1.name,p1.molecule.name)] = c1
                self.moleculeMap[c2][(p2.name,p2.molecule.name)] = c2
        #end for
    #end def

    def mapMolecules(self):
        """
        Make maps of chains and residues, between project instances
        """

        self.moleculeMap = None
        if len(self) == 0:
            return
        self.moleculeMap = NTdict()
        for p1 in self.entries:
            for p2 in self.entries:
                self._mapIt( p1, p1.molecule.allChains(), p2)
                self._mapIt( p1, p1.molecule.allResidues(), p2)
            #end for
        #end for
    #end def

    def path(self, *args):
        """
        Return a path relative to self.root/self.name
        """
        path = os.path.join(self.root, self.name, *args)
        return path

    def mkdir(self, *args):
        """Make a path relative a root of self.name
           Check for presence.
           Return the result
        """
        path = self.path(*args)
        if not os.path.exists(path):
#            nTdebug( "project.mkdir: %s" % dir )
            os.makedirs(path)
        return path
    #end def


    def format(self):  # pylint: disable=W0221
        header = sprintf('------------ ProjectTree %s ------------', self.name)
        footer = '-'*len(header)
        return sprintf("""%s
entries: %s
ranges:  %s
%s""", header, self.entries.zap('name').format('%r '), self.ranges, footer )
    #end def

    def __len__(self):
        return len(self.entries)
    #end def


    def getMolecules( self, project1, project2):
        '''Should be generalized to arbitrary sized arrays'''
        return project1.molecule, project2.molecule

    def calculatePairWisePhiPsiRmsd( self, project1, project2, ranges='auto' ):
        """
        Calculate a pairwise angular Phi,Psi rmsd between the models of mol1 and mol2
        return result NTlistOfLists, pairwise1, pairwise2, pairwise12 tuple
        """
        mol1, mol2 = self.getMolecules( project1, project2)

        fitResidues1 = mol1.setResiduesFromRanges(ranges)
        models1 = PhiPsiLists( mol1, fitResidues1 )

        fitResidues2 = mol2.setResiduesFromRanges(ranges)
        models2 = PhiPsiLists( mol2, fitResidues2 )

        #print '>', ranges, models1, models2

        l1 = len(models1)
        l2 = len(models2)
        if l1 == 0 or len(models1[0]) == 0 or l2 == 0 or len(models2[0]) == 0:
            nTdebug(">calculatePairWisePhiPsiRmsd> returning None, %s %s %s", l1, l2, ranges)
            return None, None, None, None

        models = models1 + models2

        result = NTlistOfLists(len(models), len(models), 0.0)

        #nTmessage( '==> Calculating dihedral pairwise rmsds' )

        for i in range(len(models)):
            for j in range(i+1, len(models)):
                #print '>>', i,j
                r = models[i].calculateRMSD( models[j] )
                if r == None:
                    nTdebug('calculatePairWisePhiPsiRmsd: error for %s and %s', models[i], models[j])
                    return None, None, None, None
                else:
                    result[i][j] = r
                    result[j][i] = r
            #end for
        #end for

        pairwise1 = NTlist()
        for i in range(l1):
            for j in range(i+1, l1):
                pairwise1.append(result[i][j])
    #            print '1>', i,j

        pairwise2 = NTlist()
        for i in range(l1, l1+l2):
            for j in range(i+1, l1+l2):
                pairwise2.append(result[i][j])
    #            print '2>', i,j

        pairwise12 = NTlist()
        for i in range(l1):
            for j in range(l1, l1+l2):
                pairwise12.append(result[i][j])

    #            print '12>', i,j
    #    print len(pairwise1), len(pairwise2), len(pairwise12)
        return (result,
            pairwise1.average2(fmt='%6.2f +- %5.2f'),
            pairwise2.average2(fmt='%6.2f +- %5.2f'),
            pairwise12.average2(fmt='%6.2f +- %5.2f')
        )
    #end def


    def calcPhiPsiRmsds( self, ranges='auto', relative = True ):

        n = len(self)

        rmsds = NTlistOfLists( n, n, NTvalue(NaN, NaN, fmt='%6.2f +- %5.2f' ) )
        for i in range(n):
            for j in range(i+1,n):
                #print self[i].group, self[j].group
                rmsds[i].group = self[i].group
                rmsds[j].group = self[j].group
                r, pw_i, pw_j, pw_ij = self.calculatePairWisePhiPsiRmsd( self[i], self[j], ranges = ranges)
                #print pw_i, pw_j, pw_ij
                if r != None:
                    if relative:
                        rmsds[i][i] = pw_i/(pw_i*pw_i).sqrt()
                        rmsds[j][j] = pw_j/(pw_j*pw_j).sqrt()
                        rmsds[i][j] = pw_ij/(pw_i*pw_j).sqrt()
                        rmsds[j][i] = rmsds[i][j]
                    else:
                        rmsds[i][i] = pw_i
                        rmsds[j][j] = pw_j
                        rmsds[i][j] = pw_ij
                        rmsds[j][i] = rmsds[i][j]
                    #end if
                #end if
            #end for
        #end for
        self.phiPsiRmsds = rmsds
        return rmsds
    #end def


    def calculatePairWiseRmsd( self, project1, project2, ranges=None ):
        """Calculate pairwise rmsd between mol1 and mol2
           Optionally use ranges for the fitting
        """
        mol1, mol2 = self.getMolecules( project1, project2)

        #Use ranges routines to define fitAtoms ed
        fitResidues1 = mol1.setResiduesFromRanges(ranges)
        mol1.selectFitAtoms( fitResidues1, backboneOnly=True, includeProtons = False )
        fitResidues2 = mol2.setResiduesFromRanges(ranges)
        mol2.selectFitAtoms( fitResidues2, backboneOnly=True, includeProtons = False )
    #    mol2.superpose( ranges )

        l1 = len(mol1.ensemble)
        l2 = len(mol2.ensemble)

        if (   l1 == 0 or len(mol1.ensemble[0].fitCoordinates) == 0
            or l2 == 0 or len(mol2.ensemble[0].fitCoordinates) == 0
            or len(mol1.ensemble[0].fitCoordinates) != len(mol2.ensemble[0].fitCoordinates)
        ):
            nTdebug( ">calculatePairWiseRmsd> returning None, %s %s %s" , l1, l2, ranges)
            return None, None, None, None


        models = mol1.ensemble + mol2.ensemble

        result = NTlistOfLists(len(models), len(models), 0.0)

        nTmessage('==> Calculating pairwise rmsds %s %s', mol1, mol2)

        for i in range(len(models)):
            for j in range(i+1, len(models)):
                result[i][j] = models[i].superpose( models[j] )
                result[j][i] = result[i][j]
            #end for
        #end for

        pairwise1 = NTlist()
        for i in range(l1):
            for j in range(i+1, l1):
                pairwise1.append(result[i][j])
    #            print '1>', i,j

        pairwise2 = NTlist()
        for i in range(l1, l1+l2):
            for j in range(i+1, l1+l2):
                pairwise2.append(result[i][j])
    #            print '2>', i,j

        pairwise12 = NTlist()
        for i in range(l1):
            for j in range(l1, l1+l2):
                pairwise12.append(result[i][j])

    #            print '12>', i,j
    #    print len(pairwise1), len(pairwise2), len(pairwise12)
        return (result, pairwise1.average2( fmt='%6.2f +- %5.2f'),
                        pairwise2.average2( fmt='%6.2f +- %5.2f'),
                        pairwise12.average2(fmt='%6.2f +- %5.2f') )
    #end def


    def calcRmsds( self, ranges='auto' ):

        n = len(self)

        rmsds = NTlistOfLists( n, n, NTvalue(NaN, NaN, fmt='%6.2f +- %5.2f' ) )
        for i in range(n):
            for j in range(i+1,n):
                #print self[i].group, self[j].group
                rmsds[i].group = self[i].group
                rmsds[j].group = self[j].group
                r, pw_i, pw_j, pw_ij = self.calculatePairWiseRmsd( self[i], self[j], ranges = ranges)
                #print pw_i, pw_j, pw_ij
                if r != None:
                    rmsds[i][i] = pw_i
                    rmsds[j][j] = pw_j
                    rmsds[i][j] = pw_ij
                    rmsds[j][i] = pw_ij
            #end for
        #end for
        self.rmsds = rmsds
        return rmsds
    #end def

    def printTitle(self, title, length, stream=sys.stdout ):
        line = '-'*length
        fprintf( stream, '%s\n  %s\n%s\n', line, title, line )
    #end def

    def printRmsds( self, title, rmsds, stream=sys.stdout ):
        n = len(rmsds)
        self.printTitle(title, 20*(n+1), stream)
        fprintf( stream, '%-20s%s\n','', rmsds.zap('group').format('  %-16s  '))
        for row in rmsds:
            fprintf( stream, '%-20s%s\n',  row.group, row.format('%-18s  '))
        fprintf( stream, '%s\n', '_'*20*(n+1))
    #end def

    def printScore( self, name, rogScore ):
        clist = rogScore.colorCommentList.zap(1)
        if len(clist) == 0: 
            clist.append('---')
        printf('%-20s%-10s %s\n', name, rogScore, clist[0])
        for c in clist[1:]:
            printf('%-20s%-10s %s\n', '', '', c)
    #end def

    def printOverallScores( self, stream = sys.stdout ):
        'Overall scores'

        n = len(self)
        if n == 0:
            return

        for p in self:
            p.cingSummary = p.getCingSummaryDict()
        # end for
        
        self.printTitle('Overall scores target '+self.name, 20*(n+1), stream)
    #    line = dots20*(n+1)
    #   fprintf( stream, '%s\n    Overall scores %s\n%s\n\n', line, self.name, line )
        fprintf( stream, '%-20s%s\n\n', 'Parameter', self.entries.zap('group').format('%-20s'))

        # CING scores
        for key in ['CING_red', 'CING_orange', 'CING_green']:
            fprintf( stream, '%-20s', key)
            for p in self:
                fprintf( stream, '%-20s', p.cingSummary[key])
            fprintf( stream, '\n')
        fprintf( stream, '\n')

        # Procheck scores
        for key in ['PC_core','PC_allowed','PC_generous','PC_disallowed','PC_gf']:
            fprintf( stream, '%-20s', key)
            for p in self:
                fprintf( stream, '%-20s', p.cingSummary[key])
            fprintf( stream, '\n')
        fprintf( stream, '\n')

        # Whatif scores
        for checkId in summaryCheckIdList:
            # Changed so no exceptions will be thrown in case the info is absent.
#            key = 'WI_'+self[0].molecule.runWhatif.cingCheckId(checkId)
            key = getDeepByKeysOrAttributes( self,0,'molecule','runWhatif', 'cingCheckId', 'checkId')
            if not key:
                nTmessage("Skipping values for unspecified checkId: %s" % checkId)
                continue
            key = 'WI_'+ key
            fprintf( stream, '%-20s', key)
            for p in self:
                value = getDeepByKeysOrAttributes(p, 'cingSummary', key)
                fprintf( stream, val2Str(value, '%-20s'))
            fprintf( stream, '\n')
        fprintf( stream, '\n')
    #end def

    def printRestraintScores( self, stream=sys.stdout ):

        n = len(self)
        if n == 0:
            return

    #    print dots20*(n+1)
    #    print ' Restraints target', self[0].target
    #    print dots20*(n+1)
    #    print

        hlen=40

        self.printTitle('Restraint scores target '+self.name, 110, stream)

        for p in self:
            header = sprintf('%s project %-20s %s', '-'*hlen, p.name, '-'*hlen)
            fprintf( stream,'%s\n', header)

            if len(p.dihedrals)+len(p.distances) == 0:
                fprintf( stream,'%s\n%s\n\n',   "  No restraints",'-'*len(header))
                continue


            if len( p.distances ) > 0:
                fprintf( stream,    '%-25s  %5s %5s %5s %5s %5s %5s   %-7s  %4s %4s %4s %4s    rmsd\n',
                       'DistanceRestraintLists', 'count', 'intra', 'seq', 'med', 'long', 'amb', 'ROG','low','>0.1','>0.3','>0.5'
                       )

                for r in p.distances:
                    fprintf( stream,'  %-23s %5d %5d %5d %5d %5d %5d   %-7s  %4d %4d %4d %4d    %5.3f +- %5.3f\n',
                            r.name,
                            len(r), len(r.intraResidual), len(r.sequential), len(r.mediumRange), len(r.longRange), len(r.ambiguous),
                            r.rogScore,
                            r.violCountLower, r.violCount1, r.violCount3, r.violCount5,
                            r.rmsdAv, r.rmsdSd
                           )
                fprintf(stream, "\n")
            #end if
            if len(p.dihedrals) > 0:
                fprintf( stream,    '%-25s %5s %5s %5s %5s %5s %5s   %-7s  %4s %4s %4s %4s    rmsd\n',
                       'DihedralRestraintsLists', 'count', '','','','','', 'ROG','','>1','>3','>5',
                       )
                for r in p.dihedrals:
                    fprintf( stream,'  %-23s %5s %5s %5s %5s %5s %5s   %-7s  %4s %4d %4d %4d    %5.3f +- %5.3f\n',
                            r.name,
                            len(r), '.', '.', '.', '.', '.',
                            r.rogScore, '.',
                            r.violCount1, r.violCount3, r.violCount5,
                            r.rmsdAv, r.rmsdSd
                           )
            #end if
            fprintf( stream,'%s\n\n',  '-'*len(header))
        #end for
    #end def

    def printResidueScores( self ):

        n = len(self)

        nTmessage( dots20*(n+1) )
        nTmessage( '    Residues' )
        nTmessage( dots20*(n+1) )
        p0 = self[0]
        for res in p0.molecule.allResidues():
            printf('%s %s %s\n',  '-'*5, res, '-'*5 )
    #        printf('%-20s%-10s %s\n', p0.name, res.rogScore, res.rogScore.colorCommentList.zap(1).format())
            self.printScore( p0.name, res.rogScore )
            # find the corresponding residues
            for p in self[1:]:
                nameTuple = (p.molecule.name, res.chain.name, res.resNum, None, None, None, INTERNAL)
                res2 = p.decodeNameTuple( nameTuple )
                if res2:
                    #printf('%-20s%-10s %s\n', p.name, res2.rogScore, res2.rogScore.colorCommentList.zap(1).format())
                    self.printScore( p.name, res2.rogScore )
                else:
                    printf('%-20s%-10s\n', p.name, 'Not found')
                #end if
            #end for
            nTmessage('')
        #end for
    #end def

    def test( self, stream=sys.stdout ):
        'Untested by JFD'
        # A hack to get residue specific results
        selectedResidues = self[0].molecule.setResiduesFromRanges('all')

        for res in selectedResidues:
            rmsds3 = self.calcPhiPsiRmsds( ranges=[res.resNum] )

            self.printRmsds('Relative Phi-Psi '+res.name, rmsds3, stream )
            res.phipsiRmsds = rmsds3
            for p in self.entries[1:]:
                val = getDeepByKeysOrAttributes(self, 'moleculeMap', res, p.name)
                if val == None:
                    nTerror('Setting phipsiRmsds residue %s project %s (mapping not found)', res.name, p)
                    continue
                val.phipsiRmsds = rmsds3
            #end for
        #end for
    #end def


    def test2(self):
        'Untested by JFD'
        ensemble = Ensemble()
        for p in self:
            closest = p.molecule.rmsd.closestToMean
            ensemble.append(p.molecule.ensemble[closest])
        #end for
        return ensemble
    #end def


    def runningRmsds( self ):
        selectedResidues = self[0].molecule.setResiduesFromRanges('all')
        for res in selectedResidues:
            prev = res.sibling(-1)
            next = res.sibling(1)
            if prev and next:
                res.runngRmsds = self.calcRmsds( [prev,res,next])
        #end for
    #end def

    def colorPhiPsiMacro( self, minValue=2.0, maxValue=4.0 ):

        fp = open( self.path('phipsi.mcr' ), 'w')

        fprintf(fp, 'Console off\n')
        fprintf(fp, 'ColorPar Property Min,blue, %7.3f\n', minValue)
        fprintf(fp, 'ColorPar Property Max,red,  %7.3f\n', maxValue)
        for p in self.entries[1:]:
            fprintf(fp, 'ColorRes object %d, Gray\n', p.id+1)
            fprintf(fp, 'PropRes object %d, -999\n', p.id+1)
            for res in p.molecule.allResidues():
                if res.has_key('phipsiRmsds'):
                    if not isNaN(res.phipsiRmsds[0][p.id].value):
                        fprintf( fp, 'PropRes object %d residue %d, %7.3f\n', p.id+1, res.resNum, res.phipsiRmsds[0][p.id].value)
                #end if
            #end for
            fprintf(fp, 'ColorObject %d, property\n', p.id+1)

        #end for
        fprintf(fp, 'Console off\n')
        fp.close()
    #end def

    def loadPDBmacro( self ):


        fp = open( self.path('loadPDB.mcr' ), 'w')

        fprintf(fp, 'Console off\n')
        for p in self.entries:
            #fprintf(fp, 'loadPDB %s\n', os.path.abspath(self.path(p.name+'.pdb')))
            fprintf(fp, 'loadPDB %s,Center=No\n', self.path(p.name+'.pdb'))
        #end for
        fprintf(fp, 'Style Ribbon\n')
        fprintf(fp, 'macro %s\n', self.path('colorPDB.mcr'))
        fprintf(fp, 'Console on\n')
        fp.close()
    #end def

    def colorPDBmacro( self ):


        fp = open( self.path('colorPDB.mcr' ), 'w')

        fprintf(fp, 'Console off\n')
        for p in self.entries:
            #fprintf(fp, 'loadPDB %s\n', os.path.abspath(self.path(p.name+'.pdb')))
            selectedResidues = p.molecule.setResiduesFromRanges(p.molecule.ranges)
            #print '>>', selectedResidues
            if p.has_key('color'):
                fprintf(fp, 'ColorObject %d, %d\n', p.id+1, p.color)
                for res in p.molecule.allResidues():
                    #print res,
                    if res in selectedResidues:
                        pass
                    else:
                        fprintf(fp, 'ColorRes object %d residue %d, grey\n', p.id+1, res.resNum)
                    #end if
                #end for
            #end if
        #end for
        fprintf(fp, 'Console on\n')
        fp.close()
    #end def

    def rogMacro( self ):

        stream = open( self.path('ROG.mcr' ), 'w')

        fprintf(stream, 'Console off\n')
        fprintf(stream, 'ColorRes  All, Gray\n')

        yasaraColorDict = dict(green = 240, orange = 150, red = 120)

        for p in self:
            selectedResidues = p.molecule.setResiduesFromRanges(p.molecule.ranges)
            for res in p.molecule.allResidues():
                if res in selectedResidues:
                    pass
                else:
                    fprintf(stream, 'ColorRes object %d residue %d, %s\n', p.id+1, res.resNum, yasaraColorDict[res.rogScore.colorLabel])
        #end for
        fprintf(stream, 'Console on\n')
    #end def

    def mkYasaraByResidueMacro(self, keys,
                                minValue = 0.0, maxValue = 1.0, reverseColorScheme = False,
                                path = None ):

        nTdebug('mkYasaraByResidueMacro: keys: %s, minValue: %s maxValue: %s', keys, minValue, maxValue)
        if path==None:
            stream = sys.stdout
        else:
            stream = open( path, 'w')
        #end if

        fprintf(stream, 'Console off\n')
        fprintf(stream, 'ColorRes All, Gray\n')
        fprintf(stream, 'PropRes All, -999\n')
        if reverseColorScheme:
            fprintf(stream, 'ColorPar Property Min,red,%f\n', minValue)
            fprintf(stream, 'ColorPar Property Max,blue,%f\n', maxValue)
        else:
            fprintf(stream, 'ColorPar Property Min,blue,%f\n', minValue)
            fprintf(stream, 'ColorPar Property Max,red,%f\n', maxValue)

        for p in self:
            for res in p.molecule.allResidues():
                value = getDeepByKeysOrAttributes(res, *keys)
        #        if res.has_key(property) and res[property] != None and not isNaN(res[property]):
                if value != None and not isNaN(value):
                    fprintf(stream, 'PropRes object %d Residue %d, %.4f\n', p.id+1, res.resNum, value)
            #end for

        fprintf(stream, 'ColorAll Property\n')
        fprintf(stream, 'Console on\n')

        if path:
            stream.close()
    #end def

    def qShiftMacro( self ):
        self.mkYasaraByResidueMacro( ['Qshift', 'backbone'],
                               minValue = QshiftMinValue,
                               maxValue = QshiftMaxValue,
                               reverseColorScheme = QshiftReverseColorScheme,
                               path = self.path('Qshift.mcr') )

    def copyFiles2Project( self ):
        """Copy the file in the project instances directory to each individual project
        """
        for p in self:
            source = self.path('*')
            destination = p.validationPath('Cing','CASD-NMR')
            #print '>>', source, destination
            copydir(source,destination)
    #end def

    def generatePDBfiles( self ):

        # Get the closestToMean models, superpose, export to PDB file
        closestToMean = NTlist()
        for p in self.entries[0:3]:
            cl = p.molecule.rmsd.closestToMean
            #print p.molecule.ensemble[cl].format()
            closestToMean.append( p.molecule.ensemble[cl] )

        for m in closestToMean[1:]:
            #print m.format()
            _r = m.superpose(closestToMean[0])
            #print '>', m.format()
            #print '>', r
        # Export
        for p in self:
            cl = p.molecule.rmsd.closestToMean
            #print 'saving model>', p.molecule.ensemble[cl].format()
#            p.molecule.toPDBfile( self.path(p.name+'.pdb'), model=cl)
            p.molecule.toPDB( self.path(p.name+'.pdb'), model=cl)

        return closestToMean
    #end def

    def getRanges( self, cutoff = 1.7 ):
        """
        Get the ranges from phi, psi order parameters using all members.
        As suggested by Alexandre in CASD-NMR meeting.
        """
        resList1 = NTlist()
        resList2 = NTlist()
        for res in self.entries[0].molecule.allResidues():
            phi = NTlist() # list for all phi values
            psi = NTlist() # list for all psi values
            #print '>>>', res
            if res.has_key('PHI') and res.has_key('PSI'):

                for p in self:
                    if self.moleculeMap.has_key(res) and self.moleculeMap[res].has_key((p.name, p.molecule.name)):
                        currentRes = self.moleculeMap[res][(p.name, p.molecule.name)]
                        #print p,currentRes
                        if currentRes.has_key('PHI'):
                            phi.append(*currentRes['PHI'])
                        if currentRes.has_key('PSI'):
                            psi.append(*currentRes['PSI'])
                    #end if
                #end for
                phi.cAverage()
                psi.cAverage()

                use1 = 0
                if (2.0 - res.PHI.cv - res.PSI.cv > cutoff): 
                    use1 = 1
                use2 = 0
                if (2.0 - phi.cv - psi.cv > cutoff): 
                    use2 = 1
                #printf('%-35s %-35s  %6.2f  %1d     %6.2f %6.2f   %6.2f  %1d     %2d\n',
                #      res.PHI, res.PSI, 2.0 - res.PHI.cv - res.PSI.cv, use1,
                #      phi.cv, psi.cv, 2.0 - phi.cv - psi.cv, use2, use1-use2
                #     )
                if use1:
                    resList1.append(res.resNum)
                if use2:
                    resList2.append(res.resNum)
            #end if
        #end for
        return list2asci(resList1), list2asci(resList2)
    #end def

#end class

class CircularVector( NTvector ):
    """
    Circular Distance vector class
    """
    def distanceSquared( self, other, period=360.0 ):
        n = len(self)
        if n != len(other):
            return None

        d = 0.0
        for i in range(n):
            delta = self[i]-other[i]
            fdelta = math.fabs( delta )

            if math.fabs(delta+period) < fdelta:
                d += (delta+period)*(delta+period)
            elif math.fabs(delta-period) < fdelta:
                d += (delta-period)*(delta-period)
            else:
                d += (delta)*(delta)
            #end if
        #end for
        return d
    #end def

    def distance( self, other, period=360.0 ):  # pylint: disable=W0221
        return math.sqrt( self.distanceSquared( other, period ) )
    #end def
#end class

class PhiPsiModelList( NTlist ):
    """
    Class to contain phi,psi values per model as CircularVector instances
    """

    def __init__(self, name, index ):
        NTlist.__init__(self)
        self.name = name
        self.index = index
    #end def

    def append( self, *dihedrals ):
        c = CircularVector( *dihedrals )
        NTlist.append(self, c)
    #end def

    def calculateRMSD( self, other ):
        n = len(self)
        if n != len(other) or n==0:
            return -1.0

        rmsd = 0.0
        for i in range(n):
            rmsd += self[i].distanceSquared(other[i], period=360.0)
            #print '>',i, self[i].residue, other[i].residue, rmsd
        return math.sqrt( rmsd/n )
    #end def

    def __str__(self):
        return sprintf('<PhiPsiModelList %s (%d)>', self.name, len(self))
    #end def
#end class

class PhiPsiLists( NTlist ):
    """
    Class to contain modelCount PhiPsiModelList instances
    """

    def __init__(self, molecule, residueList):
        NTlist.__init__( self )
        self.molecule     = molecule

        for i in range(0,molecule.modelCount):
            mName = sprintf('%s_model_%d', molecule.name, i)
            m = PhiPsiModelList(mName, i )
            self.append( m )
        #end for

        # Assemble the phi,psi of the models from residueList
        for res in residueList:
#            if res and res.has_key('PHI') and res.has_key('PSI'):
            if res and res.has_key('PHI') and res.has_key('PSI') and res.has_key('Cb4N') and res.has_key('Cb4C'):
                for i in range(0,molecule.modelCount):
                    #print '>>', res, i,molecule.modelCount,len(res.PHI),len(res.PSI),len(res.Cb4N),len(res.Cb4C)
#                    self[i].append(res.PHI[i],res.PSI[i])
                    self[i].append(res.PHI[i],res.PSI[i],res.Cb4N[i],res.Cb4C[i])
                    self[i].last().residue = res
                #end for
            #end if
        #end for
    #end def

    def __str__(self):
        return sprintf('<PhiPsiLists (%d)>', len(self))
    #end def
#end class

#
#
PeakIndex = 0
class Peak(NTdict, Lister):
    """Peak class:
       Peaks point to resonances
       Resonances point to atoms
       by GV 2007 07 23: added hasHeight, hasVolume attributes to the class
          GV 2007 28 09: Moved from molecule.py to project.py
          GV 19 Jun 08: PeakIndex starts at 0
          GV 19 Jun 08: change height, volume to NTvalue classes
          GV 19 Jun 08: changed hasHeight and hasVolume to methods
    """

    HEIGHT_VOLUME_FORMAT = '%9.2e +- %8.1e'
    HEIGHT_VOLUME_FORMAT2 = '%9.2e'

    def __init__(self,
                  dimension,
                  positions = None,
                  height = NaN, heightError = NaN,
                  volume = NaN, volumeError = NaN,
                  resonances = None,
                  **kwds
                ):

        NTdict.__init__(self, __CLASS__ = 'Peak', **kwds)
        Lister.__init__(self)
#       several external programs need an index
        # Using the global statement pylint: disable=W0603
        global PeakIndex
        self.peakIndex = PeakIndex
        PeakIndex += 1

        self.__FORMAT__ = self.header() + '\n' + \
                           'dimension:  %(dimension)dD\n' + \
                           'positions:  %(positions)s\n' + \
                           'height:     %(height)s\n' + \
                           'volume:     %(volume)s\n' + \
                           'resonances: %(resonances)s\n' + \
                           'rogScore:   %(rogScore)s\n' + \
                           self.footer()

        self.dimension = dimension

        # Copy the positions and resonances argument to assure they become
        # NTlist objects
        if resonances:
            self.resonances = NTlist(*resonances)
        else:
            self.resonances = nTfill(None, dimension)
        #end if

        if positions:
            self.positions = NTlist(*positions)
        else:
            self.positions = nTfill(NaN, dimension)
        #end if

        self.height = NTvalue(height, heightError, Peak.HEIGHT_VOLUME_FORMAT, Peak.HEIGHT_VOLUME_FORMAT2)
        self.volume = NTvalue(volume, volumeError, Peak.HEIGHT_VOLUME_FORMAT, Peak.HEIGHT_VOLUME_FORMAT2)

        self.rogScore = ROGscore()
    #end def

    def decriticize(self):
#        nTdebug("Now in Peak#decriticize")
        self.rogScore.reset()
    #end def

    def isAssigned(self, axis):
        if axis >= self.dimension: 
            return False
        if axis >= len(self.resonances): 
            return False
        if self.resonances[axis] == None: 
            return False
        if self.resonances[axis].atom == None: 
            return False
        return True
    #end def

    def getAssignment(self, axis):
        """Return atom instances in case of an assignment or None
        """
        if self.isAssigned(axis):
            return self.resonances[axis].atom
        #end if
        return None
    #end def

    def hasHeight(self):
        return not isNaN(self.height.value)

    def hasVolume(self):
        return not isNaN(self.volume.value)

    def __str__(self):
        #print '>>', self.resonances.zap('atom')
        return sprintf('Peak %4d (%dD)  [%s]   height: %s   volume: %s    Assiged to: %s',
                         self.peakIndex, self.dimension,
                         self.positions.format('%8.2f'),
                         self.height, self.volume,
                         self.resonances.zap('atom').format('%-20s')
                       )
    #end def

    def header(self, mdots = dots):
        """Subclass header to generate using __CLASS__, peakIndex and dots.
        """
        return sprintf('%s %s: %d %s', mdots, self.__CLASS__, self.peakIndex, mdots)
    #end def
#end class


class PeakList(NTlist, ProjectListMember):

    def __init__(self, name, status = 'keep'):
        NTlist.__init__(self)
        ProjectListMember.__init__(self)
        self.name = name
        self.status = status
        self.listIndex = -1 # list is not appended to anything yet
    #end def

    def minMaxDimension(self):
        """Return a tuple of the min and max of the spectral dimensions from all peaks
        usually min == max but not guaranteed.
        Will return (None,None) for empty lists
        """
        minD = None
        maxD = None
        for peak in self:
            minD = min(peak.dimension, minD)
            maxD = max(peak.dimension, maxD)
        return (minD, maxD)

    def peakFromAtoms(self, atoms, onlyAssigned = True):
        """Append a new Peak based on atoms list
           Return Peak instance, or None
        """
        if (None not in atoms):     # None value in atoms indicates atom not present
            if (onlyAssigned and (False in map(Atom.isAssigned, atoms))):
                pass                # Check atom assignments, if only assigned and not all assignments
                                    # present we skip it
            else:                   # all other cases we add a peak
                s = []
                r = []
                for a in atoms:
                    s.append(a.shift())
                    r.append(a.resonances())
                #end for
                peak = Peak(dimension = len(atoms),
                             positions = s,
                             resonances = r
                           )
                self.append(peak)
                return peak
            #end if
        #end if
        return None
    #end def

    def __str__(self):
        return sprintf('<PeakList "%s" (%s,%d)>', self.name, self.status, len(self))
    #end def

    def __repr__(self):
        return str(self)
    #end def

    def format(self):  # pylint: disable=W0221
        s = sprintf('%s PeakList "%s" (%s,%d,%s) %s\n', dots, self.name, self.status, len(self), self.rogScore, dots)
        for peak in self:
            s = s + str(peak) + '\n'
        #end for
        return s
    #end def

    def save(self, path = None):
        """
        Create a SML file
        Return self or None on error
        """
        if not path: 
            path = self.objectPath
        if self.SMLhandler.toFile(self, path) != self:
            nTerror('PeakList.save: failed creating "%s"', path)
            return None
        #end if

        nTdetail('==> Saved %s to "%s"', self, path)
        return self
    #end def

    def rename(self, newName):
        return self.projectList.rename(self.name, newName)
    #end def
#end class


def getAtomsFromAtomPairs(atomPairs):
    result = []
    for atomPair in atomPairs:
        for atom in atomPair:
            for real_atm in atom.realAtoms():
                result.append(real_atm)
    return result

class Restraint(NTdict):
    """
    Super class for DistanceRestraint etc.
    On initialization the atom pairs will be tested for validity and reported in self.isValid
    """
    def __init__(self, lower, upper, **kwds):
        NTdict.__init__(self, lower = lower,
                              upper = upper,
                              **kwds
                       )
        self.__CLASS__ = None     # Set by sub class.
        self.id = -1       # Undefined index number
        self.violations = None     # list with violations for each model, None indicates no analysis done
        self.violCount1 = 0        # Number of violations over 1 degree (0.1A)
        self.violCount3 = 0        # Number of violations over 3 degrees (0.3A)
        self.violCount5 = 0        # Number of violations over 5 degrees (0.5A)
        self.violMax = 0.0      # Maximum violation
        self.violAv = 0.0      # Average violation
        self.violSd = 0.0      # Sd of violations
        self.isValid = True
        self.rogScore = ROGscore()
    #end def
    def __str__(self):
        return '<%s %d>' % (self.__CLASS__, self.id)
    #end def
    
    def decriticize(self):
#        nTdebug("Now in Restraint#%s" % getCallerName())
        self.rogScore.reset()
    #end def
    
    def getModelCount(self):
        """Iterate over the atoms until an atom is found that returns not a None for getModelCount.
        Return 0 if it doesn't have any models or None on error.
        """
        modelCount = None

        if self.__CLASS__ == DR_LEVEL or self.__CLASS__ == RDC_LEVEL:
#            lAtom  = len(self.atomPairs)
            for atompair in self.atomPairs:
                for atom in atompair:
                    if not isinstance(atom, Atom):
                        nTerror("Failed to get atom in atom pair in %s for %s" % (getCallerName(), self))
                        return None
                    modelCount = atom.getModelCount()
                    if modelCount != None:
                        return modelCount
        else:
#            lAtom  = len(self.atoms)
            for atom in self.atoms:
                modelCount = atom.getModelCount()
                if modelCount != None:
                    return modelCount
#        nTwarning("%s.getModelCount returned None for all %d atom(pair)s; giving up." % (self.__CLASS__, lAtom))
        return None
    #end def

    def isValidForAquaExport(self):
        """Determine if the restraint can be exported to Aqua."""
        nTerror("Restraint.isValidForAquaExport needs to be overriden.")
    #end def

    def listViolatingModels(self, cutoff = 0.3):
        """
        Examine for violations larger then cutoff, return list of violating models or None on error
        Requires violations attribute (obtained with calculateAverage method.
        """
        if not self.has_key('violations'):
            return None

        violatingModels = NTlist()
        for i in range(len(self.violations)):
            if (math.fabs(self.violations[i]) > cutoff):
                violatingModels.append(i)
            #end if
        #end for

        return violatingModels
    #end def
# end class Restraint


class DistanceRestraint(Restraint):
    """DistanceRestraint class:
       atomPairs: list of (atom_1,atom_2) tuples,
       lower and upper bounds.
    """
    STATUS_SIMPLIFIED = 'simplified'
    STATUS_NOT_SIMPLIFIED = 'not simplified'
    STATUS_DEASSIGNED = 'deassigned'
    STATUS_NOT_DEASSIGNED = 'not deassigned'
    STATUS_REMOVED_DUPLICATE = 'removed duplicate'
    STATUS_NOT_REMOVED_DUPLICATE = 'not removed duplicate'
    # The maximum number of atom pairs expected before it will be treated normally.
    # This is to prevent HADDOCK AIR restraints to slow CING to a crawl as per issue 324. 
    MAX_ATOM_PAIRS_EXPECTED = 1000

#    def __init__( self, atomPairs=[], lower=0.0, upper=0.0, **kwds ):
    def __init__(self, atomPairs = NTlist(), lower = None, upper = None, **kwds):
        Restraint.__init__(self, lower = lower, upper = upper, **kwds)
        self.__CLASS__ = DR_LEVEL
        self.atomPairs = NTlist()
        self.distances = None     # list with distances for each model; None: not yet defined
        self.av = None      # Average distance
        self.sd = None      # sd on distance
        self.min = None      # Minimum distance
        self.max = None      # Max distance
        self.violCountLower = 0    # Lower-bound violations
        self.violUpperMax = 0.0    # Max violation over upper bound
        self.violLowerMax = 0.0    # Max violation over lower bound
        
        self.duplicates = NTlist() # NTlist instance with DistanceRestraint instances considered duplicates; TODO: check this code
        self.error = False    # Indicates if an error was encountered when analyzing restraint

        for pair in atomPairs:
            if self.appendPair(pair):
#                nTdebug('resetting self.isValid')
                self.isValid = False
                return
        #end for
    #end def

    def isValidForAquaExport(self):
        """Determine if the restraint can be exported to Aqua.
        Simplified to checking if all partners have at least one assigned atom.

        E.g. of a valid self.atomPairs
        [ [ HA ] [ HB,HC ],
          [ HA ] [ HD ] ]
        """
        if not self.atomPairs:
#            nTdebug("Failed to find any atom pair in %s" % self)
            return False
        for _i, atomPair in enumerate(self.atomPairs):
            if not atomPair: # eg [ HA ] [ HB,HC ]
#                nTdebug("Failed to find any atomList (should always be 2 present) in atompair %d of:\n%s" % (i,self))
                return False
            for _j, atomList in enumerate(atomPair):
                if not atomList: # eg [ HB,HC ]
#                    nTdebug("Failed to find any atom in atomList (%d,%d) of %s" % (i,j,self))
                    return False
                for _k, atom in enumerate(atomList):
                    if not atom: # eg HB
#                        nTdebug("Failed to find atom in atomList (%d,%d,%d) of %s" % (i,j,k,self))
                        return False
        return True
    #end def


    def criticize(self, project):
        """Only the self violations,violMax and violSd needs to be set before calling this routine"""
        self.rogScore.reset()
#        nTdebug( '%s' % self )
        if (project.valSets.DR_MAXALL_BAD != None) and (self.violMax >= project.valSets.DR_MAXALL_BAD):
            comment = 'violMax: %7.2f' % self.violMax
#            nTdebug(comment)
            self.rogScore.setMaxColor(COLOR_RED, comment)
        elif (project.valSets.DR_MAXALL_POOR != None) and (self.violMax >= project.valSets.DR_MAXALL_POOR):
            comment = 'violMax: %7.2f' % self.violMax
#            nTdebug(comment)
            self.rogScore.setMaxColor(COLOR_ORANGE, comment)
        if (project.valSets.DR_THRESHOLD_OVER_POOR != None) and (project.valSets.DR_THRESHOLD_FRAC_POOR != None):
            fractionAbove = getFractionAbove(self.violations, project.valSets.DR_THRESHOLD_OVER_POOR)
            if fractionAbove >= project.valSets.DR_THRESHOLD_FRAC_POOR:
                comment = 'fractionAbove: %7.2f' % fractionAbove
    #            nTdebug(comment)
                self.rogScore.setMaxColor(COLOR_ORANGE, comment)
        if (project.valSets.DR_THRESHOLD_OVER_BAD != None) and (project.valSets.DR_THRESHOLD_FRAC_BAD != None):
            fractionAbove = getFractionAbove(self.violations, project.valSets.DR_THRESHOLD_OVER_BAD)
            if fractionAbove >= project.valSets.DR_THRESHOLD_FRAC_BAD:
                comment = 'fractionAbove: %7.2f' % fractionAbove
    #            nTdebug(comment)
                self.rogScore.setMaxColor(COLOR_RED, comment)
        if (project.valSets.DR_RMSALL_BAD != None) and (self.violSd >= project.valSets.DR_RMSALL_BAD):
            comment = 'violSd: %7.2f' % self.violSd
#            nTdebug(comment)
            self.rogScore.setMaxColor(COLOR_RED, comment)
        elif (project.valSets.DR_RMSALL_POOR != None) and (self.violSd >= project.valSets.DR_RMSALL_POOR):
            comment = 'violSd: %7.2f' % self.violSd
#            nTdebug(comment)
            self.rogScore.setMaxColor(COLOR_ORANGE, comment)



        if project.valSets.FLAG_MISSING_COOR:
            #modelCount = self.getModelCount()
            for atm1, atm2 in self.atomPairs:
                atms1 = atm1.realAtoms()
                atms2 = atm2.realAtoms()
                for a in atms1 + atms2:
                    if a and a.hasMissingCoordinates(): # gv has mase this into a method because the getModelCount()
                    # can crash when reading back NRG dataset because of their
                    # incompleteness
                    #if len(a.coordinates) < modelCount:
                        msg = "Missing coordinates (%s)" % a.toString()
#                        nTdebug(msg)
                        self.rogScore.setMaxColor(COLOR_RED, msg)
                    #end if
                #end for
            #end for
        # end if
    #end def

    def simplify(self):
        """
        Return True on error.

        Routine is iterative itself because both sides may contain ambis to collapse and remove.
        """
        atomPairCount = len(self.atomPairs)        
        if atomPairCount > DistanceRestraint.MAX_ATOM_PAIRS_EXPECTED: # Happens for entry 2bgf as per issue 324.
#            nTdebug('In %s; skipping restraint %s with %s atom pairs which is more than the maximum expected: %s' % (
#                getCallerName(), self, atomPairCount, DistanceRestraint.MAX_ATOM_PAIRS_EXPECTED))
            return self.STATUS_NOT_SIMPLIFIED
        # end if
        
        statusOverall = self.STATUS_NOT_SIMPLIFIED
        status = self.STATUS_SIMPLIFIED
        while status == self.STATUS_SIMPLIFIED:
            status = self.simplifyForFc()
            if status == self.STATUS_SIMPLIFIED:
                statusOverall = status
#                nTdebug("simplified restraint %s" % self)
            elif status == self.STATUS_NOT_SIMPLIFIED:
                pass
#                nTdebug("not simplified restraint %s" % self)
            else:
                nTerror("Encountered an error simplifying restraint %s" % self)
                return True
            # end if
        # end while

        if self.removeDuplicateAtomPairs():
            nTerror("Encountered an error in removeDuplicateAtomPairs restraint %s" % self)
            return True
        # end if
        while self.removeDuplicateAtomPairs2() == self.STATUS_REMOVED_DUPLICATE:
            pass
#            nTdebug("Removed duplicate")
        # end if
        return statusOverall
    #end def


    def deassignStereospecificity(self):
        """If the restraint involves a stereo specifically assignable atom then expand the list to include all
        getStereoPartner's. Of course if the restraint is between partners then the restraint
        becomes useless but will be generated. E.g. Gly HA2 to HA3 will become Gly QA to QA.

        LEU MD1 -> QD
        PHE QD  -> QR (which is a problem for the xplor conversion as of yet.)
        Return None on error.
        STATUS_DEASSIGNED = 'deassigned'
        STATUS_NOT_DEASSIGNED = 'not deassigned'
        """

        nTdebug('Starting 123 deassignStereospecificity for %s' % ( self ) )
        isDeassigned = False

        for atomPairIdx in range(len(self.atomPairs)):
            atomPair = self.atomPairs[atomPairIdx]
            for atomIdx in range(2):
                atomOrg = atomPair[atomIdx]
                pseudoAtom = atomOrg.pseudoAtom()
                if not pseudoAtom:
                    continue
                # Deal with immutable tuples.
                if atomIdx == 0:
                    newTuple = ( pseudoAtom, atomPair[1])
                else:
                    newTuple = ( atomPair[0], pseudoAtom )
                atomPair = newTuple
                self.atomPairs[atomPairIdx] = atomPair
                isDeassigned = True
                nTdebug('Replaced %s by %s' % ( atomOrg, atomPair[atomIdx] ) )
        if isDeassigned:
            return self.STATUS_DEASSIGNED
        return self.STATUS_NOT_DEASSIGNED

    def simplifyForFc(self):
        """FC likes to split Val QQG in QG1 and 2 making it appear to be an ambiguous OR typed XPLOR restraint
        were it is not really one. Undone here.

        Returns:
        None                     error.
        STATUS_NOT_SIMPLIFIED    no simplifications done
        STATUS_SIMPLIFIED        simplifications done

        In the code:

        j stands for the index of the atomPair of the outer loop that might be removed upon simplification.
        i stands for the index of the atomPair of the inner loop that is compared to and that might be modified to include atoms from atomPair j.
        """
#        nTdebug('Starting simplifyForFc for\n:%r' % ( self ) )
        atomPairIdxJ = len(self.atomPairs) # starting from the end.
        while atomPairIdxJ > 1:
            atomPairIdxJ -= 1
            atomPairJ = self.atomPairs[atomPairIdxJ]
            atomPairJset = set(atomPairJ) # Important to use api of unsorted atoms in pair (left right will not matter)
            atom0J = atomPairJ[0]
            atom1J = atomPairJ[1]

#            nTdebug('For atomPairIdxJ %d using atoms J %s and %s' % ( atomPairIdxJ, atom0J, atom1J) )
            # speed up check on J as an early abort clause.
            if not (atom0J.hasPseudoAtom() or atom1J.hasPseudoAtom()):
                if not (atom0J.getPseudoOfPseudoAtom() or atom1J.getPseudoOfPseudoAtom()):
#                    nTdebug('Skipping restraint without pseudo representing J atoms')
                    continue

            for atomPairIdxI in range(atomPairIdxJ): # Compare only with the previous atom pairs
                atomPairI = self.atomPairs[atomPairIdxI]
                _atom0I = atomPairI[0]
                _atom1I = atomPairI[1]
#                nTdebug('    Using atoms I %s and %s' % ( atom0I, atom1I) )
                atomPairIset = set(atomPairI)
                atomPairIntersection = atomPairIset.intersection(atomPairJset)
                if not atomPairIntersection:
#                    nTdebug('    No intersection')
                    continue

#                 At this point it is certain that there is an intersection of at least one atom between the two pairs.
                if len(atomPairIntersection) != 1:
#                    nTdebug('More than one atom in atom set intersection: %s' % atomPairIntersection)
                    continue

                atomInCommon = atomPairIntersection.pop() # get arbitrary element of set.
                atomIinCommonIdx = 0
                atomJinCommonIdx = 0
                atomItoMergeIdx = 1
                atomJtoMergeIdx = 1
                if atomPairI[atomIinCommonIdx] != atomInCommon:
                    atomIinCommonIdx = 1
                    atomItoMergeIdx = 0
                if atomPairJ[atomJinCommonIdx] != atomInCommon:
                    atomJinCommonIdx = 1
                    atomJtoMergeIdx = 0

                # Now we know which atoms are in common and consequently the others should be tried to merge.
#                nTdebug('    atominCommonIdx I %d and J %d for %s' % ( atomIinCommonIdx, atomJinCommonIdx, atomInCommon) )

                atomItoMerge = atomPairI[atomItoMergeIdx]
                atomJtoMerge = atomPairJ[atomJtoMergeIdx]

                atomIinCommon = atomPairI[atomIinCommonIdx]
                atomJinCommon = atomPairJ[atomJinCommonIdx]

#                nTdebug('    atomIinCommon %s == atomJinCommon %s' % ( atomIinCommon, atomJinCommon ))
                if atomIinCommon != atomJinCommon:
                    nTcodeerror('    atoms toMerge I %s and J %s differ.' % ( atomItoMerge, atomJtoMerge) )
                    continue
                # end if

                if atomItoMerge.getStereoPartner() != atomJtoMerge:
#                    nTdebug('    atoms toMerge I %s and J %s have different parent if at all related.' % ( atomItoMerge, atomJtoMerge) )
                    continue
                # end if

                pseudoOfAtom = atomItoMerge.pseudoAtom()
                if not pseudoOfAtom:
#                    nTdebug('    no pseudo for this atom %s' % atomItoMerge)
                    pseudoOfAtom = atomItoMerge.getPseudoOfPseudoAtom()
                    if not pseudoOfAtom:
                        nTwarning('    no pseudo of pseudoatom %s' % atomItoMerge) # happens in 1y0j for <Atom A.VAL205.CG1>
                        continue
                    # end if
                # end if

#                nTdebug( "    New pop atom: %s" % pseudoOfAtom)
                # Change I maintaining order
                atomPairINewList = list(atomPairI)
                atomPairINewList[atomItoMergeIdx] = pseudoOfAtom
                self.atomPairs[atomPairIdxI] = tuple(atomPairINewList)
#                nTdebug("Now self.atomPairs[atomPairIdxI]: %s" % str(self.atomPairs[atomPairIdxI]))
                # Remove J
#                nTdebug("Removing self.atomPairs[atomPairIdxJ]: %s" % str(self.atomPairs[atomPairIdxJ]))
                del self.atomPairs[atomPairIdxJ]
                # Return quickly to keep code to the left (keep it simple).
#                nTdebug('Simplified.')
                return self.STATUS_SIMPLIFIED
            # end for
        # end while
#        nTdebug('Not simplified.')
        return self.STATUS_NOT_SIMPLIFIED
    # end def

    def removeDuplicateAtomPairs(self):
        """
        Used in simplify.

        Returns:
        True                     error.

        In the code:

        j stands for the index of the atomPair of the outer loop that might be removed upon removal.
        i stands for the index of the atomPair of the inner loop that is compared to.
        """

#        nTdebug('Starting %s for %s' % ( getCallerName(), self ) )
        atomPairIdxJ = len(self.atomPairs) # starting from the end.
        while atomPairIdxJ > 1:
            atomPairIdxJ -= 1
            atomPairJ = self.atomPairs[atomPairIdxJ]
            atomPairJset = set(atomPairJ) # Important to use api of unsorted atoms in pair (left right will not matter)
            _atom0J = atomPairJ[0]
            _atom1J = atomPairJ[1]

#            nTdebug('For atomPairIdxJ %d using atoms J %s and %s' % ( atomPairIdxJ, atom0J, atom1J) )

            for atomPairIdxI in range(atomPairIdxJ): # Compare only with the previous atom pairs
                atomPairI = self.atomPairs[atomPairIdxI]
                _atom0I = atomPairI[0]
                _atom1I = atomPairI[1]
#                nTdebug('    Using atoms I %s and %s' % ( atom0I, atom1I) )
                atomPairIset = set(atomPairI)
                atomPairIntersection = atomPairIset.intersection(atomPairJset)
                if not atomPairIntersection:
#                    nTdebug('    No intersection')
                    continue
                if len(atomPairIntersection) != 2:
#                    nTdebug('Only one atom in atom set intersection: %s' % atomPairIntersection)
                    continue
#                nTdebug("Removing self.atomPairs[atomPairIdxJ]: %s" % str(self.atomPairs[atomPairIdxJ]))
                del self.atomPairs[atomPairIdxJ]
            # end for
        # end while
        return
    # end def

    def removeDuplicateAtomPairs2(self):
        """
        Used in simplify.

        This code is more advanced than the above removeDuplicateAtomPairs2 in that it will also
        check when pseudos are contained in other pseudos. The widest will be retained.
        E.g.
        For 1a24
        783.00    A    20    PRO    QB    A    23    LEU    MD1   3.20    7.90    2.96    0.56    2.56    3.35    0.32    0.45    0.64    0    0    0
        783.01    A    20    PRO    QB    A    23    LEU    QD    3.20    7.90    2.96    0.56    2.56    3.35    0.32    0.45    0.64    0    0    0
        will be truncated to:
        For 1a24
        783       A    20    PRO    QB    A    23    LEU    QD    3.20    7.90    2.96    0.56    2.56    3.35    0.32    0.45    0.64    0    0    0

        Watch for e.g. intraresidual LEU with multiple atompairs:
        HB2 QD
        QB  MD1
        This can not be truncated whereas:
        QB  MD1
        HB2 QD
        HB3 QD
        can be to simply QB QD.
        Therefore previous routines should already have cleaned up to:
        QB  MD1
        QB  QD
        so that this routine will do the final collapse to QB QD.

        The ordering is irrelevant but must always be maintained.


        pseudo code:
        loop over atompairs i,j
                atomset0i
                if(
                   ( atomset0i.issuperset(atomset0j) and atomset1i.issuperset(atomset1j)) or
                   ( atomset0i.issuperset(atomset1j) and atomset1i.issuperset(atomset0j))    )
                    remove j and return
                elif(
                   ( atomset0j.issuperset(atomset0i) and atomset1j.issuperset(atomset1i)) or
                   ( atomset0j.issuperset(atomset1i) and atomset1j.issuperset(atomset0i))    )
                    remove i and return

        Returns:
        True                     error.
        STATUS_REMOVED_DUPLICATE = 'removed duplicate'
        STATUS_NOT_REMOVED_DUPLICATE = 'not removed duplicate'

        In the code:

        j stands for the index of the atomPair of the outer loop that might be removed upon removal.
        i stands for the index of the atomPair of the inner loop that is compared to.
        """

#        nTdebug('Starting %s for %s' % ( getCallerName(), self ) )

        n = len(self.atomPairs)
        for atomPairIdxJ in range(n-1):
            atomPairJ = self.atomPairs[atomPairIdxJ]
#            atomPairJset = set(atomPairJ) # Important to use api of unsorted atoms in pair (left right will not matter)
            atom0J = atomPairJ[0]
            atom1J = atomPairJ[1]
            atomset0J = set( atom0J.realAtoms() )
            atomset1J = set( atom1J.realAtoms() )

#            nTdebug('For atomPairIdxJ %d using atoms J %s and %s' % ( atomPairIdxJ, atom0J, atom1J) )

            for atomPairIdxI in range(atomPairIdxJ+1,n): # Compare only with the next atom pairs
                atomPairI = self.atomPairs[atomPairIdxI]
                atom0I = atomPairI[0] #@UnusedVariable
                atom1I = atomPairI[1] #@UnusedVariable
#                nTdebug('    Using atoms I %s and %s' % ( atom0I, atom1I) )

                atomset0I = set( atom0I.realAtoms() )
                atomset1I = set( atom1I.realAtoms() )
                if(
                   ( atomset0I.issuperset(atomset0J) and atomset1I.issuperset(atomset1J)) or
                   ( atomset0I.issuperset(atomset1J) and atomset1I.issuperset(atomset0J))    ):
#                    nTdebug("Removing self.atomPairs[atomPairIdxJ]: %s" % str(self.atomPairs[atomPairIdxJ]))
                    del self.atomPairs[ atomPairIdxJ ]
                    return self.STATUS_REMOVED_DUPLICATE
                elif(
                   ( atomset0J.issuperset(atomset0I) and atomset1J.issuperset(atomset1I)) or
                   ( atomset0J.issuperset(atomset1I) and atomset1J.issuperset(atomset0I))    ):
#                    nTdebug("Removing self.atomPairs[atomPairIdxI]: %s" % str(self.atomPairs[atomPairIdxI]))
                    del self.atomPairs[ atomPairIdxI ]
                    return self.STATUS_REMOVED_DUPLICATE
                # end if
            # end for
        # end while
        return self.STATUS_NOT_REMOVED_DUPLICATE
    # end def

    def appendPair(self, pair):
        """ pair is a (atom1,atom2) tuple

        check if atom1 already present, keep order
        otherwise: keep atom with lower residue index first
        Return True on error.
        """
        # GV says; order needs to stay: is being used for easier
        # (manual) analysis.


        if pair[0] == None or pair[1] == None:
            nTerror('DistanceRestraint.appendPair: invalid pair %s', str(pair))
            return True
        #end if

#        missesId = False
        for atom in pair:
            if not hasattr(atom, 'id'): # happens for 1f8h and LdCof (imported from CYANA data).
#                nTwarning('DistanceRestraint.appendPair: invalid pair %s for atom missing id: %s' % (str(pair), str(atom)))
#                missesId = True
                return True
        #end if

#        if missesId:
#            self.atomPairs.append((pair[0], pair[1]))
#        else:
        # gv 24 Jul: just use atoms id, they are unique and ordered
        if pair[0].id < pair[1].id:
            self.atomPairs.append((pair[0], pair[1]))
        else:
            self.atomPairs.append((pair[1], pair[0]))
    #end def

    def classify(self):
        """
        Return 0,1,2,3 depending on sequential, intra-residual, medium-range or long-range
        Simply ignore ambiguous assigned NOEs for now and take it as the first atom pair

        return -1 on error
        """
        if not self.atomPairs or len(self.atomPairs) < 1:
            return - 1

        atm1, atm2 = self.atomPairs[0]
        if atm1 == None or atm2 == None:
            return - 1

        if atm1.residue.chain != atm2.residue.chain:
            return 3
        elif atm1.residue == atm2.residue:
            return 0
        else:
            r1 = atm1.residue
            r2 = atm2.residue
            if not (r1.chain and r2.chain):
                # Deals with removed residues which don't have a parent anymore.
                return -1
            delta = int(math.fabs(r1.chain._children.index(r1) - r2.chain._children.index(r2)))
            if delta == 1:
                return 1
            elif delta > 4:
                return 3
            else:
                return 2
            #end if
        #end if
    #end def

    def isAmbiguous(self):
        return len(self.atomPairs) > 1
    #end def

    def calculateAverage(self):
        """
        Calculate R-6 average distance and violation
        for each model.
        return (av,sd,min,max) tuple, or (None, None, None, None) on error
        Important to set the violations to 0.0 if no violations were found.
        In that case the s.d. may remain None to indicate undefined.
        """

#        nTdebug('calculateAverage: %s' % self)
        self.error = False    # Indicates if an error was encountered when analyzing restraint

        modelCount = self.getModelCount()
        if not modelCount:
#            nTdebug('DistanceRestraint.calculateAverage: No structure models (%s)', self)
            self.error = True
            return (None, None, None, None)
        #end if

        self.distances = NTlist() # list with distances for each model
        self.av = None      # Average distance
        self.sd = None      # sd on distance
        self.min = None      # Minimum distance
        self.max = None      # Max distance
        self.violations = NTlist() # list with violations for each model INCLUDING non violating models!
        self.violCount1 = 0        # Number of violations > 0.1A
        self.violCount3 = 0        # Number of violations > 0.3A
        self.violCount5 = 0        # Number of violations > 0.5A
        self.violCountLower = 0    # Number of lower-bound violations over 0.1A
        self.violMax = 0.0         # Maximum violation
        self.violUpperMax = 0.0    # Max violation over upper bound
        self.violLowerMax = 0.0    # Max violation over lower bound
        self.violAv = 0.0          # Average violation
        self.violSd = None         # Sd of violations
        self.violSum = 0.0         # Sum of violations
        self.distances = nTfill(0.0, modelCount) #list with actual effective distances

        models = range(modelCount)
        i = 0
        atm1, atm2 = None, None # helping pylint.
        for atm1, atm2 in self.atomPairs:

            # GV says: Check are done to prevent crashes upon rereading
            # datasets with floating/adhoc residues/atoms

            # skip trivial cases
            if atm1 == atm2:
                continue
            if atm1 == None or atm2 == None:
                continue
            #expand pseudoatoms
            atms1 = atm1.realAtoms()
            if atms1 == None:
                #nTdebug('DistanceRestraint.calculateAverage: %s.realAtoms() None (%s)', atm1, self)
                continue
            atms2 = atm2.realAtoms()
            if atms2 == None:
                #nTdebug('DistanceRestraint.calculateAverage: %s.realAtoms() None (%s)', atm2, self)
                continue
            for a1 in atms1:
                #print '>>>', a1.format()
                if len(a1.coordinates) == modelCount:
                    for a2 in atms2:
                        #print '>>', atm1, a1, atm2, a2
                        i = 0
                        if len(a2.coordinates) == modelCount:
                            for i in models:
                                self.distances[i] += Rm6dist(a1.coordinates[i].e, a2.coordinates[i].e)
                            #end for
                        else:
#                            self.distances[0] = 0.0
                            i = 0
                            self.error = True
                            break
                        #end if
                    #end for
                else:
#                    self.distances[0] = 0.0
                    i = 0
                    self.error = True
                    break
                #end if
            #end for
        #end for
        if self.error:
            msg = "AtomPair (%s,%s) model %d without coordinates" % (atm1.toString(), atm2.toString(), i)
#            nTdebug(msg)
            self.rogScore.setMaxColor(COLOR_RED, msg)
            return (None, None, None, None)
        #end if

        # Calculate R-6 distances
        for i in models:
            if self.distances[i] > 0.0:
                self.distances[i] = math.pow(self.distances[i], -0.166666666666666667)
            #end if
        #end for

        self.av, self.sd, self.n = nTaverage(self.distances)
        self.min = min(self.distances)
        self.max = max(self.distances)

        # calculate violations
        for d in self.distances:
            if d < self.lower:
                self.violations.append(d - self.lower)
            elif (d > self.upper):
                if self.upper == None: # Happens for entry 1but
                    self.violations.append(0.0)
                else:
                    self.violations.append(d - self.upper)
            else:
                self.violations.append(0.0)
            #end if
        #end for

        # analyze violations
        for v in self.violations:
            if (v > 0.5):
                self.violCount5 += 1
            if (v > 0.3):
                self.violCount3 += 1
            if (v > 0.1):
                self.violCount1 += 1
            if (v < -0.1):
                self.violCountLower += 1
        #end for
        if self.violations:
            vAbs = map(math.fabs, self.violations)
            self.violAv, self.violSd, _n = nTaverage(vAbs)
            self.violMax = max(vAbs)
            self.violSum = sum(vAbs)
            self.violUpperMax = max(self.violations)
            self.violLowerMax = min(self.violations)
            if self.violLowerMax < 0.0:
                self.violLowerMax = math.fabs(self.violLowerMax)
            else:
                self.violLowerMax = 0.0
        #end if

        return (self.av, self.sd, self.min, self.max)
    #end def

    def _names(self):
        """
        Internal routine: generate string from atomPairs
        """
        s = ''
        for p in self.atomPairs:
#            s = s + sprintf('(%-11s - %11s)   ', p[0].cName(1), p[1].cName(1))
            s = s + sprintf('(%-13s - %13s)   ', p[0].cName(2), p[1].cName(2)) # include chain id.
        #end for
        return s.strip()
    #end def

    def format(self, allowHtml = False):
        msg = sprintf('%-25s %-6s (Target: %s %s)  (Models: min %s  av %s+-%s  max %s) ' + \
                    '(Violations: av %4.2f max %4.2f counts l,0.1,0.3,0.5:%2d,%2d,%2d,%2d) %s',
                     str(self), self.rogScore,
                     val2Str(self.lower, "%4.1f", 4),
                     val2Str(self.upper, "%4.1f", 4),
                     val2Str(self.min, "%4.1f", 4),
                     val2Str(self.av, "%4.2f", 4),
                     val2Str(self.sd, "%4.1f", 4),
                     val2Str(self.max, "%4.1f", 4),
                     self.violAv, self.violMax,
                     self.violCountLower, self.violCount1, self.violCount3, self.violCount5,
                     self._names()
                    )
        if allowHtml:
            msg = addPreTagLines(msg)
        return msg
    #end def
#end class

# Too many ancestors (8/7) pylint: disable=R0901 
class DistanceRestraintList(RestraintList):
    """
    Class based on NTlist that holds distanceRestraints.
    Also manages the "id's".
    Sort  by item of DistanceRestraint Class
    """
    # use the same spelling through out.
    def __init__(self, name, status = 'keep'):
        RestraintList.__init__(self, name, status = status)
        self.__CLASS__ = DRL_LEVEL
        self.hBond = False       # hBond: fix to keep information about hBond restraints from CCPN 
        self.violCountLower = 0   # Total lower-bound violations over 0.1 A
        self.violCount1 = 0
        self.violCount3 = 0
        self.violCount5 = 0
        self.violMax = 0.0   # Maximum violation
        self.violUpperMax = 0.0   # Max violation over upper bound
        self.violLowerMax = 0.0   # Max violation over lower bound

        # partitioning in intra, sequential, medium-range and long-range, ambigous
        self.intraResidual = NTlist()
        self.sequential = NTlist()
        self.mediumRange = NTlist()
        self.longRange = NTlist()
        self.ambiguous = NTlist()

        # Duplicate analysis
        self.uniqueDistancesCount = 0        # count of all defined distance restraints
        self.withoutDuplicates = NTlist() # list of all restraints without duplicates
        self.withDuplicates = NTlist() # list of all restraints with duplicates
    #end def

    def criticize(self, project, toFile = True):
        """
        Criticize restraints of this list; infer own ROG score from individual restraints.
        """
#        nTdebug('DistanceRestraintList.criticize %s', self)
        self.rogScore.reset()

        for dr in self:
            dr.criticize(project)
            self.rogScore.setMaxColor(dr.rogScore.colorLabel, comment = 'Cascaded from: %s' % dr)
        if toFile:
            path = project.moleculePath('analysis', self.name + '.txt')
            f = file(path, 'w')
            fprintf(f, '%s\n\n', self.format())
            for dr in self:
                fprintf(f, '%s\n', dr.format())
            #end for
            f.close()
            nTdetail('==> Analyzing %s, output to %s', self, path)
        #end if
    #end def

    def simplify(self):
        """Look at Wattos code for a full set of code that does any simplification"""
        for dr in self:
            dr.simplify()

    def deassignStereospecificity(self, max_messages=100):
        """Deassign all"""
        msgHol = MsgHoL()
        for dr in self:
            strDrAtomPairs = str(dr.atomPairs)
            status = dr.deassignStereospecificity()
            if status == DistanceRestraint.STATUS_DEASSIGNED:
                msgHol.appendMessage("%s deassigned to:%s" % (strDrAtomPairs,str(dr.atomPairs)))
        msgHol.showMessage(max_messages=max_messages)

    def analyze(self):
        """
        Calculate averages for every restraint.
        Partition restraints into classes.
        Analyze for duplicate restraints.

        Return <rmsd>, sd and total violations over 0.1, 0.3, 0.5 A as tuple
        or (None, None, None, None, None) on error
        """

#        nTdebug('DistanceRestraintList.analyze: %s', self)

        if (len(self) == 0):
            # happens for entry 2k0e imported from CCPN. Has unlinked restraints.
            nTdebug('DistanceRestraintList.analyze: "%s" empty list'% self.name )
            return (None, None, None, None, None)
        #end if

        modelCount = self.getModelCount()
        if not modelCount:
            nTerror('DistanceRestraintList.analyze: "%s" modelCount %s' % (self.name, modelCount))
            return (None, None, None, None, None)
        #end if

        # check for duplicate
        self.findDuplicates()

        self.rmsd = nTfill(0.0, modelCount)
        self.violCount1 = 0
        self.violCount3 = 0
        self.violCount5 = 0
        count = 0
        self.errors = NTlist() # Store reference to restraints with calc problems

        # partitioning in intra, sequential, medium-range and long-range, ambigous
        self.intraResidual = NTlist()
        self.sequential = NTlist()
        self.mediumRange = NTlist()
        self.longRange = NTlist()
        self.ambiguous = NTlist()

        for dr in self:
            dr.calculateAverage()
            if dr.error:
                self.errors.append(dr)
            else:
                self.violCountLower += dr.violCountLower
                self.violCount1 += dr.violCount1
                self.violCount3 += dr.violCount3
                self.violCount5 += dr.violCount5
                for i in range(0, modelCount):
                    if dr.violations[i]:
                        self.rmsd[i] += dr.violations[i] * dr.violations[i]
                #end for
                count += 1
            #end if

            c = dr.classify()
            if c == 0:
                self.intraResidual.append(dr)
            elif c == 1:
                self.sequential.append(dr)
            elif c == 2:
                self.mediumRange.append(dr)
            elif c == 3:
                self.longRange.append(dr)
            #end if
            if dr.isAmbiguous(): 
                self.ambiguous.append(dr)
        #end for

        #Set max violations
        for p in ['violMax', 'violUpperMax', 'violLowerMax']:
            myList = self.zap(p)
            myList.sort()
            setattr(self, p, myList[-1])
        #end for

        for i in range(0, modelCount):
            if count:
                if self.rmsd[i]:
                    self.rmsd[i] = math.sqrt(self.rmsd[i] / count)
                else:
                    self.rmsd[i] = None
                #end if
            #end if
        #end for
        self.rmsdAv, self.rmsdSd, _n = nTaverage(self.rmsd)
        return (self.rmsdAv, self.rmsdSd, self.violCount1, self.violCount3, self.violCount5)
    #end def

    def findDuplicates(self):
        """Find the duplicate entries in the list
        """
        pairs = {}
        for dr in self:
            dr.atomPairs.sort() # improves matching for ambiguous restraints
            t = tuple(dr.atomPairs)
            pairs.setdefault(t, [])
            pairs[t].append(dr)
        #end for
        self.uniqueDistancesCount = len(pairs)

        self.withoutDuplicates = NTlist()
        self.withDuplicates = NTlist()
        for drl in pairs.values():
            if len(drl) == 1:
                self.withoutDuplicates.append(drl[0])
            else:
                for d in drl:
                    #print "***", d.format()
                    self.withDuplicates.append(d)
                #end for
            #end if
        #end for
    #end def

    def format(self, allowHtml = False, showAll = False):  # pylint: disable=W0221
        msg = sprintf(
'''
classes
  intra-residual:     %4d
  sequential:         %4d
  medium-range:       %4d
  long-range:         %4d
  ambiguous:          %4d

counts
  singly defined      %4d
  multiple defined    %4d
  total unique:       %4d
  duplicates:         %4d
  total all:          %4d

rmsd:              %7s +-%6s

violations
  <-0.1 A:            %4d (lower-bound violations, max:%5s)
  > 0.1 A:            %4d
  > 0.3 A:            %4d
  > 0.5 A:            %4d (upper-bound violations, max:%5s)

ROG score:         %7s
''',
                        len(self.intraResidual),
                        len(self.sequential),
                        len(self.mediumRange),
                        len(self.longRange),
                        len(self.ambiguous),

                        len(self.withoutDuplicates),
                        self.uniqueDistancesCount - len(self.withoutDuplicates),
                        self.uniqueDistancesCount,
                        len(self) - self.uniqueDistancesCount,
                        len(self),

                        val2Str(self.rmsdAv, "%7.3f", 7), val2Str(self.rmsdSd, "%6.3f", 6),
                        self.violCountLower, val2Str(self.violLowerMax, "%5.2f", 5),
                        self.violCount1, self.violCount3, self.violCount5, val2Str(self.violUpperMax, "%5.2f", 5),
                        self.rogScore
                      )
        if allowHtml:
            msg = addPreTagLines(msg)
        header = '%s DistanceRestraintList "%s" (%s,%d) %s\n' % (
            dots, self.name, self.status, len(self), dots)
        msg = header + msg
        msg += RestraintList.format(self, showAll = False)
        return msg
    #end def

#end class


class DihedralRestraint(Restraint):
    """
        DihedralRestraint class:

       GV 2 Oct 2007: removed residue and angle attributes.
       If the 4 atoms constitute a known dihedral angle, this can
       be retrieved with the retrieveDefinition method

       GV&AWSS: 10 Oct 2007, upper-limit adjustment
    """

#    project.valSets.DR_MAXALL_POOR = 3. # Normally 0.3 but set low for testing 1brv to
#    DR_MAXALL_BAD  = 5. # Normally 0.5 but set low for testing 1brv to
#    DR_THRESHOLD_OVER_BAD  = 0.3 # degrees.
#    DR_THRESHOLD_FRAC_BAD  = 0.5
#    DR_RMSALL_BAD  = 0.3 # Angstrom rms violations. # Normally 0.3 but set low for testing 1brv to

    def __init__(self, atoms, lower, upper, **kwds):
        if upper < lower:
            upper += 360.0
        Restraint.__init__(self,
                              lower = lower,
                              upper = upper,
                              **kwds
                       )
        self.dihedrals = NTlist() # list with dihedral values for each model
        self.cav = None      # Average dihedral value
        self.cv = None      # cv on dihedral

        self.setdefault('discontinuous', False)
        self.__CLASS__ = AC_LEVEL
        self.atoms = NTlist(*atoms)
        if None in self.atoms:
            self.isValid = False
    #end def

    def isValidForAquaExport(self):
        """Determine if the restraint can be exported to Aqua.
        Simplified to checking if there are 4 real atoms.
        """
        if not self.atoms:
#            nTdebug("Failed to find any atom in %s" % self)
            return False
        n = len(self.atoms)
        if n != 4:
#            nTdebug("Expected four atoms but found %d in:\n%s" % (n,self))
            return False
        for _i, atom in enumerate(self.atoms):
            if not atom:
#                nTdebug("Failed to find valid atom in:\n%s" % (i,self))
                return False
        return True
    #end def

    def criticize(self, project):
        """Only the self violations,violMax and violSd needs to be set before calling this routine"""
#        nTdebug( '%s (dih)' % self )
        self.rogScore.reset()

        if (project.valSets.AC_MAXALL_BAD != None) and (self.violMax >= project.valSets.AC_MAXALL_BAD):
            comment = 'violMax: %7.2f' % self.violMax
#            nTdebug(comment)
            self.rogScore.setMaxColor(COLOR_RED, comment)
        elif (project.valSets.AC_MAXALL_POOR != None) and (self.violMax >= project.valSets.AC_MAXALL_POOR):
            comment = 'violMax: %7.2f' % self.violMax
#            nTdebug(comment)
            self.rogScore.setMaxColor(COLOR_ORANGE, comment)

        if (project.valSets.AC_THRESHOLD_OVER_POOR != None) and (project.valSets.AC_THRESHOLD_FRAC_POOR != None):
            fractionAbove = getFractionAbove(self.violations, project.valSets.AC_THRESHOLD_OVER_POOR)
            if fractionAbove >= project.valSets.AC_THRESHOLD_FRAC_POOR:
                comment = 'fractionAbove: %7.2f' % fractionAbove
    #            nTdebug(comment)
                self.rogScore.setMaxColor(COLOR_ORANGE, comment)

        if (project.valSets.AC_THRESHOLD_OVER_BAD != None) and (project.valSets.AC_THRESHOLD_FRAC_BAD != None):
            fractionAbove = getFractionAbove(self.violations, project.valSets.AC_THRESHOLD_OVER_BAD)
            if fractionAbove >= project.valSets.AC_THRESHOLD_FRAC_BAD:
                comment = 'fractionAbove: %7.2f' % fractionAbove
    #            nTdebug(comment)
                self.rogScore.setMaxColor(COLOR_RED, comment)

        if (project.valSets.AC_RMSALL_BAD != None) and (self.violSd >= project.valSets.AC_RMSALL_BAD):
            comment = 'violSd: %7.2f' % self.violSd
#            nTdebug(comment)
            self.rogScore.setMaxColor(COLOR_RED, comment)
        elif (project.valSets.AC_RMSALL_POOR != None) and (self.violSd >= project.valSets.AC_RMSALL_POOR):
            comment = 'violSd: %7.2f' % self.violSd
#            nTdebug(comment)
            self.rogScore.setMaxColor(COLOR_ORANGE, comment)

        if project.valSets.FLAG_MISSING_COOR:
            #modelCount = self.getModelCount()
                #atms = atm.realAtoms()
                #for a in atms:
            for a in self.atoms:                # GV says: no realAtoms should be called; these are dihedrals
                                                # and should be properly defined by their \atoms.

                #if len(a.coordinates) < modelCount:
                if a and a.hasMissingCoordinates(): # gv has mase this into a method because the getModelCount()
                    # can crash when reading back NRG dataset because of their
                    # incompleteness
                    msg = "Missing coordinates in dihedral (%s)" % a.toString()
#                    nTdebug(msg)
                    self.rogScore.setMaxColor(COLOR_RED, msg)
    #end def

    def isChi2TyrOrPhe(self):
        lastAtom = self.atoms[3]
        atomName = getDeepByKeysOrAttributes(lastAtom,'name')
        if atomName != 'CD1':
            return False
        lastAtomRes = lastAtom._parent
        lastAtomResType = getDeepByKeysOrAttributes(lastAtomRes, 'db', 'name')
        if lastAtomResType in ['TYR', 'PHE']:
            return True
        return False

    def calculateAverage(self):
        """Calculate the values and violations for each model
        return cav and cv tuple or (None, None) tuple on error
        """
        errorExit = (None, None)
        if len(self.atoms) != 4 or (None in self.atoms):
            nTerror('DihedralRestraint: invalid dihedral definition %s', self.atoms)
            return errorExit
        #end if

        if None in self.atoms.zap('meanCoordinate'):
            nTerror('DihedralRestraint: atom(s) without coordinates %s', self.atoms)
            return errorExit
        #end if

#        coorList = self.atoms.zap('coordinates')
#        if len( coorList ) == 0:
#            nTerror('DihedralRestraint: atom(s) without any coordinates %s', self.atoms)
#            return (None, None)
#        #end if

        modelCount = self.getModelCount()
        if modelCount == 0:
            nTerror('DihedralRestraint: no structure models')
            return errorExit
        #end if
#        lenCoorListExpected = 4 * modelCount
#        if len( coorList ) != lenCoorListExpected:
#            nTerror('DihedralRestraint: atom(s) without all coordinates %s', self.atoms)
#            return (None, None)
#        #end if


        #set the default values (JFD: this needs to be fully done in initializer in case code fails as for issue 222)
        self.dihedrals = NTlist() # list with dihedral values for each model
        self.cav = None      # Average dihedral value
        self.cv = None      # cv on dihedral

        self.violations = NTlist() # list with violations for each model
        self.violCount1 = 0        # Number of violations over 1 degree
        self.violCount3 = 0        # Number of violations over 3 degrees
        self.violCount5 = 0        # Number of violations over 5 degrees
        self.violMax = 0.0      # Maximum violation
        self.violAv = 0.0      # Average violation
        self.violSd = 0.0      # Sd of violations

        #find the range to store these dihedral values
        plotpars = plotParameters.getdefault(self.retrieveDefinition()[1], 'dihedralDefault')
        considerSymmetry = self.isChi2TyrOrPhe() # Hack for Phe/Tyr CHI2
        lastAtom = self.atoms[3]
        ssaPartner = None
        if considerSymmetry:
#            ssaPartner = lastAtom.getStereoPartner()
            try:
                ssaPartner = lastAtom._parent.CD2
            except:
                pass
#            nTdebug("ssaPartner: %s" % ssaPartner)
            if ssaPartner != None:
                considerSymmetry = True
            else:
                nTwarning("DihedralRestraint: no lastAtom's ssa for %s so ignoring symmetry on violation." % self)
                considerSymmetry = False

        if considerSymmetry:
            jLoopList = [ lastAtom, ssaPartner ]
        else:
            jLoopList = [ lastAtom ]

        try:
            # For each model we'll use the atom HD1 or HD2 that has the smallest violation or HD1 if neither one
            # is violated.
            for i in range(modelCount):
                dList = []
                vList = []
                for _j1, lastAtom2 in enumerate(jLoopList):
#                    nTdebug('i, _j1, lastAtom2, considerSymmetry: %s %s %s %s' % (i,_j1,lastAtom2, considerSymmetry))
                    atomList = [self.atoms[k] for k in range(3)]
                    atomList.append( lastAtom2 )
                    coorList = [ atom.coordinates[i] for atom in atomList]
                    d = nTdihedralOpt( *coorList )
                    if d == None:
#                        nTdebug("Failed to calculate an angle; which can happen if a coordinate is missing.")
                        continue
                    dList.append( d )
                # end for _j1
                nTlimit(dList, plotpars.min, plotpars.max)
                for _j2 in range(len(dList)):
                    v = violationAngle(value = dList[_j2], lowerBound = self.lower, upperBound = self.upper)
                    if v == None:
                        nTwarning("Failed to calculate a violation angle.")
                        return errorExit
                    vList.append( v )
                # end for _j2
                jSelected = 0
                if considerSymmetry:
                    fvList = [ math.fabs(x) for x in vList]
                    if len(fvList) == 2:
                        if fvList[1] < fvList[0]:
                            jSelected = 1
#                    nTdebug("Comparing fviolations for %s %s" % ( self, fvList))
                # end if
#                nTdebug("Comparing distances for %s %s" % ( self, dList))
#                nTdebug("Comparing violations for %s %s" % ( self, vList))
#                nTdebug("jSelected %s" % jSelected)
                self.dihedrals.append(dList[jSelected])
                self.violations.append(vList[jSelected])
#                nTdebug("self.dihedrals %s" % self.dihedrals)
#                nTdebug("self.violations %s" % self.violations)

                fv = math.fabs(vList[jSelected])
                if fv > 1.0: 
                    self.violCount1 += 1
                if fv > 3.0: 
                    self.violCount3 += 1
                if fv > 5.0: 
                    self.violCount5 += 1
                if fv > self.violMax:
                    self.violMax = fv
                #end if
            #end for all models
        except:
#            NTtracebackError() # DEFAULT this is disabled.
#            nTdebug("Ignoring violations for %s" % self.format() )
            pass # ignore missing coordinates. They're reported by criticize()

        self.violAv, self.violSd, _n = self.violations.average()
        # The CV is hard to calculate for the symmetry case detailed above. TODO:
        self.cav, self.cv, _n = self.dihedrals.cAverage(plotpars.min, plotpars.max)
        return(self.cav, self.cv)
    #end def

    def retrieveDefinition(self):
        """
        Retrieve a (<Residue>, angleName, <AngleDef>) tuple from
        the molecule._dihedralDict
        or
        (None,None,None) on error
        """
        resultError = (None, None, None)
        if (not self.atoms or (None in self.atoms)):
            return resultError
        #end if

#        mol = self.atoms[0].residue.chain.molecule
        mol = self.atoms[0].getMolecule()
        if mol == None:
            return resultError
        if mol._dihedralDict.has_key(tuple(self.atoms)):
            return mol._dihedralDict[tuple(self.atoms)]
        return resultError
        #end if
    #end def

    def getName(self):
        """
        Construct a name;
        have to do dynamically because upon restoring, the atoms are not yet defined
        """
        res, name, _tmp = self.retrieveDefinition()
        if res and name:
            return res.name + '.' + name
        else:
            return ''
    #end def

    def getDihedralName(self):
        """
        Construct a name;
        have to do dynamically because upon restoring, the atoms are not yet defined
        """
        _res, name, _tmp = self.retrieveDefinition()
        return name
    #end def

    def format(self):  # pylint: disable=W0221
        # set the last string to something readable in terms of known dihedrals, or just the atoms if nothing is found
        s = self.getName()
        if len(s) == 0:
            s = self.atoms.format('%-11s ')
        return  \
            sprintf('%-25s %-6s (Target: %s %s)  (Models: cav %6s cv %7s)  ' + \
                    '(Violations: av %4s max %4.1f counts %2d,%2d,%2d) %s',
                     self, self.rogScore,
                     val2Str(self.lower, "%6.1f", 6), # GV: does not fit in 4 fields, i.e -160.1
                     val2Str(self.upper, "%6.1f", 6),
                     val2Str(self.cav, "%6.1f", 6),
                     val2Str(self.cv, "%7.4f", 7),
                     val2Str(self.violAv, "%4.1f", 4),
                     self.violMax, self.violCount1, self.violCount3, self.violCount5,
                     s
                    )
    #end def
#end class

# Too many ancestors (8/7) pylint: disable=R0901 
class DihedralRestraintList(RestraintList):
    'List of dihedral angle restraints.'
#    export2cyana = exportDihedralRestraint2cyana
    
    def __init__(self, name, status = 'keep'):
        RestraintList.__init__(self, name, status = status)
        self.__CLASS__ = ACL_LEVEL
    #end def    

    def criticize(self, project, toFile = True):
        """
        Criticize restraints of this list; infer own ROG score from individual restraints.
        """
#        nTdebug('DihedralRestraintList.criticize %s', self)
        self.rogScore.reset()

        for dr in self:
            dr.criticize(project)
            self.rogScore.setMaxColor(dr.rogScore.colorLabel, comment = 'Cascaded from: %s' % dr)
        if toFile:
            path = project.moleculePath('analysis', self.name + '.txt')
            f = file(path, 'w')
            fprintf(f, '%s\n\n', self.format())
            for dr in self:
                fprintf(f, '%s\n', dr.format())
            #end for
            f.close()
            nTdetail('==> Analyzing %s, output to %s', self, path)
        #end if
    #end def

    def analyze(self, calculateFirst = True):
        """
        Calculate averages for every restraint.
        Return <rmsd>, sd and total violations over 1, 3, and 5 degrees as tuple
        or (None, None, None, None, None) on error
        """
        errorResult = (None, None, None, None, None)
#        nTdebug('DihedralRestraintList.analyze: %s', self)

        if not len(self):
            nTwarning('DihedralRestraintList.analyze: "%s" empty list', self.name)
            return errorResult
        #end if

        modelCount = self.getModelCount()
        if not modelCount:
            nTerror('DihedralRestraintList.analyze: "%s" modelCount 0', self.name)
            return errorResult
        #end if

        self.rmsd = nTfill(0.0, modelCount)
        self.violCount1 = 0
        self.violCount3 = 0
        self.violCount5 = 0
        for dr in self:
            if calculateFirst:
                (cav, _cv) = dr.calculateAverage()
                if cav == None:
#                    nTdebug("Failed to calculate average for: " + self.format())
                    continue # skipping dihedral with a missing coordinate or so.
            self.violCount1 += dr.violCount1
            self.violCount3 += dr.violCount3
            self.violCount5 += dr.violCount5

            countDrViolations = len(dr.violations)
            if countDrViolations > modelCount:
                nTcodeerror("Found more violations (%s) for this restraint (%s) than models (%s)" % ( countDrViolations, dr, modelCount))
                return errorResult

            for i in range(countDrViolations): # happened in entry 1bn0 that violations were not defined.
#            for i in range(0, modelCount):
                v = dr.violations[i]
                self.rmsd[i] += v * v
            #end for
        #end for

        for i in range(0, modelCount):
            self.rmsd[i] = math.sqrt(self.rmsd[i] / len(self))
        #end for

        self.rmsdAv, self.rmsdSd, _n = nTaverage(self.rmsd)
        return (self.rmsdAv, self.rmsdSd, self.violCount1, self.violCount3, self.violCount5)
    #end def

    def format(self, allowHtml = False):
        msg = sprintf(
'''
rmsd:                 %7s +-%6s
violations >1 degree: %4d
violations >3 degree: %4d
violations >5 degree: %4d

ROG score:            %s
''', val2Str(self.rmsdAv, "%7.3f", 7),
                        val2Str(self.rmsdSd, "%6.3f", 6),
                        self.violCount1,
                        self.violCount3,
                        self.violCount5,
                        self.rogScore
                      )
        if allowHtml:
            msg = addPreTagLines(msg)
        header = '%s DihedralRestraintList "%s" (%s,%d) %s\n' % (
            dots, self.name, self.status, len(self), dots)
        msg = header + msg
        return msg
    #end def

    def formatHtml(self, allowHtml = False):
        header = self.name
        if hasattr(self, 'rogScore'):
            if self.rogScore.isCritiqued():
                header = '<font color="%s">%s</font>' % (self.rogScore.colorLabel, header)
        header = '<h3>DihedralRestraintList %s</h3>' % header

        msg = '''%s
<BR>
<table>
<TR><TD>rmsd:               </TD><TD> %s +- %s                    </TD></TR>
<TR><TD>violations > 1 degree</TD><TD align="right"> %4d                          </TD></TR>
<TR><TD>violations > 3 degrees</TD><TD align="right"> %4d                          </TD></TR>
<TR><TD>violations > 5 degrees</TD><TD align="right"> %4d                          </TD></TR>
</table>
''' % (
    header,
    val2Str(self.rmsdAv, "%7.3f", 7), val2Str(self.rmsdSd, "%6.3f", 6),
    self.violCount1,
    self.violCount3,
    self.violCount5
  )
        return msg
    #end def

    def isFromTalos(self):
        return self.name.startswith(TALOSPLUS_LIST_STR)
#end class


class RDCRestraint(DistanceRestraint):
    """Residual Dipolar Coupling restraint
    much like DistanceRestraint having also atomPairs.
    """
    def __init__(self, atomPairs = [], lower = 0.0, upper = 0.0, **kwds):

        DistanceRestraint.__init__(self,
                              atomPairs = atomPairs,
                              lower = lower,
                              upper = upper,
                              **kwds
                       )
        self.__CLASS__ = RDC_LEVEL
        self.rdcs = None     # list with backcalculated rdc values for each model, None indicates no analysis done
        # copied from dihedral; to be implemented
        self.cav = None     # Average dihedral value
        self.cv = None     # cv on dihedral
    #end def


    def calculateAverage(self):
        """Calculate the values and violations for each model
           return cav and cv tuple or (None, None) tuple on error
        """

        modelCount = self.getModelCount()
        if not modelCount:
            nTerror('Error RDCRestraint: no structure models\n')
            return (None, None)
        #end if

#TODO needs work
#        if len(self.atoms) != 2 or None in self.atoms:
#            nTerror('Error RDCRestraint: invalid rdc definition %s\n', self.atoms )
#            return (None,None)
#        #end if
#
#        if None in self.atoms.zap('meanCoordinate'):
#            nTerror('Error RDCRestraint: atom without coordinates %s\n', self.atoms )
#            return (None,None)
#        #end if

        #set the default values; do not remove or it will crash upon restoring RDC lists
        self.rdcs = nTfill(0.0, modelCount) # list with dihedral values for each model
        self.cav = NaN      # Average dihedral value
        self.cv = NaN      # cv on dihedral
#        self.min        = 0.0      # Minimum dihedral
#        self.max        = 0.0      # Max dihedral
        self.violations = nTfill(0.0, modelCount) # list with violations for each model
        self.violCount1 = 0        # Number of violations over 1 degree
        self.violCount3 = 0        # Number of violations over 3 degrees
        self.violCount5 = 0        # Number of violations over 5 degrees
        self.violMax = 0.0      # Maximum violation
        self.violAv = 0.0      # Average violation
        self.violSd = 0.0      # Sd of violations

        return(None, None)
    #end def

    def _names(self):
        """
        Internal routine: generate string from atomPairs
        """
        s = ''
        for p in self.atomPairs:
            s = s + sprintf('(%-11s - %11s)   ', p[0].cName(1), p[1].cName(1))
        #end for
        return s.strip()
    #end def

    def format(self): # pylint: disable=W0221
#        s = '('
#        for p in self.atoms:
#            s = s + sprintf('%-11s ', p.cName(1) )
#        #end for
#        s = s.strip() + ')'
        return  sprintf('%-25s %-6s (Target: %6.1f %6.1f) %s',
                        str(self), self.rogScore,
                        self.lower, self.upper,
                        self._names()
                       )

    #end def
#end class

# Too many ancestors (8/7) pylint: disable=R0901 
class RDCRestraintList(RestraintList):
    """List of RDCRestraint"""

    def __init__(self, name, status = 'keep'):
        RestraintList.__init__(self, name, status = status)
        self.__CLASS__ = RDCL_LEVEL
    #end def

    def analyze(self, calculateFirst = True):
        """
        Calculate averages for every restraint.

        """

#        nTdebug('RDCRestraintList.analyze: %s', self)

        if len(self) == 0:
            nTerror('RDCRestraintList.analyze: "%s" empty list', self.name)
            return (None, None, None, None, None)
        #end if

        modelCount = 0
        firstRestraint = self[0]
        if not hasattr(firstRestraint, "atoms"):
            nTwarning("Failed to get the model count for no atoms are available in the first RDC restraint.")
            nTwarning("See also issue: %s%d" % (issueListUrl, 133))
        else:
            if len(self[0].atomPairs):
                modelCount = self[0].atomPairs[0][0].residue.chain.molecule.modelCount
        #end if

        if not modelCount: # JFD notes eg reading $CINGROOT/Tests/data/ccpn/2hgh.tgz
            nTerror('RDCRestraintList.analyze: "%s" modelCount 0', self.name)
            return (None, None, None, None, None)
        #end if

        self.rmsd = nTfill(0.0, modelCount)
        self.violCount1 = 0
        self.violCount3 = 0
        self.violCount5 = 0
        for dr in self:
            if calculateFirst:
                dr.calculateAverage()
            if dr.rdcs == None or dr.violations == None:
                nTerror('RDCRestraintList.analyze: skipping restraint %s', dr)
            else:
                self.violCount1 += dr.violCount1
                self.violCount3 += dr.violCount3
                self.violCount5 += dr.violCount5
                for i in range(0, modelCount):
                    self.rmsd[i] += dr.violations[i] * dr.violations[i]
                #end for
            #end if
        #end for

        for i in range(0, modelCount):
            self.rmsd[i] = math.sqrt(self.rmsd[i] / len(self))
        #end for

        self.rmsdAv, self.rmsdSd, dummy_n = nTaverage(self.rmsd)
        return (self.rmsdAv, self.rmsdSd, self.violCount1, self.violCount3, self.violCount5)
    #end def

    def criticize(self, project, toFile = True):
        """
        Criticize restraints of this list; infer own ROG score from individual restraints.

        TODO: Need implementation
        """
#        nTdebug('RDCRestraintList.criticize %s', self)
        self.rogScore.reset()

#        for dr in self:
#            dr.criticize(project)
#            self.rogScore.setMaxColor( dr.rogScore.colorLabel, comment='Cascaded from: %s' % dr )
#        if toFile:
#            path = project.moleculePath('analysis', self.name + '.txt')
#            f = file( path, 'w')
#            fprintf(f, '%s\n\n', self.format())
#            for dr in self:
#                fprintf(f, '%s\n', dr.format())
#            #end for
#            f.close()
#            nTdetail('Distance restraint analysis %s, output to %s', self, path)
#        #end if
    #end def


    def format(self, allowHtml = False):
        msg = sprintf('rmsd: %7.3f %6.3f',
                      self.rmsdAv, self.rmsdSd)
        if allowHtml:
            msg = addPreTagLines(msg)
        header = '%s RDCRestraintList "%s" (%s,%d) %s\n' % (
            dots, self.name, self.status, len(self), dots)
        msg = header + msg
        return msg
    #end def

#    def formatHtml( self ):
##TODO clean up
#        header = self.name
#        if hasattr(self, 'rogScore'):
#            if self.rogScore.isCritiqued():
#                header = '<font color="%s">%s</font>' % (self.rogScore.colorLabel, header)
#        header = '<h3>RDCRestraintList %s</h3>' % header
#
#        msg = '''%s
#<BR>
#<table>
#<TR><TD>rmsd</TD>               <TD> %s +- %s                    </TD></TR>
#<TR><TD>violations > 1 </TD><TD align="right"> %4d                          </TD></TR>
#<TR><TD>violations > 3 </TD><TD align="right"> %4d                          </TD></TR>
#<TR><TD>violations > 5 </TD><TD align="right"> %4d                          </TD></TR>
#</table>
#''' % (
#    header,
#    val2Str(self.rmsdAv, "%7.3f", 7), val2Str(self.rmsdSd, "%6.3f", 6),
#    self.violCount1,
#    self.violCount3,
#    self.violCount5
#  )
#        return msg
#    #end def

    def formatHtml(self, allowHtml = False):
        header = self.name
        if hasattr(self, 'rogScore'):
            if self.rogScore.isCritiqued():
                header = '<font color="%s">%s</font>' % (self.rogScore.colorLabel, header)
        header = '<h3>RDCRestraintList %s</h3>' % header

        msg = '''%s
<BR>
<table>
<TR><TD>count               </TD><TD align="right">%4d</TD></TR>
</table>
''' % (
    header,
    len(self)
  )
        return msg
    #end def
#end class


class History(NTlist):
    """Cing history storage class
    """

    def __call__(self, line, timeStamp = True):  # pylint: disable=W0221
        if timeStamp:
            self.append((time.asctime(), line))
        else:
            self.append((None, line))
        #end if
    #end def

    def __str__(self):
        s = sprintf('%s History %s\n', dots, dots)
        for timeStamp, line in self:
            if timeStamp:
                s = s + sprintf('%s: %s\n', timeStamp, line)
            else:
                s = s + line + '\n'
            #end if
        #end for
        return s
    #end def

    format = __str__

    def toXML(self, depth = 0, stream = sys.stdout, indent = '\t', lineEnd = '\n'):
        nTindent(depth, stream, indent)
        fprintf(stream, "<History>")
        fprintf(stream, lineEnd)

        for a in self:
            nTtoXML(a, depth + 1, stream, indent, lineEnd)
        #end for
        nTindent(depth, stream, indent)
        fprintf(stream, "</History>")
        fprintf(stream, lineEnd)
    #end def
#end class


class XMLHistoryHandler(XMLhandler):
    """History handler class"""
    def __init__(self):
        XMLhandler.__init__(self, name = 'History')
    #end def

    def handle(self, node):
        items = self.handleMultipleElements(node)
        if items == None: 
            return None
        result = History()
        for item in items:
            result.append(item)
        return result
    #end def
#end class

#register this handler
historyhandler = XMLHistoryHandler()


def path(*args):
    """
    Return a path from arguments relative to cing root
    """
    return os.path.join(cingRoot, *args)
#end def

def shift(atm):
    return atm.shift()
#end def


def getFractionAbove(valueList, threshold):
    """Return the fraction that is above the threshold. Return .0 if
    list contains no values.
    """
    if not valueList:
        return .0
    n = 0.0 # enforce float arithmics for below division.
    for v in valueList:
        if not v: # catch None and pure zero
            continue
        if v > threshold:
            n += 1.
    return n / len(valueList)



class Coplanar(NTdict):
    """Collection of data on an individual base pair, triplet or quadruplet.
    """
    def __init__(self, name, resList = []):
        NTdict.__init__(self,
                         __CLASS__ = COPLANAR_LEVEL,
                         resList = resList)
        self.__FORMAT__ = self.header() + '\n' + \
                          'residues:  %(resList)s\n'
        self.name = name
    #end def
# end class

class CoplanarList(NTlist):
    """List of base pairs, triplets and/or quadruplets
    """
    def __init__(self, name, status = 'skip'): # reset status to keep when SML handler finished with GWV's help.
        NTlist.__init__(self)
        self.__CLASS__ = COPLANARL_LEVEL
        self.name = name
        self.status = status
        self.currentId = 0       # Id for each element of list
    #end def
##end class
