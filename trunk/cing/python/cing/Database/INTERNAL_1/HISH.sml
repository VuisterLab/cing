<SML> 0.25

#=======================================================================
#             	name     convention
<ResidueDef>  	HISH     INTERNAL_1
#=======================================================================
	commonName = 'HISH'
	shortName  = 'H'
	comment    = 'Protonated (plus) His'
	nameDict   = {'CCPN': 'protein His prot:HD1,HE2', 'INTERNAL_0': 'HISH', 'CYANA': 'HIS+', 'CYANA2': 'HIS', 'INTERNAL_1': 'HISH', 'IUPAC': 'HIS', 'AQUA': 'HIS', 'BMRBd': 'HIS', 'XPLOR': 'HIS', 'PDB': 'HIS'}
	properties = ['protein', 'aromatic', 'large', 'polar', 'isHistidine']

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
		atoms    = [(0, 'CA'), (0, 'CB'), (0, 'CG'), (0, 'ND1')]
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
		shift      = NTdict( average = 119.52, sd = 4.3399999999999999 )
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
		shift      = NTdict( average = 8.2699999999999996, sd = 0.81999999999999995 )
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
		shift      = NTdict( average = 56.490000000000002, sd = 3.0499999999999998 )
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
		shift      = NTdict( average = 4.6500000000000004, sd = 0.77000000000000002 )
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
		shift      = NTdict( average = 30.25, sd = 2.9399999999999999 )
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
		shift      = NTdict( average = 3.3700000000000001, sd = 2.23 )
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
		shift      = NTdict( average = 3.2799999999999998, sd = 2.0299999999999998 )
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
		shift      = NTdict( average = 3.3250000000000002, sd = 2.1299999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CG      
	#---------------------------------------------------------------
		topology   = [(0, 'CB'), (0, 'ND1'), (0, 'CD2')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'CG', 'INTERNAL_0': 'CG', 'CYANA': 'CG', 'CYANA2': 'CG', 'INTERNAL_1': 'CG', 'IUPAC': 'CG', 'AQUA': 'CG', 'BMRBd': 'CG', 'XPLOR': 'CG', 'PDB': 'CG'}
		aliases    = []
		type       = 'C_VIN'
		spinType   = '13C'
		shift      = NTdict( average = 130.40000000000001, sd = 8.3399999999999999 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> ND1     
	#---------------------------------------------------------------
		topology   = [(0, 'CG'), (0, 'HD1'), (0, 'CE1')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'ND1', 'INTERNAL_0': 'ND1', 'CYANA': 'ND1', 'CYANA2': 'ND1', 'INTERNAL_1': 'ND1', 'IUPAC': 'ND1', 'AQUA': 'ND1', 'BMRBd': 'ND1', 'XPLOR': 'ND1', 'PDB': 'ND1'}
		aliases    = []
		type       = 'N_AMI'
		spinType   = '15N'
		shift      = NTdict( average = 189.56, sd = 36.140000000000001 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CD2     
	#---------------------------------------------------------------
		topology   = [(0, 'CG'), (0, 'NE2'), (0, 'HD2')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'CD2', 'INTERNAL_0': 'CD2', 'CYANA': 'CD2', 'CYANA2': 'CD2', 'INTERNAL_1': 'CD2', 'IUPAC': 'CD2', 'AQUA': 'CD2', 'BMRBd': 'CD2', 'XPLOR': 'CD2', 'PDB': 'CD2'}
		aliases    = []
		type       = 'C_ARO'
		spinType   = '13C'
		shift      = NTdict( average = 119.2, sd = 7.5 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HD1     
	#---------------------------------------------------------------
		topology   = [(0, 'ND1')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'HD1', 'INTERNAL_0': 'HD1', 'CYANA': 'HD1', 'CYANA2': 'HD1', 'INTERNAL_1': 'HD1', 'IUPAC': 'HD1', 'AQUA': 'HD1', 'BMRBd': 'HD1', 'XPLOR': 'HD1', 'PDB': 'HD1'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 12.970000000000001, sd = 14.199999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CE1     
	#---------------------------------------------------------------
		topology   = [(0, 'ND1'), (0, 'NE2'), (0, 'HE1')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'CE1', 'INTERNAL_0': 'CE1', 'CYANA': 'CE1', 'CYANA2': 'CE1', 'INTERNAL_1': 'CE1', 'IUPAC': 'CE1', 'AQUA': 'CE1', 'BMRBd': 'CE1', 'XPLOR': 'CE1', 'PDB': 'CE1'}
		aliases    = []
		type       = 'C_ARO'
		spinType   = '13C'
		shift      = NTdict( average = 135.97999999999999, sd = 8.4199999999999999 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> NE2     
	#---------------------------------------------------------------
		topology   = [(0, 'CD2'), (0, 'CE1'), (0, 'HE2')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'NE2', 'INTERNAL_0': 'NE2', 'CYANA': 'NE2', 'CYANA2': 'NE2', 'INTERNAL_1': 'NE2', 'IUPAC': 'NE2', 'AQUA': 'NE2', 'BMRBd': 'NE2', 'XPLOR': 'NE2', 'PDB': 'NE2'}
		aliases    = []
		type       = 'N_AMI'
		spinType   = '15N'
		shift      = NTdict( average = 176.81, sd = 24.539999999999999 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HD2     
	#---------------------------------------------------------------
		topology   = [(0, 'CD2')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'HD2', 'INTERNAL_0': 'HD2', 'CYANA': 'HD2', 'CYANA2': 'HD2', 'INTERNAL_1': 'HD2', 'IUPAC': 'HD2', 'AQUA': 'HD2', 'BMRBd': 'HD2', 'XPLOR': 'HD2', 'PDB': 'HD2'}
		aliases    = []
		type       = 'H_ARO'
		spinType   = '1H'
		shift      = NTdict( average = 12.970000000000001, sd = 14.199999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HE1     
	#---------------------------------------------------------------
		topology   = [(0, 'CE1')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'HE1', 'INTERNAL_0': 'HE1', 'CYANA': 'HE1', 'CYANA2': 'HE1', 'INTERNAL_1': 'HE1', 'IUPAC': 'HE1', 'AQUA': 'HE1', 'BMRBd': 'HE1', 'XPLOR': 'HE1', 'PDB': 'HE1'}
		aliases    = []
		type       = 'H_ARO'
		spinType   = '1H'
		shift      = NTdict( average = 7.6500000000000004, sd = 4.29 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HE2     
	#---------------------------------------------------------------
		topology   = [(0, 'NE2')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'HE2', 'INTERNAL_0': 'HE2', 'CYANA': 'HE2', 'CYANA2': 'HE2', 'INTERNAL_1': 'HE2', 'IUPAC': 'HE2', 'AQUA': 'HE2', 'BMRBd': None, 'XPLOR': 'HE2', 'PDB': 'HE2'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isAromatic', 'aromatic', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> C       
	#---------------------------------------------------------------
		topology   = [(0, 'CA'), (0, 'O'), (1, 'N')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'C', 'INTERNAL_0': 'C', 'CYANA': 'C', 'CYANA2': 'C', 'INTERNAL_1': 'C', 'IUPAC': 'C', 'AQUA': 'C', 'BMRBd': None, 'XPLOR': 'C', 'PDB': 'C'}
		aliases    = ['C', 'CO']
		type       = 'C_BYL'
		spinType   = '13C'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> O       
	#---------------------------------------------------------------
		topology   = [(0, 'C')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'O', 'INTERNAL_0': 'O', 'CYANA': 'O', 'CYANA2': 'O', 'INTERNAL_1': 'O', 'IUPAC': 'O', 'AQUA': 'O', 'BMRBd': None, 'XPLOR': 'O,OT1', 'PDB': 'O'}
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
		nameDict   = {'INTERNAL_0': 'H1', 'INTERNAL_1': 'H1', 'IUPAC': 'H1', 'CCPN': 'H1', 'XPLOR': 'HT1'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 8.2699999999999996, sd = 0.81999999999999995 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H2      
	#---------------------------------------------------------------
		topology   = [(0, 'N')]
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': 'H2', 'INTERNAL_1': 'H2', 'IUPAC': 'H2', 'CCPN': 'H2', 'XPLOR': 'HT3'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 8.2699999999999996, sd = 0.81999999999999995 )
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
		shift      = NTdict( average = 8.2699999999999996, sd = 0.81999999999999995 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> OXT     
	#---------------------------------------------------------------
		topology   = [(0, 'C')]
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': 'OXT', 'INTERNAL_1': 'OXT', 'IUPAC': "OXT,O''", 'CCPN': "O''", 'XPLOR': 'OT2'}
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
