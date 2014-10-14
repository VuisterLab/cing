<SML> 0.23

#=======================================================================
#             	internal short
<ResidueDef>  	cPRO     P        INTERNAL_0
#=======================================================================
	comment    = 'cis Proline'
	nameDict   = {'INTERNAL_0': 'cPRO', 'IUPAC': 'PRO', 'AQUA': 'PRO', 'BMRBd': 'PRO', 'INTERNAL_1': 'cPRO', 'CYANA': 'cPRO', 'CYANA2': 'cPRO', 'PDB': 'PRO', 'XPLOR': 'PRO'}
	properties = ['protein', 'aliphatic', 'neutral','isProline']

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
	<DihedralDef> OMEGA
	#---------------------------------------------------------------
		atoms    = [(-1, 'CA'), (-1, 'C'), (0, 'N'), (0, 'CA')]
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
	</NTlist>

	atoms      = <NTlist>
	#---------------------------------------------------------------
	<AtomDef> N
	#---------------------------------------------------------------
		topology   = [(-1, 'C'), (0, 'CD'), (0, 'CA')]
		nameDict   = {'INTERNAL_0': 'N', 'IUPAC': 'N', 'AQUA': 'N', 'BMRBd': 'N', 'INTERNAL_1': 'N', 'CYANA': 'N', 'CYANA2': 'N', 'PDB': 'N', 'XPLOR': 'N'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'N_AMI'
		spinType   = '15N'
		shift      = NTdict( average = 132.86000000000001, sd = 19.460000000000001 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CD
	#---------------------------------------------------------------
		topology   = [(0, 'N'), (0, 'CG'), (0, 'HD2'), (0, 'HD3')]
		nameDict   = {'INTERNAL_0': 'CD', 'IUPAC': 'CD', 'AQUA': 'CD', 'BMRBd': 'CD', 'INTERNAL_1': 'CD', 'CYANA': 'CD', 'CYANA2': 'CD', 'PDB': 'CD', 'XPLOR': 'CD'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 50.380000000000003, sd = 3.5899999999999999 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CA
	#---------------------------------------------------------------
		topology   = [(0, 'N'), (0, 'HA'), (0, 'CB'), (0, 'C')]
		nameDict   = {'INTERNAL_0': 'CA', 'IUPAC': 'CA', 'AQUA': 'CA', 'BMRBd': 'CA', 'INTERNAL_1': 'CA', 'CYANA': 'CA', 'CYANA2': 'CA', 'PDB': 'CA', 'XPLOR': 'CA'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 63.25, sd = 1.8899999999999999 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HA
	#---------------------------------------------------------------
		topology   = [(0, 'CA')]
		nameDict   = {'INTERNAL_0': 'HA', 'IUPAC': 'HA', 'AQUA': 'HA', 'BMRBd': 'HA', 'INTERNAL_1': 'HA', 'CYANA': 'HA', 'CYANA2': 'HA', 'PDB': 'HA', 'XPLOR': 'HA'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 4.4000000000000004, sd = 0.38 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CB
	#---------------------------------------------------------------
		topology   = [(0, 'CA'), (0, 'HB2'), (0, 'HB3'), (0, 'CG')]
		nameDict   = {'INTERNAL_0': 'CB', 'IUPAC': 'CB', 'AQUA': 'CB', 'BMRBd': 'CB', 'INTERNAL_1': 'CB', 'CYANA': 'CB', 'CYANA2': 'CB', 'PDB': 'CB', 'XPLOR': 'CB'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 34.159999999999997, sd = 1.1499999999999999 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HB2
	#---------------------------------------------------------------
		topology   = [(0, 'CB')]
		nameDict   = {'INTERNAL_0': 'HB2', 'IUPAC': 'HB2', 'AQUA': 'HB2', 'BMRBd': 'HB2', 'INTERNAL_1': 'HB2', 'CYANA': 'HB2', 'CYANA2': 'HB2', 'PDB': '1HB', 'XPLOR': 'HB2'}
		aliases    = []
		pseudo     = 'QB'
		real       = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 2.0699999999999998, sd = 0.40999999999999998 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HB3
	#---------------------------------------------------------------
		topology   = [(0, 'CB')]
		nameDict   = {'INTERNAL_0': 'HB3', 'IUPAC': 'HB3', 'AQUA': 'HB3', 'BMRBd': 'HB3', 'INTERNAL_1': 'HB3', 'CYANA': 'HB3', 'CYANA2': 'HB3', 'PDB': '2HB', 'XPLOR': 'HB1'}
		aliases    = []
		pseudo     = 'QB'
		real       = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 2.02, sd = 0.44 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QB
	#---------------------------------------------------------------
		topology   = [(0, 'CB')]
		nameDict   = {'INTERNAL_0': 'QB', 'IUPAC': 'QB', 'AQUA': 'QB', 'BMRBd': None, 'INTERNAL_1': 'QB', 'CYANA': 'QB', 'CYANA2': 'QB', 'PDB': None, 'XPLOR': 'HB*,HB#,HB%,HB+'}
		aliases    = []
		pseudo     = None
		real       = ['HB2', 'HB3']
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 2.0449999999999999, sd = 0.42499999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CG
	#---------------------------------------------------------------
		topology   = [(0, 'CD'), (0, 'CB'), (0, 'HG2'), (0, 'HG3')]
		nameDict   = {'INTERNAL_0': 'CG', 'IUPAC': 'CG', 'AQUA': 'CG', 'BMRBd': 'CG', 'INTERNAL_1': 'CG', 'CYANA': 'CG', 'CYANA2': 'CG', 'PDB': 'CG', 'XPLOR': 'CG'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 24.52, sd = 1.0900000000000001 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HG2
	#---------------------------------------------------------------
		topology   = [(0, 'CG')]
		nameDict   = {'INTERNAL_0': 'HG2', 'IUPAC': 'HG2', 'AQUA': 'HG2', 'BMRBd': 'HG2', 'INTERNAL_1': 'HG2', 'CYANA': 'HG2', 'CYANA2': 'HG2', 'PDB': '1HG', 'XPLOR': 'HG2'}
		aliases    = []
		pseudo     = 'QG'
		real       = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.9199999999999999, sd = 0.38 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HG3
	#---------------------------------------------------------------
		topology   = [(0, 'CG')]
		nameDict   = {'INTERNAL_0': 'HG3', 'IUPAC': 'HG3', 'AQUA': 'HG3', 'BMRBd': 'HG3', 'INTERNAL_1': 'HG3', 'CYANA': 'HG3', 'CYANA2': 'HG3', 'PDB': '2HG', 'XPLOR': 'HG1'}
		aliases    = []
		pseudo     = 'QG'
		real       = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.8999999999999999, sd = 0.40000000000000002 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QG
	#---------------------------------------------------------------
		topology   = [(0, 'CG')]
		nameDict   = {'INTERNAL_0': 'QG', 'IUPAC': 'QG', 'AQUA': 'QG', 'BMRBd': None, 'INTERNAL_1': 'QG', 'CYANA': 'QG', 'CYANA2': 'QG', 'PDB': None, 'XPLOR': 'HG*,HG#,HG%,HG+'}
		aliases    = []
		pseudo     = None
		real       = ['HG2', 'HG3']
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 1.9099999999999999, sd = 0.39000000000000001 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HD2
	#---------------------------------------------------------------
		topology   = [(0, 'CD')]
		nameDict   = {'INTERNAL_0': 'HD2', 'IUPAC': 'HD2', 'AQUA': 'HD2', 'BMRBd': 'HD2', 'INTERNAL_1': 'HD2', 'CYANA': 'HD2', 'CYANA2': 'HD2', 'PDB': '1HD', 'XPLOR': 'HD2'}
		aliases    = []
		pseudo     = 'QD'
		real       = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 3.6000000000000001, sd = 0.68999999999999995 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HD3
	#---------------------------------------------------------------
		topology   = [(0, 'CD')]
		nameDict   = {'INTERNAL_0': 'HD3', 'IUPAC': 'HD3', 'AQUA': 'HD3', 'BMRBd': 'HD3', 'INTERNAL_1': 'HD3', 'CYANA': 'HD3', 'CYANA2': 'HD3', 'PDB': '2HD', 'XPLOR': 'HD1'}
		aliases    = []
		pseudo     = 'QD'
		real       = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 3.5800000000000001, sd = 0.68999999999999995 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QD
	#---------------------------------------------------------------
		topology   = [(0, 'CD')]
		nameDict   = {'INTERNAL_0': 'QD', 'IUPAC': 'QD', 'AQUA': 'QD', 'BMRBd': None, 'INTERNAL_1': 'QD', 'CYANA': 'QD', 'CYANA2': 'QD', 'PDB': None, 'XPLOR': 'HD*,HD#,HD%,HD+'}
		aliases    = []
		pseudo     = None
		real       = ['HD2', 'HD3']
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 3.5899999999999999, sd = 0.68999999999999995 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> C
	#---------------------------------------------------------------
		topology   = [(0, 'CA'), (0, 'O'), (1, 'N')]
		nameDict   = {'INTERNAL_0': 'C', 'IUPAC': 'C', 'AQUA': 'C', 'BMRBd': 'C', 'INTERNAL_1': 'C', 'CYANA': 'C', 'CYANA2': 'C', 'PDB': 'C', 'XPLOR': 'C'}
		aliases    = ['C', 'CO']
		pseudo     = None
		real       = []
		type       = 'C_BYL'
		spinType   = '13C'
		shift      = NTdict( average = 176.75, sd = 1.6899999999999999 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> O
	#---------------------------------------------------------------
		topology   = [(0, 'C')]
		nameDict   = {'INTERNAL_0': 'O', 'IUPAC': 'O', 'AQUA': 'O', 'BMRBd': 'O', 'INTERNAL_1': 'O', 'CYANA': 'O', 'CYANA2': 'O', 'PDB': 'O', 'XPLOR': 'O'}
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
	<AtomDef> H2
	#---------------------------------------------------------------
		topology   = [(0, 'N')]
		nameDict   = {'INTERNAL_0': 'H2', 'INTERNAL_1': 'H2', 'IUPAC': 'H2', 'CCPN': 'H2', 'XPLOR': 'H2'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 8.3000000000000007, sd = 0.5 )
		hetatm     = False
		properties = ['PHE', 'F', 'isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
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
		shift      = NTdict( average = 8.3000000000000007, sd = 0.5 )
		hetatm     = False
		properties = ['PHE', 'F', 'isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
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
