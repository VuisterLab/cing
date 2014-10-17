"""
Code to upgrade all project <= 1.0
"""
import sys

import cing
from cing import constants
from cing.constants import definitions as cdefs
from cing.PluginCode import queeny

from cing.core import validation
from cing.core import sml
from cing.core.classes import Project
from cing.core.classes import StatusDict
from cing.core.molecule import Molecule
import cing.core.pid as pid
from cing.Libs import io
import cing.Libs.NTutils as ntu
from cing.Libs.NTutils import nTdebug
from cing.Libs.NTutils import nTmessage
from cing.Libs.NTutils import nTerror

from cing.Libs import disk
from cing.Libs.Adict import Adict
import cing.Libs.xmlTools as xmlTools


def upgradeProject2Json( name, restore  ):
    """Upgrade the project from project.xml to project.json file
    Convert several parameters to new Adict types
    """
    io.debug('upgradeToJson: restoring {0}\n', name)

    root, newName, ext = Project.rootPath(name)
    if not root:
        io.error('upgradeToJson: unable to open Project "{0}" because root is [{1}]\n', name, root)
        return None
    if not root.exists():
        io.error('upgradeToJson: unable to open Project "{0}" because root [{1}] was not found\n', name, root)
        return None
    #end if

    pfile = root / 'project.xml' # Name in all versions <= 1.0
    # Check if we find the xml file
    if pfile.exists():
        io.message('==> Upgrading cing project; please stand by\n')
        #GWV: 20140203: cannot do an update method() -> errors in partioning restraints. Do not understand
        pr = xmlTools.xML2obj(pfile)

        if pr is None:
            io.error('upgradeToJson: parsing from project file "{0}" failed\n', pfile)
            return None

        try:
            # <= 0.75 version have string
            pr.version = float(pr.version.strip('abcdefghijklmnopqrtsuvw ()!@#$%^&*').split()[0])
        except:
            pass

        # change to Time object
        pr.created = io.Time.fromString(pr.created)
        pr.lastSaved = io.Time(disk.modtime(pfile))

        # change types of names list
        for listName in 'moleculeNames peakListNames distanceListNames dihedralListNames rdcListNames'.split():
            #print 'listName>>',listName, (listName in pr)
            if listName in pr:
                pr[listName] = [n for n in pr[listName]]

        # update from old status type
        status = Adict()
        for key in constants.VALIDATION_KEYS:
            sdict = StatusDict(key)
            status[key] = sdict
            # if not isinstance(sdict, StatusDict):
            #     sdict = StatusDict(key)
            if key in pr.status:
                # print 'upgrade2json> key=', key
                # not certain if we get dict or NTdict; this circumvent unwanted keys of NTdict
                for k,v in pr.status[key].items():
                    #print 'upgrade2json>> k,v', k,v
                    sdict[k] = v
                #print '>>>\n', sdict.formatItems()
            #end if
        #end for

        #end for
        # update the status from old definitions;
        for (key, statusName) in [
                (constants.SHIFTX_KEY, 'shiftxStatus'),
                (constants.PROCHECK_KEY,'procheckStatus'),
                (constants.DSSP_KEY, 'dsspStatus'),
                (constants.WHATIF_KEY, 'whatifStatus'),
                (constants.WATTOS_KEY, 'wattosStatus'),
                (constants.VASCO_KEY, 'vascoStatus'),
                (constants.X3DNA_KEY, 'x3dnaStatus')
            ]:
            sdict = status[key]
            if statusName in pr:

                #print 'upgrade2json> statusName=', statusName

                # not certain if we get dict or NTdict; this circumvent unwanted keys of NTdict
                for k,v in pr[statusName].items():
                    #print 'upgrade2json>> k,v=', k,v
                    sdict[k] = v
                #print '>>>\n', sdict.formatItems()
            #end if
            #LEGACY names
            pr[statusName] = sdict
        #end for
        # update some fields if present
        for sdict in status.values():
            if 'molecule' in sdict and isinstance(sdict['molecule'], tuple):
                sdict['molecule'] = pid.Pid.new('Molecule:' + sdict['molecule'][0])
            if 'moleculeName' in sdict and isinstance(sdict['molecule'], tuple):
                sdict['molecule'] = pid.Pid.new('Molecule:' + sdict['moleculeName'][0])
                del sdict['moleculeName']
            if 'runVersion' in sdict:
                sdict['version'] = sdict['runVersion']
                del sdict['runVersion']
            if 'smlFile' in sdict:
                del sdict['smlFile']
