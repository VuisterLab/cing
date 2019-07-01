"""
script to extract NTdb info to json

"""
from __future__ import print_function

from cing import NTdb
import json


class DihedralDef(dict):
    """
    Simple class to store Dihedral definitions
    """
    # These definitions come from cing NTdb
    saveKeys = 'convention name aliases atoms karplus'.split()

    ATOMS = 'atoms'
    # List of atoms: (i, name) tuple
    # i:  -1=previous residue
    #      0=current residue
    #      1=next residue

    def __init__(self):
        for k in self.saveKeys:
            self[k] = None
        self.parent = None

    @property
    def name(self):
        return self['name']

    def updateFromDb(self, source):
        "Update from a NTdb entry"
        for k in self.saveKeys:
            self[k] = source[k]



class AtomDef(dict):
    """
    Simple class to store Atom definitions
    """
    # These definitions come from cing NTdb
    saveKeys = 'convention name nameDict aliases canBeModified topology  NterminalTopology CterminalTopology ' \
               'spinType shift hetatm properties'.split()

    def __init__(self):
        for k in self.saveKeys + 'pseudoAtom hasPseudoAtom isPseudoAtom realAtoms'.split():
            self[k] = None
        self.parent = None

    @property
    def name(self):
        return self['name']

    def updateFromDb(self, source):
        "Update from a NTdb entry"
        for k in self.saveKeys:
            self[k] = source[k]

        # update pseudo descriptions to more sensible names
        self['pseudoAtom'] = source['pseudo']
        self['hasPseudoAtom'] = source['pseudo'] is not None
        #
        self['isPseudoAtom'] = len(source['real']) > 0
        self['realAtoms'] = source['real']

    @property
    def isPseudoAtom(self):
        "Return True if it is a proton or pseudoAtom"
        return self['isPseudoAtom']

    @property
    def isProton(self):
        "Return True if it is a proton or pseudoAtom"
        return self['name'][0] == 'H' or (self['isPseudoAtom'] and self['realAtoms'][0][0] == 'H')

    @property
    def isCarbon(self):
        "Return True if it is a cabon"
        return self['name'][0] == 'C'

    @property
    def isNitrogen(self):
        "Return True if it is a Nitrogen"
        return self['name'][0] == 'N'


class ResidueDef(dict):
    """
    Simple class to store Residue definitions
    """
    # These definitions come from cing NTdb
    saveKeys = 'convention name commonName shortName nameDict canBeModified shouldBeSaved cingDefinition ' \
               'comment properties'.split()

    # These keys define the recursive structure
    ATOM_DEFS = 'atomDefs'
    DIHEDRAL_DEFS = 'dihedralDefs'

    def __init__(self):
        self[self.ATOM_DEFS] = []
        self[self.DIHEDRAL_DEFS] = []
        for k in self.saveKeys:
            self[k] = None

    @property
    def name(self):
        return self['name']

    def addAtomDef(self, atomDef):
        "Add an atomDef to the list"
        self[self.ATOM_DEFS].append(atomDef)
        atomDef.parent = self

    def addDihedralDef(self, dihedralDef):
        "Add an dihedralDef to the list"
        self[self.DIHEDRAL_DEFS].append(dihedralDef)
        dihedralDef.parent = self

    def updateFromDb(self, source):
        "Update from a NTdb entry"
        for k in self.saveKeys:
            self[k] = source[k]

        # Handle the atoms
        for a in source.atoms:
            aDef = AtomDef()
            aDef.updateFromDb(a)
            self.addAtomDef(aDef)

        # Handle the dihedrals
        for d in source.dihedrals:
            dDef = DihedralDef()
            dDef.updateFromDb(d)
            self.addDihedralDef(dDef)

    #------------------------------------------------------------------------------------------------------
    # atom-related properties
    #------------------------------------------------------------------------------------------------------
    @property
    def atoms(self):
        "Return atomsDefs as a dict"
        return dict([(a['name'], a) for a in self[self.ATOM_DEFS]])

    @property
    def atomNames(self):
        "Return a list of atoms names"
        return self.atoms.keys()

    @property
    def realAtoms(self):
        "Return all real atoms atomsDefs as a dict"
        return dict([(a['name'], a) for a in self[self.ATOM_DEFS] if not a.isPseudoAtom])

    @property
    def pseudoAtoms(self):
        "Return all real atoms atomsDefs as a dict"
        return dict([(a['name'], a) for a in self[self.ATOM_DEFS] if a.isPseudoAtom])

    @property
    def protons(self):
        "Return all proton atomsDefs as a dict"
        return dict([(a['name'], a) for a in self[self.ATOM_DEFS] if a.isProton])

    @property
    def carbons(self):
        "Return all proton atomsDefs as a dict"
        return dict([(a['name'], a) for a in self[self.ATOM_DEFS] if a.isCarbon])

    @property
    def nitrogens(self):
        "Return all proton atomsDefs as a dict"
        return dict([(a['name'], a) for a in self[self.ATOM_DEFS] if a.isNitrogen])

    #------------------------------------------------------------------------------------------------------
    # dihedral-related properties
    #------------------------------------------------------------------------------------------------------
    @property
    def dihedrals(self):
        "Return dihedralDefs as a dict"
        return dict([(a['name'], a) for a in self[self.DIHEDRAL_DEFS]])


    #------------------------------------------------------------------------------------------------------
    # Json save and restore
    #------------------------------------------------------------------------------------------------------
    def toJson(self, path=None):
        "Convert self to json string; optionally save to path"
        if path is None:
            return json.dumps(self, indent=4, sort_keys=True)
        else:
            with open(path, 'w') as fp:
                json.dump(self, fp, indent=4, sort_keys=True)

    def fromJson(self, path):
        "Restore self from json file path"
        with open(path, 'r') as fp:
            tmp = json.load(fp)
            self.update(tmp)
        print('tmp')

        # restore child objects
        self[self.ATOM_DEFS] = []
        for _name, theDict in self.atoms.items():
            print('>> name:', _name, theDict)
            aDef = AtomDef()
            aDef.update(theDict)
            self.addAtomDef(aDef)

        # restore child objects
        self[self.DIHEDRAL_DEFS] = []
        for _name, theDict in self.atoms.items():
            print('>> name:', _name, theDict)
            aDef = DihedralDef()
            aDef.update(theDict)
            self.addDihedralDef(aDef)


class CingDefs(dict):
    """
    Class to contain the Cing residue definitions
    """
    def updateFromDb(self, source):
        "Populate from source (the NTdb entry)"
        for dbRes in source:
            print('Handling:', dbRes)

            rDef = ResidueDef()
            rDef.updateFromDb(dbRes)
            self[rDef.name] = rDef

    #------------------------------------------------------------------------------------------------------
    # Json save and restore
    #------------------------------------------------------------------------------------------------------
    def toJson(self, path=None):
        "Convert content of self to json files; path should be a directory"
        if path is None:
            print('ERROR: path is None')
            return

        for name, rDef in self.items():
            rDef.toJson(path + rDef.name + '.json')

    def fromJson(self, path):
        "Restore self from json files in path"
        pass
        # with open(path, 'r') as fp:
        #     tmp = json.load(fp)
        #     self.update(tmp)

#------------------------------------------------------------------------------------------------------
# Code
#------------------------------------------------------------------------------------------------------

defs = CingDefs()
defs.updateFromDb(NTdb)
defs.toJson(path='../NTdb_json/')


