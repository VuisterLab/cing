# See $WS/recoord/python/recoord2/presetDict.py

help = """

'forceChainMappings': [[' ','CGR',1,-8]],   # Chain mapping: [chainCode ccpn datamodel, chainCode input, firstSeqId, offset]

For the residue numbers the offset is defined by:
offset = input - datamodel

E.g. for NeR103ACheshire it is: -8 = Gln1 - Gln9

Sort the entry codes alphabetically
"""
#presetDictByPdbId = { # not used.
#
#'1hue': {
#  'readShifts': {
#   'keywds': {
#     'forceChainMappings': [['A', 'HUBst', 1, 0]],
#      },
#    },
#  },
#'2jmx': {
#  'readShifts': {
#   'keywds': {
#     'forceChainMappings': [['A', 'OSCP N-terminal 1-120', 1, 0]],
#      },
#    },
#  },
#'1iv6': {
#  'readShifts': {
#   'keywds': {
#     'forceChainMappings': [['C', 'TRF1', 1, -1]],
#      },
#    },
#  },
#
#'2kib': {
#  'readShifts': {
#   'keywds': {
#     'forceChainMappings': [['A', 'subunit A1 peptide 1', 1, 2]],
#      },
#    },
#  },
#
#
#}


presetDict = {

'bmr4813disabled': {
  'comment': """
  """,
#  'duplicateResonances': {
#     'A': ['A', 'B'],
#     'C': ['C', 'D'],
#    },
  'linkResonances': {
   'keywds': {
     'forceChainMappings': [
       ['A', 'LAC OPERATOR C', 1, 0], # dna
       ['B', 'LAC OPERATOR C', 1, 0], # absent
       ['C', 'LAC REPRESSOR HP62 A', 3, 0],  # protein according to Wim
       ['D', 'LAC REPRESSOR HP62 A', 3, 0],
       ],
      },
    },
  },

'bmr5054': {

  'linkResonances': {
    'keywds': {
      'forceChainMappings':  [['A', 'Ap4A hydrolase monomer', 1, 0],['B', 'adenosine triphosphate', 1, 0]],
      'addNameMappings':     {'Atp': [["H51'","H5'1"],["H52'","H5'2"]]}
      }
    }
  },

'bmr20074': {
  'linkResonances': {
   'keywds': {
     'forceChainMappings': [
        ['A', 'subunit A1 peptide 1', 1, 2], ['B', 'subunit A2 peptide 1', 1, 2], 
        ['C', 'subunit B1 peptide 1', 1, 2], ['D', 'subunit B2 peptide 1', 1, 2],
        ['E', 'subunit A1 peptide 2', 1, 2], ['F', 'subunit A2 peptide 2', 1, 2], 
        ['G', 'subunit B1 peptide 2', 1, 2], ['H', 'subunit B2 peptide 2', 1, 2]
        ],
      },
    },
  },

#add one for:
#1vj6
#
#*** Setting chain mapping automatically to: [['A', 'PDZ2', 9, 0], ['B', 'PDZ2', 1, 19]] ***
#
#      WARNING: Mismatches in sequence mapping between CCPN chain 'B' and BMRB chain 'PDZ2':
#          - 2.Arg  <-> 21.Thr
#          - 3.His  <-> 22.Asp
#          - 4.Ser  <-> 23.Gly
#          - 5.Gly  <-> 24.Ser
#          - 6.Ser  <-> 25.Leu
#          - 7.Tyr  <-> 26.Gly
#          - 8.Leu  <-> 27.Ile
#          - 9.Val  <-> 28.Ser
#          - 10.Thr  <-> 29.Val
#          - 11.Ser  <-> 30.Thr
#          - 12.Val  <-> 31.Gly

}

print "Done reading shiftPresetDict.py"
