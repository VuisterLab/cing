<SML> 0.23

#=======================================================================
#             	internal short
<ResidueDef>  	LL5      LL5      INTERNAL_0
#=======================================================================
	comment    = 'Cyana pseudo residue'
	nameDict   = {'INTERNAL_0': 'LL5', 'IUPAC': None, 'AQUA': None, 'BMRBd': None, 'INTERNAL_1': 'LL5', 'CYANA': 'LL5', 'CYANA2': 'LL5', 'PDB': None, 'XPLOR': None}
	properties = ['cyanaPseudoResidue']

	dihedrals  = <NTlist>
	#---------------------------------------------------------------
	<DihedralDef> LB
	#---------------------------------------------------------------
		atoms    = [(-1, 'Q2'), (0, 'Q3'), (0, 'Q1'), (0, 'Q2')]
		karplus  = None
	</DihedralDef>
	</NTlist>

	atoms      = <NTlist>
	#---------------------------------------------------------------
	<AtomDef> Q3
	#---------------------------------------------------------------
		topology   = []
		nameDict   = {'INTERNAL_0': 'Q3', 'IUPAC': None, 'AQUA': None, 'BMRBd': None, 'INTERNAL_1': 'Q3', 'CYANA': 'Q3', 'CYANA2': 'Q3', 'PDB': None, 'XPLOR': None}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> Q1
	#---------------------------------------------------------------
		topology   = []
		nameDict   = {'INTERNAL_0': 'Q1', 'IUPAC': None, 'AQUA': None, 'BMRBd': None, 'INTERNAL_1': 'Q1', 'CYANA': 'Q1', 'CYANA2': 'Q1', 'PDB': None, 'XPLOR': None}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> Q2
	#---------------------------------------------------------------
		topology   = []
		nameDict   = {'INTERNAL_0': 'Q2', 'IUPAC': None, 'AQUA': None, 'BMRBd': None, 'INTERNAL_1': 'Q2', 'CYANA': 'Q2', 'CYANA2': 'Q2', 'PDB': None, 'XPLOR': None}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	</NTlist>
</ResidueDef>
#=======================================================================
</SML>
