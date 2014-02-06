"""
Code to upgrade all project <= 1.0
"""
import cing
import cing.definitions as cdefs
import cing.constants
from cing.core.classes import Project
from cing.core.molecule import Molecule
from cing.Libs.NTutils import nTdebug
from cing.Libs.NTutils import nTmessage
from cing.Libs.NTutils import xML2obj
from cing.core.sml import sml2obj
from cing.Libs import disk


def upgradeToSml( name, restore  ):


    nTdebug('upgradeToSml: restoring %s', name)

    root, newName = Project.rootPath(name)
    if not root:
        nTerror('upgradeToSml: unable to open Project "%s" because root is [%s].', name, root)
        return None
    if not root.exists():
        nTerror('upgradeToSml: unable to open Project "%s" because root [%s] was not found.', name, root)
        return None
    #end if

    pfile = root / 'project.xml' # Name in all versions <= 1.0
    # Check if we find the xml file
    if pfile.exists():
        nTmessage('==> Upgrading cing project; please stand by')
        #GWV: 20140203: cannot do an update method() -> errors in partioning restraints. Do not understand
        pr = xML2obj(pfile)

        if pr == None:
            nTerror('upgradeToSml: parsing from project file "%s" failed', pfile)
            return None

        try:
            # <= 0.75 version have string
            pr.version = float(pr.version.strip('abcdefghijklmnopqrtsuvw ()!@#$%^&*').split()[0])
        except:
            pass

        pr._save2sml()
        disk.rename(pfile, pfile + '.save')
        #now we should be able to open it again
        return Project.open( name, status = 'old', restore = restore )

    else:
        nTerror('upgradeToSml: missing Project file "%s"', pfile)
        return None
    #end if
#end def

def restoreQueeny100( project, tmp=None ):
    """
    Restore queeny results from sml file.

    Return True on error
    """
    if project == None:
        nTmessage("restoreQueeny100: No project defined")
        return True

    if project.molecule == None:
        return False # Gracefully returns

    queenyDefs = project.getStatusDict(QUEENY_STR)

    if not queenyDefs.completed:
        return # Return gracefully

    path = project.validationPath( queenyDefs.directory)
    if not path:
        nTerror('restoreQueeny100: directory "%s" with queeny data not found', path)
        return True

    smlFile = path / queenyDefs.smlFile
    if not smlFile.exists():
        nTerror('restoreQueeny100: file "%s" with queeny data not found', path)
        return True

    # Restore the data
    for storedProp in storedPropList:
        for res in project.molecule.allResidues():
            res[storedProp] = 0.0
        for atm in project.molecule.allAtoms():
            atm[storedProp] = 0.0
    #end for
    myList=sml2obj( smlFile, project.molecule)
    if myList==None:
        nTerror('restoreQueeny100: Failed restoring Queeny results from %s (code version %s)', smlFile, queenyDefs.saveVersion)
        return True

    try:
        for tupleInfo in myList:
            if len(tupleInfo) == 3: # Version with multiple data items
                nameTuple,storedProp,info = tupleInfo
            else: # Old version with multiple data items
                nameTuple,info = tupleInfo
                storedProp = QUEENY_INFORMATION_STR
            obj = project.molecule.decodeNameTuple(nameTuple)
            if not obj:
                atomName = nameTuple[3]
                if not (atomName in ATOM_LIST_TO_IGNORE_REPORTING):
                    nTerror('restoreQueeny100: error decoding "%s"', nameTuple)
                    # Was reporting terminal atoms eg. in "('1buq', 'A', 39, 'H2', None, None, 'INTERNAL_1')"
            else:
                obj[storedProp] = info
    except:
        nTtracebackError()
        nTerror("restoreQueeny100: Failed to restore Queeny results.")
        return True

    #success
    nTmessage('restoreQueeny100: Restored Queeny results from %s (code version %s)', smlFile, queenyDefs.saveVersion)
    return False
#end def

def restoreTalosPlus100(project):
    """
    Restore talos+ results from sml file.

    Return True on error
    """
    if project == None:
        nDebug("restoreTalosPlus100: No project defined")
        return True

    if project.molecule == None:
        return True # Gracefully returns

    for res in project.molecule.allResidues():
        res.talosPlus = None

    talosDefs = project.getStatusDict('talosPlus')

    if not talosDefs.completed:
        nDebug('restoreTalosPlus100: talosPlus not completed')
        return True

    if not talosDefs.parsed:
        nDebug('restoreTalosPlus100: talosPlus not parsed')
        return project.parseTalosPlus()

    path = project.validationPath( talosDefs.directory)
    if not path:
        nDebug('restoreTalosPlus100: directory "%s" with talosPlus data not found', path)
        return True

    smlFile = path / talosDefs.smlFile
    if smlFile.exists():
        # Restore the data
        nTdebug('restoreTalosPlus100: Restoring talos+ results from %s (code version %s)', smlFile, talosDefs.saveVersion)
        l=sml2obj( smlFile, project.molecule)
        if l != None:
            talosDefs.present = True
            return False
        #endif
    #end if
    nTdebug('restoreTalosPlus100: restoring talosPlus data from "%s" failed; reverting to parsing', smlFile)
    return project.parseTalosPlus()
#end def

def upgrade100(project, restore):
    """
    Do all things to upgrade project to current configuration
    All versions <= 1.00
    """
    nTmessage('*** upgrade100: upgrading %s from version %s ... ***', project, project.version)
    verbosity = cing.verbosity
    cing.verbosity = cing.verbosityWarning

    # Molecules
    for molName in project.moleculeNames:
        pathName = project.molecules.path(molName)
        mol = Molecule.open(pathName)
        if mol:
            mol.status = 'keep'
            project.appendMolecule(mol)
        #end if
    #end for

    # restore the lists
    for pl in [project.peaks, project.distances, project.dihedrals, project.rdcs, project.coplanars]:
        pl.restore()
    #end for

    # Now patch talos+
    if restoreTalosPlus100(project):
        nTerror('upgrade100: restoring talosPlus data failed')
        return None
    project.saveTalosPlus()

    # Now patch queeny
    if restoreQueeny100(project):
        nTerror('upgrade100: restoring queeny data failed')
        return None
    project.saveQueeny()


    # Plugin registered functions
    for p in cing.plugins.values():
        if p.isInstalled:
            #nTdebug("upgrade100: %s" % p.module)
            for f, obj in p.restores:
                nTdebug("upgrade100: Restoring with %s( %s, %s )" % (f,project,obj))
                f(project, obj)
            #end for
        #end if
    #end for

    # save to consolidate
    project.save()

    cing.verbosity = verbosity
    return Project.open( project.name, 'old', restore=restore)
#end def

