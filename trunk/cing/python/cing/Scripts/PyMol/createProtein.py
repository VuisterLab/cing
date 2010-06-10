'''
Created on Jun 7, 2010

@author: jd

Creates a PDB file for each type of turn.

Requires the pymol python code etc to be properly installed.

Execute like: ....
# From Terminal like:
# pymol -M /Users/jd/workspace35/cing/python/cing/Scripts/PyMol/createProtein.py
'''
# E.g. from relibase: [DOI: 10.1002/prot.22185]
# http://relibase.ccdc.cam.ac.uk/documentation/relibase/relibase.1.51.html#339516
from cing.Scripts.PyMol.CreateSecondaryStructures import createPeptide
from cing.Scripts.d1d2plot import reportsDir
from pymol import cmd
import os
import pymol #@UnusedImport

phiHelix, psiHelix = -60., -45.
phiSheet, psiSheet = -120., 150. # strand

phiDefault, psiDefault = phiSheet, psiSheet
turnTypes = [
['type' , 'phi1' , 'psi1' , 'omega' , 'phi2' , 'psi2', 'res0', 'res1', 'res2', 'res3' ],
['Ia' ,  124.0 , -51.0 , 175.9 , 126.7 ,  155.1, 'ASN', 'ALA', 'PHE', 'THR' ],
['Ib' ,  116.2 ,  49.8 , 174.4 , 148.6 ,  169.5, 'ASN', 'ALA', 'PHE', 'THR' ],
['IIa' , 127.4 , -26.3 , 176.4 , -87.0 ,  148.5, 'ASN', 'ALA', 'PHE', 'THR' ],
['IIb' , 104.8 , -24.5 , 174.1 ,-105.2 , -172.8, 'ASN', 'ALA', 'PHE', 'THR' ],
['IIIa' ,-113.2,  27.4, -177.5,  124.2 ,  162.9, 'ASN', 'ALA', 'PHE', 'THR' ],
['IIIb' ,-131.8,  42.2, -175.0,   84.5 , -160.8, 'ASN', 'ALA', 'PHE', 'THR' ],
['IIIc' , 166.2 , 32.7 ,-176.5 , 127.5 , -163.9, 'ASN', 'ALA', 'PHE', 'THR' ],
#['IVa' , -148.4 , 98.2 ,  -0.4 , -74.0 ,  159.7, 'ALA', 'ALA', 'ALA' ], # ignore cis omegas.
#['IVb' ,  131.7 ,115.5 ,  -9.7 , -57.9 ,  173.1, 'ALA', 'ALA', 'ALA' ],
 ]

os.chdir(reportsDir)

def createTightTurns():
    for typeIdx in range(1,len(turnTypes)):
#    for typeIdx in [2]:
        type, phi1, psi1, _omega, phi2, psi2, res0, res1, res2, res3 = turnTypes[typeIdx]
        print "Doing tight turn %s" % type
        seqInfo = [
            [ res0, phiDefault, psiDefault ],
            [ res1, phi1, psi1 ],
            [ res2, phi2, psi2 ],
            [ res3, phiDefault, psiDefault ],
        ]
    #    seqInfo = getTableFromCsvFile("seqInfo.csv")
        cmd.delete("all") # redundant with the below but good to realize.
        createPeptide(seqInfo)
        fn = 'tightTurn_'+type+'.pdb'
        if os.path.exists(fn):
            os.unlink(fn)
#        The file format is autodetected if the extension is ".pdb", ".pse", ".mol", ".mmod", or ".pkl".
        cmd.save(fn)

#if __name__ == '__main__': # TODO: enable when actually executing this.
#createTightTurns()
#cmd.quit()