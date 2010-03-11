"""
Implementation of the CING API
"""
from ConfigParser import ConfigParser
from cing import cingPythonCingDir
from cing import cingRoot
from cing import cingVersion
from cing import issueListUrl
from cing.Libs.Geometry import violationAngle
from cing.Libs.NTutils import Lister
from cing.Libs.NTutils import NTaverage
from cing.Libs.NTutils import NTcodeerror
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdetail
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTfill
from cing.Libs.NTutils import NTindent
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import NTtoXML
from cing.Libs.NTutils import NTvalue
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import XML2obj
from cing.Libs.NTutils import XMLhandler
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import matchString
from cing.Libs.NTutils import obj2XML
from cing.Libs.NTutils import removedir
from cing.Libs.NTutils import sprintf
from cing.Libs.NTutils import val2Str
from cing.Libs.cython.superpose import NTcVector #@UnresolvedImport @UnusedImport
from cing.Libs.cython.superpose import Rm6dist #@UnresolvedImport
from cing.Libs.fpconst import NaN
from cing.Libs.fpconst import isNaN
from cing.Libs.html import addPreTagLines
from cing.Libs.html import generateHtml
from cing.Libs.html import renderHtml
from cing.Libs.html import setupHtml
from cing.Libs.pdb import export2PDB
from cing.Libs.pdb import importPDB
from cing.Libs.pdb import initPDB
from cing.core.CingSummary import CingSummary
from cing.core.ROGscore import ROGscore
from cing.core.constants import ACL_LEVEL
from cing.core.constants import AC_LEVEL
from cing.core.constants import COLOR_ORANGE
from cing.core.constants import COLOR_RED
from cing.core.constants import COPLANARL_LEVEL
from cing.core.constants import COPLANAR_LEVEL
from cing.core.constants import DRL_LEVEL
from cing.core.constants import DR_LEVEL
from cing.core.constants import IUPAC
from cing.core.constants import LOOSE
from cing.core.constants import RDCL_LEVEL
from cing.core.constants import RDC_LEVEL
from cing.core.constants import VAL_SETS_CFG_DEFAULT_FILENAME
from cing.core.molecule import Atom
from cing.core.molecule import Molecule
from cing.core.molecule import NTdihedralOpt
from cing.core.molecule import NTdistanceOpt #@UnusedImport
from cing.core.molecule import dots
from cing.core.parameters import cingPaths
from cing.core.parameters import directories
from cing.core.parameters import moleculeDirectories
from cing.core.parameters import plotParameters
from cing.core.parameters import plugins
from cing.core.validate import checkForSaltbridges
from cing.core.validate import criticize
from cing.core.validate import criticizePeaks
from cing.core.validate import fixStereoAssignments
from cing.core.validate import partitionRestraints
from cing.core.validate import runCingChecks
from cing.core.validate import summary
from cing.core.validate import validate
from cing.core.validate import validateAssignments
from cing.core.validate import validateDihedrals
from cing.core.validate import validateModels
from cing.core.validate import validateRestraints
from shutil import rmtree
import cing
import math
import os
import sys
import tarfile
import time
__version__ = cing.__version__
__date__ = cing.__date__
__author__ = cing.__author__
__copyright__ = cing.__copyright__
__credits__ = cing.__credits__

projects = NTlist()

"CRV stands for CRiteria Value CRS stands for CRiteria String"
CRV_NONE = "-999.9";

#-----------------------------------------------------------------------------
# Cing classes and routines
#-----------------------------------------------------------------------------

class Project(NTdict):

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

        NTdict.__init__(self,
                           __CLASS__ = 'Project',

                           version = cingVersion,

                           root = root,
                           name = name.strip(),
                           created = time.asctime(),

                           molecule = None, # Current Molecule instance

                           moleculeNames = NTlist(), # list to store molecule names for save and restore
                           peakListNames = NTlist(), # list to store peaklist names for save and restore
                           distanceListNames = NTlist(), # list to store distancelist names names for save and restore
                           dihedralListNames = NTlist(), # list to store dihedrallist names for save and restore
                           rdcListNames = NTlist(), # list to store rdclist names for save and restore
                           coplanarListNames = NTlist(), # list to store  names for save and restore

                           reports = NTlist(), # list with validation reports names

                           history = History(),
                           contentIsRestored = False, # True if Project.restore() has been called
                           storedInCcpnFormat = False, #

                           procheckStatus = NTdict(completed = False, parsed = False, ranges = None),
                           dsspStatus = NTdict(completed = False, parsed = False),
                           whatifStatus = NTdict(completed = False, parsed = False),
                           shiftxStatus = NTdict(completed = False, parsed = False),
                           x3dnaStatus 				 = NTdict(completed = False, parsed = False),


                           # store a reference to the global things we might need
                           gui = None, # Reference to CingGui instance
                           directories = directories,
                           moleculeDirectories = moleculeDirectories,
                           cingPaths = cingPaths,
                           plotParameters = plotParameters,
                           plugins = plugins
                         )

        # These Project lists are dynamic and will be filled  on restoring a project
        # They also maintain some internal settings
        # new( name ), append( instance), save(), restore() and path( name ) and names() comprise core functionality
        self.molecules = _ProjectList(project = self,
                                         classDef = Molecule,
                                         nameListKey = 'moleculeNames',
                                         basePath = directories.molecules + '/%s.molecule'
                                       )
        self.peaks = _ProjectList(project = self,
                                         classDef = PeakList,
                                         nameListKey = 'peakListNames',
                                         basePath = directories.peaklists + '/%s.peaks'
                                       )
        self.distances = _ProjectList(project = self,
                                         classDef = DistanceRestraintList,
                                         nameListKey = 'distanceListNames',
                                         basePath = directories.restraints + '/%s.distances'
                                       )
        self.dihedrals = _ProjectList(project = self,
                                         classDef = DihedralRestraintList,
                                         nameListKey = 'dihedralListNames',
                                         basePath = directories.restraints + '/%s.dihedrals'
                                       )
        self.rdcs = _ProjectList(project = self,
                                         classDef = RDCRestraintList,
                                         nameListKey = 'rdcListNames',
                                         basePath = directories.restraints + '/%s.rdcs'
                                       )
        self.coplanars = _ProjectList(project = self,
                                         classDef = CoplanarList,
                                         nameListKey = 'coplanarListNames',
                                         basePath = directories.restraints + '/%s.coPlanars'
                                       )
#        self.dihEntities = _ProjectList(project = self,
#                                         classDef = DihedralEntityList,
#                                         nameListKey = 'dihEntityListNames',
#                                         basePath = directories.restraints + '/%s.dihEntities'
#                                       )


        # store reference to self
        #self[name] = self
        self.objectPath = self.path(cingPaths.project)
#        self.makeObjectPaths() # generates the objectPaths dict from the nameLists

        self.rogScore = ROGscore()
        self.summaryDict = CingSummary()

        self.valSets = NTdict()
        self.readValidationSettings(fn = None)

        self.saveXML('version',
                      'name', 'created',
                      'moleculeNames',
                      'peakListNames', 'distanceListNames', 'dihedralListNames', 'rdcListNames', 'coplanarListNames',
                      'storedInCcpnFormat',
                      'reports',
                      'history',
                      'procheckStatus', 'dsspStatus', 'whatifStatus', 'shiftxStatus'
                    )
    #end def


    def readValidationSettings(self, fn = None):
        """Reads the validation settings from installation first and then overwrite any if a filename is given.
        This ensures that all settings needed are present but can be overwritten. It decouples development from
        production.
        """

        validationConfigurationFile = os.path.join(cingPythonCingDir, VAL_SETS_CFG_DEFAULT_FILENAME)
