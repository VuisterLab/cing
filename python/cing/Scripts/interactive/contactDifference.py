'''
Created on Jun 25, 2010

run -i '$C/python/cing/Scripts/interactive/contactDifference.py'

for Sanne Nabuurs.
'''

from cing.PluginCode.matplib import NTplot
from cing.PluginCode.matplib import NTplotSet
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from cing.core.molecule import nTdistanceOpt
from matplotlib.pyplot import * #@UnusedWildImport
from numpy import * #@UnusedWildImport
name = 'cbd12'
pdbFile = 'cbd12.pdb'

set_printoptions(precision=1, linewidth=99999, suppress=False)
ioff()
#ion()

if False:
    p = Project.open(name, status='new')
    p.initPDB(pdbFile=pdbFile, convention=PDB)

m = p.molecule

resList = m.residuesWithProperties('protein')
n = len(resList) # 280
nn = n*n
c = 125 # cut between domains in cing residue count
res_k = 2 # requested residue of interest to Sanne in cing residue count
res_l = 279

caDiffDistMatrixList = []
for pairIdx in range(4): # p for pairs use 4 pairs for final
    #pairIdx = 0

    i = pairIdx*2 # model number
    j = i + 1
    if True:
        caDistMatrixList = []
        for k in [ i, j ]:
            caDistMatrix = zeros(nn).reshape(n,n)
            caDistMatrixList.append(caDistMatrix)
            for idx1, r1 in enumerate(resList[:n]):
                for idx2, r2 in enumerate(resList[:n]):
    #                if idx2 <= idx1:
    #                    continue # only do one part of the matrix.
        #            nTdebug("Looking at model %s between %s and %s" % (k, r1, r2))
                    atom1 = r1.CA
                    atom2 = r2.CA
                    caDistMatrix[idx1,idx2] = nTdistanceOpt(atom1.coordinates[k], atom2.coordinates[k])

    caDiffDistMatrix = caDistMatrixList[1] - caDistMatrixList[0]
    caDiffDistMatrixList.append(caDiffDistMatrix)

    strTitle = 'Models %d/%d C alpha contact difference' % (i, j)
    clf()
    ps = NTplotSet() # closes any previous plots
    ps.hardcopySize = (1000, 1000)
    myplot = NTplot(title=strTitle)
    ps.addPlot(myplot)
#    extent=(0,c,c,n)
#    caDiffDistMatrixSlice = caDiffDistMatrix[0:c,c:n]
#    norm = Normalize(vmin = -30, vmax = 10)
#    myHistNormalized = norm(caDiffDistMatrix)
    imshow(caDiffDistMatrix,interpolation='bicubic')
    #plot([1,299], [1,299], 'go-', linewidth=2)
    colorbar()
    fn = 'models_%s_%s.png' % (i, j)
    ps.hardcopy(fn)
    fn = 'models_%s_%s.csv' % (i, j)
    savetxt(fn, caDiffDistMatrix, fmt='%6.2f', delimiter=',')
#    show()
    print 'Models %d/%d C alpha contact difference res %s/%s %8.3f' % (i, j, res_k, res_l, caDiffDistMatrix[res_k,res_l])



