<SML> 0.24

#=======================================================================
#             	name     convention
<ResidueDef>  	LLM5     INTERNAL_1
#=======================================================================
	commonName = 'LLM5'
	shortName  = 'LLM5'
	comment    = 'Cyana pseudo residue'
	nameDict   = {'INTERNAL_0': 'LLM5', 'BMRBd': None, 'CYANA': 'LLM5', 'CYANA2': 'LLM5', 'INTERNAL_1': 'LLM5', 'IUPAC': None, 'AQUA': None, 'PDB': None, 'XPLOR': None}
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
	<AtomDef> Q3'     
	#---------------------------------------------------------------
		topology   = []
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': "Q3'", 'BMRBd': None, 'CYANA': "Q3'", 'CYANA2': "Q3'", 'INTERNAL_1': "Q3'", 'IUPAC': None, 'AQUA': None, 'PDB': None, 'XPLOR': None}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton', 'isNotPseudoAtom', 'notpseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> Q1      
	#---------------------------------------------------------------
		topology   = []
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': 'Q1', 'BMRBd': None, 'CYANA': 'Q1', 'CYANA2': 'Q1', 'INTERNAL_1': 'Q1', 'IUPAC': None, 'AQUA': None, 'PDB': None, 'XPLOR': None}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton', 'isNotPseudoAtom', 'notpseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> Q1'     
	#---------------------------------------------------------------
		topology   = []
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': "Q1'", 'BMRBd': None, 'CYANA': "Q1'", 'CYANA2': "Q1'", 'INTERNAL_1': "Q1'", 'IUPAC': None, 'AQUA': None, 'PDB': None, 'XPLOR': None}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton', 'isNotPseudoAtom', 'notpseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> Q2      
	#---------------------------------------------------------------
		topology   = []
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': 'Q2', 'BMRBd': None, 'CYANA': 'Q2', 'CYANA2': 'Q2', 'INTERNAL_1': 'Q2', 'IUPAC': None, 'AQUA': None, 'PDB': None, 'XPLOR': None}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton', 'isNotPseudoAtom', 'notpseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> Q2'     
	#---------------------------------------------------------------
		topology   = []
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': "Q2'", 'BMRBd': None, 'CYANA': "Q2'", 'CYANA2': "Q2'", 'INTERNAL_1': "Q2'", 'IUPAC': None, 'AQUA': None, 'PDB': None, 'XPLOR': None}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton', 'isNotPseudoAtom', 'notpseudoatom']
	</AtomDef>
	</NTlist>
</ResidueDef>
#=======================================================================
</SML>
