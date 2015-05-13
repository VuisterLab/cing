<SML> 0.23

#=======================================================================
#             	internal short   
<ResidueDef>  	GLN      Q        INTERNAL_0
#=======================================================================
	comment    = 'Regular Gln residue'
	nameDict   = {'CCPN': 'protein Gln neutral', 'INTERNAL_0': 'GLN', 'IUPAC': 'GLN', 'AQUA': 'GLN', 'BMRBd': 'GLN', 'INTERNAL_1': 'GLN', 'CYANA': 'GLN', 'CYANA2': 'GLN', 'PDB': 'GLN', 'XPLOR': 'GLN'}
	properties = ['protein', 'aliphatic', 'large', 'polar']

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
		atoms    = [(0, 'CB'), (0, 'CG'), (0, 'CD'), (0, 'OE1')]
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
		shift      = NTdict( average = 119.84, sd = 4.0300000000000002 )
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
		shift      = NTdict( average = 8.2100000000000009, sd = 0.62 )
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
		shift      = NTdict( average = 56.560000000000002, sd = 2.3199999999999998 )
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
		shift      = NTdict( average = 4.29, sd = 0.45000000000000001 )
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
		shift      = NTdict( average = 29.260000000000002, sd = 2.4399999999999999 )
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
		shift      = NTdict( average = 2.0499999999999998, sd = 0.28000000000000003 )
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
		shift      = NTdict( average = 2.04, sd = 0.40000000000000002 )
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
		shift      = NTdict( average = 2.0449999999999999, sd = 0.34000000000000002 )
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
		shift      = NTdict( average = 33.810000000000002, sd = 2.5899999999999999 )
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
		shift      = NTdict( average = 2.3199999999999998, sd = 0.29999999999999999 )
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
		shift      = NTdict( average = 2.2999999999999998, sd = 0.32000000000000001 )
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
		shift      = NTdict( average = 2.3099999999999996, sd = 0.31 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CD      
	#---------------------------------------------------------------
		topology   = [(0, 'CG'), (0, 'OE1'), (0, 'NE2')]
		nameDict   = {'CCPN': 'CD', 'INTERNAL_0': 'CD', 'IUPAC': 'CD', 'AQUA': 'CD', 'BMRBd': 'CD', 'INTERNAL_1': 'CD', 'CYANA': 'CD', 'CYANA2': 'CD', 'PDB': 'CD', 'XPLOR': 'CD'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'C_BYL'
		spinType   = '13C'
		shift      = NTdict( average = 179.63, sd = 1.4099999999999999 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> OE1     
	#---------------------------------------------------------------
		topology   = [(0, 'CD')]
		nameDict   = {'CCPN': 'OE1', 'INTERNAL_0': 'OE1', 'IUPAC': 'OE1', 'AQUA': 'OE1', 'BMRBd': 'OE1', 'INTERNAL_1': 'OE1', 'CYANA': 'OE1', 'CYANA2': 'OE1', 'PDB': 'OE1', 'XPLOR': 'OE1'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'O_BYL'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> NE2     
	#---------------------------------------------------------------
		topology   = [(0, 'CD'), (0, 'HE21'), (0, 'HE22')]
		nameDict   = {'CCPN': 'NE2', 'INTERNAL_0': 'NE2', 'IUPAC': 'NE2', 'AQUA': 'NE2', 'BMRBd': 'NE2', 'INTERNAL_1': 'NE2', 'CYANA': 'NE2', 'CYANA2': 'NE2', 'PDB': 'NE2', 'XPLOR': 'NE2'}
		aliases    = []
		pseudo     = None
		real       = []
		type       = 'N_AMI'
		spinType   = '15N'
		shift      = NTdict( average = 111.79000000000001, sd = 3.3999999999999999 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HE21    
	#---------------------------------------------------------------
		topology   = [(0, 'NE2')]
		nameDict   = {'CCPN': 'HE21', 'INTERNAL_0': 'HE21', 'IUPAC': 'HE21', 'AQUA': 'HE21', 'BMRBd': 'HE21', 'INTERNAL_1': 'HE21', 'CYANA': 'HE21', 'CYANA2': 'HE21', 'PDB': '2HE2', 'XPLOR': 'HE21'}
		aliases    = []
		pseudo     = 'QE2'
		real       = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 7.1900000000000004, sd = 0.51000000000000001 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HE22    
	#---------------------------------------------------------------
		topology   = [(0, 'NE2')]
		nameDict   = {'CCPN': 'HE22', 'INTERNAL_0': 'HE22', 'IUPAC': 'HE22', 'AQUA': 'HE22', 'BMRBd': 'HE22', 'INTERNAL_1': 'HE22', 'CYANA': 'HE22', 'CYANA2': 'HE22', 'PDB': '1HE2', 'XPLOR': 'HE22'}
		aliases    = []
		pseudo     = 'QE2'
		real       = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 7.0499999999999998, sd = 0.5 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QE2     
	#---------------------------------------------------------------
		topology   = [(0, 'NE2')]
		nameDict   = {'CCPN': 'HE2*', 'INTERNAL_0': 'QE2', 'IUPAC': 'QE', 'AQUA': 'QE', 'BMRBd': None, 'INTERNAL_1': 'QE', 'CYANA': 'QE2', 'CYANA2': 'QE2', 'PDB': None, 'XPLOR': 'HE2*,HE2#,HE2%,HE2+,HE*,HE#'}
		aliases    = ['QE', 'QE2']
		pseudo     = None
		real       = ['HE21', 'HE22']
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 7.1200000000000001, sd = 0.505 )
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
		shift      = NTdict( average = 176.38, sd = 1.95 )
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
		shift      = NTdict( average = 8.2100000000000009, sd = 0.62 )
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
		shift      = NTdict( average = 8.2100000000000009, sd = 0.62 )
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
		shift      = NTdict( average = 8.2100000000000009, sd = 0.62 )
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
