'''
Created on Apr 6, 2010

@author: jd
'''
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTmessageNoEOL
from cing.Libs.NTutils import getDeepByKeysOrDefault
from cing.Libs.pdb import defaultPrintChainCode
from cing.core.classes import Project
from cing.core.constants import IUPAC
import cing

def printSequenceFromPdbFile(fn):
    verbosityOriginal = cing.verbosity
    cing.verbosity = cing.verbosityError
    entryId = 'getSequenceFromPdbFile'
    project = Project(entryId)
    project.removeFromDisk()
    project = Project.open(entryId, status='new')
    project.initPDB(pdbFile=fn, convention=IUPAC)
    fastaString = ''
    for res in project.molecule.allResidues():
        # db doesn't always exist.
        fastaString += getDeepByKeysOrDefault(res, defaultPrintChainCode, 'db', 'shortName')
    NTmessage("Sequence from PDB file:")
    NTmessage(fastaString)
    for res in project.molecule.allResidues():
        NTmessageNoEOL(res.shortName)
    NTmessage('')
    project.removeFromDisk()
    del project
    cing.verbosity = verbosityOriginal

