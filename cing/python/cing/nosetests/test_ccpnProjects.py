from nose import with_setup
import cing
import os

from cing import definitions as cdefs
from cing import constants
from cing.core import classes
from cing.core import molecule
from cing.Libs import io
from cing.Libs.Adict import Adict

project = None
cing.verbosity = 9

targets = Adict()

targets['1a4d'] = Adict(
    molecule = (2,41,1492,1),
    restraintLists = [
        ('distance_constraint_list', 375)
    ]
)
targets['1a24'] = Adict(
    molecule = (1,189,3449,20),
    restraintLists = [
        ('distance_constraint_list', 1671),
        ('hBond_constraint_list', 118),
        ('dihedral_constraint_list', 293),
    ]
)
targets['1afp'] = Adict(
    molecule = (1,51,929,40),
    restraintLists = [
        ('distance_constraint_list', 834),
    ]
)
targets['1ai0'] = Adict(
    molecule = (24,318,558,10),
    restraintLists = [
        ('distance_constraint_list', 4182),
        ('distance_constraint_list_1', 156),
        ('hBond_constraint_list', 24),
    ]
)
targets['1b4y'] = Adict(
    molecule = (1,30,1077,2),
    restraintLists = [
        ('distance_constraint_list', 141),
        ('distance_constraint_list_1', 71),
        ('distance_constraint_list_2', 430),
    ]
)
targets['1brv'] = Adict(
    molecule = (1,32,546,48),
    restraintLists = [
        ('distance_constraint_list', 264),
        ('dihedral_constraint_list', 29),
    ]
)
targets['1bus'] = Adict(
    molecule = (1,57,965,5),
    restraintLists = [
    ]
)
targets['1cjg'] = Adict(
    molecule = (4,168,3863,11),
    restraintLists = [
        ('distance_constraint_list', 1322),
        ('distance_constraint_list_1', 46),
        ('distance_constraint_list_2', 1342),
        ('distance_constraint_list_3', 122),
        ('hBond_constraint_list', 108),
    ]
)
targets['1hue'] = Adict(
    molecule = (2,180,3260,25),
    restraintLists = [
        ('distance_constraint_list', 2490),
        ('hBond_constraint_list', 50),
        ('dihedral_constraint_list', 160),
    ]
)
targets['1ieh'] = Adict(
    molecule = (1,135,2299,10),
    restraintLists = [
        ('distance_constraint_list', 2241),
    ]
)
targets['1iv6'] = Adict(
    molecule = (1,189,3449,20),
    restraintLists = [
        ('distance_constraint_list', 837),
        ('distance_constraint_list_1', 227),
        ('distance_constraint_list_2', 221),
        ('distance_constraint_list_3', 46),
        ('hBond_constraint_list', 48),
        ('hBond_constraint_list_1', 66),
        ('dihedral_constraint_list', 151),
    ]
)
targets['1kr8'] = Adict(
    molecule = (1,189,3449,20),
    restraintLists = [
        ('distance_constraint_list', 10),
        ('distance_constraint_list_1', 89),
        ('distance_constraint_list_2', 10),
        ('dihedral_constraint_list', 37),
        ('rdc_constraint_list', 38),
    ]
)
targets['2hgh'] = Adict(
    molecule = (1,189,3449,20),
    restraintLists = [
        ('distance_constraint_list', 24),
        ('distance_constraint_list_1', 432),
        ('distance_constraint_list_2', 71),
        ('distance_constraint_list_3', 6),
        ('distance_constraint_list_4', 372),
        ('distance_constraint_list_5', 6),
        ('distance_constraint_list_6', 250),
        ('distance_constraint_list_7', 312),
        ('hBond_constraint_list', 116),
        ('dihedral_constraint_list', 435),
    ]
)
targets['2k0e'] = Adict(
    molecule = (5,152,2647,160),
    restraintLists = [
        ('distance_constraint_list', 0),
        ('hBond_constraint_list', 0),
        ('dihedral_constraint_list', 97),
    ]
)

def setup_EmptyProject():
    global project
    project = classes.Project.open(target, constants.PROJECT_NEW)

def teardown_project():
    project.nosave = True
    path = project.path()
    project.close()
    path.remove()

#@with_setup(setup_EmptyProject,teardown_project)
def openCcpn(target, path):
    io.debug('\nopenCcpn: doing {0} from {1}\n', target, path)
    project = classes.Project.open(target, constants.PROJECT_NEW)
    assert project is not None
    p = project.initCcpn(path)
    assert p is not None
    io.debug('{0}\n',project.format())
    chains, residues, atoms, models = targets[target].molecule
    assert chains == len(project.molecule.allChains())
    assert residues == len(project.molecule.allResidues())
    assert atoms == len(project.molecule.allAtoms())
    assert models == project.molecule.modelCount
    for restraintList, n in targets[target].restraintLists:
        assert restraintList in project
        assert len(project[restraintList]) == n

    project.nosave = True
    p = project.path()
    io.debug('openCcpn: closing {0} and removing {1}\n', target, p)
    project.close()
    p.rmdir()

def test_openCcpnProjects():
    os.chdir(cdefs.cingDefinitions.tmpdir)
    dataPath = cdefs.cingDefinitions.rootPath / 'Tests' / 'data' / 'ccpn'
#    for target in '1a4d 1a24 1afp 1ai0 1b4y 1brv 1bus 1cjg 1d3z 1hkt 1hue 1ieh 1iv6 1jwe 1kr8 2hgh 2k0e'.split():
#    for target in '1brv'.split():
    for target in targets.keys():
        path = dataPath / target+'.tgz'
        if path.exists():
            openCcpn(target, path)

