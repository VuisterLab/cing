# See NRG presetDict.py
# vi $CINGROOT/python/cing/NRG/casdNmrPresetDict.py

help = """

'forceChainMappings': [[' ','CGR',1,-8]],   # Chain mapping: [chainCode ccpn datamodel, chainCode input, firstSeqId, offset]

For the residue numbers the offset is defined by:
offset = input - datamodel

E.g. for NeR103ACheshire it is: -8 = Gln1 - Gln9

Sort the entry codes alphabetically
"""
presetDict = {

'NeR103ACheshire': {
  'readCoordinates': {
   'keywds': {
     'forceChainMappings': [['A', 'CGR', 1, -8]],
      },
    },
  },

}
