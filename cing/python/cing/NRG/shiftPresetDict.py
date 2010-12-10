# See NRG presetDict.py
# vi $CINGROOT/python/cing/NRG/nrgCingPresetDict.py

help = """

'forceChainMappings': [[' ','CGR',1,-8]],   # Chain mapping: [chainCode ccpn datamodel, chainCode input, firstSeqId, offset]

For the residue numbers the offset is defined by:
offset = input - datamodel

E.g. for NeR103ACheshire it is: -8 = Gln1 - Gln9

Sort the entry codes alphabetically
"""
presetDictByPdbId = { # not used.

'1hue': {
  'readShifts': {
   'keywds': {
     'forceChainMappings': [['A', 'HUBst', 1, 0]],
      },
    },
  },
'2jmx': {
  'readShifts': {
   'keywds': {
     'forceChainMappings': [['A', 'OSCP N-terminal 1-120', 1, 0]],
      },
    },
  },
'1iv6': {
  'readShifts': {
   'keywds': {
     'forceChainMappings': [['C', 'TRF1', 1, -1]],
      },
    },
  },

'2kib': {
  'readShifts': {
   'keywds': {
     'forceChainMappings': [['A', 'subunit A1 peptide 1', 1, 2]],
      },
    },
  },


}


presetDict = {

'bmr4813': {
#  'duplicateResonances': {
#     'A': ['A', 'B'],
#     'C': ['C', 'D'],
#    },
  'linkResonances': {
   'keywds': {
     'forceChainMappings': [
       ['A', 'LAC OPERATOR C', 1, 0], ['B', 'LAC OPERATOR D', 1, 0],
       ['C', 'LAC REPRESSOR HP62 A', 3, 0], ['D', 'LAC REPRESSOR HP62 B', 3, 0]
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
        ['A', 'subunit A1 peptide 1', 1, 2], ['B', 'subunit A2 peptide 1', 1, 2], ['C', 'subunit B1 peptide 1', 1, 2], ['D', 'subunit B2 peptide 1', 1, 2],
        ['E', 'subunit A1 peptide 2', 1, 2], ['F', 'subunit A2 peptide 2', 1, 2], ['G', 'subunit B1 peptide 2', 1, 2], ['H', 'subunit B2 peptide 2', 1, 2]
        ],
      },
    },
  },



}

print "Done reading shiftPresetDict.py"
