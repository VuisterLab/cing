#!/usr/bin/env python -u

"""
Needed a place to store just one time use small scripts that replace some shell scripting
Expect this to be useless to others but still nice to have in svn to ensure backups.

To load:
from cing.Scripts.smallScriptCollection import *

To reload module copy 'n paste:
reload cing.Scripts.smallScriptCollection

Usually however execution from within Eclipse is still easiest.
"""
#import cing #@UnusedImport
from cing import cingDirScripts
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode import Whatif
from cing.PluginCode import dssp
from cing.PluginCode import molgrap
from cing.PluginCode import procheck
from cing.PluginCode import shiftx
from cing.Scripts.getPhiPsi import doYasaraRewritePdb
from cing.Scripts.getPhiPsiWrapper import Janin
from cing.Scripts.getPhiPsiWrapper import Ramachandran
from cing.Scripts.getPhiPsiWrapper import d1d2
from cing.Scripts.getPhiPsiWrapper import dihedralComboTodo
from cing.core.parameters import directories
from cing.core.parameters import moleculeDirectories

if dihedralComboTodo == Ramachandran:
    subdir = 'phipsi_wi_db'
elif dihedralComboTodo == Janin:
    subdir = 'chi1chi2_wi_db'
elif dihedralComboTodo == d1d2:
    subdir = 'd1d2_wi_db'
dihedralComboTodo = d1d2
startDir = os.path.join(cingDirTmp, subdir)


def truncatePdbList():
    os.chdir(os.path.join(cingDirScripts, 'data'))
    obsEntriesList = readLinesFromFile('obsoleteSince2009-02-28.LIS')
    entriesList = readLinesFromFile('PDB_WI_SELECT_Rfactor_2.1_Res2.0_2009-02-28.LIS')

    codeList = []
    for code in entriesList:
        entryCode = code.strip()[0:4]
        if entryCode in obsEntriesList:
            print 'removing', entryCode
            continue
        codeList.append(code)

    writeTextToFile('t.txt', toCsv(codeList))


def findMissingCsv():
    d1d2Dir = os.path.join(startDir, 'data')

    os.chdir(d1d2Dir)
    NTmessage("Now in %s" % os.getcwd())
    entriesList = readLinesFromFile(os.path.join(cingDirScripts, 'data', 'PDB_WI_SELECT_Rfactor0.21_Res2.0_2009-02-28_noObs.LIS'))

    count = 0
    for code in entriesList:
#    for code in ['1abaA']:
        entryCode = code.strip()[0:4].lower()
        chainCode = code.strip()[4:5]
        ch23 = entryCode[1:3]
        searchFile = '%s/%s/cb4ncb4c_wi_db_%s%s.csv' % (ch23, entryCode, entryCode, chainCode)
        if not os.path.exists(searchFile):
#        csvFileList = glob( '%s/%s/*.csv' % ( ch23, entryCode ) )
#        if not csvFileList:
            NTerror("Failed to find csv: %s" % searchFile)
            count += 1
    n = len(entriesList)
    NTmessage("Found %d from %d" % (n - count, n))

def allDoYasaraRewritePdb():
    for entry in """
1i1s
1ka3
1tgq
1tkv
1y4o""".split():
        doYasaraRewritePdb(entry)


def removeTempFiles():
#    entryCode = '1brv'
    entryCode = '1cjg'
    ch23 = entryCode[1:3]
    D = '/Library/WebServer/Documents'
#    D = '/Volumes/tera4'
    projectDir = D + '/NRG-CING/data/%s/%s/%s.cing' % (ch23, entryCode, entryCode)
    molDir = projectDir + '/' + entryCode
    Whatif.removeTempFiles(os.path.join( molDir, moleculeDirectories.whatif ))
    dssp.removeTempFiles(os.path.join( molDir, moleculeDirectories.dssp ))
    procheck.removeTempFiles(os.path.join( molDir, moleculeDirectories.procheck ))
    shiftx.removeTempFiles(os.path.join(molDir, moleculeDirectories.shiftx))
    molgrap.removeTempFiles(os.path.join(projectDir, directories.tmp))

if __name__ == '__main__':
    cing.verbosity = cing.verbosityDebug
    removeTempFiles()
