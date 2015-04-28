import os
import cing
import cing.Libs.disk
import cing.Libs.io as io
from cing.Legacy.Legacy100.upgrade100 import upgrade100
from cing.core.molecule import Molecule


def upgrade095(project, restore):
    for molName in project.moleculeNames:
        pathName = project.molecules.path(molName)
        mol = openMol_094(pathName+'.molecule')
        mol.save(pathName)
        cing.Libs.disk.remove(pathName+'.molecule')
    #end for
    # restore
    project.restore()
    # Save to consolidate
    project.save()
    return upgrade100(project,restore)
#end def


def openMol_094(path)   :
    """Static method to restore molecule from SML file path: 0.75< version <= 0.90
       returns Molecule instance or None on error
    """
    #print '*** Opening using Molecule.openMol_094'

    if (not os.path.exists( path )):
        io.error('Molecule.open: smlFile "{0}" not found\n', path)
        return None
    #end if

    mol = Molecule.SMLhandler.fromFile(path)  # pylint: disable=E1101
    if not mol:
        io.error('openMol_094: open from "{0}" failed\n', path)
        return None
    #end if

    mol._check()
    mol.updateAll()

    return mol
#end def

