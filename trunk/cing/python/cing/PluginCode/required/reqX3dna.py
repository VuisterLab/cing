'required items for this plugin for CING setup'
from cing.Libs.NTutils import * #@UnusedWildImport

X3DNA_STR = "x3dna"

SHIFT_STR = 'shift'
SLIDE_STR = 'slide'
RISE_STR = 'rise'
TILT_STR = 'tilt'
ROLL_STR = 'roll'
TWIST_STR = 'twist'
SHEAR_STR = 'shear'
STRETCH_STR = 'stretch'
STAGGER_STR = 'stagger'
BUCKLE_STR = 'buckle'
PROPELLER_STR = 'propeller'
OPENING_STR = 'opening'
MINPP_STR = 'minPP'
MAJPP_STR = 'majPP'

x3dnaPlotList = []
x3dnaPlotList.append( ('_01_all','data not used from here right?') )

nameDefs = [
    (SHIFT_STR    , None, 'shift'    , 'shift/slide/rise (A)'), # trick to combine in plot
    (SLIDE_STR    , None, 'slide'    , 'slide'),
    (RISE_STR     , None, 'rise'     , 'rise'),
    (TILT_STR     , None, 'tilt'     , 'tilt/roll/twist (o)'),
    (ROLL_STR     , None, 'roll'     , 'roll'),
    (TWIST_STR    , None, 'twist'    , 'twist'),
    (SHEAR_STR    , None, 'shear'    , 'shear/strech/stagger'),
    (STRETCH_STR  , None, 'stretch'  , 'stretch'),
    (STAGGER_STR  , None, 'stagger'  , 'stagger'),
    (BUCKLE_STR   , None, 'buckle'   , 'buckle/propeller/opening (o)'),
    (PROPELLER_STR, None, 'propeller', 'propeller'),
    (OPENING_STR  , None, 'opening'  , 'opening'),
    (MINPP_STR    , None, 'minor groove phosphorus-phosphorus', 'minor/major PP (A)'),
    (MAJPP_STR    , None, 'major minor groove phosphorus-phosphorus', 'majPP'),
]
cingNameDict = NTdict(zip(nTzap(nameDefs, 0), nTzap(nameDefs, 1)))
nameDict = NTdict(zip(nTzap(nameDefs, 0), nTzap(nameDefs, 2)))
shortNameDict = NTdict(zip(nTzap(nameDefs, 0), nTzap(nameDefs, 3)))
cingNameDict.keysformat()
nameDict.keysformat()
shortNameDict.keysformat()
