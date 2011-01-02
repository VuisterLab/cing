<SML> 0.24

#=======================================================================
#             	name     convention
<ResidueDef>  	PLM      INTERNAL_1
#=======================================================================
	commonName = 'PLM'
	shortName  = 'PLM'
	comment    = 'Cyana pseudo residue'
	nameDict   = {'INTERNAL_0': 'PLM', 'BMRBd': None, 'CYANA': 'PLM', 'CYANA2': 'PLM', 'INTERNAL_1': 'PLM', 'IUPAC': None, 'AQUA': None, 'PDB': None, 'XPLOR': None}
	properties = ['cyanaPseudoResidue']

	dihedrals  = <NTlist>
	#---------------------------------------------------------------
	<DihedralDef> LB      
	#---------------------------------------------------------------
		atoms    = [(-1, 'O'), (0, 'N'), (0, 'Q1'), (0, 'Q2')]
		karplus  = None
	</DihedralDef>
	</NTlist>

	atoms      = <NTlist>
	#---------------------------------------------------------------
	<AtomDef> N       
	#---------------------------------------------------------------
		topology   = []
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': 'N', 'BMRBd': None, 'CYANA': 'N', 'CYANA2': 'N', 'INTERNAL_1': 'N', 'IUPAC': None, 'AQUA': None, 'PDB': None, 'XPLOR': None}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '15N'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
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
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
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
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
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
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
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
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	</NTlist>
</ResidueDef>
#=======================================================================
</SML>
