'''
Created on Mar 30, 2010

@author: jd
'''

from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from glob import glob
from yasaramodule import * #@UnusedWildImport
import yasara #@UnusedImport @UnresolvedImport

#filename = '/Users/jd/CASD-NMR-CING/data/eR/NeR103ACheshire/Author/mod.pdb'
#LoadPDB(filename, center=None, correct=None, model=None, download=None)
#SavePDB All,/Users/jd/CASD-NMR-CING/data/eR/NeR103ACheshire/Author/mod_Yasara.pdb,Format=IUPAC,Transform=No

yasara.info.mode = 'txt'
yasara.Console('off')


os.chdir(cingDirTmp)
os.chdir('Models')
cwd = os.getcwd()

fileList = glob('*')
for fn in fileList[0:10]:
    #if True:
#    fn = fileList[1]
    #fn = 'x.pdb'
    entryCode = fn[:-2]
    fnFull = os.path.join(cwd,fn)
    NTmessage('Add hydrogens using Yasara on %s' % fnFull)
    obj = yasara.LoadPDB(fnFull, center = 'No', correct = 'No', model=1)
    #    yasara.CleanAll() # needed for OptHydObj
    #    yasara.OptHydObj(obj,method='Yasara')
    yasara.DelHydObj(obj)
    yasara.AddHydObj(obj)
    outputDir = '/Users/jd/CASP-NMR-CING/data/05/%s/Author' % entryCode
    if not os.path.exists(outputDir):
        mkdirs(outputDir)
    newPdbFileName = os.path.join( outputDir, entryCode+".pdb")
    yasara.SavePDB(obj,newPdbFileName,format='IUPAC', transform='No')
    yasara.Clear()
    #    yasara.StopPlugin()
    #    yasara.Exit()
