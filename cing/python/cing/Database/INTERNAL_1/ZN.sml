<SML> 0.24

#=======================================================================
#             	name     convention
<ResidueDef>  	ZN       INTERNAL_1
#=======================================================================
	commonName = 'ZN'
	shortName  = 'ZN'
	comment    = 'Zinc 2plus ion'
	nameDict   = {'INTERNAL_0': 'ZN', 'BMRBd': None, 'CYANA': 'ZN', 'CYANA2': 'ZN', 'INTERNAL_1': 'ZN', 'IUPAC': 'ZN', 'AQUA': 'ZN', 'PDB': 'ZN', 'XPLOR': 'ZN2'}
	properties = ['ion', 'metal', 'charged']

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
	<AtomDef> ZN      
	#---------------------------------------------------------------
		topology   = []
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': 'ZN', 'BMRBd': None, 'CYANA': 'ME', 'CYANA2': 'ME', 'INTERNAL_1': 'ZN', 'IUPAC': 'ZN', 'AQUA': 'ZN', 'PDB': 'ZN', 'XPLOR': 'ZN+2'}
		aliases    = ['ZN', 'ME']
		type       = None
		spinType   = '??Zn'
		shift      = None
		hetatm     = True
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
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
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
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
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
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