#            sdict['date'] = io.Time(1360158182.7)  # Wed Feb  6 13:43:02 2013
            sdict['date'] = io.Time(pr.lastSaved) # make a copy because otherwise the json handler breaks
            sdict['version'] = 0.95  # old version
        #end for
        # make this the new status dict
        pr.status = status

        #print '>>>>>\n', pr.status.queeny.formatItems()

        pr._save2json()
        disk.rename(pfile, pfile + '.save')
        #now we should be able to open it again
        return Project.open( name, status = constants.PROJECT_OLD, restore = restore )

    else:
        io.error('upgradeToJson: missing Project file "{0}"\n', pfile)
        return None
    #end if
#end def


def restoreQueeny100( project, tmp=None ):
    """
    Restore queeny results from sml file.

    Return True on error
    """
    if project is None:
        nTmessage("restoreQueeny100: No project defined")
        return True

    if project.molecule is None:
        return False # Gracefully returns

    queenyDefs = project.getStatusDict(constants.QUEENY_KEY)

    if not queenyDefs.completed: # old definition
        nTdebug('restoreQueeny100: no queeny completed')
        return False # Return gracefully

    path = project.validationPath( queenyDefs.directory)
    if not path:
        nTerror('restoreQueeny100: directory "%s" with queeny data not found', path)
        return True

    smlFile = path / queenyDefs.smlFile
    if not smlFile.exists():
        nTerror('restoreQueeny100: file "%s" with queeny data not found', path)
        return True

    # Restore the data
    for storedProp in [constants.QUEENY_UNCERTAINTY1_STR, constants.QUEENY_UNCERTAINTY2_STR, constants.QUEENY_INFORMATION_STR ]:
        for res in project.molecule.allResidues():
            res[storedProp] = 0.0
        for atm in project.molecule.allAtoms():
            atm[storedProp] = 0.0
    #end for

    myList=sml.sml2obj( smlFile, project.molecule)
    if myList==None:
        nTerror('restoreQueeny100: Failed restoring Queeny results from %s (code version %s)', smlFile, queenyDefs.saveVersion)
        return True

    try:
        for tupleInfo in myList:
            if len(tupleInfo) == 3: # Version with multiple data items
                nameTuple,storedProp,info = tupleInfo
            else: # Old version with multiple data items
                nameTuple,info = tupleInfo
                storedProp = constants.QUEENY_INFORMATION_STR
            obj = project.molecule.decodeNameTuple(nameTuple)
            if not obj:
                atomName = nameTuple[3]
                if not (atomName in constants.ATOM_LIST_TO_IGNORE_REPORTING):
                    nTerror('restoreQueeny100: error decoding "%s"', nameTuple)
                    # Was reporting terminal atoms eg. in "('1buq', 'A', 39, 'H2', None, None, 'INTERNAL_1')"
                return True
            #end if
            obj[storedProp] = info
    except:
        ntu.nTtracebackError()
        nTerror("restoreQueeny100: Failed to restore Queeny results.")
        return True
    #success
    # Store as new data structure
    for obj in project.molecule.allResidues() + project.molecule.allAtoms():
        qDict = queeny.QueenyResult()
        for storedProp in [constants.QUEENY_UNCERTAINTY1_STR, constants.QUEENY_UNCERTAINTY2_STR, constants.QUEENY_INFORMATION_STR ]:
            qDict[storedProp] = obj[storedProp]
        validation.setValidationResult(obj, constants.QUEENY_KEY, qDict)
    #end for
    queenyDefs.present = True
    nTmessage('restoreQueeny100: Restored Queeny results from %s (code version %s)', smlFile, queenyDefs.saveVersion)
    return False
