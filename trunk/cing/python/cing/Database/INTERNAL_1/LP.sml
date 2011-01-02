<SML> 0.24

#=======================================================================
#             	name     convention
<ResidueDef>  	LP       INTERNAL_1
#=======================================================================
	commonName = 'LP'
	shortName  = 'LP'
	comment    = 'Cyana pseudo residue'
	nameDict   = {'INTERNAL_0': 'LP', 'BMRBd': None, 'CYANA': 'LP', 'CYANA2': 'LP', 'INTERNAL_1': 'LP', 'IUPAC': None, 'AQUA': None, 'PDB': None, 'XPLOR': None}
	properties = ['cyanaPseudoResidue']

	dihedrals  = <NTlist>
	#---------------------------------------------------------------
	<DihedralDef> LB      
	#---------------------------------------------------------------
		atoms    = [(-1, 'Q2'), (0, 'Q3'), (0, 'C'), (0, 'O')]
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
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> C       
	#---------------------------------------------------------------
		topology   = []
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': 'C', 'BMRBd': None, 'CYANA': 'C', 'CYANA2': 'C', 'INTERNAL_1': 'C', 'IUPAC': None, 'AQUA': None, 'PDB': None, 'XPLOR': None}
		aliases    = ['C', 'CO']
		type       = 'PSEUD'
		spinType   = '13C'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> O       
	#---------------------------------------------------------------
		topology   = []
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': 'O', 'BMRBd': None, 'CYANA': 'O', 'CYANA2': 'O', 'INTERNAL_1': 'O', 'IUPAC': None, 'AQUA': None, 'PDB': None, 'XPLOR': None}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	</NTlist>
</ResidueDef>
#=======================================================================
</SML>
