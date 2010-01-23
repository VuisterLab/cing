"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTplotDihedral2D.py

make sure the projects to run are already in the tmpdir.
"""

from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import getDeepByKeys
from cing.Libs.html import makeDihedralPlot
from cing.PluginCode.required.reqWhatif import BBCCHK_STR
from cing.PluginCode.required.reqWhatif import VALUE_LIST_STR
from cing.PluginCode.required.reqWhatif import WHATIF_STR
from cing.Scripts.d1d2plotConstants import BBCCHK_CUTOFF
from cing.Scripts.d1d2plotConstants import CV_CUTOFF
from cing.core.classes import Project
from cing.core.molecule import Dihedral
from pylab import * #@UnusedWildImport
import cing
import os #@Reimport

def plot(entryId):
    "Arbitrary 20 bb occurences as cuttoff for now"
    dihedralName1 = 'Cb4N'
    dihedralName2 = 'Cb4C'
    graphicsFormat = "png"

    os.chdir(cingDirTmp)
    project = Project.open(entryId, status='old')
    title = 'd1d2 all resType'

    fpGood = open(project.name + '_all_testCb2Good.out', 'w')
    fpBad = open(project.name + '_all_testCb2Bad.out', 'w')

    mCount = project.molecule.modelCount
    residueList = project.molecule.A.allResidues()

    for res in residueList:
        triplet = NTlist()
        for i in [-1, 0, 1]:
            triplet.append(res.sibling(i))
        if None in triplet:
            NTdebug('Skipping because not all in triplet for %s' % res)
            continue

        CA_atms = triplet.zap('CA')
        CB_atms = triplet.zap('CB')

        if None in CB_atms: # skip Gly for now
            NTdebug('Skipping because not all CB present (e.g. for Gly) for %s ' % res)
            continue

        d1 = Dihedral(res, 'Cb4N', range=[0.0, 360.0])
        d1.atoms = [CB_atms[0], CA_atms[0], CA_atms[1], CB_atms[1]]
        d1.calculateValues()
        res['Cb4N'] = d1 # append dihedral to residue

        d2 = Dihedral(res, 'Cb4C', range=[0.0, 360.0])
        d2.atoms = [CB_atms[1], CA_atms[1], CA_atms[2], CB_atms[2]]
        d2.calculateValues()
        res['Cb4C'] = d2 # append dihedral to residue

        bb = getDeepByKeys(res, WHATIF_STR, BBCCHK_STR, VALUE_LIST_STR, 0) # check first one.
        if bb == None:
            NTdebug('Skipping without BBCCHK values (please run What If): %s' % res)
            continue

        if not ( d1.cv < CV_CUTOFF and d2.cv < CV_CUTOFF):
            NTdebug("Skipping unstructured residue (cvs %f %f): %s" % (d1.cv, d2.cv, res))
            continue

        NTdebug( "%s %s %s %s" % (res, triplet, CA_atms, CB_atms ))

        for i in range(mCount): # Consider each model individually
            bb = getDeepByKeys(res, WHATIF_STR, BBCCHK_STR, VALUE_LIST_STR, i)
            if bb == None:
                NTerror('Skipping without BB: %s' % res)
                continue
            angles = NTlist() # store phi, psi, chi1, chi2
            for angle in ['PHI', 'PSI', 'CHI1', 'CHI2']:
                if res.has_key(angle):
                    angles.append(res[angle][i])
                else:
                    angles.append(0.0)
            if bb < BBCCHK_CUTOFF:
                fprintf(fpBad, '%4d   %7.2f  %7.2f  %7.2f  %s  %s %s\n', res.resNum, d1[i], d2[i], bb, angles.format("%7.2f  "), res, res.dssp.consensus)
            else:
                fprintf(fpGood, '%4d   %7.2f  %7.2f  %7.2f  %s  %s %s\n', res.resNum, d1[i], d2[i], bb, angles.format("%7.2f  "), res, res.dssp.consensus)
            #end if
        #end for models
        fn = "d1d2_%03d_%s." % ( res.resNum, res.resName) + graphicsFormat
#        residueHTMLfile = ResidueHTMLfile(project, res)
        ps = makeDihedralPlot( project, [res], dihedralName1, dihedralName2,
                          plotTitle = title, plotCav=False,htmlOnly=False )
        ps.hardcopy(fn, graphicsFormat)
    #        plot.show()
    #end for residues
    fpBad.close()
    fpGood.close()

    project.close(save=False)


if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    entryList = "1y4o".split()
#    entryList = "1tgq 1y4o".split()
#    entryList = "1brv".split()
    for entryId in entryList:
        plot(entryId)