#        NTdebug("Using system validation configuration file: " + validationConfigurationFile)
        self._readValidationSettingsFromfile(validationConfigurationFile)
        validationConfigurationFile = None

        if fn:
            validationConfigurationFile = fn
#            NTdebug("Using validation configuration file: " + validationConfigurationFile)
        elif os.path.exists(VAL_SETS_CFG_DEFAULT_FILENAME):
            validationConfigurationFile = VAL_SETS_CFG_DEFAULT_FILENAME
#            NTdebug("Using local validation configuration file: " + validationConfigurationFile)
        if validationConfigurationFile:
            self._readValidationSettingsFromfile(validationConfigurationFile)

    #end def

    def _readValidationSettingsFromfile(self, fn):
        """Return True on error.   """
        if not fn:
            NTcodeerror("No input filename given at: _readValidationSettingsFromfile")
            return True

        if not os.path.exists(fn):
            NTcodeerror("Input file does not exist at: " + fn)
            return True

#        NTdebug("Reading validation file: " + fn)
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
            valueStr = `value`
            if self.valSets.has_key(key):
                valueFromStr = `self.valSets[key]`
                if valueStr == valueFromStr:
                    continue  # no print
                NTdebug("Replacing value for key " + key + " from " + valueFromStr + " with " + valueStr)
            else:
