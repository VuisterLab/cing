#@PydevCodeAnalysisIgnore # pylint: disable-all
import os

from pdbe.adatah.Constants import archivesDataDir, dataDir
from pdbe.adatah.Pdb import pdbDataDir

analysisDataDir = os.path.join(archivesDataDir,'analysis')
pdbProtonatedDataDir = os.path.join(pdbDataDir,'protonated')

csiRefFile = os.path.join(dataDir,'ccp','csi','csiRefValues.str')

resultsDirName = 'results'
graphsDirName = 'graphs'

#
# Solvent exposure normalisation values for DSSP, from Wolfgang code
#

solventExposure =  {'ALA': 105,
                    'CYS': 135,
                    'ASP': 163,
                    'GLU': 194,
                    'PHE': 197,
                    'GLY': 84,
                    'HIS': 184,
                    'ILE': 169,
                    'LYS': 205,
                    'LEU': 164,
                    'MET': 188,
                    'ASN': 157,
                    'PRO': 136,
                    'GLN': 198,
                    'ARG': 248,
                    'SER': 130,
                    'THR': 142,
                    'VAL': 142,
                    'TRP': 227,
                    'TYR': 222}


#
# Values from http://www.imb-jena.de/IMAGE_AA.html
#
# Colums are surface, volume, solubility (99999 means very high)
#

aminoAcidProperties = {

    'ALA': (115,88.6,16.65),
    'ARG': (225,173.4,15),
    'ASP': (150,111.1,0.778),
    'ASN': (160,114.1,3.53),
    'CYS': (135,108.5,99999),
    'GLU': (190,138.4,0.864),
    'GLN': (180,143.8,2.5),
    'GLY': (75,60.1,24.99),
    'HIS': (195,153.2,4.19),
    'ILE': (175,166.7,4.117),
    'LEU': (170,166.7,2.426),
    'LYS': (200,168.6,99999),
    'MET': (185,162.9,3.381),
    'PHE': (210,189.9,2.965),
    'PRO': (145,112.7,162.3),
    'SER': (115,89.0,5.023),
    'THR': (140,116.1,99999),
    'TRP': (255,227.8,1.136),
    'TYR': (230,193.6,0.0453),
    'VAL': (155,140.0,8.85)
    
    }


#
# Reference shift values
#

