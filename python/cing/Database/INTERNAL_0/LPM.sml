<SML> 0.23

#=======================================================================
#             	internal short   
<ResidueDef>  	LPM      LPM      INTERNAL_0
#=======================================================================
	comment    = 'Cyana pseudo residue'
	nameDict   = {'INTERNAL_0': 'LPM', 'IUPAC': None, 'AQUA': None, 'BMRBd': None, 'INTERNAL_1': 'LPM', 'CYANA': 'LPM', 'CYANA2': 'LPM', 'PDB': None, 'XPLOR': None}
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
		nameDict   = {'INTERNAL_0': 'Q3', 'IUPAC': None, 'AQUA': None, 'BMRBd': None, 'INTERNAL_1': 'Q3', 'CYANA': 'Q3', 'CYANA2': 'Q3', 'PDB': None, 'XPLOR': None}
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
	<AtomDef> Q3'     
	#---------------------------------------------------------------
		topology   = []
		nameDict   = {'INTERNAL_0': "Q3'", 'IUPAC': None, 'AQUA': None, 'BMRBd': None, 'INTERNAL_1': "Q3'", 'CYANA': "Q3'", 'CYANA2': "Q3'", 'PDB': None, 'XPLOR': None}
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
	<AtomDef> C       
	#---------------------------------------------------------------
		topology   = []
		nameDict   = {'INTERNAL_0': 'C', 'IUPAC': None, 'AQUA': None, 'BMRBd': None, 'INTERNAL_1': 'C', 'CYANA': 'C', 'CYANA2': 'C', 'PDB': None, 'XPLOR': None}
		aliases    = ['C', 'CO']
		pseudo     = None
		real       = []
		type       = 'PSEUD'
		spinType   = '13C'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> O       
	#---------------------------------------------------------------
		topology   = []
		nameDict   = {'INTERNAL_0': 'O', 'IUPAC': None, 'AQUA': None, 'BMRBd': None, 'INTERNAL_1': 'O', 'CYANA': 'O', 'CYANA2': 'O', 'PDB': None, 'XPLOR': None}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'PSEUD'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	</NTlist>
</ResidueDef>
#=======================================================================
</SML>
