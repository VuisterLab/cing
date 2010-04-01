# See NRG presetDict.py
#
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

'NeR103AParis': {
  'linkResonances': {
   'keywds': {
     'forceDefaultChainMapping': 1,
      },
    },
  },

'PGR122ACheshire': {
  'comment': """
Offset should be -416 why doesn't it figure that out?
 """,
  'readCoordinates': {
   'keywds': {
#     'forceChainMappings': [['A', 'DEMO', 1, -416]],
      'forceDefaultChainMapping': 1,  # Use if default chain mapping is correct
                                      # Only works if one CCPN chain, one format chain present!
      },
    },
  },


'CGR26ACheshire'   : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1,},},},
'CGR26AFrankfurt'  : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1,},},},
'CGR26ALyon'       : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1,},},},
'CGR26APiscataway' : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1,},},},
'CGR26ASeattle4'   : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1,},},},
'CGR26ASeattle5'   : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1,},},},
'CGR26AUtrecht2'   : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1,},},},
'ET109AoxSeattle'  : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1,},},},
'ET109AoxUtrecht2' : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1,},},},
'ET109AredCheshire': {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1,},},},
'ET109AredParis'   : {'readCoordinates': {'keywds': {
                                                     'forceDefaultChainMapping': 1,
#     'forceChainMappings': [['A', 'A', 1, 0]], # The RDC frame coordinates are messing things up. Best if removed.

    },},},
'ET109AredSeattle' : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1,},},},
'ET109AredUtrecht2': {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1,},},},
'PGR122ACheshire'  : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1,},},},
'PGR122APiscataway': {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1,},},},
'PGR122ASeattle4'  : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1,},},},
'PGR122AUtrecht'   : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1,},},},

}
