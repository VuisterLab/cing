'''
Created on Apr 6, 2010

@author: jd
'''
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.pdb import defaultPrintChainCode
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport

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
    cing.verbosity = verbosityOriginal
    NTmessage("Sequence from PDB file:")
    NTmessage(fastaString)

    for res in project.molecule.allResidues():
        NTmessageNoEOL(res.shortName)
    NTmessage('')
    cing.verbosity = cing.verbosityError

    project.removeFromDisk()
    del project
    cing.verbosity = verbosityOriginal