#                NTdebug("Adding              key " + key + " with value: " + valueStr)
                pass
            self.valSets[key] = value # name value pairs.
        #end for
        self.valSets.keysformat()
    #end def

    def getCingSummaryDict(self):
        """Get a CING summary dict from self
        Return summayDict or None on error
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
        root, name, ext = NTpath(pathName)
        if name == '' or name == 'project': # indicate we had a full path
            root, name, ext = NTpath(root)
        #end if
        if (len(ext) > 0 and ext != '.cing'):
            NTerror('FATAL: unable to parse "%s"; invalid extention "%s"\n', pathName, ext)
#            exit(1) # no more hard exits for we might call this from GUI or so wrappers
            return None, None

        rootp = os.path.join(root, name + '.cing')
#        NTdebug("rootp, name: [%s] [%s]" % (rootp, name))
        return rootp, name
    #end def
    rootPath = staticmethod(rootPath)

    def mkdir(self, *args):
        """Make a directory relative to to root of project from joined args.
           Check for presence.
           Return the result
        """
        dir = self.path(*args)
        if not os.path.exists(dir):
#            NTdebug( "project.mkdir: %s" % dir )
            os.makedirs(dir)
        return dir
    #end def

    def moleculePath(self, subdir = None, *args):
        """ Path relative to molecule.
        Return path or None in case of error.
        """
        if not self.molecule:
            return None
        if subdir == None:
            return self.path(self.molecule.name)

        return self.path(self.molecule.name, moleculeDirectories[subdir], *args)
    #end def

    def validationPath(self, *args):
        """Path relative to validation directory for molecule.
        Create path if does not exist.

        **** Highly redundant with moleculePath at present time, but should replace it eventually ***

        Return path or None in case of error.
        """
        if not self.molecule:
            return None
        path = self.mkdir(self.molecule.name) # should become self.mkdir( 'Validation', self.molecule.name )

        if not path:
            return None

        return os.path.join(path, *args)
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


    def open(name, status = 'create', restore = True):
        """Static method open returns a new/existing Project instance depending on status.

           status == 'new': open a new project 'name'
           status == 'old: open existing project 'name'
                      project data is restored when restore == True.
           status == 'create': if project name if exists open as old, open as new otherwise.

           Returns Project instance or None on error.
        """
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
#            NTdebug('New project %s', pr)

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
                NTdebug("Unpacking possibleTgz: " + possibleTgz)
                tar = tarfile.open(possibleTgz, "r:gz")
                for itar in tar:
                    tar.extract(itar.name, '.') # itar is a TarInfo object
#                    NTdebug("extracted: " + itar.name)
                tar.close()
                if not os.path.exists(possibleProjectDir):
                    NTerror('Project.open: Failed to find project in .tgz file. Unable to open Project "%s"\n', name)
                    return None
            else:
                if os.path.exists(possibleTgz):
                    NTdebug("Skipping .tgz because there's already a .cing")
                else:
                    NTdebug("No " + possibleTgz + " found.")

            root, newName = Project.rootPath(name)
            if not root:
                return None
            if not os.path.exists(root):
                NTerror('Project.open: unable to open Project "%s"\n', name)
                return None
            #end if

            # Restore Project info from xml-file
            pfile = os.path.join(root, cingPaths.project)
            if not os.path.exists(pfile):
                NTerror('Project.open: missing Project file "%s"\n', pfile)
                return None
            #end if
            pr = XML2obj(pfile)
            if pr == None:
                NTerror('Project.open: error parsing Project file "%s"\n', pfile)
                return None
            #end if
            # This allows renaming/relative addressing at the shell level
            pr.root = root
            pr.name = newName
            pr.objectPath = pfile

            pr.contentIsRestored = False

            pr.whatifStatus.parsed = False
            pr.shiftxStatus.parsed = False
            pr.dsspStatus.parsed = False
            pr.procheckStatus.parsed = False
            pr.x3dnaStatus.parsed = False

            try:
                # <= 0.75 version have string
                pr.version = float(pr.version.strip('abcdefghijklmnopqrtsuvw ()!@#$%^&*').split()[0])
            except:
                pass

            if pr.version <= 0.75:
                NTmessage('Project.Open: converting from CING version %s', pr.version)
                NTdebug('Project.open: conversion: old project settings\n%s', pr.format())

                # 0.75 version had moleculeNames stored in molecules attribute
                # >=0.76 version molecules is a ProjectList instance
                pr.moleculeNames = pr.molecules
                if 'molecules' in pr.__SAVEXML__:
                    pr.__SAVEXML__.remove('molecules')
                pr.saveXML('moleculeNames')

                # store the xmlFile and reopen to have correct settings
                if obj2XML(pr, path = pfile) != pr:
                    NTerror('Project.Open: conversion from version %s failed on write', pr.version)
                    return None
                pr = XML2obj(pfile)
                if pr == None:
                    NTerror('Project.Open: conversion from version %s failed on read', pr.version)
                    return None

                for molName in pr.moleculeNames:
                    if pr.version <= 0.48:
                        path = pr.path('Molecules', molName) # old reference
                    else:
                        path = pr.path(directories.molecules, molName) # old reference, versions 0.48-0.75
                    NTdebug('Project.open: trying molecule conversion from %s', path)
                    if not os.path.exists(path):
                        NTerror('Project.open: old molecule path "%s" does not exist.', path)
                        return None
                    mol = Molecule._open075(path)
                    if not mol:
                        NTerror('Project.Open: conversion from version %s failed on molecule %s', pr.version, molName)
                        return None
                    removedir(path)
                    # Save molecule to new format
                    mol.save(pr.molecules.path(molName))
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

            NTdebug('Opened old project %s', pr)

        else:
            NTerror('ERROR Project.open: invalid status option "%s"\n', status)
            return None
        #end if

        # Check the subdirectories
        tmpdir = pr.path(directories.tmp)
        # have to use cing.verbosity to work?
        if os.path.exists(tmpdir) and cing.verbosity != cing.verbosityDebug:
            removedir(tmpdir)
        for dir in directories.values():
            pr.mkdir(dir)
        #end for

        projects.append(pr)
        return pr
    #end def
    open = staticmethod(open)

    def close(self, save = True):
        """
        Save project data and close project.
        TODO: Call destructor on self and its elements
        """
        global projects
        #self.export()
        if save: self.save()
        # remove the tmpdir
        tmpdir = self.path(directories.tmp)
        # have to use cing.verbosity to work?
        #print '>>', cing.verbosity, cing.verbosityDebug
        if os.path.exists(tmpdir) and cing.verbosity != cing.verbosityDebug:
            removedir(tmpdir)

        projects.remove(self)
        return None
    #end def

    def superpose(self, ranges = None, backboneOnly = True, includeProtons = False, iterations = 2):
        """
        Calculate a superposition of current active molecule
        return rmsd result of molecule, or None on error

        """

        if not self.molecule:
            NTerror('Project.superpose: undefined molecule')
            return None
        #end if

        if self.molecule.modelCount == 0:
            NTerror('Project.superpose: no coordinates for %s\n', self.molecule)
            return None
        #end if
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
        NTmessage('' + dots * 5 + '')
        NTmessage('==> Saving %s', self)

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
#                NTdebug("Skipping save for disabled plugin: %s" % p)
            else:
                for f, o in p.saves:
                    f(self, o)
            #end for
        #end for

        # Update version number since it is now saved with this cingVersion
        self.version = cingVersion
        # Save the project data to xml file
        if obj2XML(self, path = self.objectPath) != self:
            NTerror('Project.save: writing Project file "%s" failed', self.objectPath)
        #end if

        self.addHistory('Saved project')
        return True
    #end def

    def restore(self):
        """
        Restore the project: molecules and lists
        """
        if self.contentIsRestored:
            NTerror("Project.restore: content was already restored")
            return

        NTmessage('==> Restoring %s ... ', self)

        # Molecules
        for molName in self.moleculeNames:
            path = self.molecules.path(molName)
            mol = Molecule.open(path)
            if mol:
                mol.status = 'keep'
                self.appendMolecule(mol)
            #end if
        #end for

        # restore the lists
        for pl in [self.peaks, self.distances, self.dihedrals, self.rdcs, self.coplanars]:
            pl.restore()
        #end for

        self.analyzeRestraints()
#            l.criticize(self) now in criticize of validate plugin

        # Plugin registered functions
        for p in self.plugins.values():
            if p.isInstalled:
                for f, o in p.restores:
                    f(self, o)
                #end for
            #end if
        #end for

        self.contentIsRestored = True

        self.updateProject()
    #end def

    def removeCcpnReferences(self):
        """To slim down the memory footprint; should allow garbage collection."""
        attributeToRemove = "ccpn"
        try:
            self.removeRecursivelyAttribute(attributeToRemove)
        except:
            NTerror("Failed removeCcpnReferences")

    def export(self):
        """Call export routines from the plugins to export the project
        """
        NTmessage('' + dots * 5 + '')
        NTmessage('==> Exporting %s', self)

        for p in self.plugins.values():
            for f, o in p.exports:
                f(self, o)
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
        if not molecule: return None

        # Store names and references and append
        self.molecule = molecule
        self.molecules.append(molecule)

        # generate the required directories for export and HTML data
        for dir in moleculeDirectories.values():
            self.mkdir(molecule.name, dir)
        #end for

# GV 21 Jun 08: do not know why we would need a save here
#        self.molecule.save( path = self.molecule.objectPath )
        return self.molecule
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
        Return Molecle instance or None on error
        """
        path = self.molecules.path(name)
        mol = Molecule.open(path)
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
            NTerror('Project.mergeResonances: No molecule defined\n')
            return
        #end if
        self.molecule.mergeResonances(order = order, selection = selection, append = append)
        NTdetail("==> Merged resonances")
    #end def

    def initResonances(self):
        """ Initialize resonances for all the atoms
        """
        if not self.molecule:
            NTerror('Project.initResonances: No molecule defined\n')
            return
        self.molecule.initResonances()
    #end def

    #-------------------------------------------------------------------------
    # actions other
    #-------------------------------------------------------------------------

    def addHistory(self, line, timeStamp = True):
        self.history(line, timeStamp)
    #end def

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
        """Call analyze method for all restraint lists
        """
        NTdetail('==> Analyzing restraints')
        for drl in self.allRestraintLists():
            drl.analyze()
    #end def

    def allRestraintLists(self):
        """Return an NTlist instance with all restraints lists
        """
        return self.distances + self.dihedrals + self.rdcs

    def header(self, dots = '---------'):
        """Subclass header to generate using __CLASS__, name and dots.
        """
        return sprintf('%s %s: %s %s', dots, self.__CLASS__, self.name, dots)
    #end def

    def __str__(self):
        return sprintf('<Project %s>', self.name)
    #end def

    def __repr__(self):
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

    def format(self):
        dots = '-----------'
        result = self.header(dots) + '\n' + \
                            'created:    %(created)s\n'
        result = result % self
        for firstString, item in [('molecules:  ', 'molecules'),
                                 ('peaks:      ', 'peaks'),
                                 ('distances:  ', 'distances'),
                                 ('dihedrals:  ', 'dihedrals'),
                                 ('rdcs:       ', 'rdcs'),
                                 ('coplanars:  ', 'coplanars'),
                                ]:
            result = result + self._list2string(self[item], firstString, 2) + '\n'
        #end for
        result = result + self.footer(dots)
        return result
    #end def

    def removeFromDisk(self):
        """Removes True on error. If no cing project is found on disk None (Success) will
        still be returned. Note that you should set the nosave option on the project
        before exiting."""
        pathString, _name = self.rootPath(self.name)
        if not os.path.exists(pathString):
            NTdebug("No cing project is found at: " + pathString)
            return None
        NTmessage('Removing existing cing project "%s"', self)
        if rmtree(pathString):
            NTerror("Failed to remove existing cing project")
            return True

    # Convenience methods calls to validate.py.
    def initPDB(self, pdbFile, convention = IUPAC, name = None, nmodels = None, update = True, allowNonStandardResidue = True):
        """Initializes from a pdb file."""
        return initPDB(self, pdbFile, convention = convention, name = name, nmodels = nmodels, update = update, allowNonStandardResidue = allowNonStandardResidue)

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

    def validateModels(self):
        return validateModels(self)

    def validateRestraints(self, toFile = True):
        return validateRestraints(self, toFile = toFile)

    def criticizePeaks(self, toFile = True):
        return criticizePeaks(self, toFile = toFile)

    def fixStereoAssignments(self, toFile = True):
        return fixStereoAssignments(self, toFile = toFile)

    def summary(self, toFile = True):
        return summary(self, toFile = toFile)

    def criticize(self, toFile = True):
        return criticize(self, toFile = toFile)

    def validate(self, ranges = None, parseOnly = False, htmlOnly = False, doProcheck = True, doWhatif = True, doWattos = True):
        return validate(self, ranges = ranges, parseOnly = parseOnly, htmlOnly = htmlOnly, doProcheck = doProcheck, doWhatif = doWhatif, doWattos = doWattos)

    def runCingChecks(self, ranges = None):
        return runCingChecks(self, ranges = ranges)

    def checkForSaltbridges(self, cutoff = 0.5, toFile = False):
        return checkForSaltbridges(self, cutoff = cutoff, toFile = toFile)

    def partitionRestraints(self, tmp = None):
        return partitionRestraints(self, tmp = tmp)

    def setupHtml(self):
        return setupHtml(self)

    def renderHtml(self):
        return renderHtml(self)

    def generateHtml(self, htmlOnly = False):
        return generateHtml(self, htmlOnly = htmlOnly)



