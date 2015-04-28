<SML> 0.23

#=======================================================================
#             	internal short   
<ResidueDef>  	NLM      NLM      INTERNAL_0
#=======================================================================
	comment    = 'Cyana pseudo residue'
	nameDict   = {'INTERNAL_0': 'NLM', 'IUPAC': None, 'AQUA': None, 'BMRBd': None, 'INTERNAL_1': 'NLM', 'CYANA': 'NLM', 'CYANA2': 'NLM', 'PDB': None, 'XPLOR': None}
	properties = ['cyanaPseudoResidue']

	dihedrals  = <NTlist>
	#---------------------------------------------------------------
	<DihedralDef> LB      
	#---------------------------------------------------------------
		atoms    = [(-1, "O3'"), (0, 'P'), (0, 'Q1'), (0, 'Q2')]
		karplus  = None
	</DihedralDef>
	</NTlist>

	atoms      = <NTlist>
	#---------------------------------------------------------------
	<AtomDef> P       
	#---------------------------------------------------------------
		topology   = []
		nameDict   = {'INTERNAL_0': 'P', 'IUPAC': None, 'AQUA': None, 'BMRBd': None, 'INTERNAL_1': 'P', 'CYANA': 'P', 'CYANA2': 'P', 'PDB': None, 'XPLOR': None}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'PSEUD'
		spinType   = '31P'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
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
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> Q1'     
	#---------------------------------------------------------------
		topology   = []
		nameDict   = {'INTERNAL_0': "Q1'", 'IUPAC': None, 'AQUA': None, 'BMRBd': None, 'INTERNAL_1': "Q1'", 'CYANA': "Q1'", 'CYANA2': "Q1'", 'PDB': None, 'XPLOR': None}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
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
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> Q2'     
	#---------------------------------------------------------------
		topology   = []
		nameDict   = {'INTERNAL_0': "Q2'", 'IUPAC': None, 'AQUA': None, 'BMRBd': None, 'INTERNAL_1': "Q2'", 'CYANA': "Q2'", 'CYANA2': "Q2'", 'PDB': None, 'XPLOR': None}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	</NTlist>
</ResidueDef>
#=======================================================================
</SML>
