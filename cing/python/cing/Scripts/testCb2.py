"""
@author: GWV

# test script for 4-bond dihedrals
# execute:
# %run -i /Users/jd/workspace35/cing/python/cing/Scripts/testCb2.py
"""
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqWhatif import * #@UnusedWildImport
from cing.core.constants import * #@UnusedWildImport
from cing.core.molecule import Dihedral

project = p #@UndefinedVariable

fpGood = open(project.name + '.testCb2Good.out', 'w')
fpBad = open(project.name + '.testCb2Bad.out', 'w')

mCount = project.molecule.modelCount

for res in project.molecule.A.allResidues():
    triplet = NTlist()
    for i in [-1,0,1]:
        triplet.append( res.sibling(i) )
    if None in triplet:
        print 'Skipping ', res

    else:
        CA_atms = triplet.zap('CA')
        CB_atms = triplet.zap('CB')

#        print res, triplet, CA_atms, CB_atms

        if None in CB_atms: # skip Gly for now
            print 'Skipping ', res
        else:
            d1 = Dihedral( res, 'Cb4N', range=[0.0,360.0] )
            d1.atoms = [CB_atms[0], CA_atms[0], CA_atms[1], CB_atms[1]]
            d1.calculateValues()
            res['Cb4N'] = d1 # append dihedral to residue

            d2 = Dihedral( res, 'Cb4C', range=[0.0,360.0] )
            d2.atoms = [CB_atms[1], CA_atms[1], CA_atms[2], CB_atms[2]]
            d2.calculateValues()
            res['Cb4C'] = d2 # append dihedral to residue

            bb = getDeepByKeys( res, WHATIF_STR, BBCCHK_STR, VALUE_LIST_STR, 0) # check first one.
            if bb ==  None:
                print 'Skipping without BB', res
                continue

            if d1.cv < 0.03 and d2.cv < 0.03: # Only include structured residues
                for i in range(mCount): # Consider each model individually
#                    bb = res.Whatif.bbNormality.valueList[i]
                    bb = getDeepByKeys( res, WHATIF_STR, BBCCHK_STR, VALUE_LIST_STR, i)
                    if bb ==  None:
                        print 'Skipping without BB', res
                        continue
                    angles = NTlist() # store phi, psi, chi1, chi2
                    for angle in ['PHI','PSI','CHI1','CHI2']:
                        if res.has_key(angle):
                            angles.append( res[angle][i] )
                        else:
                            angles.append( 0.0 )
                    #end for
                    if bb<20.0: # Arbitrary 20 bb occurences as cuttoff for now
                        fprintf(fpBad,'%4d   %7.2f  %7.2f  %7.2f  %s  %s %s\n', res.resNum, d1[i], d2[i], bb, angles.format("%7.2f  "), res, res.dssp.consensus)
                    else:
                        fprintf(fpGood,'%4d   %7.2f  %7.2f  %7.2f  %s  %s %s\n', res.resNum, d1[i], d2[i], bb, angles.format("%7.2f  "), res, res.dssp.consensus)
            #end if
        #end if
    #end if
#end for
fpBad.close()
fpGood.close()