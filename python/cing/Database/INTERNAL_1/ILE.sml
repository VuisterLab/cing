<SML> 0.25

#=======================================================================
#             	name     convention
<ResidueDef>  	ILE      INTERNAL_1
#=======================================================================
	commonName = 'ILE'
	shortName  = 'I'
	comment    = 'Regular Ile residue'
	nameDict   = {'STAP': 'ILE', 'IUPAC': 'ILE', 'CYANA': 'ILE', 'PDB': 'ILE', 'XPLOR': 'ILE', 'CCPN': 'protein Ile neutral', 'BMRBd': 'ILE', 'AQUA': 'ILE', 'INTERNAL_0': 'ILE', 'INTERNAL_1': 'ILE', 'CYANA2': 'ILE'}
	properties = ['protein', 'aliphatic', 'methyl_containing', 'large', 'neutral']

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
		atoms    = [(0, 'N'), (0, 'CA'), (0, 'CB'), (0, 'CG1')]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> CHI2    
	#---------------------------------------------------------------
		atoms    = [(0, 'CA'), (0, 'CB'), (0, 'CG1'), (0, 'CD1')]
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
		shift      = NTdict( average = 121.59, sd = 4.86 )
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
		shift      = NTdict( average = 8.28, sd = 0.71 )
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
		shift      = NTdict( average = 61.6, sd = 2.78 )
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
		shift      = NTdict( average = 4.19, sd = 0.58 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CB      
	#---------------------------------------------------------------
		topology   = [(0, 'CA'), (0, 'HB'), (0, 'CG2'), (0, 'CG1')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'CB', 'IUPAC': 'CB', 'CYANA': 'CB', 'PDB': 'CB', 'XPLOR': 'CB', 'CCPN': 'CB', 'BMRBd': 'CB', 'AQUA': 'CB', 'INTERNAL_0': 'CB', 'INTERNAL_1': 'CB', 'CYANA2': 'CB'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 38.66, sd = 2.75 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HB      
	#---------------------------------------------------------------
		topology   = [(0, 'CB')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'HB', 'IUPAC': 'HB', 'CYANA': 'HB', 'PDB': 'HB', 'XPLOR': 'HB', 'CCPN': 'HB', 'BMRBd': 'HB', 'AQUA': 'HB', 'INTERNAL_0': 'HB', 'INTERNAL_1': 'HB', 'CYANA2': 'HB'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.8, sd = 0.54 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> MG      
	#---------------------------------------------------------------
		topology   = [(0, 'CG2')]
		real       = ['HG21', 'HG22', 'HG23']
		pseudo     = None
		nameDict   = {'STAP': None, 'IUPAC': 'MG', 'CYANA': 'QG2', 'PDB': None, 'XPLOR': 'HG2*,HG2#,HG2%,HG2+', 'CCPN': 'HG2*', 'BMRBd': 'HG2', 'AQUA': 'MG', 'INTERNAL_0': 'QG2', 'INTERNAL_1': 'MG', 'CYANA2': 'QG2'}
		aliases    = ['MG', 'QG2']
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 0.78, sd = 0.4 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isMethylProton', 'methylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CG2     
	#---------------------------------------------------------------
		topology   = [(0, 'CB'), (0, 'HG21'), (0, 'HG22'), (0, 'HG23')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'CG2', 'IUPAC': 'CG2', 'CYANA': 'CG2', 'PDB': 'CG2', 'XPLOR': 'CG2', 'CCPN': 'CG2', 'BMRBd': 'CG2', 'AQUA': 'CG2', 'INTERNAL_0': 'CG2', 'INTERNAL_1': 'CG2', 'CYANA2': 'CG2'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 17.67, sd = 2.92 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HG21    
	#---------------------------------------------------------------
		topology   = [(0, 'CG2')]
		real       = []
		pseudo     = 'MG'
		nameDict   = {'STAP': 'HG21', 'IUPAC': 'HG21', 'CYANA': 'HG21', 'PDB': '1HG2', 'XPLOR': 'HG21', 'CCPN': 'HG21', 'BMRBd': None, 'AQUA': 'HG21', 'INTERNAL_0': 'HG21', 'INTERNAL_1': 'HG21', 'CYANA2': 'HG21'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isMethylProton', 'methylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HG22    
	#---------------------------------------------------------------
		topology   = [(0, 'CG2')]
		real       = []
		pseudo     = 'MG'
		nameDict   = {'STAP': 'HG22', 'IUPAC': 'HG22', 'CYANA': 'HG22', 'PDB': '2HG2', 'XPLOR': 'HG22', 'CCPN': 'HG22', 'BMRBd': None, 'AQUA': 'HG22', 'INTERNAL_0': 'HG22', 'INTERNAL_1': 'HG22', 'CYANA2': 'HG22'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isMethylProton', 'methylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HG23    
	#---------------------------------------------------------------
		topology   = [(0, 'CG2')]
		real       = []
		pseudo     = 'MG'
		nameDict   = {'STAP': 'HG23', 'IUPAC': 'HG23', 'CYANA': 'HG23', 'PDB': '3HG2', 'XPLOR': 'HG23', 'CCPN': 'HG23', 'BMRBd': None, 'AQUA': 'HG23', 'INTERNAL_0': 'HG23', 'INTERNAL_1': 'HG23', 'CYANA2': 'HG23'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isMethylProton', 'methylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CG1     
	#---------------------------------------------------------------
		topology   = [(0, 'CB'), (0, 'HG12'), (0, 'HG13'), (0, 'CD1')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'CG1', 'IUPAC': 'CG1', 'CYANA': 'CG1', 'PDB': 'CG1', 'XPLOR': 'CG1', 'CCPN': 'CG1', 'BMRBd': 'CG1', 'AQUA': 'CG1', 'INTERNAL_0': 'CG1', 'INTERNAL_1': 'CG1', 'CYANA2': 'CG1'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 27.8, sd = 3.81 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HG12    
	#---------------------------------------------------------------
		topology   = [(0, 'CG1')]
		real       = []
		pseudo     = 'QG'
		nameDict   = {'STAP': 'HG12', 'IUPAC': 'HG12', 'CYANA': 'HG12', 'PDB': '1HG1', 'XPLOR': 'HG12', 'CCPN': 'HG12', 'BMRBd': 'HG12', 'AQUA': 'HG12', 'INTERNAL_0': 'HG12', 'INTERNAL_1': 'HG12', 'CYANA2': 'HG12'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.26, sd = 0.62 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HG13    
	#---------------------------------------------------------------
		topology   = [(0, 'CG1')]
		real       = []
		pseudo     = 'QG'
		nameDict   = {'STAP': 'HG11', 'IUPAC': 'HG13', 'CYANA': 'HG13', 'PDB': '2HG1', 'XPLOR': 'HG11', 'CCPN': 'HG13', 'BMRBd': 'HG13', 'AQUA': 'HG13', 'INTERNAL_0': 'HG13', 'INTERNAL_1': 'HG13', 'CYANA2': 'HG13'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.22, sd = 0.73 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QG      
	#---------------------------------------------------------------
		topology   = [(0, 'CG1')]
		real       = ['HG12', 'HG13']
		pseudo     = None
		nameDict   = {'STAP': None, 'IUPAC': 'QG', 'CYANA': 'QG1', 'PDB': None, 'XPLOR': 'HG1*,HG1#,HG1%,HG1+', 'CCPN': 'HG1*', 'BMRBd': None, 'AQUA': 'QG', 'INTERNAL_0': 'QG1', 'INTERNAL_1': 'QG', 'CYANA2': 'QG1'}
		aliases    = ['QG', 'QG1']
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 1.24, sd = 0.675 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> MD      
	#---------------------------------------------------------------
		topology   = [(0, 'CD1')]
		real       = ['HD11', 'HD12', 'HD13']
		pseudo     = None
		nameDict   = {'STAP': None, 'IUPAC': 'MD', 'CYANA': 'QD1', 'PDB': None, 'XPLOR': 'HD1*,HD1#,HD1%,HD1+,HD*,HD#', 'CCPN': 'HD1*', 'BMRBd': 'HD1', 'AQUA': 'MD', 'INTERNAL_0': 'QD1', 'INTERNAL_1': 'MD', 'CYANA2': 'QD1'}
		aliases    = ['MD', 'QD1']
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 0.67, sd = 0.45 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isMethylProton', 'methylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CD1     
	#---------------------------------------------------------------
		topology   = [(0, 'CG1'), (0, 'HD11'), (0, 'HD12'), (0, 'HD13')]
		real       = []
		pseudo     = None
		nameDict   = {'STAP': 'CD', 'IUPAC': 'CD1', 'CYANA': 'CD1', 'PDB': 'CD1', 'XPLOR': 'CD1', 'CCPN': 'CD1', 'BMRBd': 'CD1', 'AQUA': 'CD1', 'INTERNAL_0': 'CD1', 'INTERNAL_1': 'CD1', 'CYANA2': 'CD1'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 13.69, sd = 3.6 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HD11    
	#---------------------------------------------------------------
		topology   = [(0, 'CD1')]
		real       = []
		pseudo     = 'MD'
		nameDict   = {'STAP': 'HD1', 'IUPAC': 'HD11', 'CYANA': 'HD11', 'PDB': '1HD1', 'XPLOR': 'HD11', 'CCPN': 'HD11', 'BMRBd': None, 'AQUA': 'HD11', 'INTERNAL_0': 'HD11', 'INTERNAL_1': 'HD11', 'CYANA2': 'HD11'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isMethylProton', 'methylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HD12    
	#---------------------------------------------------------------
		topology   = [(0, 'CD1')]
		real       = []
		pseudo     = 'MD'
		nameDict   = {'STAP': 'HD2', 'IUPAC': 'HD12', 'CYANA': 'HD12', 'PDB': '2HD1', 'XPLOR': 'HD12', 'CCPN': 'HD12', 'BMRBd': None, 'AQUA': 'HD12', 'INTERNAL_0': 'HD12', 'INTERNAL_1': 'HD12', 'CYANA2': 'HD12'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isMethylProton', 'methylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HD13    
	#---------------------------------------------------------------
		topology   = [(0, 'CD1')]
		real       = []
		pseudo     = 'MD'
		nameDict   = {'STAP': 'HD3', 'IUPAC': 'HD13', 'CYANA': 'HD13', 'PDB': '3HD1', 'XPLOR': 'HD13', 'CCPN': 'HD13', 'BMRBd': None, 'AQUA': 'HD13', 'INTERNAL_0': 'HD13', 'INTERNAL_1': 'HD13', 'CYANA2': 'HD13'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isMethylProton', 'methylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
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
		shift      = NTdict( average = 175.94, sd = 1.93 )
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
		shift      = NTdict( average = 8.28, sd = 0.71 )
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
		shift      = NTdict( average = 8.28, sd = 0.71 )
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
		shift      = NTdict( average = 8.28, sd = 0.71 )
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
