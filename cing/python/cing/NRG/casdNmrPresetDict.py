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

'NeR103AParis': {
  'comment': """
' ' is used inside FC for where there is no chain code.
The funny thing is that '   A' needs to be used for xplor's '   A' and not simply 'A'.

 """,
  'linkResonances': {
   'keywds': {
#     'forceDefaultChainMapping': 1,
     'forceChainMappings': [['A', ' ', 1, 0], ['A', '   A', 1, 0]],
      },
    },
  },

#'PGR122ACheshire': {
#  'comment': """
#Offset should be -416 why doesn't it figure that out?
# """,
#  'readCoordinates': {
#   'keywds': {
##     'forceChainMappings': [['A', 'DEMO', 1, -416]],
#      'forceDefaultChainMapping': 1, # Use if default chain mapping is correct
#                                      # Only works if one CCPN chain, one format chain present!
#      },
#    },
#  },


'CGR26ACheshire'   : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1, }, }, },
'CGR26AFrankfurt'  : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1, }, }, },
'CGR26ALyon'       : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1, }, }, },
'CGR26APiscataway' : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1, }, }, },
'CGR26ASeattle4'   : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1, }, }, },
'CGR26ASeattle5'   : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1, }, }, },
#'CGR26AUtrecht2'   : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1,},},},
'ET109AoxSeattle'  : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1, }, }, },
'ET109AoxUtrecht2' : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1, }, }, },
'ET109AredCheshire': {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1, }, }, },
'ET109AredSeattle' : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1, }, }, },
'ET109AredUtrecht2': {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1, }, }, },
'PGR122ACheshire'  : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1, }, }, },
'PGR122APiscataway': {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1, }, }, },
'PGR122ASeattle4'  : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1, }, }, },
'PGR122AUtrecht'   : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1, }, }, },

'ET109AredParis'   : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1, }, }, # The RDC frame coordinates are messing things up. Best if removed.
                      'linkResonances':  {'keywds': {'forceChainMappings': [['A', ' ', 1, 89], ['A', '   A', 1, 89], ['A', 'A', 1, 89]], }},
                      },
'ET109AoxParis'    : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1, }, }, # The RDC frame coordinates are messing things up. Best if removed.
                      'linkResonances':  {'keywds': {'forceChainMappings': [['A', ' ', 1, 89], ['A', '   A', 1, 89], ['A', 'A', 1, 89]], }},
                      },
'PGR122AParis2'    : {'readCoordinates': {'keywds': {'forceDefaultChainMapping': 1, }, }, # The RDC frame coordinates are messing things up. Best if removed.
#                      'linkResonances':  {'keywds': {'forceChainMappings': [['A', ' ', 1, 0], ['A', '   A', 1, 0]],}},
#                      'linkResonances':  {'keywds': {'forceDefaultChainMapping': 1,},},
                      },

'AtT13Paris'    : {'linkResonances': {'keywds': {'forceChainMappings': [['A', ' ', 1, 0], ['A', '   A', 1, 0]], }}},
'CGR26AParis'   : {'linkResonances': {'keywds': {'forceChainMappings': [['A', ' ', 1, 40], ['A', '   A', 1, 40]], }}},
'CtR69AParis'   : {'linkResonances': {'keywds': {'forceChainMappings': [['A', ' ', 1, 0], ['A', '   A', 1, 0]], }}},
'HR5537AParis'  : {'linkResonances': {'keywds': {'forceChainMappings': [['A', ' ', 1, 0], ['A', '   A', 1, 0]], }}},

'VpR247Paris'   : {'linkResonances': {'keywds': {'forceChainMappings': [['A', ' ', 1, 0], ['A', '   A', 1, 0]], }}},

'AtT13Utrecht'   : {
    'comments': 'ccpn met4 is pdb met1',
    'readCoordinates': {'keywds': {
     'forceChainMappings': [['A', ' ', 1, -3]],
}, }, },

'HR5537AUtrecht2'   : {
    'comments': 'ccpn Lys39 is pdb Lys1',
    'readCoordinates': {'keywds': {
     'forceChainMappings': [['A', ' ', 1, -38]],
}, }, },

'CGR26AUtrecht2'   : {
    'comments': 'ccpn Glu11 is pdb Glu1',
    'readCoordinates': {'keywds': {
     'forceChainMappings': [['A', ' ', 1, -10]],
}, }, },

'AR3436ACheshire'   : {
    'comments': 'ccpn His10 is pdb His1',
    'readCoordinates': {'keywds': {
     'forceChainMappings': [['A', 'A', 1, -9]],
}, }, },

'HR5537ACheshire'   : {
    'comments': 'ccpn Ile37 is pdb Ile1',
    'readCoordinates': {'keywds': {
     'forceChainMappings': [['A', 'A', 1, -36]],
}, }, },

'NeR103AUtrecht2'   : {
    'comments': 'ccpn Lys18 is pdb Lys1',
    'readCoordinates': {'keywds': {
     'forceChainMappings': [['A', ' ', 1, -17]],
}, }, },

'CtR69ACheshire'   : {
    'comments': 'ccpn Leu4 is pdb Leu1',
    'readCoordinates': {'keywds': {
     'forceChainMappings': [['A', 'A', 1, -3]],
}, }, },

'CtR69AUtrecht'   : {
    'comments': 'ccpn Glu3 is pdb Glu1',
    'readCoordinates': {'keywds': {
     'forceChainMappings': [['A', ' ', 1, -2]],
}, }, },

'VpR247Cheshire'   : {
    'comments': 'ccpn Ile CD1 is pseudo pdb CD',
    'readCoordinates': {   'keywds': {
     'addNameMappings': {'Ile': [['CD', 'CD1']]}, # second name is CCPN
}, }, },

}