rcShiftValues = {
  
  'JBiomolNMR_5_14':
  
    {'origin':      'GGXGG peptides',
     'solvent':     '90% H2O, 10% D2O',
     'temperature': 277.2,
     'pH':          5.0,
     'shiftRef':    'dioxane',
     'shiftRefPpm': 3.75,
     'remarks':     'methylene shifts not stereospecific!!',
     
     'values': {
     
       'ALA': {
       
         'HN':  8.67,
         'HA':  4.34,
         'HB*': 1.41,       
       
       },
       
       'ARG': {
       
         'HN':   8.69,
         'HA':   4.34,
         'HB2':  1.80,       
         'HB3':  1.90,       
         'HG2':  1.67,       
         'HG3':  1.67,       
         'HD2':  3.22,       
         'HD3':  3.22,       
         'HE':   7.26,       
         'HH1*': 6.49,       # This not certain
         'HH2*': 6.92,       # This not certain
       
       },
       
       'ASN': {
       
         'HN':   8.76,
         'HA':   4.76,
         'HB2':  2.79,       
         'HB3':  2.88,
         'HD21': 7.74,
         'HD22': 7.03,

       },
       
       'ASP': {
       
         'HN':  8.61,
         'HA':  4.63,
         'HB2': 2.70,       
         'HB3': 2.71,

       },

       'CYS': {
       
         'HN':  8.75,
         'HA':  4.58,
         'HB2': 2.97,       
         'HB3': 2.97,       

       },

       'GLN': {
       
         'HN':   8.70,
         'HA':   4.36,
         'HB2':  2.02,       
         'HB3':  2.15,       
         'HG2':  2.39,       
         'HG3':  2.40,
         'HE21': 7.69,       
         'HE22': 6.97,       

       },

       'GLU': {
       
         'HN':  8.83,
         'HA':  4.29,
         'HB2': 1.99,       
         'HB3': 2.09,       
         'HG2': 2.34,       
         'HG3': 2.34,       

       },

       'GLY': {
       
         'HN':  8.66,
         'HA2': 4.01,
         'HA3': 4.01,       
       
       },

       'HIS': {
              
         'HN':  8.79,
         'HA':  4.77,
         'HB2': 3.19,       
         'HB3': 3.33,
         'HD2': 7.31,       
         'HE1': 8.59,       

       },

       'ILE': {

         'HN':   8.52,
         'HA':   4.18,
         'HB':   1.89,       
         'HG12': 1.21,       
         'HG13': 1.49,
         'HG2*': 0.93,
         'HD2*': 0.88,
       
       },

       'LEU': {

         'HN':   8.64,
         'HA':   4.35,
         'HB2':  1.64,       
         'HB3':  1.64,       
         'HG':   1.64,       
         'HD1*': 0.89,
         'HD2*': 0.93,
       
       },

       'LYS': {
       
         'HN':   8.67,
         'HA':   4.32,
         'HB2':  1.79,       
         'HB3':  1.87,       
         'HG2':  1.46,       
         'HG3':  1.46,       
         'HD2':  1.68,       
         'HD3':  1.68,       
         'HE2':  2.99,       
         'HE3':  2.99,       
         'HZ*':  7.59,       
       
       },

       'MET': {

         'HN':   8.73,
         'HA':   4.52,
         'HB2':  2.03,       
         'HB3':  2.15,       
         'HG2':  2.56,       
         'HG3':  2.63,       
         'HE*':  2.10,       
       
       },

       'PHE': {
       
         'HN':  8.61,
         'HA':  4.62,
         'HB2': 3.06,       
         'HB3': 3.15,       
         'HD1': 7.28,       
         'HD2': 7.28,       
         'HE1': 7.38,       
         'HE2': 7.38,       
         'HZ':  7.32,       
       
       },

       'PRO': {
       
         'HA':   4.44,
         'HB2':  2.03,       
         'HB3':  2.30,       
         'HG2':  2.06,       
         'HG3':  2.06,       
         'HD2':  3.63,       
         'HD3':  3.67,       
       
       },

       'SER': {
       
         'HN':  8.69,
         'HA':  4.49,
         'HB2': 3.93,       
         'HB3': 3.95,       
       
       },

       'THR': {
       
         'HN':   8.52,
         'HA':   4.39,
         'HB':   4.32,
         'HG2*': 1.22,       
       
       },

       'TRP': {
       
         'HN':  8.46,
         'HA':  4.67,
         'HB2': 3.28,       
         'HB3': 3.28,       
         'HD1': 7.27,
         'HE1': 10.20,
         'HE3': 7.64,
         'HZ2': 7.50,
         'HZ3': 7.17,
         'HH2': 7.24,
       
       },

       'TYR': {
       
         'HN':  8.59,
         'HA':  4.56,
         'HB2': 2.98,       
         'HB3': 3.06,       
         'HD1': 7.15,       
         'HD2': 7.15,       
         'HE1': 6.85,       
         'HE2': 6.85,       
       
       },

       'VAL': {

         'HN':   8.51,
         'HA':   4.13,
         'HB':   2.12,       
         'HG1*': 0.95,
         'HG2*': 0.97,
       
       },
    }  
  }
}

#
# List of proton to heavy atom names for standard amino acids and nucleotides (ccp names)
#