#end def


def restoreShiftx100(project):
    """
    Restore shiftx results by parsing files.

    Return True on error
    """
    if project is None:
        nTdebug("restoreShiftx100: No project defined")
        return True

    if project.molecule == None:
        return True # Gracefully returns

    defs = project.getStatusDict(constants.SHIFTX_KEY)

    # Older versions; initialize the required keys of shiftx Status from xml file
    if project.version < 0.881:

        path = project.validationPath(cdefs.validationsDirectories.shiftx)
        if not path:
            nTerror('restoreShiftx100: directory "%s" with shiftx data not found', path)
            return True
        xmlFile = project.path() / 'content.xml'

        if not xmlFile.exists():
            nTerror('restoreShiftx100: Shiftx results xmlFile "%s" not found', xmlFile)
            return True
        #end if

        shiftxResult = xmlTools.xML2obj(xmlFile)
        if not shiftxResult:
            nTerror('restoreShiftx100: restoring Shiftx results from xmlFile "%s" failed', xmlFile)
            return None

        defs.update(shiftxResult)
        defs.completed = True
    #end if

    #update some of the settings
    if 'moleculeName' in defs:
        del defs['moleculeName']

    if 'path' in defs:
        defs.directory = disk.Path(defs.path)[-1:]
        del defs['path']
    else:
        defs.directory = constants.SHIFTX_KEY
    if 'contenFile' in defs:
        del defs['contentFile']

    if not defs.completed:
        nTdebug('restoreShiftx100: shiftx not completed')
        return True

    return project.parseShiftx()
#end defs


def restoreTalosPlus100(project):
    """
    Restore talos+ results by parsing files.

    Return True on error
    """
    if project is None:
        io.error("restoreTalosPlus100: No project defined\n")
        return True

    if project.molecule is None:
        return True # Gracefully returns

    talosDefs = project.getStatusDict('talosPlus')

    if not talosDefs.completed:
        io.error('restoreTalosPlus100: talosPlus not completed\n')
        return True

    return project.parseTalosPlus()
#end def


def upgrade100(project, restore):
    """
    Do all things to upgrade project to current configuration
    All versions <= 1.00
    """
    nTmessage('*** upgrade100: upgrading %s from version %s ***', project, project.version)
    verbosity = cing.verbosity
    # make sure we get all if we heave debug on
    if cing.verbosity < cing.verbosityDebug:
        cing.verbosity = cing.verbosityWarning

    # Molecules
    for molName in project.moleculeNames:
        pathName = project.molecules.path(molName)
        mol = Molecule.open(pathName)
        if mol:
            mol.status = 'keep'
            project.appendMolecule(mol)
        #end if
        nTdebug('upgrade100: restored %s', mol)
    #end for

    # restore the lists
    for pl in [project.peaks, project.distances, project.dihedrals, project.rdcs, project.coplanars]:
        pl.restore()
    #end for

    # Now patch talos+
    if restoreTalosPlus100(project):
        io.error('upgrade100: restoring talosPlus data failed\n')
    # project.saveTalosPlus()
    #
    # # Now patch queeny
    # if restoreQueeny100(project):
    #     nTerror('upgrade100: restoring queeny data failed')
    #     return None
    # project.saveQueeny()
    #
    # # Now patch shiftx
    # if restoreShiftx100(project):
    #     nTerror('upgrade100: restoring shiftx data failed')
    #     return None
    # project.saveShiftx()

    # Plugin registered functions
    nTdebug('upgrade100: calling plugins')
    project._callPluginRestores()

    # save to consolidate
    project.save()

    cing.verbosity = verbosity
    return Project.open(project.name, constants.PROJECT_OLD, restore=restore)
#end def

