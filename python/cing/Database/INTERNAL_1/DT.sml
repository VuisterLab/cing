<SML> 0.24

#=======================================================================
#             	name     convention
<ResidueDef>  	DT       INTERNAL_1
#=======================================================================
	commonName = 'THY'
	shortName  = 't'
	comment    = 'deoxy-thymine'
	nameDict   = {'CCPN': 'DNA T prot:H3', 'INTERNAL_0': 'THY', 'CYANA': 'THY', 'CYANA2': 'THY', 'INTERNAL_1': 'DT', 'IUPAC': 'DT', 'AQUA': 'T', 'BMRBd': 'THY', 'XPLOR': 'THY', 'PDB': 'THY'}
	properties = ['nucleic', 'deoxy', 'DNA']

	dihedrals  = <NTlist>
	#---------------------------------------------------------------
	<DihedralDef> ALPHA   
	#---------------------------------------------------------------
		atoms    = [(-1, "O3'"), (0, 'P'), (0, "O5'"), (0, "C5'")]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> BETA    
	#---------------------------------------------------------------
		atoms    = [(0, 'P'), (0, "O5'"), (0, "C5'"), (0, "C4'")]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> GAMMA   
	#---------------------------------------------------------------
		atoms    = [(0, "O5'"), (0, "C5'"), (0, "C4'"), (0, "C3'")]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> DELTA   
	#---------------------------------------------------------------
		atoms    = [(0, "C5'"), (0, "C4'"), (0, "C3'"), (0, "O3'")]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> EPSILON 
	#---------------------------------------------------------------
		atoms    = [(0, "C4'"), (0, "C3'"), (0, "O3'"), (1, 'P')]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> ZETA    
	#---------------------------------------------------------------
		atoms    = [(0, "C3'"), (0, "O3'"), (1, 'P'), (1, "O5'")]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> NU0     
	#---------------------------------------------------------------
		atoms    = [(0, "C4'"), (0, "O4'"), (0, "C1'"), (0, "C2'")]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> NU1     
	#---------------------------------------------------------------
		atoms    = [(0, "O4'"), (0, "C1'"), (0, "C2'"), (0, "C3'")]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> NU2     
	#---------------------------------------------------------------
		atoms    = [(0, "C1'"), (0, "C2'"), (0, "C3'"), (0, "C4'")]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> NU3     
	#---------------------------------------------------------------
		atoms    = [(0, "C2'"), (0, "C3'"), (0, "C4'"), (0, "O4'")]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> NU4     
	#---------------------------------------------------------------
		atoms    = [(0, "C3'"), (0, "C4'"), (0, "O4'"), (0, "C1'")]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> CHI     
	#---------------------------------------------------------------
		atoms    = [(0, 'C4'), (0, 'C5'), (0, 'N1'), (0, 'C2')]
		karplus  = None
	</DihedralDef>
	</NTlist>

	atoms      = <NTlist>
	#---------------------------------------------------------------
	<AtomDef> P       
	#---------------------------------------------------------------
		topology   = [(-1, "O3'"), (0, 'OP1'), (0, 'OP2'), (0, "O5'")]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'P', 'INTERNAL_0': 'P', 'CYANA': 'P', 'CYANA2': 'P', 'INTERNAL_1': 'P', 'IUPAC': 'P', 'AQUA': 'P', 'BMRBd': None, 'XPLOR': 'P', 'PDB': None}
		aliases    = []
		type       = 'P_ALI'
		spinType   = '31P'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isBackbone', 'backbone', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> OP1     
	#---------------------------------------------------------------
		topology   = [(0, 'P')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'OP1', 'INTERNAL_0': 'OP1', 'CYANA': 'OP1', 'CYANA2': 'OP1', 'INTERNAL_1': 'OP1', 'IUPAC': 'OP1', 'AQUA': 'OP1', 'BMRBd': None, 'XPLOR': 'O1P', 'PDB': None}
		aliases    = []
		type       = 'O_BYL'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> OP2     
	#---------------------------------------------------------------
		topology   = [(0, 'P')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'OP2', 'INTERNAL_0': 'OP2', 'CYANA': 'OP2', 'CYANA2': 'OP2', 'INTERNAL_1': 'OP2', 'IUPAC': 'OP2', 'AQUA': 'OP2', 'BMRBd': None, 'XPLOR': 'O2P', 'PDB': None}
		aliases    = []
		type       = 'O_BYL'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> O5'     
	#---------------------------------------------------------------
		topology   = [(0, 'P'), (0, "C5'")]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': "O5'", 'INTERNAL_0': "O5'", 'CYANA': "O5'", 'CYANA2': "O5'", 'INTERNAL_1': "O5'", 'IUPAC': "O5'", 'AQUA': "O5'", 'BMRBd': None, 'XPLOR': "O5'", 'PDB': None}
		aliases    = []
		type       = 'O_EST'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isBackbone', 'backbone', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> C5'     
	#---------------------------------------------------------------
		topology   = [(0, "O5'"), (0, "H5'"), (0, "H5''"), (0, "C4'")]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': "C5'", 'INTERNAL_0': "C5'", 'CYANA': "C5'", 'CYANA2': "C5'", 'INTERNAL_1': "C5'", 'IUPAC': "C5'", 'AQUA': "C5'", 'BMRBd': None, 'XPLOR': "C5'", 'PDB': None}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isBackbone', 'backbone', 'isMethylene', 'methylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H5'     
	#---------------------------------------------------------------
		topology   = [(0, "C5'")]
		real       = []
		pseudo     = "Q5'"
		nameDict   = {'CCPN': "H5'", 'INTERNAL_0': "H5'", 'CYANA': "H5'", 'CYANA2': "H5'", 'INTERNAL_1': "H5'", 'IUPAC': "H5'", 'AQUA': "H5'", 'BMRBd': None, 'XPLOR': "H5'", 'PDB': None}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H5''    
	#---------------------------------------------------------------
		topology   = [(0, "C5'")]
		real       = []
		pseudo     = "Q5'"
		nameDict   = {'CCPN': "H5''", 'INTERNAL_0': 'H5"', 'CYANA': 'H5"', 'CYANA2': 'H5"', 'INTERNAL_1': "H5''", 'IUPAC': "H5''", 'AQUA': "H5''", 'BMRBd': None, 'XPLOR': "H5''", 'PDB': None}
		aliases    = ["H5''", 'H5"']
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> Q5'     
	#---------------------------------------------------------------
		topology   = []
		real       = ["H5'", "H5''"]
		pseudo     = None
		nameDict   = {'CCPN': "H5'*", 'INTERNAL_0': "Q5'", 'CYANA': "Q5'", 'CYANA2': "Q5'", 'INTERNAL_1': "Q5'", 'IUPAC': "Q5'", 'AQUA': "Q5'", 'BMRBd': None, 'XPLOR': "Q5'", 'PDB': None}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> C4'     
	#---------------------------------------------------------------
		topology   = [(0, "C5'"), (0, "H4'"), (0, "O4'"), (0, "C3'")]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': "C4'", 'INTERNAL_0': "C4'", 'CYANA': "C4'", 'CYANA2': "C4'", 'INTERNAL_1': "C4'", 'IUPAC': "C4'", 'AQUA': "C4'", 'BMRBd': None, 'XPLOR': "C4'", 'PDB': None}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isBackbone', 'backbone', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H4'     
	#---------------------------------------------------------------
		topology   = [(0, "C4'")]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': "H4'", 'INTERNAL_0': "H4'", 'CYANA': "H4'", 'CYANA2': "H4'", 'INTERNAL_1': "H4'", 'IUPAC': "H4'", 'AQUA': "H4'", 'BMRBd': None, 'XPLOR': "H4'", 'PDB': None}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> C3'     
	#---------------------------------------------------------------
		topology   = [(0, "C4'"), (0, "C2'"), (0, "H3'"), (0, "O3'")]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': "C3'", 'INTERNAL_0': "C3'", 'CYANA': "C3'", 'CYANA2': "C3'", 'INTERNAL_1': "C3'", 'IUPAC': "C3'", 'AQUA': "C3'", 'BMRBd': None, 'XPLOR': "C3'", 'PDB': None}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isBackbone', 'backbone', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H3'     
	#---------------------------------------------------------------
		topology   = [(0, "C3'")]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': "H3'", 'INTERNAL_0': "H3'", 'CYANA': "H3'", 'CYANA2': "H3'", 'INTERNAL_1': "H3'", 'IUPAC': "H3'", 'AQUA': "H3'", 'BMRBd': None, 'XPLOR': "H3'", 'PDB': None}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> C2'     
	#---------------------------------------------------------------
		topology   = [(0, "C1'"), (0, "H2'"), (0, "H2''"), (0, "C3'")]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': "C2'", 'INTERNAL_0': "C2'", 'CYANA': "C2'", 'CYANA2': "C2'", 'INTERNAL_1': "C2'", 'IUPAC': "C2'", 'AQUA': "C2'", 'BMRBd': None, 'XPLOR': "C2'", 'PDB': None}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H2'     
	#---------------------------------------------------------------
		topology   = [(0, "C2'")]
		real       = []
		pseudo     = "Q2'"
		nameDict   = {'CCPN': "H2'", 'INTERNAL_0': "H2'", 'CYANA': "H2'", 'CYANA2': "H2'", 'INTERNAL_1': "H2'", 'IUPAC': "H2'", 'AQUA': "H2'", 'BMRBd': None, 'XPLOR': "H2'", 'PDB': None}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H2''    
	#---------------------------------------------------------------
		topology   = [(0, "C2'")]
		real       = []
		pseudo     = "Q2'"
		nameDict   = {'CCPN': "H2''", 'INTERNAL_0': 'H2"', 'CYANA': 'H2"', 'CYANA2': 'H2"', 'INTERNAL_1': "H2''", 'IUPAC': "H2''", 'AQUA': "H2''", 'BMRBd': None, 'XPLOR': "H2''", 'PDB': None}
		aliases    = ["H2''", 'H2"']
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> Q2'     
	#---------------------------------------------------------------
		topology   = []
		real       = ["H2'", "H2''"]
		pseudo     = None
		nameDict   = {'CCPN': "H2'*", 'INTERNAL_0': "Q2'", 'CYANA': "Q2'", 'CYANA2': "Q2'", 'INTERNAL_1': "Q2'", 'IUPAC': "Q2'", 'AQUA': "Q2'", 'BMRBd': None, 'XPLOR': "Q2'", 'PDB': None}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> C1'     
	#---------------------------------------------------------------
		topology   = [(0, "O4'"), (0, "H1'"), (0, 'N1'), (0, "C2'")]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': "C1'", 'INTERNAL_0': "C1'", 'CYANA': "C1'", 'CYANA2': "C1'", 'INTERNAL_1': "C1'", 'IUPAC': "C1'", 'AQUA': "C1'", 'BMRBd': None, 'XPLOR': "C1'", 'PDB': None}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H1'     
	#---------------------------------------------------------------
		topology   = [(0, "C1'")]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': "H1'", 'INTERNAL_0': "H1'", 'CYANA': "H1'", 'CYANA2': "H1'", 'INTERNAL_1': "H1'", 'IUPAC': "H1'", 'AQUA': "H1'", 'BMRBd': None, 'XPLOR': "H1'", 'PDB': None}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> O4'     
	#---------------------------------------------------------------
		topology   = [(0, "C4'"), (0, "C1'")]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': "O4'", 'INTERNAL_0': "O4'", 'CYANA': "O4'", 'CYANA2': "O4'", 'INTERNAL_1': "O4'", 'IUPAC': "O4'", 'AQUA': "O4'", 'BMRBd': None, 'XPLOR': "O4'", 'PDB': None}
		aliases    = []
		type       = 'O_EST'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> N1      
	#---------------------------------------------------------------
		topology   = [(0, "C1'"), (0, 'C2'), (0, 'C6')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'N1', 'INTERNAL_0': 'N1', 'CYANA': 'N1', 'CYANA2': 'N1', 'INTERNAL_1': 'N1', 'IUPAC': 'N1', 'AQUA': 'N1', 'BMRBd': None, 'XPLOR': 'N1', 'PDB': None}
		aliases    = []
		type       = 'N_AMI'
		spinType   = '15N'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> C2      
	#---------------------------------------------------------------
		topology   = [(0, 'N1'), (0, 'O2'), (0, 'N3')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'C2', 'INTERNAL_0': 'C2', 'CYANA': 'C2', 'CYANA2': 'C2', 'INTERNAL_1': 'C2', 'IUPAC': 'C2', 'AQUA': 'C2', 'BMRBd': None, 'XPLOR': 'C2', 'PDB': None}
		aliases    = []
		type       = 'C_ARO'
		spinType   = '13C'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> O2      
	#---------------------------------------------------------------
		topology   = [(0, 'C2')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'O2', 'INTERNAL_0': 'O2', 'CYANA': 'O2', 'CYANA2': 'O2', 'INTERNAL_1': 'O2', 'IUPAC': 'O2', 'AQUA': 'O2', 'BMRBd': None, 'XPLOR': 'O2', 'PDB': None}
		aliases    = []
		type       = 'O_BYL'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> N3      
	#---------------------------------------------------------------
		topology   = [(0, 'C2'), (0, 'H3'), (0, 'C4')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'N3', 'INTERNAL_0': 'N3', 'CYANA': 'N3', 'CYANA2': 'N3', 'INTERNAL_1': 'N3', 'IUPAC': 'N3', 'AQUA': 'N3', 'BMRBd': None, 'XPLOR': 'N3', 'PDB': None}
		aliases    = []
		type       = 'N_AMI'
		spinType   = '15N'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H3      
	#---------------------------------------------------------------
		topology   = [(0, 'N3')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'H3', 'INTERNAL_0': 'H3', 'CYANA': 'H3', 'CYANA2': 'H3', 'INTERNAL_1': 'H3', 'IUPAC': 'H3', 'AQUA': 'H3', 'BMRBd': None, 'XPLOR': 'H3', 'PDB': None}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> C4      
	#---------------------------------------------------------------
		topology   = [(0, 'N3'), (0, 'O4'), (0, 'C5')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'C4', 'INTERNAL_0': 'C4', 'CYANA': 'C4', 'CYANA2': 'C4', 'INTERNAL_1': 'C4', 'IUPAC': 'C4', 'AQUA': 'C4', 'BMRBd': None, 'XPLOR': 'C4', 'PDB': None}
		aliases    = []
		type       = 'C_ARO'
		spinType   = '13C'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> O4      
	#---------------------------------------------------------------
		topology   = [(0, 'C4')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'O4', 'INTERNAL_0': 'O4', 'CYANA': 'O4', 'CYANA2': 'O4', 'INTERNAL_1': 'O4', 'IUPAC': 'O4', 'AQUA': 'O4', 'BMRBd': None, 'XPLOR': 'O4', 'PDB': None}
		aliases    = []
		type       = 'O_BYL'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> C5      
	#---------------------------------------------------------------
		topology   = [(0, 'C4'), (0, 'C7'), (0, 'C6')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'C5', 'INTERNAL_0': 'C5', 'CYANA': 'C5', 'CYANA2': 'C5', 'INTERNAL_1': 'C5', 'IUPAC': 'C5', 'AQUA': 'C5', 'BMRBd': None, 'XPLOR': 'C5', 'PDB': None}
		aliases    = []
		type       = 'C_ARO'
		spinType   = '13C'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> C7      
	#---------------------------------------------------------------
		topology   = [(0, 'C5'), (0, 'H71'), (0, 'H72'), (0, 'H73')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'C7', 'INTERNAL_0': 'C7', 'CYANA': 'C7', 'CYANA2': 'C7', 'INTERNAL_1': 'C7', 'IUPAC': 'C7', 'AQUA': 'C7', 'BMRBd': None, 'XPLOR': 'C7', 'PDB': None}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H71     
	#---------------------------------------------------------------
		topology   = [(0, 'C7')]
		real       = []
		pseudo     = 'M7'
		nameDict   = {'CCPN': 'H71', 'INTERNAL_0': 'H71', 'CYANA': 'H71', 'CYANA2': 'H71', 'INTERNAL_1': 'H71', 'IUPAC': 'H71', 'AQUA': 'H71', 'BMRBd': None, 'XPLOR': 'H71', 'PDB': None}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isMethylProton', 'methylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H72     
	#---------------------------------------------------------------
		topology   = [(0, 'C7')]
		real       = []
		pseudo     = 'M7'
		nameDict   = {'CCPN': 'H72', 'INTERNAL_0': 'H72', 'CYANA': 'H72', 'CYANA2': 'H72', 'INTERNAL_1': 'H72', 'IUPAC': 'H72', 'AQUA': 'H72', 'BMRBd': None, 'XPLOR': 'H72', 'PDB': None}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isMethylProton', 'methylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H73     
	#---------------------------------------------------------------
		topology   = [(0, 'C7')]
		real       = []
		pseudo     = 'M7'
		nameDict   = {'CCPN': 'H73', 'INTERNAL_0': 'H73', 'CYANA': 'H73', 'CYANA2': 'H73', 'INTERNAL_1': 'H73', 'IUPAC': 'H73', 'AQUA': 'H73', 'BMRBd': None, 'XPLOR': 'H73', 'PDB': None}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isMethylProton', 'methylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> M7      
	#---------------------------------------------------------------
		topology   = []
		real       = ['H71', 'H72', 'H73']
		pseudo     = None
		nameDict   = {'CCPN': 'H7*', 'INTERNAL_0': 'Q7', 'CYANA': 'Q7', 'CYANA2': 'Q7', 'INTERNAL_1': 'M7', 'IUPAC': 'M7', 'AQUA': 'M7', 'BMRBd': None, 'XPLOR': 'Q7', 'PDB': None}
		aliases    = ['M7', 'Q7']
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> C6      
	#---------------------------------------------------------------
		topology   = [(0, 'N1'), (0, 'C5'), (0, 'H6')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'C6', 'INTERNAL_0': 'C6', 'CYANA': 'C6', 'CYANA2': 'C6', 'INTERNAL_1': 'C6', 'IUPAC': 'C6', 'AQUA': 'C6', 'BMRBd': None, 'XPLOR': 'C6', 'PDB': None}
		aliases    = []
		type       = 'C_ARO'
		spinType   = '13C'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H6      
	#---------------------------------------------------------------
		topology   = [(0, 'C6')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'H6', 'INTERNAL_0': 'H6', 'CYANA': 'H6', 'CYANA2': 'H6', 'INTERNAL_1': 'H6', 'IUPAC': 'H6', 'AQUA': 'H6', 'BMRBd': None, 'XPLOR': 'H6', 'PDB': None}
		aliases    = []
		type       = 'H_ARO'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> O3'     
	#---------------------------------------------------------------
		topology   = [(0, "C3'"), (1, 'P')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': "O3'", 'INTERNAL_0': "O3'", 'CYANA': "O3'", 'CYANA2': "O3'", 'INTERNAL_1': "O3'", 'IUPAC': "O3'", 'AQUA': "O3'", 'BMRBd': None, 'XPLOR': "O3'", 'PDB': None}
		aliases    = []
		type       = 'O_EST'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isBackbone', 'backbone', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	</NTlist>
</ResidueDef>
#=======================================================================
</SML>
