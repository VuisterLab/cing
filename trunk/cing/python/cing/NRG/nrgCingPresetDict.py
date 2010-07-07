# See NRG presetDict.py
# vi $CINGROOT/python/cing/NRG/nrgCingPresetDict.py

help = """

'forceChainMappings': [[' ','CGR',1,-8]],   # Chain mapping: [chainCode ccpn datamodel, chainCode input, firstSeqId, offset]

For the residue numbers the offset is defined by:
offset = input - datamodel

E.g. for NeR103ACheshire it is: -8 = Gln1 - Gln9

Sort the entry codes alphabetically
"""
presetDict = {

'1cjg': {
  'readShifts': {
   'keywds': {
     'forceChainMappings': [['C', 'LAC REPRESSOR HP62 A', 1, 0]],
      },
    },
  },

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

print "Done reading nrgCingPresetDict.py"