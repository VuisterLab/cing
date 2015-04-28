<SML> 0.23

#=======================================================================
#             	internal short   
<ResidueDef>  	TYR      Y        INTERNAL_0
#=======================================================================
	comment    = 'Regular Tyr residue'
	nameDict   = {'CCPN': 'protein Tyr prot:HH', 'INTERNAL_0': 'TYR', 'IUPAC': 'TYR', 'AQUA': 'TYR', 'BMRBd': 'TYR', 'INTERNAL_1': 'TYR', 'CYANA': 'TYR', 'CYANA2': 'TYR', 'PDB': 'TYR', 'XPLOR': 'TYR'}
	properties = ['protein', 'aromatic', 'large', 'polar']

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
		atoms    = [(0, 'CA'), (0, 'CB'), (0, 'CG'), (0, 'CD1')]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> CHI6    
	#---------------------------------------------------------------
		atoms    = [(0, 'CE1'), (0, 'CZ'), (0, 'OH'), (0, 'HH')]
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
		shift      = NTdict( average = 121.13, sd = 12.289999999999999 )
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
		shift      = NTdict( average = 8.3399999999999999, sd = 0.75 )
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
		shift      = NTdict( average = 58.049999999999997, sd = 2.79 )
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
		shift      = NTdict( average = 4.6299999999999999, sd = 0.57999999999999996 )
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
		shift      = NTdict( average = 39.399999999999999, sd = 3.0800000000000001 )
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
		shift      = NTdict( average = 2.9100000000000001, sd = 0.5 )
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
		shift      = NTdict( average = 2.8799999999999999, sd = 0.5 )
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
		shift      = NTdict( average = 2.895, sd = 0.5 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QD      
	#---------------------------------------------------------------
		topology   = [(0, 'CD1'), (0, 'CD2')]
		nameDict   = {'CCPN': 'HD*', 'INTERNAL_0': 'QD', 'IUPAC': 'QD', 'AQUA': 'QD', 'BMRBd': None, 'INTERNAL_1': 'QD', 'CYANA': 'QD', 'CYANA2': 'QD', 'PDB': None, 'XPLOR': 'HD*,HD#,HD%,HD+'}
		aliases    = []
		pseudo     = None
		real       = ['HD1', 'HD2']
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 6.8949999999999996, sd = 0.54499999999999993 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QE      
	#---------------------------------------------------------------
		topology   = [(0, 'CE1'), (0, 'CE2')]
		nameDict   = {'CCPN': 'HE*', 'INTERNAL_0': 'QE', 'IUPAC': 'QE', 'AQUA': 'QE', 'BMRBd': None, 'INTERNAL_1': 'QE', 'CYANA': 'QE', 'CYANA2': 'QE', 'PDB': None, 'XPLOR': 'HE*,HE#,HE%,HE+'}
		aliases    = []
		pseudo     = None
		real       = ['HE1', 'HE2']
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 6.6749999999999998, sd = 0.48999999999999999 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QR      
	#---------------------------------------------------------------
		topology   = [(0, 'CD1'), (0, 'CE1'), (0, 'CE2'), (0, 'CD2')]
		nameDict   = {'CCPN': 'HD*|HE*', 'INTERNAL_0': 'QR', 'IUPAC': 'QR', 'AQUA': 'QR', 'BMRBd': None, 'INTERNAL_1': 'QR', 'CYANA': 'QR', 'CYANA2': 'QR', 'PDB': None, 'XPLOR': None}
		aliases    = []
		pseudo     = None
		real       = ['HD1', 'HD2', 'HE1', 'HE2']
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 6.7850000000000001, sd = 0.51749999999999996 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CG      
	#---------------------------------------------------------------
		topology   = [(0, 'CB'), (0, 'CD1'), (0, 'CD2')]
		nameDict   = {'CCPN': 'CG', 'INTERNAL_0': 'CG', 'IUPAC': 'CG', 'AQUA': 'CG', 'BMRBd': 'CG', 'INTERNAL_1': 'CG', 'CYANA': 'CG', 'CYANA2': 'CG', 'PDB': 'CG', 'XPLOR': 'CG'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'C_VIN'
		spinType   = '13C'
		shift      = NTdict( average = 129.12, sd = 2.5299999999999998 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CD1     
	#---------------------------------------------------------------
		topology   = [(0, 'CG'), (0, 'HD1'), (0, 'CE1')]
		nameDict   = {'CCPN': 'CD1', 'INTERNAL_0': 'CD1', 'IUPAC': 'CD1', 'AQUA': 'CD1', 'BMRBd': 'CD1', 'INTERNAL_1': 'CD1', 'CYANA': 'CD1', 'CYANA2': 'CD1', 'PDB': 'CD1', 'XPLOR': 'CD1'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'C_ARO'
		spinType   = '13C'
		shift      = NTdict( average = 131.94999999999999, sd = 7.4100000000000001 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HD1     
	#---------------------------------------------------------------
		topology   = [(0, 'CD1')]
		nameDict   = {'CCPN': 'HD1', 'INTERNAL_0': 'HD1', 'IUPAC': 'HD1', 'AQUA': 'HD1', 'BMRBd': 'HD1', 'INTERNAL_1': 'HD1', 'CYANA': 'HD1', 'CYANA2': 'HD1', 'PDB': 'HD1', 'XPLOR': 'HD1'}
		aliases    = []
		pseudo     = 'QD'
		real       = []
		type       = 'H_ARO'
		spinType   = '1H'
		shift      = NTdict( average = 6.9000000000000004, sd = 0.52000000000000002 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CE1     
	#---------------------------------------------------------------
		topology   = [(0, 'CD1'), (0, 'HE1'), (0, 'CZ')]
		nameDict   = {'CCPN': 'CE1', 'INTERNAL_0': 'CE1', 'IUPAC': 'CE1', 'AQUA': 'CE1', 'BMRBd': 'CE1', 'INTERNAL_1': 'CE1', 'CYANA': 'CE1', 'CYANA2': 'CE1', 'PDB': 'CE1', 'XPLOR': 'CE1'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'C_ARO'
		spinType   = '13C'
		shift      = NTdict( average = 117.56999999999999, sd = 4.5199999999999996 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HE1     
	#---------------------------------------------------------------
		topology   = [(0, 'CE1')]
		nameDict   = {'CCPN': 'HE1', 'INTERNAL_0': 'HE1', 'IUPAC': 'HE1', 'AQUA': 'HE1', 'BMRBd': 'HE1', 'INTERNAL_1': 'HE1', 'CYANA': 'HE1', 'CYANA2': 'HE1', 'PDB': 'HE1', 'XPLOR': 'HE1'}
		aliases    = []
		pseudo     = 'QE'
		real       = []
		type       = 'H_ARO'
		spinType   = '1H'
		shift      = NTdict( average = 6.6799999999999997, sd = 0.46999999999999997 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CZ      
	#---------------------------------------------------------------
		topology   = [(0, 'CE1'), (0, 'CE2'), (0, 'OH')]
		nameDict   = {'CCPN': 'CZ', 'INTERNAL_0': 'CZ', 'IUPAC': 'CZ', 'AQUA': 'CZ', 'BMRBd': 'CZ', 'INTERNAL_1': 'CZ', 'CYANA': 'CZ', 'CYANA2': 'CZ', 'PDB': 'CZ', 'XPLOR': 'CZ'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'C_VIN'
		spinType   = '13C'
		shift      = NTdict( average = 153.34, sd = 18.84 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CE2     
	#---------------------------------------------------------------
		topology   = [(0, 'CZ'), (0, 'HE2'), (0, 'CD2')]
		nameDict   = {'CCPN': 'CE2', 'INTERNAL_0': 'CE2', 'IUPAC': 'CE2', 'AQUA': 'CE2', 'BMRBd': 'CE2', 'INTERNAL_1': 'CE2', 'CYANA': 'CE2', 'CYANA2': 'CE2', 'PDB': 'CE2', 'XPLOR': 'CE2'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'C_ARO'
		spinType   = '13C'
		shift      = NTdict( average = 117.45999999999999, sd = 5.1799999999999997 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HE2     
	#---------------------------------------------------------------
		topology   = [(0, 'CE2')]
		nameDict   = {'CCPN': 'HE2', 'INTERNAL_0': 'HE2', 'IUPAC': 'HE2', 'AQUA': 'HE2', 'BMRBd': 'HE2', 'INTERNAL_1': 'HE2', 'CYANA': 'HE2', 'CYANA2': 'HE2', 'PDB': 'HE2', 'XPLOR': 'HE2'}
		aliases    = []
		pseudo     = 'QE'
		real       = []
		type       = 'H_ARO'
		spinType   = '1H'
		shift      = NTdict( average = 6.6699999999999999, sd = 0.51000000000000001 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CD2     
	#---------------------------------------------------------------
		topology   = [(0, 'CG'), (0, 'CE2'), (0, 'HD2')]
		nameDict   = {'CCPN': 'CD2', 'INTERNAL_0': 'CD2', 'IUPAC': 'CD2', 'AQUA': 'CD2', 'BMRBd': 'CD2', 'INTERNAL_1': 'CD2', 'CYANA': 'CD2', 'CYANA2': 'CD2', 'PDB': 'CD2', 'XPLOR': 'CD2'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'C_ARO'
		spinType   = '13C'
		shift      = NTdict( average = 131.52000000000001, sd = 9.2599999999999998 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HD2     
	#---------------------------------------------------------------
		topology   = [(0, 'CD2')]
		nameDict   = {'CCPN': 'HD2', 'INTERNAL_0': 'HD2', 'IUPAC': 'HD2', 'AQUA': 'HD2', 'BMRBd': 'HD2', 'INTERNAL_1': 'HD2', 'CYANA': 'HD2', 'CYANA2': 'HD2', 'PDB': 'HD2', 'XPLOR': 'HD2'}
		aliases    = []
		pseudo     = 'QD'
		real       = []
		type       = 'H_ARO'
		spinType   = '1H'
		shift      = NTdict( average = 6.8899999999999997, sd = 0.56999999999999995 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> OH      
	#---------------------------------------------------------------
		topology   = [(0, 'CZ'), (0, 'HH')]
		nameDict   = {'CCPN': 'OH', 'INTERNAL_0': 'OH', 'IUPAC': 'OH', 'AQUA': 'OH', 'BMRBd': 'OH', 'INTERNAL_1': 'OH', 'CYANA': 'OH', 'CYANA2': 'OH', 'PDB': 'OH', 'XPLOR': 'OH'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'O_HYD'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HH      
	#---------------------------------------------------------------
		topology   = [(0, 'OH')]
		nameDict   = {'CCPN': 'HH', 'INTERNAL_0': 'HH', 'IUPAC': 'HH', 'AQUA': 'HH', 'BMRBd': 'HH', 'INTERNAL_1': 'HH', 'CYANA': 'HH', 'CYANA2': 'HH', 'PDB': 'HH', 'XPLOR': 'HH'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'H_OXY'
		spinType   = '1H'
		shift      = NTdict( average = 9.0800000000000001, sd = 3.0299999999999998 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
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
		shift      = NTdict( average = 175.41, sd = 3.96 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isAromatic', 'aromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
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
		shift      = NTdict( average = 8.3399999999999999, sd = 0.75 )
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
		shift      = NTdict( average = 8.3399999999999999, sd = 0.75 )
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
		shift      = NTdict( average = 8.3399999999999999, sd = 0.75 )
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
