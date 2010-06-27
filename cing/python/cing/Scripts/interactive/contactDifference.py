'''
Created on Jun 25, 2010

run -i '/Users/jd/workspace35/cing/python/cing/Scripts/interactive/contactDifference.py'

@author: jd
For Sanne Nabuurs.
'''
from cing.Libs.NTplot import NTplot
from cing.Libs.NTplot import NTplotSet
from cing.core.molecule import NTdistanceOpt
from matplotlib.pyplot import * #@UnusedWildImport
from numpy import * #@UnusedWildImport

p = p #@UndefinedVariable
m = p.molecule

if False:
    p.importPDB('cbd12.pdb')

resList = m.residuesWithProperties('protein')
n = len(resList) # 280
nn = n*n

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
        #            NTdebug("Looking at model %s between %s and %s" % (k, r1, r2))
                    atom1 = r1.CA
                    atom2 = r2.CA
                    caDistMatrix[idx1,idx2] = NTdistanceOpt(atom1.coordinates[k], atom2.coordinates[k])

    caDiffDistMatrix = caDistMatrixList[1] - caDistMatrixList[0]
    caDiffDistMatrixList.append(caDiffDistMatrix)

    strTitle = 'Models %d/%d C alpha contact difference' % (i, j)
    clf()
    ps = NTplotSet() # closes any previous plots
    ps.hardcopySize = (500, 500)
    myplot = NTplot(title=strTitle)
    ps.addPlot(myplot)
    #extent=(0,n,0,n)
    imshow(caDiffDistMatrix,interpolation='bicubic')
    #plot([1,299], [1,299], 'go-', linewidth=2)

    colorbar()
    fn = 'models_%s_%s.png' % (i, j)
    ps.hardcopy(fn)



