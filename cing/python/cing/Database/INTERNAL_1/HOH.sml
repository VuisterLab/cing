<SML> 0.23

#=======================================================================
#             	internal short   
<ResidueDef>  	HOH      O        INTERNAL_1
#=======================================================================
	comment    = 'Regular Water residue'
	nameDict   = {'CCPN': 'other Hoh neutral', 'BMRBd': 'HOH', 'IUPAC': 'HOH', 'AQUA': 'HOH', 'INTERNAL_0': 'HOH', 'INTERNAL_1': 'HOH', 'CYANA': None, 'CYANA2': None, 'PDB': 'HOH', 'XPLOR': 'HOH'}
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
		nameDict   = {'CCPN': 'O', 'BMRBd': 'O', 'IUPAC': 'O', 'AQUA': 'O', 'INTERNAL_0': 'O', 'INTERNAL_1': 'O', 'CYANA': None, 'CYANA2': None, 'PDB': 'O', 'XPLOR': 'O'}
		aliases    = []
		type       = 'O_HYD'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H1      
	#---------------------------------------------------------------
		topology   = [(0, 'O')]
		real       = []
		pseudo     = 'QH'
		nameDict   = {'CCPN': 'H1', 'BMRBd': 'H1', 'IUPAC': 'H1', 'AQUA': 'H1', 'INTERNAL_0': 'H1', 'INTERNAL_1': 'H1', 'CYANA': None, 'CYANA2': None, 'PDB': 'H1', 'XPLOR': 'H1'}
		aliases    = []
		type       = 'H_OXY'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H2      
	#---------------------------------------------------------------
		topology   = [(0, 'O')]
		real       = []
		pseudo     = 'QH'
		nameDict   = {'CCPN': 'H2', 'BMRBd': 'H2', 'IUPAC': 'H2', 'AQUA': 'H2', 'INTERNAL_0': 'H2', 'INTERNAL_1': 'H2', 'CYANA': None, 'CYANA2': None, 'PDB': 'H2', 'XPLOR': 'H2'}
		aliases    = []
		type       = 'H_OXY'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QH      
	#---------------------------------------------------------------
		topology   = [(0, 'O')]
		real       = ['H1', 'H2']
		pseudo     = None
		nameDict   = {'CCPN': 'H*', 'BMRBd': None, 'IUPAC': None, 'AQUA': None, 'INTERNAL_0': 'QH', 'INTERNAL_1': 'QH', 'CYANA': None, 'CYANA2': None, 'PDB': None, 'XPLOR': None}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isPseudoAtom', 'pseudoatom']
	</AtomDef>
	</NTlist>
</ResidueDef>
#=======================================================================
</SML>
