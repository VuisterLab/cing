<SML> 0.25

#=======================================================================
#             	name     convention
<ResidueDef>  	LYS      INTERNAL_1
#=======================================================================
	commonName = 'LYS'
	shortName  = 'K'
	comment    = 'Protonated (plus) Lys (common)'
	nameDict   = {'STAP': 'LYS', 'IUPAC': 'LYS', 'CYANA': 'LYS+', 'PDB': 'LYS', 'XPLOR': 'LYS', 'CCPN': 'protein Lys prot:HZ3', 'BMRBd': 'LYS', 'AQUA': 'LYS', 'INTERNAL_0': 'LYS', 'INTERNAL_1': 'LYS', 'CYANA2': 'LYS'}
	properties = ['protein', 'aliphatic', 'large', 'charged', 'isLysine']

	dihedrals  = <NTlist>
	#---------------------------------------------------------------
	<DihedralDef> PHI     
	#---------------------------------------------------------------
		atoms    = [(-1, 'C'), (0, 'N'), (0, 'CA'), (0, 'C')]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> PSI     
	#---------------------------------------------------------------
		atoms    = [(0, 'N'), (0, 'CA'), (0, 'C'), (1, 'N')]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> CHI1    
	#---------------------------------------------------------------
		atoms    = [(0, 'N'), (0, 'CA'), (0, 'CB'), (0, 'CG')]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> CHI2    
	#---------------------------------------------------------------
		atoms    = [(0, 'CA'), (0, 'CB'), (0, 'CG'), (0, 'CD')]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> CHI3    
	#---------------------------------------------------------------
		atoms    = [(0, 'CB'), (0, 'CG'), (0, 'CD'), (0, 'CE')]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> CHI4    
	#---------------------------------------------------------------
		atoms    = [(0, 'CG'), (0, 'CD'), (0, 'CE'), (0, 'NZ')]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> CHI5    
	#---------------------------------------------------------------
		atoms    = [(0, 'CD'), (0, 'CE'), (0, 'NZ'), (0, 'HZ1')]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> OMEGA   
	#---------------------------------------------------------------
		atoms    = [(-1, 'CA'), (-1, 'C'), (0, 'N'), (0, 'CA')]
		karplus  = None
	</DihedralDef>
	</NTlist>

	atoms      = <NTlist>
	#---------------------------------------------------------------
	<AtomDef> N       
	#---------------------------------------------------------------
		topology   = [(-1, 'C'), (0, 'H'), (0, 'CA')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'N', 'IUPAC': 'N', 'CYANA': 'N', 'PDB': 'N', 'XPLOR': 'N', 'CCPN': 'N', 'BMRBd': 'N', 'AQUA': 'N', 'INTERNAL_0': 'N', 'INTERNAL_1': 'N', 'CYANA2': 'N'}
		aliases    = []
		type       = 'N_AMI'
		spinType   = '15N'
		shift      = NTdict( average = 121.13, sd = 4.38 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H       
	#---------------------------------------------------------------
		topology   = [(0, 'N')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'HN', 'IUPAC': 'H', 'CYANA': 'HN', 'PDB': 'H', 'XPLOR': 'HN', 'CCPN': 'H', 'BMRBd': 'H', 'AQUA': 'H', 'INTERNAL_0': 'HN', 'INTERNAL_1': 'H', 'CYANA2': 'H'}
		aliases    = ['HN', 'H']
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 8.19, sd = 0.64 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CA      
	#---------------------------------------------------------------
		topology   = [(0, 'N'), (0, 'HA'), (0, 'CB'), (0, 'C')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'CA', 'IUPAC': 'CA', 'CYANA': 'CA', 'PDB': 'CA', 'XPLOR': 'CA', 'CCPN': 'CA', 'BMRBd': 'CA', 'AQUA': 'CA', 'INTERNAL_0': 'CA', 'INTERNAL_1': 'CA', 'CYANA2': 'CA'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 56.9, sd = 2.29 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HA      
	#---------------------------------------------------------------
		topology   = [(0, 'CA')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'HA', 'IUPAC': 'HA', 'CYANA': 'HA', 'PDB': 'HA', 'XPLOR': 'HA', 'CCPN': 'HA', 'BMRBd': 'HA', 'AQUA': 'HA', 'INTERNAL_0': 'HA', 'INTERNAL_1': 'HA', 'CYANA2': 'HA'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 4.27, sd = 0.47 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CB      
	#---------------------------------------------------------------
		topology   = [(0, 'CA'), (0, 'HB2'), (0, 'HB3'), (0, 'CG')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'CB', 'IUPAC': 'CB', 'CYANA': 'CB', 'PDB': 'CB', 'XPLOR': 'CB', 'CCPN': 'CB', 'BMRBd': 'CB', 'AQUA': 'CB', 'INTERNAL_0': 'CB', 'INTERNAL_1': 'CB', 'CYANA2': 'CB'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 32.82, sd = 2.49 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HB2     
	#---------------------------------------------------------------
		topology   = [(0, 'CB')]
		real       = []
		pseudo     = 'QB'
		nameDict   = {'STAP': 'HB2', 'IUPAC': 'HB2', 'CYANA': 'HB2', 'PDB': '1HB', 'XPLOR': 'HB2', 'CCPN': 'HB2', 'BMRBd': 'HB2', 'AQUA': 'HB2', 'INTERNAL_0': 'HB2', 'INTERNAL_1': 'HB2', 'CYANA2': 'HB2'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.79, sd = 0.29 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HB3     
	#---------------------------------------------------------------
		topology   = [(0, 'CB')]
		real       = []
		pseudo     = 'QB'
		nameDict   = {'STAP': 'HB1', 'IUPAC': 'HB3', 'CYANA': 'HB3', 'PDB': '2HB', 'XPLOR': 'HB1', 'CCPN': 'HB3', 'BMRBd': 'HB3', 'AQUA': 'HB3', 'INTERNAL_0': 'HB3', 'INTERNAL_1': 'HB3', 'CYANA2': 'HB3'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.76, sd = 0.3 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QB      
	#---------------------------------------------------------------
		topology   = [(0, 'CB')]
		real       = ['HB2', 'HB3']
		pseudo     = None
		nameDict   = {'STAP': None, 'IUPAC': 'QB', 'CYANA': 'QB', 'PDB': None, 'XPLOR': 'HB*,HB#,HB%,HB+', 'CCPN': 'HB*', 'BMRBd': None, 'AQUA': 'QB', 'INTERNAL_0': 'QB', 'INTERNAL_1': 'QB', 'CYANA2': 'QB'}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 1.775, sd = 0.295 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CG      
	#---------------------------------------------------------------
		topology   = [(0, 'CB'), (0, 'HG2'), (0, 'HG3'), (0, 'CD')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'CG', 'IUPAC': 'CG', 'CYANA': 'CG', 'PDB': 'CG', 'XPLOR': 'CG', 'CCPN': 'CG', 'BMRBd': 'CG', 'AQUA': 'CG', 'INTERNAL_0': 'CG', 'INTERNAL_1': 'CG', 'CYANA2': 'CG'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 24.99, sd = 2.52 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HG2     
	#---------------------------------------------------------------
		topology   = [(0, 'CG')]
		real       = []
		pseudo     = 'QG'
		nameDict   = {'STAP': 'HG2', 'IUPAC': 'HG2', 'CYANA': 'HG2', 'PDB': '1HG', 'XPLOR': 'HG2', 'CCPN': 'HG2', 'BMRBd': 'HG2', 'AQUA': 'HG2', 'INTERNAL_0': 'HG2', 'INTERNAL_1': 'HG2', 'CYANA2': 'HG2'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.38, sd = 0.29 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HG3     
	#---------------------------------------------------------------
		topology   = [(0, 'CG')]
		real       = []
		pseudo     = 'QG'
		nameDict   = {'STAP': 'HG1', 'IUPAC': 'HG3', 'CYANA': 'HG3', 'PDB': '2HG', 'XPLOR': 'HG1', 'CCPN': 'HG3', 'BMRBd': 'HG3', 'AQUA': 'HG3', 'INTERNAL_0': 'HG3', 'INTERNAL_1': 'HG3', 'CYANA2': 'HG3'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.36, sd = 0.31 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QG      
	#---------------------------------------------------------------
		topology   = [(0, 'CG')]
		real       = ['HG2', 'HG3']
		pseudo     = None
		nameDict   = {'STAP': None, 'IUPAC': 'QG', 'CYANA': 'QG', 'PDB': None, 'XPLOR': 'HG*,HG#,HG%,HG+', 'CCPN': 'HG*', 'BMRBd': None, 'AQUA': 'QG', 'INTERNAL_0': 'QG', 'INTERNAL_1': 'QG', 'CYANA2': 'QG'}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 1.37, sd = 0.3 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CD      
	#---------------------------------------------------------------
		topology   = [(0, 'CG'), (0, 'HD2'), (0, 'HD3'), (0, 'CE')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'CD', 'IUPAC': 'CD', 'CYANA': 'CD', 'PDB': 'CD', 'XPLOR': 'CD', 'CCPN': 'CD', 'BMRBd': 'CD', 'AQUA': 'CD', 'INTERNAL_0': 'CD', 'INTERNAL_1': 'CD', 'CYANA2': 'CD'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 28.97, sd = 2.41 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HD2     
	#---------------------------------------------------------------
		topology   = [(0, 'CD')]
		real       = []
		pseudo     = 'QD'
		nameDict   = {'STAP': 'HD2', 'IUPAC': 'HD2', 'CYANA': 'HD2', 'PDB': '1HD', 'XPLOR': 'HD2', 'CCPN': 'HD2', 'BMRBd': 'HD2', 'AQUA': 'HD2', 'INTERNAL_0': 'HD2', 'INTERNAL_1': 'HD2', 'CYANA2': 'HD2'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.63, sd = 1.43 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HD3     
	#---------------------------------------------------------------
		topology   = [(0, 'CD')]
		real       = []
		pseudo     = 'QD'
		nameDict   = {'STAP': 'HD1', 'IUPAC': 'HD3', 'CYANA': 'HD3', 'PDB': '2HD', 'XPLOR': 'HD1', 'CCPN': 'HD3', 'BMRBd': 'HD3', 'AQUA': 'HD3', 'INTERNAL_0': 'HD3', 'INTERNAL_1': 'HD3', 'CYANA2': 'HD3'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.6, sd = 0.27 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QD      
	#---------------------------------------------------------------
		topology   = [(0, 'CD')]
		real       = ['HD2', 'HD3']
		pseudo     = None
		nameDict   = {'STAP': None, 'IUPAC': 'QD', 'CYANA': 'QD', 'PDB': None, 'XPLOR': 'HD*,HD#,HD%,HD+', 'CCPN': 'HD*', 'BMRBd': None, 'AQUA': 'QD', 'INTERNAL_0': 'QD', 'INTERNAL_1': 'QD', 'CYANA2': 'QD'}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 1.615, sd = 0.85 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CE      
	#---------------------------------------------------------------
		topology   = [(0, 'CD'), (0, 'HE2'), (0, 'HE3'), (0, 'NZ')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'CE', 'IUPAC': 'CE', 'CYANA': 'CE', 'PDB': 'CE', 'XPLOR': 'CE', 'CCPN': 'CE', 'BMRBd': 'CE', 'AQUA': 'CE', 'INTERNAL_0': 'CE', 'INTERNAL_1': 'CE', 'CYANA2': 'CE'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 41.92, sd = 2.26 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HE2     
	#---------------------------------------------------------------
		topology   = [(0, 'CE')]
		real       = []
		pseudo     = 'QE'
		nameDict   = {'STAP': 'HE2', 'IUPAC': 'HE2', 'CYANA': 'HE2', 'PDB': '1HE', 'XPLOR': 'HE2', 'CCPN': 'HE2', 'BMRBd': 'HE2', 'AQUA': 'HE2', 'INTERNAL_0': 'HE2', 'INTERNAL_1': 'HE2', 'CYANA2': 'HE2'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 2.93, sd = 0.24 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HE3     
	#---------------------------------------------------------------
		topology   = [(0, 'CE')]
		real       = []
		pseudo     = 'QE'
		nameDict   = {'STAP': 'HE1', 'IUPAC': 'HE3', 'CYANA': 'HE3', 'PDB': '2HE', 'XPLOR': 'HE1', 'CCPN': 'HE3', 'BMRBd': 'HE3', 'AQUA': 'HE3', 'INTERNAL_0': 'HE3', 'INTERNAL_1': 'HE3', 'CYANA2': 'HE3'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 2.92, sd = 0.25 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QE      
	#---------------------------------------------------------------
		topology   = [(0, 'CE')]
		real       = ['HE2', 'HE3']
		pseudo     = None
		nameDict   = {'STAP': None, 'IUPAC': 'QE', 'CYANA': 'QE', 'PDB': None, 'XPLOR': 'HE*,HE#,HE%,HE+', 'CCPN': 'HE*', 'BMRBd': None, 'AQUA': 'QE', 'INTERNAL_0': 'QE', 'INTERNAL_1': 'QE', 'CYANA2': 'QE'}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 2.925, sd = 0.245 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> NZ      
	#---------------------------------------------------------------
		topology   = [(0, 'CE'), (0, 'HZ1'), (0, 'HZ2'), (0, 'HZ3')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'NZ', 'IUPAC': 'NZ', 'CYANA': 'NZ', 'PDB': 'NZ', 'XPLOR': 'NZ', 'CCPN': 'NZ', 'BMRBd': 'NZ', 'AQUA': 'NZ', 'INTERNAL_0': 'NZ', 'INTERNAL_1': 'NZ', 'CYANA2': 'NZ'}
		aliases    = []
		type       = 'N_AMO'
		spinType   = '15N'
		shift      = NTdict( average = 48.17, sd = 36.38 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HZ1     
	#---------------------------------------------------------------
		topology   = [(0, 'NZ')]
		real       = []
		pseudo     = 'QZ'
		nameDict   = {'STAP': 'HZ1', 'IUPAC': 'HZ1', 'CYANA': 'HZ1', 'PDB': '1HZ', 'XPLOR': 'HZ1', 'CCPN': 'HZ1', 'BMRBd': 'HZ1', 'AQUA': 'HZ1', 'INTERNAL_0': 'HZ1', 'INTERNAL_1': 'HZ1', 'CYANA2': 'HZ1'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 7.43, sd = 1.14 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HZ2     
	#---------------------------------------------------------------
		topology   = [(0, 'NZ')]
		real       = []
		pseudo     = 'QZ'
		nameDict   = {'STAP': 'HZ2', 'IUPAC': 'HZ2', 'CYANA': 'HZ2', 'PDB': '2HZ', 'XPLOR': 'HZ2', 'CCPN': 'HZ2', 'BMRBd': 'HZ2', 'AQUA': 'HZ2', 'INTERNAL_0': 'HZ2', 'INTERNAL_1': 'HZ2', 'CYANA2': 'HZ2'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HZ3     
	#---------------------------------------------------------------
		topology   = [(0, 'NZ')]
		real       = []
		pseudo     = 'QZ'
		nameDict   = {'STAP': 'HZ3', 'IUPAC': 'HZ3', 'CYANA': 'HZ3', 'PDB': '3HZ', 'XPLOR': 'HZ3', 'CCPN': 'HZ3', 'BMRBd': 'HZ3', 'AQUA': 'HZ3', 'INTERNAL_0': 'HZ3', 'INTERNAL_1': 'HZ3', 'CYANA2': 'HZ3'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QZ      
	#---------------------------------------------------------------
		topology   = [(0, 'NZ')]
		real       = ['HZ1', 'HZ2', 'HZ3']
		pseudo     = None
		nameDict   = {'STAP': None, 'IUPAC': 'QZ', 'CYANA': 'QZ', 'PDB': None, 'XPLOR': 'HZ*,HZ#,HZ%,HZ+', 'CCPN': 'HZ*', 'BMRBd': None, 'AQUA': 'QZ', 'INTERNAL_0': 'QZ', 'INTERNAL_1': 'QZ', 'CYANA2': 'QZ'}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 7.43, sd = 1.14 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> C       
	#---------------------------------------------------------------
		topology   = [(0, 'CA'), (0, 'O'), (1, 'N')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'C', 'IUPAC': 'C', 'CYANA': 'C', 'PDB': 'C', 'XPLOR': 'C', 'CCPN': 'C', 'BMRBd': 'C', 'AQUA': 'C', 'INTERNAL_0': 'C', 'INTERNAL_1': 'C', 'CYANA2': 'C'}
		aliases    = ['C', 'CO']
		type       = 'C_BYL'
		spinType   = '13C'
		shift      = NTdict( average = 176.81, sd = 10.32 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> O       
	#---------------------------------------------------------------
		topology   = [(0, 'C')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'O,OT1', 'IUPAC': 'O', 'CYANA': 'O', 'PDB': 'O', 'XPLOR': 'O,OT1', 'CCPN': 'O', 'BMRBd': 'O', 'AQUA': 'O', 'INTERNAL_0': 'O', 'INTERNAL_1': 'O', 'CYANA2': 'O'}
		aliases    = ['O', "O'"]
		type       = 'O_BYL'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isSidechain', 'sidechain', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H1      
	#---------------------------------------------------------------
		topology   = [(0, 'N')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'H1', 'STAP': 'H1,HT1', 'IUPAC': 'H1', 'INTERNAL_0': 'H1', 'INTERNAL_1': 'H1', 'XPLOR': 'HT1'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 8.19, sd = 0.64 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H2      
	#---------------------------------------------------------------
		topology   = [(0, 'N')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'H2', 'STAP': 'H2,HT2', 'IUPAC': 'H2', 'INTERNAL_0': 'H2', 'INTERNAL_1': 'H2', 'XPLOR': 'HT2'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 8.19, sd = 0.64 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H3      
	#---------------------------------------------------------------
		topology   = [(0, 'N')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'H3', 'STAP': 'H3,HT3', 'IUPAC': 'H3', 'INTERNAL_0': 'H3', 'INTERNAL_1': 'H3', 'XPLOR': 'HT3'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 8.19, sd = 0.64 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> OXT     
	#---------------------------------------------------------------
		topology   = [(0, 'C')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': "O''", 'STAP': 'OXT,OT2', 'IUPAC': "OXT,O''", 'INTERNAL_0': 'OXT', 'INTERNAL_1': 'OXT', 'XPLOR': 'OT2'}
		aliases    = ['OXT', "O''"]
		type       = 'O_BYL'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isSidechain', 'sidechain', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	</NTlist>
</ResidueDef>
#=======================================================================
</SML>