protonToHeavyAtom = {

     'protein': {'Cys': {'H': 'N', "H''": "O''", ('HB2', 'HB3'): 'CB', 'HA': 'CA', 'HG': 'SG', 'HB3': 'CB', 'HB2': 'CB', 'HB*': 'CB'},
                 'Asp': {'HD2': 'OD2', 'H': 'N', "H''": "O''", ('HB2', 'HB3'): 'CB', 'HA': 'CA', 'HB3': 'CB', 'HB2': 'CB', 'HB*': 'CB'},
                 'Ser': {'H': 'N', "H''": "O''", ('HB2', 'HB3'): 'CB', 'HA': 'CA', 'HG': 'OG', 'HB3': 'CB', 'HB2': 'CB', 'HB*': 'CB'},
                 'Gln': {('HG2', 'HG3'): 'CG', 'H': 'N', 'HG2': 'CG', 'HG3': 'CG', "H''": "O''", 'HE22': 'NE2', ('HB2', 'HB3'): 'CB', 'HA': 'CA', 'HE21': 'NE2', 'HB3': 'CB', 'HB2': 'CB', 'HG*': 'CG', 'HB*': 'CB'},
                 'Lys': {('HD2', 'HD3'): 'CD', 'HD3': 'CD', 'HD2': 'CD', 'HE2': 'CE', 'HE3': 'CE', ('HG2', 'HG3'): 'CG', 'H': 'N', 'HG2': 'CG', 'HG3': 'CG', ('HZ1', 'HZ2', 'HZ3'): 'NZ', "H''": "O''", ('HE2', 'HE3'): 'CE', ('HB2', 'HB3'): 'CB', 'HA': 'CA', 'HB3': 'CB', 'HB2': 'CB', 'HD*': 'CD', 'HG*': 'CG', 'HB*': 'CB', 'HE*': 'CE', 'HZ*': 'NZ'},
                 'Trp': {'HH2': 'CH2', 'HE1': 'NE1', 'HD1': 'CD1', 'HE3': 'CE3', 'H': 'N', 'HZ3': 'CZ3', 'HZ2': 'CZ2', "H''": "O''", ('HB2', 'HB3'): 'CB', 'HA': 'CA', 'HB3': 'CB', 'HB2': 'CB', 'HB*': 'CB'},
                 'Pro': {('HD2', 'HD3'): 'CD', 'HD3': 'CD', 'HD2': 'CD', ('HG2', 'HG3'): 'CG', 'H': 'N', 'HG2': 'CG', 'HG3': 'CG', "H''": "O''", ('HB2', 'HB3'): 'CB', 'HA': 'CA', 'HB3': 'CB', 'HB2': 'CB', 'HD*': 'CD', 'HG*': 'CG', 'HB*': 'CB'},
                 'Thr': {('HG21', 'HG22', 'HG23'): 'CG2', 'H': 'N', 'HG1': 'OG1', 'HB': 'CB', "H''": "O''", 'HA': 'CA', 'HG2*': 'CG2'},
                 'Ile': {('HG21', 'HG22', 'HG23'): 'CG2', 'H': 'N', ('HD11', 'HD12', 'HD13'): 'CD1', 'HG12': 'CG1', 'HG13': 'CG1', ('HG12', 'HG13'): 'CG1', 'HB': 'CB', "H''": "O''", 'HA': 'CA', 'HG2*': 'CG2', 'HD1*': 'CD1', 'HG1*': 'CG1'},
                 'Ala': {'H': 'N', 'HA': 'CA', ('HB1', 'HB2', 'HB3'): 'CB', "H''": "O''", 'HB*': 'CB'},
                 'Phe': {'HZ': 'CZ', 'HE2': 'CE2', 'HD2': 'CD2', 'HD1': 'CD1', 'H': 'N', 'HE1': 'CE1', "H''": "O''", ('HB2', 'HB3'): 'CB', 'HA': 'CA', 'HB3': 'CB', 'HB2': 'CB', 'HB*': 'CB'},
                 'Gly': {'H': 'N', 'HA2': 'CA', 'HA3': 'CA', ('HA2', 'HA3'): 'CA', "H''": "O''", 'HA*': 'CA'},
                 'His': {'HE2': 'NE2', 'HE1': 'CE1', 'HD1': 'ND1', 'H': 'N', 'HB2': 'CB', "H''": "O''", ('HB2', 'HB3'): 'CB', 'HA': 'CA', 'HB3': 'CB', 'HD2': 'CD2', 'HB*': 'CB'},
                 'Leu': {'H': 'N', ('HD11', 'HD12', 'HD13'): 'CD1', ('HD21', 'HD22', 'HD23'): 'CD2', "H''": "O''", ('HB2', 'HB3'): 'CB', 'HA': 'CA', 'HG': 'CG', 'HB3': 'CB', 'HB2': 'CB', 'HD1*': 'CD1', 'HD2*': 'CD2', 'HB*': 'CB'},
                 'Arg': {('HD2', 'HD3'): 'CD', 'HD3': 'CD', 'HD2': 'CD', ('HG2', 'HG3'): 'CG', 'H': 'N', 'HG2': 'CG', 'HG3': 'CG', 'HH22': 'NH2', 'HH21': 'NH2', 'HH12': 'NH1', 'HH11': 'NH1', "H''": "O''", ('HB2', 'HB3'): 'CB', 'HA': 'CA', 'HE': 'NE', 'HB3': 'CB', 'HB2': 'CB', 'HD*': 'CD', 'HG*': 'CG', 'HB*': 'CB'},
                 'Met': {('HE1', 'HE2', 'HE3'): 'CE', ('HG2', 'HG3'): 'CG', 'H': 'N', 'HG2': 'CG', 'HG3': 'CG', "H''": "O''", ('HB2', 'HB3'): 'CB', 'HA': 'CA', 'HB3': 'CB', 'HB2': 'CB', 'HE*': 'CE', 'HG*': 'CG', 'HB*': 'CB'},
                 'Glu': {'HE2': 'OE2', ('HG2', 'HG3'): 'CG', 'H': 'N', 'HG2': 'CG', 'HG3': 'CG', "H''": "O''", ('HB2', 'HB3'): 'CB', 'HA': 'CA', 'HB3': 'CB', 'HB2': 'CB', 'HG*': 'CG', 'HB*': 'CB'},
                 'Asn': {'HD22': 'ND2', 'HD2': 'ND2', 'HD21': 'ND2', 'H': 'N', "H''": "O''", ('HB2', 'HB3'): 'CB', 'HA': 'CA', 'HB3': 'CB', 'HB2': 'CB', 'HB*': 'CB'},
                 'Tyr': {'HE2': 'CE2', 'HD2': 'CD2', 'HD1': 'CD1', 'H': 'N', 'HE1': 'CE1', 'HH': 'OH', "H''": "O''", ('HB2', 'HB3'): 'CB', 'HA': 'CA', 'HB3': 'CB', 'HB2': 'CB', 'HB*': 'CB'},
                 'Val': {('HG21', 'HG22', 'HG23'): 'CG2', 'H': 'N', 'HB': 'CB', "H''": "O''", 'HA': 'CA', ('HG11', 'HG12', 'HG13'): 'CG1', 'HG2*': 'CG2', 'HG1*': 'CG1'}},

     'DNA':     {'A': {"H4'": "C4'", "HO3'": "O3'", 'H8': 'C8', "H2''": "C2'", "H3'": "C3'", "HO5'": "O5'", 'H2': 'C2', 'HOP2': 'OP2', 'HOP3': 'OP3', 'H1': 'N1', ("H2'", "H2''"): "C2'", "H5''": "C5'", ("H5'", "H5''"): "C5'", "H5'": "C5'", 'H61': 'N6', "H2'": "C2'", 'H62': 'N6', "H1'": "C1'", "H2'*": "C2'", "H5'*": "C5'"},
                 'C': {"H4'": "C4'", "HO3'": "O3'", "H5'": "C5'", "H3'": "C3'", "H2''": "C2'", 'H3': 'N3', 'HOP3': 'OP3', 'H6': 'C6', 'H5': 'C5', ("H2'", "H2''"): "C2'", "H5''": "C5'", ("H5'", "H5''"): "C5'", 'H42': 'N4', 'H41': 'N4', 'HOP2': 'OP2', "HO5'": "O5'", "H2'": "C2'", "H1'": "C1'", "H2'*": "C2'", "H5'*": "C5'"},
                 'T': {"H4'": "C4'", "HO3'": "O3'", "H5''": "C5'", "H3'": "C3'", "H2''": "C2'", 'H3': 'N3', 'HOP3': 'OP3', 'H6': 'C6', ("H2'", "H2''"): "C2'", ("H5'", "H5''"): "C5'", ('H71', 'H72', 'H73'): 'C7', 'HOP2': 'OP2', "H5'": "C5'", "HO5'": "O5'", "H2'": "C2'", "H1'": "C1'", "H2'*": "C2'", 'H7*': 'C7', "H5'*": "C5'"},
                 'G': {"H4'": "C4'", "HO3'": "O3'", 'H8': 'C8', "H5'": "C5'", "H3'": "C3'", "H2''": "C2'", 'HOP2': 'OP2', 'HOP3': 'OP3', 'H1': 'N1', 'H21': 'N2', 'H7': 'N7', 'H22': 'N2', ("H2'", "H2''"): "C2'", "H5''": "C5'", ("H5'", "H5''"): "C5'", "HO5'": "O5'", "H2'": "C2'", "H1'": "C1'", "H2'*": "C2'", "H5'*": "C5'"}},

     'RNA':     {'A': {"H4'": "C4'", "HO3'": "O3'", 'H8': 'C8', "H5''": "C5'", ("H5'", "H5''"): "C5'", "HO2'": "O2'", 'H2': 'C2', 'HOP2': 'OP2', 'H1': 'N1', 'HOP3': 'OP3', "H5'": "C5'", 'H62': 'N6', 'H61': 'N6', "HO5'": "O5'", "H2'": "C2'", "H1'": "C1'", "H3'": "C3'", "H5'*": "C5'"},
                 'C': {"H4'": "C4'", "HO3'": "O3'", "H5'": "C5'", ("H5'", "H5''"): "C5'", "HO2'": "O2'", 'HOP3': 'OP3', 'H3': 'N3', 'H6': 'C6', 'H5': 'C5', "H5''": "C5'", 'H42': 'N4', 'H41': 'N4', 'HOP2': 'OP2', "HO5'": "O5'", "H2'": "C2'", "H1'": "C1'", "H3'": "C3'", "H5'*": "C5'"},
                 'U': {"H4'": "C4'", "HO3'": "O3'", "H5''": "C5'", ("H5'", "H5''"): "C5'", "HO2'": "O2'", 'HOP3': 'OP3', 'H3': 'N3', 'H6': 'C6', 'H5': 'C5', "H5'": "C5'", 'HOP2': 'OP2', "HO5'": "O5'", "H2'": "C2'", "H1'": "C1'", "H3'": "C3'", "H5'*": "C5'"},
                 'G': {"H4'": "C4'", "HO3'": "O3'", 'H8': 'C8', "H5'": "C5'", ("H5'", "H5''"): "C5'", "HO2'": "O2'", 'HOP3': 'OP3', 'HOP2': 'OP2', 'H1': 'N1', 'H21': 'N2', 'H7': 'N7', 'H22': 'N2', "H5''": "C5'", "HO5'": "O5'", "H2'": "C2'", "H1'": "C1'", "H3'": "C3'", "H5'*": "C5'"}}
                                 
}
