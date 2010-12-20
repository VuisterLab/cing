"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/cingTest.py
"""
from cing.PluginCode.xplor import createProjectFromXplorMemory
import protocol #@UnresolvedImport

pdb='''
REMARK FILENAME="g_xray_withprotons.pdbfit"
REMARK GB1 xray struct with built-on hydrogrens
REMARK ---------------------
REMARK RMS to xray struct = 0.222854 backbone, 0.339624 heavyatoms
REMARK ---------------------
REMARK energies:
REMARK bond angle impr vdw
REMARK 7.14096 20.1928 3.38311 26.8739
REMARK ---------------------
REMARK NOE violations: 0
REMARK ---------------------
REMARK DATE:24-Aug-02  04:32:25       created by user: johnk
ATOM      1  N   MET     1     -14.642   2.847  -3.053  1.00 15.93
ATOM      2  HT1 MET     1     -15.524   3.189  -3.486  1.00  0.00
ATOM      3  HT2 MET     1     -14.499   3.321  -2.138  1.00  0.00
ATOM      4  HT3 MET     1     -14.707   1.820  -2.906  1.00  0.00
ATOM      5  CA  MET     1     -13.494   3.152  -3.954  1.00 17.40
ATOM      6  HA  MET     1     -13.840   3.190  -4.977  1.00  0.00
ATOM      7  CB  MET     1     -12.890   4.506  -3.567  1.00 20.72
ATOM      8  HB1 MET     1     -12.273   4.388  -2.691  1.00  0.00
ATOM      9  HB2 MET     1     -13.688   5.200  -3.349  1.00  0.00
ATOM     10  CG  MET     1     -12.037   5.054  -4.718  1.00 23.81
ATOM     11  HG1 MET     1     -11.504   4.243  -5.195  1.00  0.00
ATOM     12  HG2 MET     1     -11.324   5.768  -4.331  1.00  0.00
ATOM     13  SD  MET     1     -13.111   5.866  -5.933  1.00 28.11
ATOM     14  CE  MET     1     -13.451   7.391  -5.006  1.00 27.51
ATOM     15  HE1 MET     1     -13.017   8.232  -5.529  1.00  0.00
ATOM     16  HE2 MET     1     -13.025   7.330  -4.016  1.00  0.00
ATOM     17  HE3 MET     1     -14.521   7.527  -4.926  1.00  0.00
ATOM     18  C   MET     1     -12.436   2.055  -3.816  1.00 14.65
ATOM     19  O   MET     1     -12.227   1.513  -2.750  1.00 13.04
END
'''

protocol.loadPDB(string=pdb)

cingp = createProjectFromXplorMemory()

print len(cingp['molecule']['A'].allAtoms())
