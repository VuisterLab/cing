<SML> 0.23

#=======================================================================
#             	internal short
<ResidueDef>  	ARGx     R        INTERNAL_0
#=======================================================================
	comment    = 'non-protonated (neutral) ARG (uncommon)'
	nameDict   = {'CCPN': 'protein Arg deprot:HH12', 'INTERNAL_0': 'ARGx', 'IUPAC': 'ARG', 'AQUA': 'ARG', 'BMRBd': None, 'INTERNAL_1': 'ARGx', 'CYANA': 'ARG', 'CYANA2': None, 'PDB': None, 'XPLOR': None}
	properties = ['protein', 'aliphatic', 'large', 'charged','isArginine']

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
		topology   = [(-1, 'C'), (0, 'HN'), (0, 'CA')]
		nameDict   = {'CCPN': 'N', 'INTERNAL_0': 'N', 'IUPAC': 'N', 'AQUA': 'N', 'BMRBd': 'N', 'INTERNAL_1': 'N', 'CYANA': 'N', 'CYANA2': 'N', 'PDB': 'N', 'XPLOR': 'N'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'N_AMI'
		spinType   = '15N'
		shift      = NTdict( average = 120.72, sd = 4.0099999999999998 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HN
	#---------------------------------------------------------------
		topology   = [(0, 'N')]
		nameDict   = {'CCPN': 'H', 'INTERNAL_0': 'HN', 'IUPAC': 'H', 'AQUA': 'H', 'BMRBd': 'H', 'INTERNAL_1': 'H', 'CYANA': 'HN', 'CYANA2': 'H', 'PDB': 'H', 'XPLOR': 'HN'}
		aliases    = ['HN', 'H']
		pseudo     = None
		real       = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 8.2400000000000002, sd = 0.60999999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CA
	#---------------------------------------------------------------
		topology   = [(0, 'N'), (0, 'HA'), (0, 'CB'), (0, 'C')]
		nameDict   = {'CCPN': 'CA', 'INTERNAL_0': 'CA', 'IUPAC': 'CA', 'AQUA': 'CA', 'BMRBd': 'CA', 'INTERNAL_1': 'CA', 'CYANA': 'CA', 'CYANA2': 'CA', 'PDB': 'CA', 'XPLOR': 'CA'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 56.840000000000003, sd = 2.52 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HA
	#---------------------------------------------------------------
		topology   = [(0, 'CA')]
		nameDict   = {'CCPN': 'HA', 'INTERNAL_0': 'HA', 'IUPAC': 'HA', 'AQUA': 'HA', 'BMRBd': 'HA', 'INTERNAL_1': 'HA', 'CYANA': 'HA', 'CYANA2': 'HA', 'PDB': 'HA', 'XPLOR': 'HA'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 4.29, sd = 0.47999999999999998 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CB
	#---------------------------------------------------------------
		topology   = [(0, 'CA'), (0, 'HB2'), (0, 'HB3'), (0, 'CG')]
		nameDict   = {'CCPN': 'CB', 'INTERNAL_0': 'CB', 'IUPAC': 'CB', 'AQUA': 'CB', 'BMRBd': 'CB', 'INTERNAL_1': 'CB', 'CYANA': 'CB', 'CYANA2': 'CB', 'PDB': 'CB', 'XPLOR': 'CB'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 30.710000000000001, sd = 2.6000000000000001 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HB2
	#---------------------------------------------------------------
		topology   = [(0, 'CB')]
		nameDict   = {'CCPN': 'HB2', 'INTERNAL_0': 'HB2', 'IUPAC': 'HB2', 'AQUA': 'HB2', 'BMRBd': 'HB2', 'INTERNAL_1': 'HB2', 'CYANA': 'HB2', 'CYANA2': 'HB2', 'PDB': '1HB', 'XPLOR': 'HB2'}
		aliases    = []
		pseudo     = 'QB'
		real       = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.8, sd = 0.29999999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HB3
	#---------------------------------------------------------------
		topology   = [(0, 'CB')]
		nameDict   = {'CCPN': 'HB3', 'INTERNAL_0': 'HB3', 'IUPAC': 'HB3', 'AQUA': 'HB3', 'BMRBd': 'HB3', 'INTERNAL_1': 'HB3', 'CYANA': 'HB3', 'CYANA2': 'HB3', 'PDB': '2HB', 'XPLOR': 'HB1'}
		aliases    = []
		pseudo     = 'QB'
		real       = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.78, sd = 0.28999999999999998 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QB
	#---------------------------------------------------------------
		topology   = [(0, 'CB')]
		nameDict   = {'CCPN': 'HB*', 'INTERNAL_0': 'QB', 'IUPAC': 'QB', 'AQUA': 'QB', 'BMRBd': None, 'INTERNAL_1': 'QB', 'CYANA': 'QB', 'CYANA2': 'QB', 'PDB': None, 'XPLOR': 'HB*,HB#,HB%,HB+'}
		aliases    = []
		pseudo     = None
		real       = ['HB2', 'HB3']
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 1.79, sd = 0.29499999999999998 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CG
	#---------------------------------------------------------------
		topology   = [(0, 'CB'), (0, 'HG2'), (0, 'HG3'), (0, 'CD')]
		nameDict   = {'CCPN': 'CG', 'INTERNAL_0': 'CG', 'IUPAC': 'CG', 'AQUA': 'CG', 'BMRBd': 'CG', 'INTERNAL_1': 'CG', 'CYANA': 'CG', 'CYANA2': 'CG', 'PDB': 'CG', 'XPLOR': 'CG'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 27.379999999999999, sd = 2.5899999999999999 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HG2
	#---------------------------------------------------------------
		topology   = [(0, 'CG')]
		nameDict   = {'CCPN': 'HG2', 'INTERNAL_0': 'HG2', 'IUPAC': 'HG2', 'AQUA': 'HG2', 'BMRBd': 'HG2', 'INTERNAL_1': 'HG2', 'CYANA': 'HG2', 'CYANA2': 'HG2', 'PDB': '1HG', 'XPLOR': 'HG2'}
		aliases    = []
		pseudo     = 'QG'
		real       = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.5800000000000001, sd = 0.28000000000000003 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HG3
	#---------------------------------------------------------------
		topology   = [(0, 'CG')]
		nameDict   = {'CCPN': 'HG3', 'INTERNAL_0': 'HG3', 'IUPAC': 'HG3', 'AQUA': 'HG3', 'BMRBd': 'HG3', 'INTERNAL_1': 'HG3', 'CYANA': 'HG3', 'CYANA2': 'HG3', 'PDB': '2HG', 'XPLOR': 'HG1'}
		aliases    = []
		pseudo     = 'QG'
		real       = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.5600000000000001, sd = 0.29999999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QG
	#---------------------------------------------------------------
		topology   = [(0, 'CG')]
		nameDict   = {'CCPN': 'HG*', 'INTERNAL_0': 'QG', 'IUPAC': 'QG', 'AQUA': 'QG', 'BMRBd': None, 'INTERNAL_1': 'QG', 'CYANA': 'QG', 'CYANA2': 'QG', 'PDB': None, 'XPLOR': 'HG*,HG#,HG%,HG+'}
		aliases    = []
		pseudo     = None
		real       = ['HG2', 'HG3']
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 1.5700000000000001, sd = 0.29000000000000004 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CD
	#---------------------------------------------------------------
		topology   = [(0, 'CG'), (0, 'HD2'), (0, 'HD3'), (0, 'NE')]
		nameDict   = {'CCPN': 'CD', 'INTERNAL_0': 'CD', 'IUPAC': 'CD', 'AQUA': 'CD', 'BMRBd': 'CD', 'INTERNAL_1': 'CD', 'CYANA': 'CD', 'CYANA2': 'CD', 'PDB': 'CD', 'XPLOR': 'CD'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 43.210000000000001, sd = 2.27 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HD2
	#---------------------------------------------------------------
		topology   = [(0, 'CD')]
		nameDict   = {'CCPN': 'HD2', 'INTERNAL_0': 'HD2', 'IUPAC': 'HD2', 'AQUA': 'HD2', 'BMRBd': 'HD2', 'INTERNAL_1': 'HD2', 'CYANA': 'HD2', 'CYANA2': 'HD2', 'PDB': '1HD', 'XPLOR': 'HD2'}
		aliases    = []
		pseudo     = 'QD'
		real       = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 3.1200000000000001, sd = 0.29999999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HD3
	#---------------------------------------------------------------
		topology   = [(0, 'CD')]
		nameDict   = {'CCPN': 'HD3', 'INTERNAL_0': 'HD3', 'IUPAC': 'HD3', 'AQUA': 'HD3', 'BMRBd': 'HD3', 'INTERNAL_1': 'HD3', 'CYANA': 'HD3', 'CYANA2': 'HD3', 'PDB': '2HD', 'XPLOR': 'HD1'}
		aliases    = []
		pseudo     = 'QD'
		real       = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 3.1099999999999999, sd = 0.28000000000000003 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QD
	#---------------------------------------------------------------
		topology   = [(0, 'CD')]
		nameDict   = {'CCPN': 'HD*', 'INTERNAL_0': 'QD', 'IUPAC': 'QD', 'AQUA': 'QD', 'BMRBd': None, 'INTERNAL_1': 'QD', 'CYANA': 'QD', 'CYANA2': 'QD', 'PDB': None, 'XPLOR': 'HD*,HD#,HD%,HD+'}
		aliases    = []
		pseudo     = None
		real       = ['HD2', 'HD3']
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 3.1150000000000002, sd = 0.29000000000000004 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> NE
	#---------------------------------------------------------------
		topology   = [(0, 'CD'), (0, 'HE'), (0, 'CZ')]
		nameDict   = {'CCPN': 'NE', 'INTERNAL_0': 'NE', 'IUPAC': 'NE', 'AQUA': 'NE', 'BMRBd': 'NE', 'INTERNAL_1': 'NE', 'CYANA': 'NE', 'CYANA2': 'NE', 'PDB': 'NE', 'XPLOR': 'NE'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'N_AMI'
		spinType   = '15N'
		shift      = NTdict( average = 93.790000000000006, sd = 15.460000000000001 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HE
	#---------------------------------------------------------------
		topology   = [(0, 'NE')]
		nameDict   = {'CCPN': 'HE', 'INTERNAL_0': 'HE', 'IUPAC': 'HE', 'AQUA': 'HE', 'BMRBd': 'HE', 'INTERNAL_1': 'HE', 'CYANA': 'HE', 'CYANA2': 'HE', 'PDB': 'HE', 'XPLOR': 'HE'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 7.3300000000000001, sd = 0.64000000000000001 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CZ
	#---------------------------------------------------------------
		topology   = [(0, 'NE'), (0, 'NH1'), (0, 'NH2')]
		nameDict   = {'CCPN': 'CZ', 'INTERNAL_0': 'CZ', 'IUPAC': 'CZ', 'AQUA': 'CZ', 'BMRBd': 'CZ', 'INTERNAL_1': 'CZ', 'CYANA': 'CZ', 'CYANA2': 'CZ', 'PDB': 'CZ', 'XPLOR': 'CZ'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'C_VIN'
		spinType   = '13C'
		shift      = NTdict( average = 159.16, sd = 1.0 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> NH1
	#---------------------------------------------------------------
		topology   = [(0, 'CZ'), (0, 'HH1')]
		nameDict   = {'CCPN': 'NH1', 'INTERNAL_0': 'NH1', 'IUPAC': 'NH1', 'AQUA': 'NH1', 'BMRBd': 'NH1', 'INTERNAL_1': 'NH1', 'CYANA': 'NH1', 'CYANA2': 'NH1', 'PDB': 'NH1', 'XPLOR': 'NH1'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'N_AMI'
		spinType   = '15N'
		shift      = NTdict( average = 74.219999999999999, sd = 7.7000000000000002 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HH1
	#---------------------------------------------------------------
		topology   = [(0, 'NH1')]
		nameDict   = {'CCPN': 'HH11', 'INTERNAL_0': 'HH1', 'IUPAC': 'HH1', 'AQUA': 'HH1', 'BMRBd': 'HH1', 'INTERNAL_1': 'HH1', 'CYANA': 'HH1', 'CYANA2': 'HH1', 'PDB': 'HH1', 'XPLOR': 'HH1'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 6.8499999999999996, sd = 0.51000000000000001 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> NH2
	#---------------------------------------------------------------
		topology   = [(0, 'CZ'), (0, 'HH21'), (0, 'HH22')]
		nameDict   = {'CCPN': 'NH2', 'INTERNAL_0': 'NH2', 'IUPAC': 'NH2', 'AQUA': 'NH2', 'BMRBd': 'NH2', 'INTERNAL_1': 'NH2', 'CYANA': 'NH2', 'CYANA2': 'NH2', 'PDB': 'NH2', 'XPLOR': 'NH2'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'N_AMI'
		spinType   = '15N'
		shift      = NTdict( average = 75.180000000000007, sd = 10.68 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HH21
	#---------------------------------------------------------------
		topology   = [(0, 'NH2')]
		nameDict   = {'CCPN': 'HH21', 'INTERNAL_0': 'HH21', 'IUPAC': 'HH21', 'AQUA': 'HH21', 'BMRBd': 'HH21', 'INTERNAL_1': 'HH21', 'CYANA': 'HH21', 'CYANA2': 'HH21', 'PDB': '1HH2', 'XPLOR': 'HH21'}
		aliases    = []
		pseudo     = 'QH2'
		real       = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 6.79, sd = 0.46999999999999997 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HH22
	#---------------------------------------------------------------
		topology   = [(0, 'NH2')]
		nameDict   = {'CCPN': 'HH22', 'INTERNAL_0': 'HH22', 'IUPAC': 'HH22', 'AQUA': 'HH22', 'BMRBd': 'HH22', 'INTERNAL_1': 'HH22', 'CYANA': 'HH22', 'CYANA2': 'HH22', 'PDB': '2HH2', 'XPLOR': 'HH22'}
		aliases    = []
		pseudo     = 'QH2'
		real       = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 6.7699999999999996, sd = 0.5 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QH2
	#---------------------------------------------------------------
		topology   = [(0, 'NH2')]
		nameDict   = {'CCPN': 'HH2*', 'INTERNAL_0': 'QH2', 'IUPAC': 'QH2', 'AQUA': 'QH2', 'BMRBd': None, 'INTERNAL_1': 'QH2', 'CYANA': 'QH2', 'CYANA2': 'QH2', 'PDB': None, 'XPLOR': 'HH2*,HH2#,HH2%,HH2+'}
		aliases    = []
		pseudo     = None
		real       = ['HH21', 'HH22']
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 6.7799999999999994, sd = 0.48499999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> C
	#---------------------------------------------------------------
		topology   = [(0, 'CA'), (0, 'O'), (1, 'N')]
		nameDict   = {'CCPN': 'C', 'INTERNAL_0': 'C', 'IUPAC': 'C', 'AQUA': 'C', 'BMRBd': 'C', 'INTERNAL_1': 'C', 'CYANA': 'C', 'CYANA2': 'C', 'PDB': 'C', 'XPLOR': 'C'}
		aliases    = ['C', 'CO']
		pseudo     = None
		real       = []
		type       = 'C_BYL'
		spinType   = '13C'
		shift      = NTdict( average = 176.43000000000001, sd = 4.2999999999999998 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> O
	#---------------------------------------------------------------
		topology   = [(0, 'C')]
		nameDict   = {'CCPN': 'O', 'INTERNAL_0': 'O', 'IUPAC': 'O', 'AQUA': 'O', 'BMRBd': 'O', 'INTERNAL_1': 'O', 'CYANA': 'O', 'CYANA2': 'O', 'PDB': 'O', 'XPLOR': 'O'}
		aliases    = ['O', "O'"]
		pseudo     = None
		real       = []
		type       = 'O_BYL'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isSidechain', 'sidechain']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H1
	#---------------------------------------------------------------
		topology   = [(0, 'N')]
		nameDict   = {'INTERNAL_0': 'H1', 'INTERNAL_1': 'H1', 'IUPAC': 'H1', 'CCPN': 'H1', 'XPLOR': 'H1'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 8.2400000000000002, sd = 0.60999999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H2
	#---------------------------------------------------------------
		topology   = [(0, 'N')]
		nameDict   = {'INTERNAL_0': 'H2', 'INTERNAL_1': 'H2', 'IUPAC': 'H2', 'CCPN': 'H2', 'XPLOR': 'H2'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 8.2400000000000002, sd = 0.60999999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H3
	#---------------------------------------------------------------
		topology   = [(0, 'N')]
		nameDict   = {'INTERNAL_0': 'H3', 'INTERNAL_1': 'H3', 'IUPAC': 'H3', 'CCPN': 'H3', 'XPLOR': 'H3'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 8.2400000000000002, sd = 0.60999999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> OXT
	#---------------------------------------------------------------
		topology   = [(0, 'C')]
		nameDict   = {'INTERNAL_0': 'OXT', 'INTERNAL_1': 'OXT', 'IUPAC': "OXT,O''", 'CCPN': "O''", 'XPLOR': 'OXT'}
		aliases    = ['OXT', "O''"]
		pseudo     = None
		real       = []
		type       = 'O_BYL'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isSidechain', 'sidechain']
	</AtomDef>
	</NTlist>
</ResidueDef>
#=======================================================================
</SML>
