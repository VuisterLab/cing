'''
Created on Jun 7, 2010

@author: jd
'''
from cing.Libs.pdb import initPDB
from cing.Scripts.PyMol.createProtein import reportsDir
from cing.core.classes import Project
from cing.core.constants import IUPAC
import glob
import os
import cing

cing.verbosity = cing.verbosityDebug

os.chdir(reportsDir)

pdbFileList = glob.glob('*.pdb')

#for pdbFile in pdbFileList[1:2]:
pdbFileFound = pdbFileList[0]
for pdbFile in pdbFileList:
#for pdbFile  in [ pdbFileFound ]:
    x = len(pdbFile) - 4
    entryId = pdbFile[0:x]
    project = Project.open(entryId, status='new')
    initPDB(project, pdbFile, convention=IUPAC)
    project.validate(doProcheck=False,doWhatif=False,htmlOnly=False)
