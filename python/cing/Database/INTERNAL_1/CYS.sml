<SML> 0.25

#=======================================================================
#             	name     convention
<ResidueDef>  	CYS      INTERNAL_1
#=======================================================================
	commonName = 'CYS'
	shortName  = 'C'
	comment    = 'Regular Cys residue'
	nameDict   = {'STAP': 'CYS', 'IUPAC': 'CYS', 'CYANA': 'CYS', 'PDB': 'CYS', 'XPLOR': 'CYS', 'CCPN': 'protein Cys prot:HG', 'BMRBd': 'CYS', 'AQUA': 'CYS', 'INTERNAL_0': 'CYS', 'INTERNAL_1': 'CYS', 'CYANA2': 'CYS'}
	properties = ['protein', 'aliphatic', 'polar', 'isCystine']

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
		atoms    = [(0, 'N'), (0, 'CA'), (0, 'CB'), (0, 'SG')]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> CHI2    
	#---------------------------------------------------------------
		atoms    = [(0, 'CA'), (0, 'CB'), (0, 'SG'), (0, 'HG')]
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
		shift      = NTdict( average = 119.97, sd = 4.7 )
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
		shift      = NTdict( average = 8.41, sd = 0.69 )
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
		shift      = NTdict( average = 57.74, sd = 3.47 )
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
		shift      = NTdict( average = 4.81, sd = 1.7 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CB      
	#---------------------------------------------------------------
		topology   = [(0, 'CA'), (0, 'HB2'), (0, 'HB3'), (0, 'SG')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'CB', 'IUPAC': 'CB', 'CYANA': 'CB', 'PDB': 'CB', 'XPLOR': 'CB', 'CCPN': 'CB', 'BMRBd': 'CB', 'AQUA': 'CB', 'INTERNAL_0': 'CB', 'INTERNAL_1': 'CB', 'CYANA2': 'CB'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 33.86, sd = 6.64 )
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
		shift      = NTdict( average = 3.27, sd = 4.48 )
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
		shift      = NTdict( average = 3.23, sd = 4.68 )
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
		shift      = NTdict( average = 3.25, sd = 4.58 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> SG      
	#---------------------------------------------------------------
		topology   = [(0, 'CB'), (0, 'HG')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'SG', 'IUPAC': 'SG', 'CYANA': 'SG', 'PDB': 'SG', 'XPLOR': 'SG', 'CCPN': 'SG', 'BMRBd': 'SG', 'AQUA': 'SG', 'INTERNAL_0': 'SG', 'INTERNAL_1': 'SG', 'CYANA2': 'SG'}
		aliases    = []
		type       = 'S_RED'
		spinType   = '32S'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isSulfur', 'isSulphur', 'sulfur', 'sulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HG      
	#---------------------------------------------------------------
		topology   = [(0, 'SG')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'HG1', 'IUPAC': 'HG', 'CYANA': 'HG', 'PDB': 'HG', 'XPLOR': 'HG', 'CCPN': 'HG', 'BMRBd': 'HG', 'AQUA': 'HG', 'INTERNAL_0': 'HG', 'INTERNAL_1': 'HG', 'CYANA2': 'HG'}
		aliases    = []
		type       = 'H_SUL'
		spinType   = '1H'
		shift      = NTdict( average = 2.43, sd = 1.69 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
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
		shift      = NTdict( average = 174.76, sd = 4.99 )
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
		shift      = NTdict( average = 8.41, sd = 0.69 )
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
		shift      = NTdict( average = 8.41, sd = 0.69 )
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
		shift      = NTdict( average = 8.41, sd = 0.69 )
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
