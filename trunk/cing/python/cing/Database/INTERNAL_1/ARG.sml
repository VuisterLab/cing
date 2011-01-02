<SML> 0.24

#=======================================================================
#             	name     convention
<ResidueDef>  	ARG      INTERNAL_1
#=======================================================================
	commonName = 'ARG'
	shortName  = 'R'
	comment    = 'Protonated (plus) ARG (common)'
	nameDict   = {'CCPN': 'protein Arg prot:HH12', 'INTERNAL_0': 'ARG', 'CYANA': 'ARG+', 'CYANA2': 'ARG', 'INTERNAL_1': 'ARG', 'IUPAC': 'ARG', 'AQUA': 'ARG', 'BMRBd': 'ARG', 'XPLOR': 'ARG', 'PDB': 'ARG'}
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
		nameDict   = {'CCPN': 'N', 'INTERNAL_0': 'N', 'CYANA': 'N', 'CYANA2': 'N', 'INTERNAL_1': 'N', 'IUPAC': 'N', 'AQUA': 'N', 'BMRBd': 'N', 'XPLOR': 'N', 'PDB': 'N'}
		aliases    = []
		type       = 'N_AMI'
		spinType   = '15N'
		shift      = NTdict( average = 120.72, sd = 4.0099999999999998 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H       
	#---------------------------------------------------------------
		topology   = [(0, 'N')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'H', 'INTERNAL_0': 'HN', 'CYANA': 'HN', 'CYANA2': 'H', 'INTERNAL_1': 'H', 'IUPAC': 'H', 'AQUA': 'H', 'BMRBd': 'H', 'XPLOR': 'HN', 'PDB': 'H'}
		aliases    = ['HN', 'H']
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 8.2400000000000002, sd = 0.60999999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CA      
	#---------------------------------------------------------------
		topology   = [(0, 'N'), (0, 'HA'), (0, 'CB'), (0, 'C')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'CA', 'INTERNAL_0': 'CA', 'CYANA': 'CA', 'CYANA2': 'CA', 'INTERNAL_1': 'CA', 'IUPAC': 'CA', 'AQUA': 'CA', 'BMRBd': 'CA', 'XPLOR': 'CA', 'PDB': 'CA'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 56.840000000000003, sd = 2.52 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HA      
	#---------------------------------------------------------------
		topology   = [(0, 'CA')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'HA', 'INTERNAL_0': 'HA', 'CYANA': 'HA', 'CYANA2': 'HA', 'INTERNAL_1': 'HA', 'IUPAC': 'HA', 'AQUA': 'HA', 'BMRBd': 'HA', 'XPLOR': 'HA', 'PDB': 'HA'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 4.29, sd = 0.47999999999999998 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CB      
	#---------------------------------------------------------------
		topology   = [(0, 'CA'), (0, 'HB2'), (0, 'HB3'), (0, 'CG')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'CB', 'INTERNAL_0': 'CB', 'CYANA': 'CB', 'CYANA2': 'CB', 'INTERNAL_1': 'CB', 'IUPAC': 'CB', 'AQUA': 'CB', 'BMRBd': 'CB', 'XPLOR': 'CB', 'PDB': 'CB'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 30.710000000000001, sd = 2.6000000000000001 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HB2     
	#---------------------------------------------------------------
		topology   = [(0, 'CB')]
		real       = []
		pseudo     = 'QB'
		nameDict   = {'CCPN': 'HB2', 'INTERNAL_0': 'HB2', 'CYANA': 'HB2', 'CYANA2': 'HB2', 'INTERNAL_1': 'HB2', 'IUPAC': 'HB2', 'AQUA': 'HB2', 'BMRBd': 'HB2', 'XPLOR': 'HB2', 'PDB': '1HB'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.8, sd = 0.29999999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HB3     
	#---------------------------------------------------------------
		topology   = [(0, 'CB')]
		real       = []
		pseudo     = 'QB'
		nameDict   = {'CCPN': 'HB3', 'INTERNAL_0': 'HB3', 'CYANA': 'HB3', 'CYANA2': 'HB3', 'INTERNAL_1': 'HB3', 'IUPAC': 'HB3', 'AQUA': 'HB3', 'BMRBd': 'HB3', 'XPLOR': 'HB1', 'PDB': '2HB'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.78, sd = 0.28999999999999998 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QB      
	#---------------------------------------------------------------
		topology   = [(0, 'CB')]
		real       = ['HB2', 'HB3']
		pseudo     = None
		nameDict   = {'CCPN': 'HB*', 'INTERNAL_0': 'QB', 'CYANA': 'QB', 'CYANA2': 'QB', 'INTERNAL_1': 'QB', 'IUPAC': 'QB', 'AQUA': 'QB', 'BMRBd': None, 'XPLOR': 'HB*,HB#,HB%,HB+', 'PDB': None}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 1.79, sd = 0.29499999999999998 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CG      
	#---------------------------------------------------------------
		topology   = [(0, 'CB'), (0, 'HG2'), (0, 'HG3'), (0, 'CD')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'CG', 'INTERNAL_0': 'CG', 'CYANA': 'CG', 'CYANA2': 'CG', 'INTERNAL_1': 'CG', 'IUPAC': 'CG', 'AQUA': 'CG', 'BMRBd': 'CG', 'XPLOR': 'CG', 'PDB': 'CG'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 27.379999999999999, sd = 2.5899999999999999 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HG2     
	#---------------------------------------------------------------
		topology   = [(0, 'CG')]
		real       = []
		pseudo     = 'QG'
		nameDict   = {'CCPN': 'HG2', 'INTERNAL_0': 'HG2', 'CYANA': 'HG2', 'CYANA2': 'HG2', 'INTERNAL_1': 'HG2', 'IUPAC': 'HG2', 'AQUA': 'HG2', 'BMRBd': 'HG2', 'XPLOR': 'HG2', 'PDB': '1HG'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.5800000000000001, sd = 0.28000000000000003 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HG3     
	#---------------------------------------------------------------
		topology   = [(0, 'CG')]
		real       = []
		pseudo     = 'QG'
		nameDict   = {'CCPN': 'HG3', 'INTERNAL_0': 'HG3', 'CYANA': 'HG3', 'CYANA2': 'HG3', 'INTERNAL_1': 'HG3', 'IUPAC': 'HG3', 'AQUA': 'HG3', 'BMRBd': 'HG3', 'XPLOR': 'HG1', 'PDB': '2HG'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.5600000000000001, sd = 0.29999999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QG      
	#---------------------------------------------------------------
		topology   = [(0, 'CG')]
		real       = ['HG2', 'HG3']
		pseudo     = None
		nameDict   = {'CCPN': 'HG*', 'INTERNAL_0': 'QG', 'CYANA': 'QG', 'CYANA2': 'QG', 'INTERNAL_1': 'QG', 'IUPAC': 'QG', 'AQUA': 'QG', 'BMRBd': None, 'XPLOR': 'HG*,HG#,HG%,HG+', 'PDB': None}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 1.5700000000000001, sd = 0.29000000000000004 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CD      
	#---------------------------------------------------------------
		topology   = [(0, 'CG'), (0, 'HD2'), (0, 'HD3'), (0, 'NE')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'CD', 'INTERNAL_0': 'CD', 'CYANA': 'CD', 'CYANA2': 'CD', 'INTERNAL_1': 'CD', 'IUPAC': 'CD', 'AQUA': 'CD', 'BMRBd': 'CD', 'XPLOR': 'CD', 'PDB': 'CD'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 43.210000000000001, sd = 2.27 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HD2     
	#---------------------------------------------------------------
		topology   = [(0, 'CD')]
		real       = []
		pseudo     = 'QD'
		nameDict   = {'CCPN': 'HD2', 'INTERNAL_0': 'HD2', 'CYANA': 'HD2', 'CYANA2': 'HD2', 'INTERNAL_1': 'HD2', 'IUPAC': 'HD2', 'AQUA': 'HD2', 'BMRBd': 'HD2', 'XPLOR': 'HD2', 'PDB': '1HD'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 3.1200000000000001, sd = 0.29999999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HD3     
	#---------------------------------------------------------------
		topology   = [(0, 'CD')]
		real       = []
		pseudo     = 'QD'
		nameDict   = {'CCPN': 'HD3', 'INTERNAL_0': 'HD3', 'CYANA': 'HD3', 'CYANA2': 'HD3', 'INTERNAL_1': 'HD3', 'IUPAC': 'HD3', 'AQUA': 'HD3', 'BMRBd': 'HD3', 'XPLOR': 'HD1', 'PDB': '2HD'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 3.1099999999999999, sd = 0.28000000000000003 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QD      
	#---------------------------------------------------------------
		topology   = [(0, 'CD')]
		real       = ['HD2', 'HD3']
		pseudo     = None
		nameDict   = {'CCPN': 'HD*', 'INTERNAL_0': 'QD', 'CYANA': 'QD', 'CYANA2': 'QD', 'INTERNAL_1': 'QD', 'IUPAC': 'QD', 'AQUA': 'QD', 'BMRBd': None, 'XPLOR': 'HD*,HD#,HD%,HD+', 'PDB': None}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 3.1150000000000002, sd = 0.29000000000000004 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> NE      
	#---------------------------------------------------------------
		topology   = [(0, 'CD'), (0, 'HE'), (0, 'CZ')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'NE', 'INTERNAL_0': 'NE', 'CYANA': 'NE', 'CYANA2': 'NE', 'INTERNAL_1': 'NE', 'IUPAC': 'NE', 'AQUA': 'NE', 'BMRBd': 'NE', 'XPLOR': 'NE', 'PDB': 'NE'}
		aliases    = []
		type       = 'N_AMI'
		spinType   = '15N'
		shift      = NTdict( average = 93.790000000000006, sd = 15.460000000000001 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HE      
	#---------------------------------------------------------------
		topology   = [(0, 'NE')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'HE', 'INTERNAL_0': 'HE', 'CYANA': 'HE', 'CYANA2': 'HE', 'INTERNAL_1': 'HE', 'IUPAC': 'HE', 'AQUA': 'HE', 'BMRBd': 'HE', 'XPLOR': 'HE', 'PDB': 'HE'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 7.3300000000000001, sd = 0.64000000000000001 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CZ      
	#---------------------------------------------------------------
		topology   = [(0, 'NE'), (0, 'NH1'), (0, 'NH2')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'CZ', 'INTERNAL_0': 'CZ', 'CYANA': 'CZ', 'CYANA2': 'CZ', 'INTERNAL_1': 'CZ', 'IUPAC': 'CZ', 'AQUA': 'CZ', 'BMRBd': 'CZ', 'XPLOR': 'CZ', 'PDB': 'CZ'}
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
		nameDict   = {'CCPN': 'NH1', 'INTERNAL_0': 'NH1', 'CYANA': 'NH1', 'CYANA2': 'NH1', 'INTERNAL_1': 'NH1', 'IUPAC': 'NH1', 'AQUA': 'NH1', 'BMRBd': 'NH1', 'XPLOR': 'NH1', 'PDB': 'NH1'}
		aliases    = []
		type       = 'N_AMO'
		spinType   = '15N'
		shift      = NTdict( average = 74.219999999999999, sd = 7.7000000000000002 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HH11    
	#---------------------------------------------------------------
		topology   = [(0, 'NH1')]
		real       = []
		pseudo     = 'QH1'
		nameDict   = {'CCPN': 'HH11', 'INTERNAL_0': 'HH11', 'CYANA': 'HH11', 'CYANA2': 'HH11', 'INTERNAL_1': 'HH11', 'IUPAC': 'HH11', 'AQUA': 'HH11', 'BMRBd': 'HH11', 'XPLOR': 'HH11', 'PDB': '1HH1'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 6.8499999999999996, sd = 0.51000000000000001 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HH12    
	#---------------------------------------------------------------
		topology   = [(0, 'NH1')]
		real       = []
		pseudo     = 'QH1'
		nameDict   = {'CCPN': 'HH12', 'INTERNAL_0': 'HH12', 'CYANA': 'HH12', 'CYANA2': 'HH12', 'INTERNAL_1': 'HH12', 'IUPAC': 'HH12', 'AQUA': 'HH12', 'BMRBd': 'HH12', 'XPLOR': 'HH12', 'PDB': '2HH1'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 6.79, sd = 0.47999999999999998 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QH1     
	#---------------------------------------------------------------
		topology   = [(0, 'NH1')]
		real       = ['HH11', 'HH12']
		pseudo     = None
		nameDict   = {'CCPN': 'HH1*', 'INTERNAL_0': 'QH1', 'CYANA': 'QH1', 'CYANA2': 'QH1', 'INTERNAL_1': 'QH1', 'IUPAC': 'QH1', 'AQUA': 'QH1', 'BMRBd': None, 'XPLOR': 'HH1*,HH1#,HH1%,HH1+', 'PDB': None}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 6.8200000000000003, sd = 0.495 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> NH2     
	#---------------------------------------------------------------
		topology   = [(0, 'CZ'), (0, 'HH21'), (0, 'HH22')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'NH2', 'INTERNAL_0': 'NH2', 'CYANA': 'NH2', 'CYANA2': 'NH2', 'INTERNAL_1': 'NH2', 'IUPAC': 'NH2', 'AQUA': 'NH2', 'BMRBd': 'NH2', 'XPLOR': 'NH2', 'PDB': 'NH2'}
		aliases    = []
		type       = 'N_AMO'
		spinType   = '15N'
		shift      = NTdict( average = 75.180000000000007, sd = 10.68 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HH21    
	#---------------------------------------------------------------
		topology   = [(0, 'NH2')]
		real       = []
		pseudo     = 'QH2'
		nameDict   = {'CCPN': 'HH21', 'INTERNAL_0': 'HH21', 'CYANA': 'HH21', 'CYANA2': 'HH21', 'INTERNAL_1': 'HH21', 'IUPAC': 'HH21', 'AQUA': 'HH21', 'BMRBd': 'HH21', 'XPLOR': 'HH21', 'PDB': '1HH2'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 6.79, sd = 0.46999999999999997 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HH22    
	#---------------------------------------------------------------
		topology   = [(0, 'NH2')]
		real       = []
		pseudo     = 'QH2'
		nameDict   = {'CCPN': 'HH22', 'INTERNAL_0': 'HH22', 'CYANA': 'HH22', 'CYANA2': 'HH22', 'INTERNAL_1': 'HH22', 'IUPAC': 'HH22', 'AQUA': 'HH22', 'BMRBd': 'HH22', 'XPLOR': 'HH22', 'PDB': '2HH2'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 6.7699999999999996, sd = 0.5 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QH2     
	#---------------------------------------------------------------
		topology   = [(0, 'NH2')]
		real       = ['HH21', 'HH22']
		pseudo     = None
		nameDict   = {'CCPN': 'HH2*', 'INTERNAL_0': 'QH2', 'CYANA': 'QH2', 'CYANA2': 'QH2', 'INTERNAL_1': 'QH2', 'IUPAC': 'QH2', 'AQUA': 'QH2', 'BMRBd': None, 'XPLOR': 'HH2*,HH2#,HH2%,HH2+', 'PDB': None}
		aliases    = []
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 6.7799999999999994, sd = 0.48499999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> C       
	#---------------------------------------------------------------
		topology   = [(0, 'CA'), (0, 'O'), (1, 'N')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'C', 'INTERNAL_0': 'C', 'CYANA': 'C', 'CYANA2': 'C', 'INTERNAL_1': 'C', 'IUPAC': 'C', 'AQUA': 'C', 'BMRBd': 'C', 'XPLOR': 'C', 'PDB': 'C'}
		aliases    = ['C', 'CO']
		type       = 'C_BYL'
		spinType   = '13C'
		shift      = NTdict( average = 176.43000000000001, sd = 4.2999999999999998 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> O       
	#---------------------------------------------------------------
		topology   = [(0, 'C')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'O', 'INTERNAL_0': 'O', 'CYANA': 'O', 'CYANA2': 'O', 'INTERNAL_1': 'O', 'IUPAC': 'O', 'AQUA': 'O', 'BMRBd': 'O', 'XPLOR': 'O', 'PDB': 'O'}
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
		nameDict   = {'INTERNAL_0': 'H1', 'INTERNAL_1': 'H1', 'IUPAC': 'H1', 'CCPN': 'H1', 'XPLOR': 'H1'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 8.2400000000000002, sd = 0.60999999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H2      
	#---------------------------------------------------------------
		topology   = [(0, 'N')]
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': 'H2', 'INTERNAL_1': 'H2', 'IUPAC': 'H2', 'CCPN': 'H2', 'XPLOR': 'H2'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 8.2400000000000002, sd = 0.60999999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H3      
	#---------------------------------------------------------------
		topology   = [(0, 'N')]
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': 'H3', 'INTERNAL_1': 'H3', 'IUPAC': 'H3', 'CCPN': 'H3', 'XPLOR': 'H3'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 8.2400000000000002, sd = 0.60999999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> OXT     
	#---------------------------------------------------------------
		topology   = [(0, 'C')]
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': 'OXT', 'INTERNAL_1': 'OXT', 'IUPAC': "OXT,O''", 'CCPN': "O''", 'XPLOR': 'OXT'}
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
