<SML> 0.24

#=======================================================================
#             	name     convention
<ResidueDef>  	HOH      INTERNAL_1
#=======================================================================
	commonName = 'HOH'
	shortName  = 'O'
	comment    = 'Regular Water residue'
	nameDict   = {'CCPN': 'other Hoh neutral', 'INTERNAL_0': 'HOH', 'CYANA': None, 'CYANA2': None, 'INTERNAL_1': 'HOH', 'IUPAC': 'HOH', 'AQUA': 'HOH', 'BMRBd': 'HOH', 'XPLOR': 'HOH', 'PDB': 'HOH'}
	properties = ['small', 'polar']

	dihedrals  = <NTlist>
	</NTlist>

	atoms      = <NTlist>
	#---------------------------------------------------------------
	<AtomDef> O       
	#---------------------------------------------------------------
		topology   = [(0, 'H1'), (0, 'H2')]
		real       = []
		pseudo     = 'QH'
		nameDict   = {'CCPN': 'O', 'INTERNAL_0': 'O', 'CYANA': None, 'CYANA2': None, 'INTERNAL_1': 'O', 'IUPAC': 'O', 'AQUA': 'O', 'BMRBd': 'O', 'XPLOR': 'O', 'PDB': 'O'}
		aliases    = []
		type       = 'O_HYD'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H1      
	#---------------------------------------------------------------
		topology   = [(0, 'O')]
		real       = []
		pseudo     = 'QH'
		nameDict   = {'CCPN': 'H1', 'INTERNAL_0': 'H1', 'CYANA': None, 'CYANA2': None, 'INTERNAL_1': 'H1', 'IUPAC': 'H1', 'AQUA': 'H1', 'BMRBd': 'H1', 'XPLOR': 'H1', 'PDB': 'H1'}
		aliases    = []
		type       = 'H_OXY'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H2      
	#---------------------------------------------------------------
		topology   = [(0, 'O')]
		real       = []
		pseudo     = 'QH'
		nameDict   = {'CCPN': 'H2', 'INTERNAL_0': 'H2', 'CYANA': None, 'CYANA2': None, 'INTERNAL_1': 'H2', 'IUPAC': 'H2', 'AQUA': 'H2', 'BMRBd': 'H2', 'XPLOR': 'H2', 'PDB': 'H2'}
		aliases    = []
		type       = 'H_OXY'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QH      
	#---------------------------------------------------------------
		topology   = [(0, 'O')]
		real       = ['H1', 'H2']
		pseudo     = None
		nameDict   = {'CCPN': 'H*', 'INTERNAL_0': 'QH', 'CYANA': None, 'CYANA2': None, 'INTERNAL_1': 'QH', 'IUPAC': None, 'AQUA': None, 'BMRBd': None, 'XPLOR': None, 'PDB': None}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isPseudoAtom', 'pseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	</NTlist>
</ResidueDef>
#=======================================================================
</SML>