class XMLProjectHandler(XMLhandler):
    """Project handler class"""
    def __init__(self):
        XMLhandler.__init__(self, name = 'Project')
    #end def

    def handle(self, node):
        attrs = self.handleDictElements(node)
        if attrs == None: return None
        result = Project(name = attrs['name'])

        # update the attrs values
        result.update(attrs)

        return result
    #end def
#end class

#register this handler
projecthandler = XMLProjectHandler()


class _ProjectList(NTlist):
    """Generic Project list class: the list of lists of the project; e.g. molecules, peaks, ...
       only to be used internally
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

    def append(self, instance):
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
#        NTdebug( s )
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
        for l in self:
#            NTdebug('l is %s' % l)
            if l.status == 'keep':
                NTdetail('==> Saving %s to %s', l, l.objectPath)
                if self.classDef.SMLhandler.toFile(l, l.objectPath) == l:
                    saved.append(l.name)
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
            l = self.classDef.SMLhandler.fromFile(path, self.project) # Lists get append to project by SML routines
            if l != None:
                NTdetail('==> Restored %s from %s', l, path)
                l.objectPath = path
            #end if
        #end for
    #end def

    def names(self, *patterns):
        "Return a list of names of self, optionally screen using "
        names = NTlist()
        for l in self:
            if len(patterns) == 0:
                names.append(l.name)
            else:
                for p in patterns:
                    if matchString(l.name, p):
                        names.append(l.name)
                        break
                    #end if
                #end for
            #end if
        #end for
        return names

    def rename(self, oldName, newName):
        """
        Rename listitem oldName to newName
        return the listitem of None on error
        """
        if not oldName in self.names():
            NTerror('_ProjectList.rename: old name "%s" not found', oldName)
            return None
        #end if
        if newName in self.project:
            NTerror('_ProjectList.rename: new name "%s" aleady exists in %s', oldName, self.project)
            return None
        #end if
        l = self.project[oldName]
        del(self.project[oldName])
        l.name = newName
        self.project[newName] = l
        l.objectPath = self.path(l.name)
        return l
    #end def

    def delete(self, name):
        """
        Delete listitem name from the project
        return the listitem of None on error
        """
        if not name in self.names():
            NTerror('_ProjectList.delete: name "%s" not found', name)
            return None
        #end if
        l = self.project[name]
        del(self.project[name])
        NTlist.remove(self, l)
        return l
    #end def

    def className(self):
        """Return a string describing the class of lists of this project list
        """
        # eg. to extract from <class 'cing.classes.PeakList'>
        return str(self.classDef)[8:-2].split(".")[-1:][0]
    #end def
#end class ProjectList

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
#       several external programs need an index
        global PeakIndex
        self.peakIndex = PeakIndex
        PeakIndex += 1

        self.__FORMAT__ = self.header(dots) + '\n' + \
                           'dimension:  %(dimension)dD\n' + \
                           'positions:  %(positions)s\n' + \
                           'height:     %(height)s\n' + \
                           'volume:     %(volume)s\n' + \
                           'resonances: %(resonances)s\n' + \
                           'rogScore:   %(rogScore)s\n' + \
                           self.footer(dots)

        self.dimension = dimension

        # Copy the positions and resonances argument to assure they become
        # NTlist objects
        if resonances:
            self.resonances = NTlist(*resonances)
        else:
            self.resonances = NTfill(None, dimension)
        #end if

        if positions:
            self.positions = NTlist(*positions)
        else:
            self.positions = NTfill(NaN, dimension)
        #end if

        self.height = NTvalue(height, heightError, Peak.HEIGHT_VOLUME_FORMAT, Peak.HEIGHT_VOLUME_FORMAT2)
        self.volume = NTvalue(volume, volumeError, Peak.HEIGHT_VOLUME_FORMAT, Peak.HEIGHT_VOLUME_FORMAT2)

        self.rogScore = ROGscore()
    #end def

    def isAssigned(self, axis):
        if (axis >= self.dimension): return False
        if (axis >= len(self.resonances)): return False
        if (self.resonances[axis] == None): return False
        if (self.resonances[axis].atom == None): return False
        return True
    #end def

    def getAssignment(self, axis):
        """Return atom instances in case of an assignment or None
        """
        if (self.isAssigned(axis)):
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

    def header(self, dots = '---------'):
        """Subclass header to generate using __CLASS__, peakIndex and dots.
        """
        return sprintf('%s %s: %d %s', dots, self.__CLASS__, self.peakIndex, dots)
    #end def
#end class


class PeakList(NTlist):

    def __init__(self, name, status = 'keep'):
        NTlist.__init__(self)
        self.name = name
        self.status = status
        self.listIndex = -1 # list is not appended to anything yet
        self.rogScore = ROGscore()
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

    def format(self):
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
        if not path: path = self.objectPath
        if self.SMLhandler.toFile(self, path) != self:
            NTerror('PeakList.save: failed creating "%s"', path)
            return None
        #end if

        NTdetail('==> Saved %s to "%s"', self, path)
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
    "Super class for DistanceRestraint etc."
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
        self.rogScore = ROGscore()
    #end def
    def __str__(self):
        return '<%s %d>' % (self.__CLASS__, self.id)
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
                    modelCount = atom.getModelCount()
                    if modelCount != None:
                        return modelCount
        else:
#            lAtom  = len(self.atoms)
            for atom in self.atoms:
                modelCount = atom.getModelCount()
                if modelCount != None:
                    return modelCount
#        NTwarning("%s.getModelCount returned None for all %d atom(pair)s; giving up." % (self.__CLASS__, lAtom))
        return None
    #end def

    def isValidForAquaExport(self):
        """Determine if the restraint can be exported to Aqua."""
        NTerror("Restraint.isValidForAquaExport needs to be overriden.")
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
       lower and upper bounds
    """
    STATUS_SIMPLIFIED = 'simplified'
    STATUS_NOT_SIMPLIFIED = 'not simplified'

#    def __init__( self, atomPairs=[], lower=0.0, upper=0.0, **kwds ):
    def __init__(self, atomPairs = NTlist(), lower = None, upper = None, **kwds):

        Restraint.__init__(self, lower = lower,
                               upper = upper,
                               **kwds
                        )
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
            self.appendPair(pair)
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
            NTdebug("Failed to find any atom pair in %s" % self)
            return False
        for i, atomPair in enumerate(self.atomPairs):
            if not atomPair: # eg [ HA ] [ HB,HC ]
                NTdebug("Failed to find any atomList (should always be 2 present) in atompair %d of:\n%s" % (i,self))
                return False
            for j, atomList in enumerate(atomPair):
                if not atomList: # eg [ HB,HC ]
                    NTdebug("Failed to find any atom in atomList (%d,%d) of %s" % (i,j,self))
                    return False
                for k, atom in enumerate(atomList):
                    if not atom: # eg HB
                        NTdebug("Failed to find atom in atomList (%d,%d,%d) of %s" % (i,j,k,self))
                        return False
        return True
    #end def


    def criticize(self, project):
        """Only the self violations,violMax and violSd needs to be set before calling this routine"""

        self.rogScore.reset()
