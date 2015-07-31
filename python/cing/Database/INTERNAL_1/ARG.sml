<SML> 0.25

#=======================================================================
#             	name     convention
<ResidueDef>  	ARG      INTERNAL_1
#=======================================================================
	commonName = 'ARG'
	shortName  = 'R'
	comment    = 'Protonated (plus) ARG (common)'
	nameDict   = {'STAP': 'ARG', 'IUPAC': 'ARG', 'CYANA': 'ARG+', 'PDB': 'ARG', 'XPLOR': 'ARG', 'CCPN': 'protein Arg prot:HH12', 'BMRBd': 'ARG', 'AQUA': 'ARG', 'INTERNAL_0': 'ARG', 'INTERNAL_1': 'ARG', 'CYANA2': 'ARG'}
	properties = ['protein', 'aliphatic', 'large', 'charged', 'isArginine']

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
		atoms    = [(0, 'CB'), (0, 'CG'), (0, 'CD'), (0, 'NE')]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> CHI4    
	#---------------------------------------------------------------
		atoms    = [(0, 'CG'), (0, 'CD'), (0, 'NE'), (0, 'CZ')]
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
		shift      = NTdict( average = 120.72, sd = 4.01 )
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
		shift      = NTdict( average = 8.24, sd = 0.61 )
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
		shift      = NTdict( average = 56.84, sd = 2.52 )
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
		shift      = NTdict( average = 4.29, sd = 0.48 )
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
		shift      = NTdict( average = 30.71, sd = 2.6 )
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
		shift      = NTdict( average = 1.8, sd = 0.3 )
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
		shift      = NTdict( average = 1.78, sd = 0.29 )
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
		shift      = NTdict( average = 1.79, sd = 0.295 )
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
		shift      = NTdict( average = 27.38, sd = 2.59 )
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
		shift      = NTdict( average = 1.58, sd = 0.28 )
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
		shift      = NTdict( average = 1.56, sd = 0.3 )
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
		shift      = NTdict( average = 1.57, sd = 0.29000000000000004 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CD      
	#---------------------------------------------------------------
		topology   = [(0, 'CG'), (0, 'HD2'), (0, 'HD3'), (0, 'NE')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'CD', 'IUPAC': 'CD', 'CYANA': 'CD', 'PDB': 'CD', 'XPLOR': 'CD', 'CCPN': 'CD', 'BMRBd': 'CD', 'AQUA': 'CD', 'INTERNAL_0': 'CD', 'INTERNAL_1': 'CD', 'CYANA2': 'CD'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 43.21, sd = 2.27 )
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
		shift      = NTdict( average = 3.12, sd = 0.3 )
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
		shift      = NTdict( average = 3.11, sd = 0.28 )
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
		shift      = NTdict( average = 3.115, sd = 0.29000000000000004 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> NE      
	#---------------------------------------------------------------
		topology   = [(0, 'CD'), (0, 'HE'), (0, 'CZ')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'NE', 'IUPAC': 'NE', 'CYANA': 'NE', 'PDB': 'NE', 'XPLOR': 'NE', 'CCPN': 'NE', 'BMRBd': 'NE', 'AQUA': 'NE', 'INTERNAL_0': 'NE', 'INTERNAL_1': 'NE', 'CYANA2': 'NE'}
		aliases    = []
		type       = 'N_AMI'
		spinType   = '15N'
		shift      = NTdict( average = 93.79, sd = 15.46 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HE      
	#---------------------------------------------------------------
		topology   = [(0, 'NE')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'HE', 'IUPAC': 'HE', 'CYANA': 'HE', 'PDB': 'HE', 'XPLOR': 'HE', 'CCPN': 'HE', 'BMRBd': 'HE', 'AQUA': 'HE', 'INTERNAL_0': 'HE', 'INTERNAL_1': 'HE', 'CYANA2': 'HE'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 7.33, sd = 0.64 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CZ      
	#---------------------------------------------------------------
		topology   = [(0, 'NE'), (0, 'NH1'), (0, 'NH2')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'CZ', 'IUPAC': 'CZ', 'CYANA': 'CZ', 'PDB': 'CZ', 'XPLOR': 'CZ', 'CCPN': 'CZ', 'BMRBd': 'CZ', 'AQUA': 'CZ', 'INTERNAL_0': 'CZ', 'INTERNAL_1': 'CZ', 'CYANA2': 'CZ'}
		aliases    = []
		type       = 'C_VIN'
		spinType   = '13C'
		shift      = NTdict( average = 159.16, sd = 1.0 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> NH1     
	#---------------------------------------------------------------
		topology   = [(0, 'CZ'), (0, 'HH11'), (0, 'HH12')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'NH1', 'IUPAC': 'NH1', 'CYANA': 'NH1', 'PDB': 'NH1', 'XPLOR': 'NH1', 'CCPN': 'NH1', 'BMRBd': 'NH1', 'AQUA': 'NH1', 'INTERNAL_0': 'NH1', 'INTERNAL_1': 'NH1', 'CYANA2': 'NH1'}
		aliases    = []
		type       = 'N_AMO'
		spinType   = '15N'
		shift      = NTdict( average = 74.22, sd = 7.7 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HH11    
	#---------------------------------------------------------------
		topology   = [(0, 'NH1')]
		real       = []
		pseudo     = 'QH1'
		nameDict   = {'STAP': 'HH11', 'IUPAC': 'HH11', 'CYANA': 'HH11', 'PDB': '1HH1', 'XPLOR': 'HH11', 'CCPN': 'HH11', 'BMRBd': 'HH11', 'AQUA': 'HH11', 'INTERNAL_0': 'HH11', 'INTERNAL_1': 'HH11', 'CYANA2': 'HH11'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 6.85, sd = 0.51 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HH12    
	#---------------------------------------------------------------
		topology   = [(0, 'NH1')]
		real       = []
		pseudo     = 'QH1'
		nameDict   = {'STAP': 'HH12', 'IUPAC': 'HH12', 'CYANA': 'HH12', 'PDB': '2HH1', 'XPLOR': 'HH12', 'CCPN': 'HH12', 'BMRBd': 'HH12', 'AQUA': 'HH12', 'INTERNAL_0': 'HH12', 'INTERNAL_1': 'HH12', 'CYANA2': 'HH12'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 6.79, sd = 0.48 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QH1     
	#---------------------------------------------------------------
		topology   = [(0, 'NH1')]
		real       = ['HH11', 'HH12']
		pseudo     = None
		nameDict   = {'STAP': None, 'IUPAC': 'QH1', 'CYANA': 'QH1', 'PDB': None, 'XPLOR': 'HH1*,HH1#,HH1%,HH1+', 'CCPN': 'HH1*', 'BMRBd': None, 'AQUA': 'QH1', 'INTERNAL_0': 'QH1', 'INTERNAL_1': 'QH1', 'CYANA2': 'QH1'}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 6.82, sd = 0.495 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> NH2     
	#---------------------------------------------------------------
		topology   = [(0, 'CZ'), (0, 'HH21'), (0, 'HH22')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'NH2', 'IUPAC': 'NH2', 'CYANA': 'NH2', 'PDB': 'NH2', 'XPLOR': 'NH2', 'CCPN': 'NH2', 'BMRBd': 'NH2', 'AQUA': 'NH2', 'INTERNAL_0': 'NH2', 'INTERNAL_1': 'NH2', 'CYANA2': 'NH2'}
		aliases    = []
		type       = 'N_AMO'
		spinType   = '15N'
		shift      = NTdict( average = 75.18, sd = 10.68 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HH21    
	#---------------------------------------------------------------
		topology   = [(0, 'NH2')]
		real       = []
		pseudo     = 'QH2'
		nameDict   = {'STAP': 'HH21', 'IUPAC': 'HH21', 'CYANA': 'HH21', 'PDB': '1HH2', 'XPLOR': 'HH21', 'CCPN': 'HH21', 'BMRBd': 'HH21', 'AQUA': 'HH21', 'INTERNAL_0': 'HH21', 'INTERNAL_1': 'HH21', 'CYANA2': 'HH21'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 6.79, sd = 0.47 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HH22    
	#---------------------------------------------------------------
		topology   = [(0, 'NH2')]
		real       = []
		pseudo     = 'QH2'
		nameDict   = {'STAP': 'HH22', 'IUPAC': 'HH22', 'CYANA': 'HH22', 'PDB': '2HH2', 'XPLOR': 'HH22', 'CCPN': 'HH22', 'BMRBd': 'HH22', 'AQUA': 'HH22', 'INTERNAL_0': 'HH22', 'INTERNAL_1': 'HH22', 'CYANA2': 'HH22'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 6.77, sd = 0.5 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QH2     
	#---------------------------------------------------------------
		topology   = [(0, 'NH2')]
		real       = ['HH21', 'HH22']
		pseudo     = None
		nameDict   = {'STAP': None, 'IUPAC': 'QH2', 'CYANA': 'QH2', 'PDB': None, 'XPLOR': 'HH2*,HH2#,HH2%,HH2+', 'CCPN': 'HH2*', 'BMRBd': None, 'AQUA': 'QH2', 'INTERNAL_0': 'QH2', 'INTERNAL_1': 'QH2', 'CYANA2': 'QH2'}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 6.779999999999999, sd = 0.485 )
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
		shift      = NTdict( average = 176.43, sd = 4.3 )
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
		shift      = NTdict( average = 8.24, sd = 0.61 )
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
		shift      = NTdict( average = 8.24, sd = 0.61 )
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
		shift      = NTdict( average = 8.24, sd = 0.61 )
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
