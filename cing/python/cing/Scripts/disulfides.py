from cing.core.molecule import NTdistance
from math import acos, pi
import cing

# TODO: incorporate into CING

def chi3SS( dCbCb ):
    """
    Return approximation of the chi3 torsion angle as 
    fie of the distance between the Cb atoms of each Cys residue
    
    Dombkowski, A.A., Crippen, G.M, Protein Enginering, 13, 679-89, 2000
    DOI: ??
    
    Page 684, eq. 9
    """
    return acos( 1.0 - (dCbCb*dCbCb - 8.555625) / 6.160 ) * 180.0/pi
#end def


mol = project.molecule #@UndefinedVariable

def disulfideScore( cys1, cys2 ):
    """
    Define a score [0.0,1.0] for a potential cys1-cys2 disulfide bridge.
    Based upon simple counting:
    - Ca-Ca distance
    - Cb-Cb distance
    - Ability to form S-S dihedral within specified range or the presence 
      of short distance SG-SG
      
    Initial test show that existing disulfides have scores > 0.9
    Potential disulfides score > ~0.25
    
    Limits based upon analysis by:
      Pellequer J-L and Chen, S-W.W, Proteins, Struct, Func and Bioinformatics 
      65, 192-2002 (2006)
      DOI: 10.1002/prot.21059
    
    cys1, cys2: Residue instances
    returns a NTlist with four numbers:
        [d(Ca-Ca) count, d(Cb-Cb) count, S-S count, final score]
        
    """
    mc = len(cys1.CA.coordinates)
    score = cing.NTlist(0.0, 0.0, 0.0, 0.0)
    for m in range( mc ):
        da = NTdistance( cys1.CA.coordinates[m], cys2.CA.coordinates[m] )
        if da >= 3.72 and da <= 6.77: 
            score[0] += 1.0
            
        db = NTdistance( cys1.CB.coordinates[m], cys2.CB.coordinates[m] )
        if db >= 3.18 and db <= 4.78: 
            score[1] += 1.0
        
        dg = NTdistance( cys1.SG.coordinates[m], cys2.SG.coordinates[m] )
        chi3 = chi3SS( db )
        if (dg >= 1.63 and dg <= 2.72) or (chi3 >= 27.0 and chi3 <= 153.0): 
            score[2] += 1.0
        #print '>', da, db, dg, chi3, score
    #end for
        
    score[3] = score.sum() / (3.0*float(mc))
    return score
#end def


###
# testing
###
cys=mol.residuesWithProperties('C')
# all cys(i), cys(j) pairs with j>i
for i in range(len(cys)):
    c1 = cys[i]
    for j in range(i+1, len(cys)):
        c2 = cys[j]
        da = c1.CA.distance( c2.CA )
        db = c1.CB.distance( c2.CB )
        dg = c1.SG.distance( c2.SG )
        print '===='
        print c1, c1.CA.shift(), c1.CB.shift(), c1.CA.shift() - c1.CB.shift()
        print c2, c2.CA.shift(), c2.CB.shift(), c2.CA.shift() - c2.CB.shift()
        print 'Ca-Ca', da
        print 'Cb-Cb', db
        print 'Sg-Sg', dg
        print 'chi3 ', chi3SS( db[0] )
        print 'scores', disulfideScore( c1, c2)
        print ""

                