#        NTdebug( '%s' % self )
        if (project.valSets.DR_MAXALL_BAD != None) and (self.violMax >= project.valSets.DR_MAXALL_BAD):
            comment = 'violMax: %7.2f' % self.violMax
#            NTdebug(comment)
            self.rogScore.setMaxColor(COLOR_RED, comment)
        elif (project.valSets.DR_MAXALL_POOR != None) and (self.violMax >= project.valSets.DR_MAXALL_POOR):
            comment = 'violMax: %7.2f' % self.violMax
#            NTdebug(comment)
            self.rogScore.setMaxColor(COLOR_ORANGE, comment)
        if (project.valSets.DR_THRESHOLD_OVER_POOR != None) and (project.valSets.DR_THRESHOLD_FRAC_POOR != None):
            fractionAbove = getFractionAbove(self.violations, project.valSets.DR_THRESHOLD_OVER_POOR)
            if fractionAbove >= project.valSets.DR_THRESHOLD_FRAC_POOR:
                comment = 'fractionAbove: %7.2f' % fractionAbove
    #            NTdebug(comment)
                self.rogScore.setMaxColor(COLOR_ORANGE, comment)
        if (project.valSets.DR_THRESHOLD_OVER_BAD != None) and (project.valSets.DR_THRESHOLD_FRAC_BAD != None):
            fractionAbove = getFractionAbove(self.violations, project.valSets.DR_THRESHOLD_OVER_BAD)
            if fractionAbove >= project.valSets.DR_THRESHOLD_FRAC_BAD:
                comment = 'fractionAbove: %7.2f' % fractionAbove
    #            NTdebug(comment)
                self.rogScore.setMaxColor(COLOR_RED, comment)
        if (project.valSets.DR_RMSALL_BAD != None) and (self.violSd >= project.valSets.DR_RMSALL_BAD):
            comment = 'violSd: %7.2f' % self.violSd
#            NTdebug(comment)
            self.rogScore.setMaxColor(COLOR_RED, comment)
        elif (project.valSets.DR_RMSALL_POOR != None) and (self.violSd >= project.valSets.DR_RMSALL_POOR):
            comment = 'violSd: %7.2f' % self.violSd
#            NTdebug(comment)
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
#                        NTdebug(msg)
                        self.rogScore.setMaxColor(COLOR_RED, msg)
                    #end if
                #end for
            #end for
        # end if
    #end def

    def simplify(self):
        """Return True on error"""
        status = self.STATUS_SIMPLIFIED
        while status == self.STATUS_SIMPLIFIED:
            status = self.simplifySpecificallyForFcFeature()
            if status == self.STATUS_SIMPLIFIED:
                pass
#                NTdebug("simplified restraint %s" % self)
            elif status == self.STATUS_NOT_SIMPLIFIED:
                pass
#                NTdebug("not simplified restraint %s" % self)
            else:
                NTerror("Encountered an error simplifying restraint %s" % self)
                return True


    def simplifySpecificallyForFcFeature(self):
        """FC likes to split Val QQG in QG1 and 2 making it appear to be an ambiguous OR typed XPLOR restraint
        were it is not really one. Undone here.
        Return None on error.
        STATUS_NOT_SIMPLIFIED for no simplifications done
        STATUS_SIMPLIFIED for simplifications done
        """

#        NTdebug('Starting simplifySpecificallyForFcFeature for %s' % ( self ) )
        atomPairIdxJ = len(self.atomPairs)
        while atomPairIdxJ > 1:
            atomPairIdxJ -= 1
            atomPairJ = self.atomPairs[atomPairIdxJ]
            atomPairJset = set(atomPairJ) # Important to use api of unsorted atoms in pair (left right will not matter)
            atom0J = atomPairJ[0]
            atom1J = atomPairJ[1]

#            NTdebug('Using atoms J %s and %s' % ( atom0J, atom1J) )
            # speed up check on J.
            if not (atom0J.hasPseudoAtom() or atom1J.hasPseudoAtom()):
                if not (atom0J.getPseudoOfPseudoAtom() or atom1J.getPseudoOfPseudoAtom()):
#                    NTdebug('Skipping restraint without pseudo representing J atoms')
                    continue

            for atomPairIdxI in range(atomPairIdxJ): # Compare only with the previous atom pairs
                atomPairI = self.atomPairs[atomPairIdxI]
#                atom0I = atomPairI[0]
#                atom1I = atomPairI[1]
#                NTdebug('    Using atoms I %s and %s' % ( atom0I, atom1I) )
                atomPairIset = set(atomPairI)
                atomPairIntersection = atomPairIset.intersection(atomPairJset)
                if not atomPairIntersection:
#                    NTdebug('    No intersection')
                    continue

                # At this point it is certain that there is an intersection of an atom between the two pairs.
                if len(atomPairIntersection) != 1:
                    NTcodeerror('Unexpected more than one atom in atom set intersection')
                    return None

                atomPairInCommon = atomPairIntersection.pop()
                atomIinCommonIdx = 0
                atomJinCommonIdx = 0
                atomItoMergeIdx = 1
                atomJtoMergeIdx = 1
                if atomPairI[atomIinCommonIdx] != atomPairInCommon:
                      atomIinCommonIdx = 1
                      atomItoMergeIdx = 0
                if atomPairJ[atomJinCommonIdx] != atomPairInCommon:
                      atomJinCommonIdx = 1
                      atomJtoMergeIdx = 0

                # Now we know which atoms are in common and consequently the others should be tried to merge.
#                NTdebug('    atominCommonIdx I %d and J %d' % ( atomIinCommonIdx, atomJinCommonIdx) )

                atomItoMerge = atomPairI[atomItoMergeIdx]
                atomJtoMerge = atomPairJ[atomJtoMergeIdx]

                if atomItoMerge.getSterospecificallyRelatedlPartner() != atomJtoMerge:
#                    NTdebug('    atoms toMerge I %s and J %s have different parent if at all' % ( atomItoMerge, atomJtoMerge) )
                    continue

                #
                pseudoOfAtom = atomItoMerge.pseudoAtom()
                if not pseudoOfAtom:
#                    NTdebug('    no pseudo for this atom %s' % atomItoMerge)
                    pseudoOfAtom = atomItoMerge.getPseudoOfPseudoAtom()
                    if not pseudoOfAtom:
                        NTerror('    no pseudo of pseudoatom %s' % atomItoMerge)
                        continue

#                NTdebug( "    New pop atom: %s" % pseudoOfAtom)
                # Change I maintaining order
                atomPairINewList = list(atomPairI)
                atomPairINewList[atomItoMergeIdx] = pseudoOfAtom
                self.atomPairs[atomPairIdxI] = tuple(atomPairINewList)
                # Remove J
                del self.atomPairs[atomPairIdxJ]
                # Return qucikly to keep code to the left (keep it simple).
#                NTdebug('Simplified.')
                return self.STATUS_SIMPLIFIED
