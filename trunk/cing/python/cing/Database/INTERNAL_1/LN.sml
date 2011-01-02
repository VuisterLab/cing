<SML> 0.24

#=======================================================================
#             	name     convention
<ResidueDef>  	LN       INTERNAL_1
#=======================================================================
	commonName = 'LN'
	shortName  = 'LN'
	comment    = 'Cyana pseudo residue'
	nameDict   = {'INTERNAL_0': 'LN', 'BMRBd': None, 'CYANA': 'LN', 'CYANA2': 'LN', 'INTERNAL_1': 'LN', 'IUPAC': None, 'AQUA': None, 'PDB': None, 'XPLOR': None}
	properties = ['cyanaPseudoResidue']

	dihedrals  = <NTlist>
	#---------------------------------------------------------------
	<DihedralDef> LB      
	#---------------------------------------------------------------
		atoms    = [(-1, 'Q2'), (0, 'Q3'), (0, "C3'"), (0, "O3'")]
		karplus  = None
	</DihedralDef>
	</NTlist>

	atoms      = <NTlist>
	#---------------------------------------------------------------
	<AtomDef> Q3      
	#---------------------------------------------------------------
		topology   = []
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': 'Q3', 'BMRBd': None, 'CYANA': 'Q3', 'CYANA2': 'Q3', 'INTERNAL_1': 'Q3', 'IUPAC': None, 'AQUA': None, 'PDB': None, 'XPLOR': None}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton', 'isNotPseudoAtom', 'notpseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> C3'     
	#---------------------------------------------------------------
		topology   = []
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': "C3'", 'BMRBd': None, 'CYANA': "C3'", 'CYANA2': "C3'", 'INTERNAL_1': "C3'", 'IUPAC': None, 'AQUA': None, 'PDB': None, 'XPLOR': None}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '13C'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton', 'isNotPseudoAtom', 'notpseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> O3'     
	#---------------------------------------------------------------
		topology   = []
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': "O3'", 'BMRBd': None, 'CYANA': "O3'", 'CYANA2': "O3'", 'INTERNAL_1': "O3'", 'IUPAC': None, 'AQUA': None, 'PDB': None, 'XPLOR': None}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton', 'isNotPseudoAtom', 'notpseudoatom']
	</AtomDef>
	</NTlist>
</ResidueDef>
#=======================================================================
</SML>