#        NTdebug('Not simplified.')
        return self.STATUS_NOT_SIMPLIFIED

    def appendPair(self, pair):
        """ pair is a (atom1,atom2) tuple

        check if atom1 already present, keep order
        otherwise: keep atom with lower residue index first
        """
        # GV says; order needs to stay: is beeing used for easier
        # (manual) analysis.


        if pair[0] == None or pair[1] == None:
            NTerror('DistanceRestraint.appendPair: invalid pair %s', str(pair))
            return
        #end if

        for atom in pair:
            if not hasattr(atom, 'id'): # happens for 1f8h
                NTerror('DistanceRestraint.appendPair: invalid pair %s for atom: %s' % (str(pair), str(atom)))
                return
        #end if

        # gv 24 Jul: just use atoms id, they are unique and ordered
        if pair[0].id < pair[1].id:
            self.atomPairs.append((pair[0], pair[1]))
        else:
            self.atomPairs.append((pair[1], pair[0]))
    #end def

    def classify(self):
        """
        Return 0,1,2,3 depending on sequential, intra-residual, medium-range or long-range
        Simply ignore ambigious assigned NOEs for now and take it as the first atom pair

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

    def isAmbigious(self):
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

#        NTdebug('calculateAverage: %s' % self)
        self.error = False    # Indicates if an error was encountered when analyzing restraint

        modelCount = self.getModelCount()
        if not modelCount:
#            NTdebug('DistanceRestraint.calculateAverage: No structure models (%s)', self)
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
        self.violMax = 0.0    # Maximum violation
        self.violUpperMax = 0.0    # Max violation over upper bound
        self.violLowerMax = 0.0    # Max violation over lower bound
        self.violAv = 0.0      # Average violation
        self.violSd = None     # Sd of violations
        self.violSum = 0.0      # Sum of violations
        self.distances = NTfill(0.0, modelCount) #list with actual effective distances

        models = range(modelCount)
        i = 0
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
                #NTdebug('DistanceRestraint.calculateAverage: %s.realAtoms() None (%s)', atm1, self)
                continue
            atms2 = atm2.realAtoms()
            if atms2 == None:
                #NTdebug('DistanceRestraint.calculateAverage: %s.realAtoms() None (%s)', atm2, self)
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
#            NTdebug(msg)
            self.rogScore.setMaxColor(COLOR_RED, msg)
            return (None, None, None, None)
        #end if

        # Calculate R-6 distances
        for i in models:
            if self.distances[i] > 0.0:
                self.distances[i] = math.pow(self.distances[i], -0.166666666666666667)
            #end if
        #end for

        self.av, self.sd, self.n = NTaverage(self.distances)
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
            self.violAv, self.violSd, _n = NTaverage(vAbs)
            self.violMax = max(vAbs)
            self.violSum = sum(vAbs)
            self.violUpperMax = max(self.violations)
            self.violLowerMax = math.fabs(min(self.violations))
        #end if

        return (self.av, self.sd, self.min, self.max)
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

class RestraintList(NTlist):
    """
    Super class for DistanceRestraintList etc..
    Moving functionality to here gradually.
    """
    # use the same spelling through out.
    def __init__(self, name, status = 'keep'):
        NTlist.__init__(self)
        self.__CLASS__ = None
        self.name = name        # Name of the list
        self.status = status      # Status of the list; 'keep' indicates storage required
        self.currentId = 0       # Id for each element of list

        self.rmsd = None    # rmsd per model, None indicate no analysis done
        self.rmsdAv = 0.0
        self.rmsdSd = 0.0
        self.violCount1 = 0       # Total violations over 0.1 A (1 degree)
        self.violCount3 = 0       # Total violations over 0.3 A (3 degrees)
        self.violCount5 = 0       # Total violations over 0.5 A (5 degrees)

        self.rogScore = ROGscore()
    #end def
    def __str__(self):
        return sprintf('<%s "%s" (%s,%d)>' % (self.__CLASS__, self.name, self.status, len(self)))
    #end def
    def __repr__(self):
        return self.__str__()
    #end def
    def rename(self, newName):
        return self.projectList.rename(self.name, newName)
    #end def
    def append(self, restraint):
        restraint.id = self.currentId
        NTlist.append(self, restraint)
        self.currentId += 1
    #end def
    def save(self, path = None):
        """
        Create a SML file
        Return self or None on error
        """
        if not path: path = self.objectPath
        if self.SMLhandler.toFile(self, path) != self:
            NTerror('%s.save: failed creating "%s"' % (self.__CLASS__, self. path))
            return None
        #end if
        NTdetail('==> Saved %s to "%s"', self, path)
        return self
    #end def

    def getModelCount(self):
        """Iterate over the restraints until a restraint is found that returns not a None for getModelCount.
        Return 0 if it doesn't have any models or None on error.
        Never complain.
        """
        modelCount = None
        MAX_RESTRAINTS_TO_TEST = 10 # disable feature after testing.
        for i, restraint in enumerate(self):
            modelCount = restraint.getModelCount()
            if modelCount != None:
                return modelCount
            if i == MAX_RESTRAINTS_TO_TEST:
#                NTwarning("getModelCount returned None for the first %d restraints; giving up." % i)
                return None
#        NTwarning("getModelCount returned None for all %d restraints; giving up." % len(self))
        return None
    #end def

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
        self.Hbond = False       # Hbond: fix to keep information about Hbond restraints from CCPN
        self.violCountLower = 0   # Total lower-bound violations over 0.1 A
        self.violMax = 0.0   # Maximum violation
        self.violUpperMax = 0.0   # Max violation over upper bound
        self.violLowerMax = 0.0   # Max violation over lower bound

        # partitioning in intra, sequential, medium-range and long-range, ambigous
        self.intraResidual = NTlist()
        self.sequential = NTlist()
        self.mediumRange = NTlist()
        self.longRange = NTlist()
        self.ambigious = NTlist()

        # Duplicate analysis
        self.uniqueDistancesCount = 0        # count of all defined distance restraints
        self.withoutDuplicates = NTlist() # list of all restraints without duplicates
        self.withDuplicates = NTlist() # list of all restraints with duplicates
    #end def

    def criticize(self, project, toFile = True):
        """
        Criticize restraints of this list; infer own ROG score from individual restraints.
        """
#        NTdebug('DistanceRestraintList.criticize %s', self)

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
            NTdetail('==> Analyzing %s, output to %s', self, path)
        #end if
    #end def

    def simplify(self):
        """Look at Wattos code for a full set of code that does any simplification"""
        for dr in self:
            dr.simplify()

    def analyze(self):
        """
        Calculate averages for every restraint.
        Partition restraints into classes.
        Analyse for duplicate restraints.

        Return <rmsd>, sd and total violations over 0.1, 0.3, 0.5 A as tuple
        or (None, None, None, None, None) on error
        """

#        NTdebug('DistanceRestraintList.analyze: %s', self)

        if (len(self) == 0):
            # happens for entry 2k0e imported from CCPN. Has unlinked restraints.
#            NTdebug('DistanceRestraintList.analyze: "%s" empty list'% self.name )
            return (None, None, None, None, None)
        #end if

        modelCount = self.getModelCount()
        if not modelCount:
            NTerror('DistanceRestraintList.analyze: "%s" modelCount %s' % (self.name, modelCount))
            return (None, None, None, None, None)
        #end if

        # check for duplicate
        self.findDuplicates()

        self.rmsd = NTfill(0.0, modelCount)
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
        self.ambigious = NTlist()

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
            if dr.isAmbigious(): self.ambigious.append(dr)
        #end for

        #Set max violations
        for p in ['violMax', 'violUpperMax', 'violLowerMax']:
            l = self.zap(p)
            l.sort()
            setattr(self, p, l[-1])
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
        self.rmsdAv, self.rmsdSd, _n = NTaverage(self.rmsd)
        return (self.rmsdAv, self.rmsdSd, self.violCount1, self.violCount3, self.violCount5)
    #end def

    def findDuplicates(self):
        """Find the duplicate entries in the list
        """
        pairs = {}
        for dr in self:
            dr.atomPairs.sort() # improves matching for ambigious restraints
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

    def format(self, allowHtml = False):
        msg = sprintf(
'''
classes
  sequential:         %4d
  intra-residual:     %4d
  medium-range:       %4d
  long-range:         %4d
  ambigious:          %4d

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
                        len(self.intraResidual), len(self.sequential), len(self.mediumRange), len(self.longRange), len(self.ambigious),

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
        return msg
    #end def

    def formatHtml(self):

        header = self.name
        if hasattr(self, 'rogScore'):
            if self.rogScore.isCritiqued():
                header = '<font color="%s">%s</font>' % (self.rogScore.colorLabel, header)
        header = '<h3>DistanceRestraintList %s</h3>' % header

        msg = '''%s
<BR>
<table>
<TR><TD>sequential    </TD><TD align="right">%4d</TD></TR>
<TR><TD>intra-residual</TD><TD align="right">%4d</TD></TR>
<TR><TD>medium-range  </TD><TD align="right">%4d</TD></TR>
<TR><TD>long-range    </TD><TD align="right">%4d</TD></TR>
<TR><TD>ambigious     </TD><TD align="right">%4d</TD></TR>
<TR><TD>sum           </TD><TD align="right">%4d</TD></TR>
</table>
<BR>
<table>
<TR><TD>rmsd</TD>               <TD> %s +- %s                    </TD></TR>
<TR><TD>violations <-0.1 A (lower-bound violations)</TD><TD align="right"> %4d </TD></TR>
<TR><TD>violations > 0.1 A </TD><TD align="right"> %4d                          </TD></TR>
<TR><TD>violations > 0.3 A </TD><TD align="right"> %4d                          </TD></TR>
<TR><TD>violations > 0.5 A </TD><TD align="right"> %4d                          </TD></TR>
</table>
''' % (
    header,
    len(self.intraResidual),
    len(self.sequential),
    len(self.mediumRange),
    len(self.longRange),
    len(self.ambigious),
    len(self),
    val2Str(self.rmsdAv, "%7.3f", 7), val2Str(self.rmsdSd, "%6.3f", 6),
    self.violCountLower,
    self.violCount1,
    self.violCount3,
    self.violCount5
  )
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
    #end def

    def isValidForAquaExport(self):
        """Determine if the restraint can be exported to Aqua.
        Simplified to checking if there are 4 real atoms.
        """
        if not self.atoms:
            NTdebug("Failed to find any atom in %s" % self)
            return False
        l = len(self.atoms)
        if l != 4:
            NTdebug("Expected four atoms but found %d in:\n%s" % (l,self))
            return False
        for i, atom in enumerate(self.atoms):
            if not atom:
                NTdebug("Failed to find valid atom in:\n%s" % (i,self))
                return False
        return True
    #end def

    def criticize(self, project):
        """Only the self violations,violMax and violSd needs to be set before calling this routine"""
#        NTdebug( '%s (dih)' % self )
        if (project.valSets.AC_MAXALL_BAD != None) and (self.violMax >= project.valSets.AC_MAXALL_BAD):
            comment = 'violMax: %7.2f' % self.violMax
#            NTdebug(comment)
            self.rogScore.setMaxColor(COLOR_RED, comment)
        elif (project.valSets.AC_MAXALL_POOR != None) and (self.violMax >= project.valSets.AC_MAXALL_POOR):
            comment = 'violMax: %7.2f' % self.violMax
#            NTdebug(comment)
            self.rogScore.setMaxColor(COLOR_ORANGE, comment)

        if (project.valSets.AC_THRESHOLD_OVER_POOR != None) and (project.valSets.AC_THRESHOLD_FRAC_POOR != None):
            fractionAbove = getFractionAbove(self.violations, project.valSets.AC_THRESHOLD_OVER_POOR)
            if fractionAbove >= project.valSets.AC_THRESHOLD_FRAC_POOR:
                comment = 'fractionAbove: %7.2f' % fractionAbove
    #            NTdebug(comment)
                self.rogScore.setMaxColor(COLOR_ORANGE, comment)

        if (project.valSets.AC_THRESHOLD_OVER_BAD != None) and (project.valSets.AC_THRESHOLD_FRAC_BAD != None):
            fractionAbove = getFractionAbove(self.violations, project.valSets.AC_THRESHOLD_OVER_BAD)
            if fractionAbove >= project.valSets.AC_THRESHOLD_FRAC_BAD:
                comment = 'fractionAbove: %7.2f' % fractionAbove
    #            NTdebug(comment)
                self.rogScore.setMaxColor(COLOR_RED, comment)

        if (project.valSets.AC_RMSALL_BAD != None) and (self.violSd >= project.valSets.AC_RMSALL_BAD):
            comment = 'violSd: %7.2f' % self.violSd
#            NTdebug(comment)
            self.rogScore.setMaxColor(COLOR_RED, comment)
        elif (project.valSets.AC_RMSALL_POOR != None) and (self.violSd >= project.valSets.AC_RMSALL_POOR):
            comment = 'violSd: %7.2f' % self.violSd
#            NTdebug(comment)
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
#                    NTdebug(msg)
                    self.rogScore.setMaxColor(COLOR_RED, msg)
    #end def

    def calculateAverage(self):
        """Calculate the values and violations for each model
        return cav and cv tuple or (None, None) tuple on error
        """

        if len(self.atoms) != 4 or (None in self.atoms):
            NTerror('DihedralRestraint: invalid dihedral definition %s', self.atoms)
            return (None, None)
        #end if

        if None in self.atoms.zap('meanCoordinate'):
            NTerror('DihedralRestraint: atom(s) without coordinates %s', self.atoms)
            return (None, None)
        #end if

        modelCount = self.getModelCount()
        if modelCount == 0:
            NTerror('DihedralRestraint: no structure models')
            return (None, None)
        #end if


        #set the default values (JFD: this needs to be fully done in initializer in case code fails as for issue 222)
        self.dihedrals = NTlist() # list with dihedral values for each model
        self.cav = None      # Average dihedral value
        self.cv = None      # cv on dihedral
#        self.min        = 0.0      # Minimum dihedral
#        self.max        = 0.0      # Max dihedral
        self.violations = NTlist() # list with violations for each model
        self.violCount1 = 0        # Number of violations over 1 degree
        self.violCount3 = 0        # Number of violations over 3 degrees
        self.violCount5 = 0        # Number of violations over 5 degrees
        self.violMax = 0.0      # Maximum violation
        self.violAv = 0.0      # Average violation
        self.violSd = 0.0      # Sd of violations

        try:
            for i in range(modelCount):
                d = NTdihedralOpt(
                                self.atoms[0].coordinates[i],
                                self.atoms[1].coordinates[i],
                                self.atoms[2].coordinates[i],
                                self.atoms[3].coordinates[i]
                              )
                self.dihedrals.append(d)
            #end for
        except:
            pass # ignore missing coordinates. They're reported by criticize()

        #find the range to store these dihedral values
        #limit = 0.0
        #if limit > self.lower: limit = -180.0
        #self.dihedrals.limit(limit, limit+360.0)

        plotpars = plotParameters.getdefault(self.retrieveDefinition()[1],
                                             'dihedralDefault')

        self.dihedrals.limit(plotpars.min, plotpars.max)

        # Analyze violations, account for periodicity
        for d in self.dihedrals:
            v = violationAngle(value = d, lowerBound = self.lower, upperBound = self.upper)
            if v == None: # already send a message
                continue
            fv = math.fabs(v)
            self.violations.append(v)
            if fv > 1.0: self.violCount1 += 1
            if fv > 3.0: self.violCount3 += 1
            if fv > 5.0: self.violCount5 += 1
            if fv > self.violMax:
                self.violMax = fv
            #end if
        #end for
        self.violAv, self.violSd, _n = self.violations.average()

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
        if name:
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

    def format(self):
        return  \
            sprintf('%-25s %-6s (Target: %s %s)  (Models: cav %6s cv %7s)  ' + \
                    '(Violations: av %4s max %4.1f counts %2d,%2d,%2d) %s',
                     self, self.rogScore,
                     val2Str(self.lower, "%4.1f", 4),
                     val2Str(self.upper, "%4.1f", 4),
                     val2Str(self.cav, "%6.1f", 6),
                     val2Str(self.cv, "%7.4f", 7),
                     val2Str(self.violAv, "%4.1f", 4),
                     self.violMax, self.violCount1, self.violCount3, self.violCount5,
                     self.atoms.format('%-11s ')
                    )
    #end def
#end class


class DihedralRestraintList(RestraintList):

    def __init__(self, name, status = 'keep'):
        RestraintList.__init__(self, name, status = status)
        self.__CLASS__ = ACL_LEVEL
    #end def

    def criticize(self, project, toFile = True):
        """
        Criticize restraints of this list; infer own ROG score from individual restraints.
        """
#        NTdebug('DihedralRestraintList.criticize %s', self)

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
            NTdetail('==> Analyzing %s, output to %s', self, path)
        #end if
    #end def

    def analyze(self, calculateFirst = True):
        """
        Calculate averages for every restraint.
        Return <rmsd>, sd and total violations over 1, 3, and 5 degrees as tuple
        or (None, None, None, None, None) on error
        """

        NTdebug('DihedralRestraintList.analyze: %s', self)

        if not len(self):
            NTerror('DihedralRestraintList.analyze: "%s" empty list', self.name)
            return (None, None, None, None, None)
        #end if

        modelCount = self.getModelCount()
        if not modelCount:
            NTerror('DihedralRestraintList.analyze: "%s" modelCount 0', self.name)
            return (None, None, None, None, None)
        #end if

        self.rmsd = NTfill(0.0, modelCount)
        self.violCount1 = 0
        self.violCount3 = 0
        self.violCount5 = 0
        for dr in self:
            if calculateFirst:
                (cav, _cv) = dr.calculateAverage()
                if cav == None:
#                    NTdebug("Failed to calculate average for: " + self.format())
                    continue # skipping dihedral with a missing coordinate or so.
            self.violCount1 += dr.violCount1
            self.violCount3 += dr.violCount3
            self.violCount5 += dr.violCount5
            for i in range(len(dr.violations)): # happened in entry 1bn0 that violations were not defined.
#            for i in range(0, modelCount):
                v = dr.violations[i]
                self.rmsd[i] += v * v
            #end for
        #end for

        for i in range(0, modelCount):
            self.rmsd[i] = math.sqrt(self.rmsd[i] / len(self))
        #end for

        self.rmsdAv, self.rmsdSd, _n = NTaverage(self.rmsd)
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
<TR><TD>count               </TD><TD align="right">%4d</TD></TR>
<TR><TD>rmsd:               </TD><TD> %s +- %s                    </TD></TR>
<TR><TD>violations > 1 degree</TD><TD align="right"> %4d                          </TD></TR>
<TR><TD>violations > 3 degrees</TD><TD align="right"> %4d                          </TD></TR>
<TR><TD>violations > 5 degrees</TD><TD align="right"> %4d                          </TD></TR>
</table>
''' % (
    header,
    len(self),
    val2Str(self.rmsdAv, "%7.3f", 7), val2Str(self.rmsdSd, "%6.3f", 6),
    self.violCount1,
    self.violCount3,
    self.violCount5
  )
        return msg
    #end def
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
            NTerror('Error RDCRestraint: no structure models\n')
            return (None, None)
        #end if

#TODO needs work
#        if len(self.atoms) != 2 or None in self.atoms:
#            NTerror('Error RDCRestraint: invalid rdc definition %s\n', self.atoms )
#            return (None,None)
#        #end if
#
#        if None in self.atoms.zap('meanCoordinate'):
#            NTerror('Error RDCRestraint: atom without coordinates %s\n', self.atoms )
#            return (None,None)
#        #end if

        #set the default values; do not remove or it will crash upon restoring RDC lists
        self.rdcs = NTfill(0.0, modelCount) # list with dihedral values for each model
        self.cav = NaN      # Average dihedral value
        self.cv = NaN      # cv on dihedral
#        self.min        = 0.0      # Minimum dihedral
#        self.max        = 0.0      # Max dihedral
        self.violations = NTfill(0.0, modelCount) # list with violations for each model
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
            s = s + sprintf('(%-11s - %11s)   ', p[0]._Cname(1), p[1]._Cname(1))
        #end for
        return s.strip()
    #end def

    def format(self):
#        s = '('
#        for p in self.atoms:
#            s = s + sprintf('%-11s ', p._Cname(1) )
#        #end for
#        s = s.strip() + ')'
        return  sprintf('%-25s %-6s (Target: %6.1f %6.1f) %s',
                        str(self), self.rogScore,
                        self.lower, self.upper,
                        self._names()
                       )

    #end def
#end class


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

        NTdebug('RDCRestraintList.analyze: %s', self)

        if len(self) == 0:
            NTerror('RDCRestraintList.analyze: "%s" empty list', self.name)
            return (None, None, None, None, None)
        #end if

        modelCount = 0
        firstRestraint = self[0]
        if not hasattr(firstRestraint, "atoms"):
            NTwarning("Failed to get the model count for no atoms are available in the first RDC restraint.")
            NTwarning("See also issue: %s%d" % (issueListUrl, 133))
        else:
            if len(self[0].atomPairs):
                modelCount = self[0].atomPairs[0][0].residue.chain.molecule.modelCount
        #end if

        if not modelCount: # JFD notes eg reading $CINGROOT/Tests/data/ccpn/2hgh.tgz
            NTerror('RDCRestraintList.analyze: "%s" modelCount 0', self.name)
            return (None, None, None, None, None)
        #end if

        self.rmsd = NTfill(0.0, modelCount)
        self.violCount1 = 0
        self.violCount3 = 0
        self.violCount5 = 0
        for dr in self:
            if calculateFirst:
                dr.calculateAverage()
            if dr.rdcs == None or dr.violations == None:
                NTerror('RDCRestraintList.analyze: skipping restraint %s', dr)
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

        self.rmsdAv, self.rmsdSd, dummy_n = NTaverage(self.rmsd)
        return (self.rmsdAv, self.rmsdSd, self.violCount1, self.violCount3, self.violCount5)
    #end def

    def criticize(self, project, toFile = True):
        """
        Criticize restraints of this list; infer own ROG score from individual restraints.

        Need implementation
        """

        NTdebug('RDCRestraintList.criticize %s', self)

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
#            NTdetail('Distance restraint analysis %s, output to %s', self, path)
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

    def __call__(self, line, timeStamp = True):
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
        NTindent(depth, stream, indent)
        fprintf(stream, "<History>")
        fprintf(stream, lineEnd)

        for a in self:
            NTtoXML(a, depth + 1, stream, indent, lineEnd)
        #end for
        NTindent(depth, stream, indent)
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
        if items == None: return None
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
        self.__FORMAT__ = self.header(dots) + '\n' + \
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
